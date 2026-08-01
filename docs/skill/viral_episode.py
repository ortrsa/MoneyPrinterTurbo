#!/usr/bin/env python3
"""
端到端生成一集"事实合集"短视频：脚本 -> 语音 -> 素材 -> 逐词高亮字幕叠加层。

用法::

    uv run python docs/skill/viral_episode.py \
        --facts-file facts.txt --episode 2 [--dry-run]

`facts.txt` 每行一条原始事实（中英文均可，脚本会按 `--language` 改写）。

流程
----
1. 用 LLM 把每条原始事实改写成 1-2 句的口播稿，并生成开场钩子。
2. 拼成完整脚本，交给 MoneyPrinterTurbo 生成"无字幕"成片
   （字幕交给叠加层，避免和 MoviePy 字幕重叠）。
3. 用 faster-whisper 从成片音频反解逐词时间轴。
4. 把每条事实的文本对齐到词序列，得到计数器/进度条所需的区间。
5. 生成并烧录 ASS 叠加层：逐词高亮字幕 + `3/6` 计数器 + 进度条。
6. 输出成片路径与可直接发布的标题/文案/话题标签。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger  # noqa: E402

from app.services import viral  # noqa: E402

# 研究结论：50-60 秒档位在事实类短视频里平均表现最好，而完播率仍是核心指标。
# 按 150-170 WPM 的口播语速，约 50 秒对应 125-140 个词，正好放得下 6 条事实。
DEFAULT_FACT_COUNT = 6

# 一组常见的、读起来明显"像 AI 写的"词汇/说法，直接写进 prompt 里禁止，
# 比重新生成后再事后过滤要便宜、也更可靠——模型一开始就不会往这个方向写。
AI_TELL_BLOCKLIST = (
    "here's the thing, let's dive in, game-changer, revolutionary, unlock, "
    "unleash, in today's fast-paced world, it's important to note, leverage, "
    "delve, boasts, testament to, elevate, tapestry, in conclusion, moreover, "
    "furthermore"
)

# 段落开头的过渡词、以及只在 25 词内容里就用长破折号的习惯，都是"AI 腔"的
# 常见来源，和 AI_TELL_BLOCKLIST 一起作为负向约束写进 prompt。
HUMANIZATION_NOTE = (
    "Do not start a sentence with 'However', 'Moreover', or 'Overall'. "
    "Use contractions where natural (it's, that's, you're). Vary sentence "
    "length instead of writing uniform-length sentences."
)

# 每条事实的词数上限直接决定成片长度：25 词一条大约 8-9 秒口播，六条就是
# 50-60 秒；要压到 20 秒以内（增长指南 Rank 1 的硬指标）只能同时减少条数
# 并把每条压到 14 词左右（约 4-5 秒）。所以词数必须可调，不能写死。
DEFAULT_FACT_MAX_WORDS = 25

FACT_PROMPT = (
    "Rewrite this fact as ONE or TWO short punchy sentences for a rapid-fire facts "
    "compilation video. Open directly with the surprising claim - no greeting, no "
    "'did you know', no preamble, no filler words. Keep it under {max_words} words. "
    f"Never use any of these overused AI-writing phrases: {AI_TELL_BLOCKLIST}. "
    f"{HUMANIZATION_NOTE} "
    "Write in {language}."
)

# 三种经过验证的开场钩子结构，取代原本笼统的"写一句吸引人的开场"——
# 给模型具体的句式模板，比只说"要有悬念"更容易稳定产出好结果。
HOOK_PROMPT = (
    "Write a single opening hook sentence, at most 12 words, for a short video that "
    "lists {count} surprising facts. Use ONE of these three structures, whichever "
    "fits best: "
    "(1) Prediction + stakes - 'This is the [thing] that [consequence]'; "
    "(2) Before/after compression - 'What used to take [X] now just [Y]'; "
    "(3) A specific curiosity gap that promises a real payoff, not a vague tease. "
    "Do not greet the viewer. Do not use 'did you know'. "
    f"Never use any of these overused AI-writing phrases: {AI_TELL_BLOCKLIST}. "
    f"{HUMANIZATION_NOTE} "
    "Return only the sentence, in {language}."
)

# 明确要求关注/评论是被允许的，被压制的是"点赞就关注"这类模板化空话。
# 但同一句结尾反复用会让系列显得自动化，所以正确做法是每集在内容日历里
# 单独写一句、并轮换 FOLLOW / COMMENT / BOTH。这里的默认值只是兜底，
# 调用方应当始终通过 --outro 传入当集专属文案。
DEFAULT_OUTRO = (
    "Follow this page so episode {next_episode} actually reaches you."
)


def find_ai_tells(text: str) -> list[str]:
    """
    在生成好的文案里做一次事后检查，看有没有漏网的 AI 腔调用词。

    prompt 里已经明确禁止了这些词，这里只是兜底——LLM 偶尔还是会忽略指令。
    检测到时只记录日志，不做自动改写：自动改写有改变原意的风险，不如让人
    决定是否要重新生成这一句。
    """
    lowered = text.lower()
    return [
        term.strip()
        for term in AI_TELL_BLOCKLIST.split(",")
        if term.strip() and term.strip() in lowered
    ]


# 高唤醒度、负向措辞往往比正向措辞点击率更高；这里只是一个粗糙的启发式词表，
# 不是精确的情绪分类器，只用来做方向性打分，不作为唯一判据。
_HIGH_AROUSAL_WORDS = (
    "shocking secret hidden banned exposed mistake wrong lie danger deadly "
    "warning brain blind never nobody worst destroy"
).split()


def score_title(title: str) -> dict:
    """
    只用于「独立单条」视频的自由标题，不用于本频道固定的系列标题
    （"AI Unfiltered 3 👀" 这类标题不需要打分，也不该被打分逻辑影响）。

    三个维度各打 0-3 分，总分 9 分，7 分为发布门槛。这是启发式规则，不是
    精确度量——目的是给一个方向性信号，用来决定"这个标题要不要再改一版"，
    而不是自动卡死发布流程。
    """
    lowered = title.lower()

    specificity = 3 if any(ch.isdigit() for ch in title) else 0

    emotion_hits = sum(1 for word in _HIGH_AROUSAL_WORDS if word in lowered)
    emotion = min(3, emotion_hits * 2) if emotion_hits else 0

    # 好奇心信号：标题提出问题/悬念但不直接给出答案。粗略地用问号、
    # "why/how/secret/reason" 这类词，或者标题明显没有把结论写全来近似。
    curiosity_markers = ("?", "why", "how", "secret", "reason", "this is")
    curiosity = 3 if any(m in lowered for m in curiosity_markers) else 1

    total = specificity + emotion + curiosity
    return {
        "specificity": specificity,
        "emotion": emotion,
        "curiosity": curiosity,
        "total": total,
        "passes": total >= 7,
    }


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    logger.info("$ " + " ".join(command[:6]) + (" ..." if len(command) > 6 else ""))
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True)


# 五个批判视角合并成一次调用，而不是五次独立的 LLM 请求：对一条 12 词的
# 钩子来说，五次往返的成本和延迟不值得，把五个视角都交给同一次调用去权衡
# 通常就够了。只精炼钩子这一句——它是整条视频里杠杆最大的一句话。
HOOK_CRITIQUE_PROMPT = (
    "You are five critics reviewing this video hook, one after another: "
    "(1) a skeptic asking why anyone should care, "
    "(2) a subject-matter expert checking it is not misleading or wrong, "
    "(3) someone scrolling fast who will only stop for a real pattern interrupt, "
    "(4) a competitor who has seen a dozen similar videos and wants real difference, "
    "(5) an editor who cuts anything that does not earn its place. "
    "Hook: \"{hook}\"\n"
    "Fact this hook is teasing: \"{first_fact}\"\n"
    "If the hook already survives all five, return it completely unchanged. "
    "If not, return an improved version, still at most 12 words, still no greeting "
    "and no 'did you know'. Return ONLY the final hook sentence, nothing else."
)


def refine_hook(hook: str, first_fact: str, language: str) -> str:
    """对开场钩子跑一次五视角合并批判，返回原句或改写后的句子。"""
    from app.services import llm

    critique_prompt = HOOK_CRITIQUE_PROMPT.format(hook=hook, first_fact=first_fact)
    revised = llm.generate_script(
        video_subject=hook,
        language=language,
        paragraph_number=1,
        video_script_prompt=critique_prompt,
    ).strip()
    revised = revised.split(". ")[0].strip().rstrip(".") + "."
    if revised.lower() != hook.lower():
        logger.info(f"hook refined: {hook!r} -> {revised!r}")
    return revised


def build_scripts(
    raw_facts: list[str],
    language: str,
    episode: int,
    outro: str | None = None,
    hook: str | None = None,
    fact_max_words: int = DEFAULT_FACT_MAX_WORDS,
) -> dict:
    """调用项目内的 LLM 服务，把原始事实改写成口播稿并生成钩子。"""
    from app.services import llm

    fact_lines = []
    for fact in raw_facts:
        line = llm.generate_script(
            video_subject=fact,
            language=language,
            paragraph_number=1,
            video_script_prompt=FACT_PROMPT.format(
                language=language, max_words=fact_max_words
            ),
        ).strip()
        logger.info(f"fact: {line}")
        tells = find_ai_tells(line)
        if tells:
            logger.warning(f"AI-tell phrase slipped through despite the prompt guard: {tells} in: {line}")
        fact_lines.append(line)

    if hook:
        # 内容日历里已经写好了钩子：直接采用，避免每集都被 LLM 写成同一句
        logger.info(f"hook (provided): {hook}")
        resolved_outro = outro or DEFAULT_OUTRO.format(next_episode=episode + 1)
        return {"hook": hook.strip(), "facts": fact_lines, "outro": resolved_outro}

    hook = llm.generate_script(
        video_subject=f"{len(fact_lines)} surprising facts",
        language=language,
        paragraph_number=1,
        video_script_prompt=HOOK_PROMPT.format(
            count=len(fact_lines), language=language
        ),
    ).strip()
    # 钩子必须只有一句；LLM 偶尔会多写，这里截断到第一个句号
    hook = hook.split(". ")[0].strip().rstrip(".") + "."
    logger.info(f"hook: {hook}")
    # 只有自由生成的钩子才跑五视角批判；日历里手写好的钩子已经是人工把关过的，
    # 不需要再让 LLM 重写一遍。
    hook = refine_hook(hook, first_fact=fact_lines[0] if fact_lines else "", language=language)
    tells = find_ai_tells(hook)
    if tells:
        logger.warning(f"AI-tell phrase slipped through despite the prompt guard: {tells} in: {hook}")

    resolved_outro = outro or DEFAULT_OUTRO.format(next_episode=episode + 1)
    return {"hook": hook, "facts": fact_lines, "outro": resolved_outro}


# 每段单独出搜索词。关键约束是"可被素材库搜到"——LLM 很容易写出
# "artificial intelligence concept"这种在图库里只会返回蓝色电路板抽象画面的词，
# 所以这里强制要求写成"能被拍下来的具体场景"。
SEGMENT_TERMS_PROMPT = (
    "You are choosing stock-footage search terms for ONE line of a narrated video.\n"
    'Line: "{text}"\n\n'
    "Return exactly 3 search terms, comma-separated.\n"
    "Rules:\n"
    "- If the line names a specific animal, species, object or place, the FIRST "
    "term must be that noun ON ITS OWN, with no describing words. Stock search "
    "dilutes a rare keyword when it is padded out: 'wombat' returns wombats, "
    "'wombat walking in grass' returns grass. Make the other two terms wider, so "
    "there is still usable footage if the bare noun finds nothing.\n"
    "- Otherwise each term is 2-4 plain English words naming a scene that could "
    "actually be filmed: concrete objects, people doing something, or real places.\n"
    "- No abstract concept words ('innovation', 'future', 'technology concept', "
    "'data abstract') - stock sites return generic blue circuit-board filler for those.\n"
    "- If the line is abstract, pick the closest literal scene a viewer would "
    "connect to it. Example: a line about voice cloning -> 'person speaking microphone'.\n"
    "- Never put a year or a date in a term. Stock libraries do not tag footage "
    "by the year an event happened, so '1956 summer workshop' matches nothing and "
    "falls back to generic filler. Describe how the period looked instead: "
    "'vintage lecture hall', 'retro computer room'.\n"
    "- No brand names, no on-screen text requests, no camera directions.\n"
    "Return ONLY the comma-separated terms, nothing else."
)

# 开场 3 秒对应研究里的 Declare 阶段：画面必须一眼看懂，不能让观众先花
# 半秒去解析构图。所以钩子这一段额外要求单一主体、干净背景。
HOOK_TERMS_EXTRA = (
    " This is the opening shot, so every term must describe a CLEAN scene with a "
    "single clear subject, strong lighting and an uncluttered background."
)


# 句尾误判的常见来源：这些缩写后面的点不是句号。
_ABBREVIATIONS = frozenset(
    "mr. mrs. ms. dr. prof. st. jr. sr. vs. etc. fig. no. approx. inc. ltd. dept.".split()
)


def _ends_with_abbreviation(text: str) -> bool:
    """判断一段文字是不是停在缩写上（因而不该在这里断句）。"""
    match = re.search(r"(\S+)\s*$", text)
    if not match:
        return False
    token = match.group(1)
    if token.lower() in _ABBREVIATIONS:
        return True
    # 首字母缩写，如 "U.S."、"A.I."：结尾是"单个字母 + 点"
    return bool(re.search(r"(?:^|\W)[A-Za-z]\.$", token))


def format_caption_paragraphs(caption: str) -> str:
    """
    每句之间空一行。

    LLM 返回的是一整块文字，在 YouTube 描述框里会挤成一堵墙，观众不会读。
    每条事实各占一段之后才扫得动。

    断句先要求"句号 + 空格 + 大写字母"，这样 "0.4" 这类小数不会被切开；
    但这条规则挡不住 "U.S. Constitution"——本集脚本里就有这个词。所以切完
    之后再把停在缩写上的碎片并回去。Python 的 lookbehind 要求定长，
    没法在正则里直接排除长度不一的缩写，只能事后合并。
    """
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", caption.strip())

    merged: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if merged and _ends_with_abbreviation(merged[-1]):
            merged[-1] = f"{merged[-1]} {part}"
        else:
            merged.append(part)
    return "\n\n".join(merged)


def generate_segment_terms(
    segments: list[str],
    language: str,
    overrides: dict[int, list[str]] | None = None,
) -> list[list[str]]:
    """为每段口播各生成一组素材搜索词。"""
    from app.services import llm

    overrides = overrides or {}
    all_terms: list[list[str]] = []
    used: list[str] = []
    for index, text in enumerate(segments):
        # 有些主题图库就是没有对得上的素材（树懒），或者同名词会命中完全
        # 不同的东西（"octopus" 会返回章鱼料理）。这类段落靠改 prompt 是
        # 治不好的，只能人工把关键词钉死，所以这里允许按段覆盖。
        if index in overrides:
            terms = overrides[index]
            logger.info(f"segment {index} terms (override): {terms}")
            all_terms.append(terms)
            used.extend(terms)
            continue

        prompt = SEGMENT_TERMS_PROMPT.format(text=text)
        if index == 0:
            prompt += HOOK_TERMS_EXTRA
        if used:
            # 同一集里各条事实主题相近时，模型很容易每段都给出"person typing laptop"。
            # 把已用过的词回传，强制它换一个角度，避免整条视频看起来都是同一个画面。
            #
            # 但"不要重复"绝不能把主体本身挤掉。之前钩子用了 wombat，这条
            # 禁令就让讲袋熊肠道的那一段改用 "cubical feces"，图库回给了
            # 一排方形写字楼。所以这里只约束陪衬镜头，并明确说明主体名词
            # 该重复就重复。
            prompt += (
                "\nThese terms already appear earlier in this same video. Do not "
                "repeat them AS SUPPORTING SHOTS, and do not return near-identical "
                "wording for them: " + "; ".join(used) + "\n"
                "This does NOT apply to the subject itself. If this line is about "
                "the same animal, object or place as an earlier line, the first "
                "term must still be that noun, even though it repeats. Showing the "
                "right subject twice is correct; switching to a different subject "
                "to avoid repeating a word is wrong."
            )
        raw = llm.generate_script(
            video_subject=text,
            language=language,
            paragraph_number=1,
            video_script_prompt=prompt,
        ).strip()

        terms = [t.strip(" .\"'") for t in raw.replace("\n", ",").split(",")]
        terms = [t for t in terms if t and len(t.split()) <= 6][:3]
        if not terms:
            # LLM 偶尔会返回一整句话；退回用这段口播的前几个词去搜，
            # 至少还和当前主题相关，比落回全局通用素材好。
            terms = [" ".join(text.split()[:4])]
        logger.info(f"segment {index} terms: {terms}")
        all_terms.append(terms)
        used.extend(terms)
    return all_terms


def generate_audio_only(
    script_text: str,
    subject: str,
    voice_name: str,
    task_id: str,
    root: Path,
    threads: int,
) -> Path:
    """
    只跑到音频阶段，返回 audio.mp3 路径。

    画面要对齐口播就必须先有真实音频：每段的起止时间来自 whisper，
    而不是按字数估算。mpt_agent.py 固定 `--stop-at video`，所以这里直接调 cli.py。
    """
    command = [
        "uv", "run", "--no-project", "--python", "3.11", "python", "cli.py",
        "--task-id", task_id,
        "--video-subject", subject,
        "--video-script", script_text,
        "--voice-name", voice_name,
        "--n-threads", str(threads),
        "--no-subtitle-enabled",
        "--stop-at", "audio",
    ]
    result = run(command, cwd=root)
    if result.returncode != 0:
        tail = (result.stdout or "") + (result.stderr or "")
        raise RuntimeError("audio generation failed:\n" + tail[-2000:])

    audio_path = root / "storage" / "tasks" / task_id / "audio.mp3"
    if not audio_path.is_file():
        raise RuntimeError(f"audio stage finished but {audio_path} is missing")
    return audio_path


def generate_base_video(
    script_text: str,
    subject: str,
    voice_name: str,
    video_terms: str,
    root: Path,
    skill_dir: Path,
    threads: int,
) -> Path:
    """跑 MoneyPrinterTurbo 生成无字幕成片，返回 final-1.mp4 的路径。"""
    command = [
        "uv", "run", "--no-project", "--python", "3.11", "python", "mpt_agent.py",
        "--root", str(root),
        "--subject", subject,
        "--",
        "--voice-name", voice_name,
        "--video-source", "pexels",
        "--video-script", script_text,
        "--video-terms", video_terms,
        "--n-threads", str(threads),
        # 字幕由 ASS 叠加层负责，这里必须关掉，否则两层字幕会叠在一起
        "--no-subtitle-enabled",
    ]
    result = run(command, cwd=skill_dir)
    if result.returncode != 0:
        tail = (result.stdout or "") + (result.stderr or "")
        raise RuntimeError("base video generation failed:\n" + tail[-2000:])

    video_file = ""
    for line in (result.stdout or "").splitlines():
        if line.startswith("VIDEO_FILE="):
            video_file = line.split("=", 1)[1].strip()
    if not video_file:
        raise RuntimeError("could not find VIDEO_FILE in helper output")
    return Path(video_file)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--facts-file", required=True, type=Path)
    parser.add_argument("--episode", type=int, default=1)
    parser.add_argument("--series-name", default="Random But True Facts")
    parser.add_argument("--language", default="en-US")
    parser.add_argument("--voice-name", default="gemini:Puck-Male")
    parser.add_argument("--fact-count", type=int, default=DEFAULT_FACT_COUNT)
    parser.add_argument(
        "--fact-max-words",
        type=int,
        default=DEFAULT_FACT_MAX_WORDS,
        help=(
            "每条事实口播的词数上限，直接决定成片长度。25 词约 8-9 秒一条；"
            "要做 20 秒以内的短版本，配合 --fact-count 3 用 14 左右。"
        ),
    )
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--video-terms",
        default="kinetic sand cutting satisfying,slime asmr satisfying,"
        "hydraulic press crushing,soap cutting satisfying,"
        "paint pouring abstract satisfying,glass cutting satisfying",
    )
    parser.add_argument(
        "--outro",
        default=None,
        help=(
            "结尾口播语。应当每集不同：绑定当集内容，并在 FOLLOW / COMMENT / "
            "BOTH 之间轮换（内容日历的 outro_line_spoken 与 cta_type 两列即为此设计）。"
            "不传则退回一句通用兜底文案。"
        ),
    )
    parser.add_argument(
        "--hook",
        default=None,
        help="开场钩子；不传则由 LLM 生成。内容日历里逐集写好钩子可避免开头雷同。",
    )
    parser.add_argument(
        "--footage-mode",
        choices=("synced", "generic"),
        default="synced",
        help=(
            "synced：每段口播单独出搜索词、单独取材，画面精确铺在该段时间窗里，"
            "讲到第 N 条事实时画面就是第 N 条的内容（默认）。"
            "generic：旧行为，用 --video-terms 的全局素材池，画面与口播无关。"
        ),
    )
    parser.add_argument(
        "--segment-terms",
        default=None,
        help=(
            "按段钉死素材搜索词，JSON 对象：段序号 -> 逗号分隔的关键词。"
            "段序号 0 是钩子，1..N 是每条事实，最后一段是结尾。"
            "用于图库确实没有对应素材、或同名词会命中别的东西的段落"
            '（例："{\\"5\\": \\"octopus underwater,coral reef\\"}"）。'
        ),
    )
    parser.add_argument("--highlight-color", default="#FFE500")
    parser.add_argument("--words-per-caption", type=int, default=3)
    parser.add_argument("--whisper-model", default="base.en")
    parser.add_argument(
        "--threads",
        type=int,
        default=max(1, os.cpu_count() or 2),
        help="ffmpeg 编码线程数，默认用满可用核心（项目默认值 2 只用了一半算力）",
    )
    parser.add_argument(
        "--title",
        default=None,
        help=(
            "完整标题，直接使用，不再用 --series-name/--episode 拼接。"
            "内容日历里的标题列应始终用这个参数传入——系列名不一定等于标题前缀"
            "（例如系列名 'Random But True' 但标题是 'Random But True Facts N'），"
            "拼接会产出错误标题。"
        ),
    )
    parser.add_argument(
        "--standalone",
        action="store_true",
        help=(
            "一次性单条视频，不属于任何系列：保留 LLM 自由生成的标题（而不是"
            "覆盖成固定的系列标题格式），并对该标题跑启发式打分"
            "（curiosity/specificity/emotion，各 0-3 分，7/9 为发布门槛）。"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只生成脚本和元数据，不渲染视频",
    )
    parser.add_argument(
        "--pinned-comment",
        default=None,
        help="发布后建议置顶的评论文案，随成片一起发去 Telegram。不传则跳过这一项。",
    )
    parser.add_argument(
        "--no-telegram",
        action="store_true",
        help="渲染成功后不自动发去 Telegram（默认会发；需要先在 config.toml 配 [telegram]）。",
    )
    args = parser.parse_args(argv)

    skill_dir = Path(__file__).resolve().parent
    raw_facts = [
        line.strip()
        for line in args.facts_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ][: args.fact_count]
    if not raw_facts:
        parser.error(f"no facts found in {args.facts_file}")
    logger.info(f"episode {args.episode}: {len(raw_facts)} facts")

    parts = build_scripts(
        raw_facts,
        language=args.language,
        episode=args.episode,
        outro=args.outro,
        hook=args.hook,
        fact_max_words=args.fact_max_words,
    )
    spoken_segments = [parts["hook"], *parts["facts"], parts["outro"]]
    script_text = " ".join(spoken_segments)

    # 覆盖表在这里就校验：写错段序号是很容易犯的错，等跑完 TTS 再报错
    # 会白白浪费一次语音生成。
    term_overrides: dict[int, list[str]] = {}
    if args.segment_terms:
        for key, value in json.loads(args.segment_terms).items():
            parsed = [t.strip() for t in value.split(",") if t.strip()]
            if not parsed:
                parser.error(f"--segment-terms entry {key!r} has no usable terms")
            term_overrides[int(key)] = parsed
        out_of_range = sorted(
            i for i in term_overrides if not 0 <= i < len(spoken_segments)
        )
        if out_of_range:
            parser.error(
                f"--segment-terms index out of range: {out_of_range}; "
                f"this episode has segments 0..{len(spoken_segments) - 1} "
                f"(0 = hook, {len(spoken_segments) - 1} = outro)"
            )

    from app.services import llm

    metadata = llm.generate_social_metadata(
        video_subject=f"{len(raw_facts)} surprising true facts",
        video_script=script_text,
        language="en",
        platform="youtube_shorts",
    )
    metadata["caption"] = format_caption_paragraphs(metadata["caption"])
    if args.standalone and not args.title:
        # 独立单条视频：保留 LLM 自由生成的标题，并打分记录，方便发布前决定
        # 要不要再改一版。7/9 只是启发式门槛，不阻断生成。
        score = score_title(metadata["title"])
        logger.info(f"title score: {score['total']}/9 ({metadata['title']!r})")
        if not score["passes"]:
            logger.warning(
                f"title scored below the 7/9 threshold: {score} — consider rewriting before publishing"
            )
        metadata["title_score"] = score
    else:
        # 系列视频：标题固定为 series-name + episode，不让 LLM 自由发挥
        metadata["title"] = args.title or f"{args.series_name} {args.episode} \U0001F440"

    if args.dry_run:
        print(json.dumps({"script": script_text, "metadata": metadata}, indent=2, ensure_ascii=False))
        return 0

    def transcribe(audio_file: Path):
        """从音频反解逐词时间轴，并把字幕文字换回脚本原文。"""
        raw_words = viral.transcribe_word_timings(
            str(audio_file), model_size=args.whisper_model
        )
        if not raw_words:
            raise RuntimeError("no word timings produced; cannot build overlay")
        total = max(word.end for word in raw_words)
        # 字幕文字取自脚本原文，Whisper 只负责提供时间：避免识别错误或
        # `[Music]` 这类非语音标注被直接烧进画面
        return viral.align_script_to_words(script_text, raw_words), total

    segment_terms: list[list[str]] | None = None
    if args.footage_mode == "synced":
        # 先出音频 -> 反解每段时间窗 -> 每段按自己的主题取材，
        # 保证讲到第 N 条时画面就是第 N 条的画面。
        from app.services import topic_footage

        task_id = str(uuid.uuid4())
        audio_path = generate_audio_only(
            script_text=script_text,
            subject=f"{args.series_name} {args.episode}",
            voice_name=args.voice_name,
            task_id=task_id,
            root=args.root,
            threads=args.threads,
        )
        task_dir = audio_path.parent
        words, duration = transcribe(audio_path)

        all_segments = viral.align_facts_to_words(
            spoken_segments, words, total_duration=duration
        )
        segment_terms = generate_segment_terms(
            spoken_segments, language=args.language, overrides=term_overrides
        )
        plans = [
            topic_footage.SegmentPlan(
                index=i,
                text=text,
                start=seg.start,
                end=seg.end,
                terms=terms,
            )
            for i, (text, seg, terms) in enumerate(
                zip(spoken_segments, all_segments, segment_terms)
            )
        ]
        video_path = Path(
            topic_footage.build_synced_footage(
                plans=plans,
                audio_file=str(audio_path),
                output_path=str(task_dir / "combined-synced.mp4"),
                task_id=task_id,
                threads=args.threads,
            )
        )
    else:
        video_path = generate_base_video(
            script_text=script_text,
            subject=f"{args.series_name} {args.episode}",
            voice_name=args.voice_name,
            video_terms=args.video_terms,
            root=args.root,
            skill_dir=skill_dir,
            threads=args.threads,
        )
        task_dir = video_path.parent
        words, duration = transcribe(task_dir / "audio.mp3")
        all_segments = viral.align_facts_to_words(
            spoken_segments, words, total_duration=duration
        )

    # 钩子和结尾不计入"第 N 条事实"，所以先把它们一起参与对齐，再只取中间的事实区间
    fact_segments = all_segments[1:-1] if len(all_segments) >= 3 else all_segments
    fact_segments = [
        viral.FactSegment(index=i + 1, start=s.start, end=s.end)
        for i, s in enumerate(fact_segments)
    ]

    ass_text = viral.build_ass(
        words=words,
        duration=duration,
        facts=fact_segments,
        highlight_color=args.highlight_color,
        words_per_caption=args.words_per_caption,
    )
    ass_path = task_dir / "overlay.ass"
    ass_path.write_text(ass_text, encoding="utf-8")

    output_path = task_dir / "final-viral.mp4"
    viral.burn_overlay(
        video_in=str(video_path),
        ass_file=str(ass_path),
        video_out=str(output_path),
        fonts_dir=str(PROJECT_ROOT / "resource" / "fonts"),
    )

    result = {
        "episode": args.episode,
        "video_file": str(output_path),
        "duration_seconds": round(duration, 2),
        "fact_count": len(fact_segments),
        "footage_mode": args.footage_mode,
        "script": script_text,
        # 保留分段与区间，便于只重跑叠加层而不必重新渲染底片
        "segments": spoken_segments,
        # 记录每段实际用的搜索词，方便事后核对"画面为什么配成这样"
        "segment_terms": segment_terms if args.footage_mode == "synced" else None,
        "segment_timings": [
            {"index": i, "start": round(s.start, 2), "end": round(s.end, 2)}
            for i, s in enumerate(all_segments)
        ],
        "fact_timings": [
            {"index": s.index, "start": round(s.start, 2), "end": round(s.end, 2)}
            for s in fact_segments
        ],
        "metadata": metadata,
    }
    (task_dir / "viral-result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("VIRAL_RESULT")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if not args.no_telegram:
        from send_to_telegram import send_episode

        send_episode(result, root=args.root, pinned_comment=args.pinned_comment)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
