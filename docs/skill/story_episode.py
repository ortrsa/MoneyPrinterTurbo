#!/usr/bin/env python3
"""
把一个真实故事做成 30-90 秒的叙事短视频（与 viral_episode.py 并列的另一条流程）。

`viral_episode.py` 做的是"清单式"内容：N 条互不相关的事实，配 N/6 计数器和
进度条。故事不是清单——它只有一条线，靠悬念往前拉，中途插一个 "3/6" 反而
提醒观众"还剩三条"，把叙事张力拆掉。所以这里：

- **关掉计数器**（`show_counter=False`），保留进度条（它告诉观众"快到头了，
  再撑一下"，对留存是正向的）。
- **长度由故事本身决定**，不是固定 6 条。素材撑不起 90 秒的故事就做 30 秒，
  硬撑只会把留存拖垮。
- **段落是"节拍"不是"事实"**：每个节拍结尾留一个未回答的问题，观众为了得到
  答案继续看；最后一拍回收开头埋的钩子。

来源与版权（重要，见 channel_playbook.md §9）：
故事线索可以来自任何地方（Facebook 帖子、新闻、维基），但**事实要自己重新
核实，文字要自己重新写**。事实本身不受版权保护，别人写的那段话受保护。
`--source-note` 就是用来把线索出处记进 result json 的，方便事后追溯。
"""

from __future__ import annotations

import argparse
import json
import re
import uuid
from pathlib import Path

from loguru import logger

import viral_episode as ve

PROJECT_ROOT = ve.PROJECT_ROOT

# 实测（脚本词数 / 成片时长）：
#   Facts 7   152 词 / 57.14 秒 = 2.66
#   Facts 10  145 词 / 54.12 秒 = 2.68
#   Story 1   135 词 / 44.74 秒 = 3.02   <- 叙事稿更连贯，停顿少，语速更快
# 清单式内容每条事实之间有停顿，叙事是一条连续的线，所以同样词数更短。
# 这里取 2.9：偏向叙事的实测值，同时留一点余量，避免把稿子写得过长。
WORDS_PER_SECOND = 2.9

# 增长指南 Rank 1 要求 ≤20 秒，但那条是为"清单/排行"类短视频写的：
# 叙事故事在 20 秒内讲不出转折，钩子还没兑现就结束了。这条流程按用户指定的
# 30-90 秒走，并把"没什么可展开的故事就别拉长"写进 prompt。
MIN_SECONDS = 30
MAX_SECONDS = 90

# 这两个 prompt 必须走 `custom_system_prompt`（上限 8000 字符）而不是
# `video_script_prompt`（上限 2000）。原因有两条，都是实测踩出来的：
#   1. 故事原文本身就有一两千字符，塞进 2000 的槽里会被 `_limit_script_text`
#      从中间截断，把后面的输出格式说明整段切掉——模型于是回了一段散文，
#      解析必然失败。
#   2. 默认的 system prompt 明确写着"不许出现任何 markdown 或格式""只返回
#      脚本正文"，正好和这里要的 HOOK:/BEAT:/REVEAL: 标签冲突。传
#      custom_system_prompt 会整体替换掉它，冲突随之消失。
STORY_SYSTEM_PROMPT = """
# Role: Narrative Short-Video Writer

You write the spoken narration for a short vertical video telling ONE true story.

## Output format - mandatory, nothing else in the reply
HOOK: <one sentence, at most 14 words>
BEAT: <one or two sentences>
... exactly {beats} BEAT lines in total ...
REVEAL: <one or two sentences>

## Rules that decide whether this video works
1. Total narration must be about {word_budget} words. This sets the video length,
   so treat it as a hard budget, not a suggestion.
2. The HOOK is the first 2 seconds of the video. Lead with the single most
   shocking or absurd element of the whole story, even if it happens late in it.
   Do not set the scene, do not give background, do not open with a date or a
   place name. No greeting, no "did you know".
3. Every BEAT ends on an unanswered question or an unresolved turn, so quitting
   the video half way feels like walking out on something. Escalate: each beat
   should be harder to believe than the one before it.
4. The REVEAL answers the hook and names the consequence. Where the story allows,
   echo a word or image from the HOOK so the ending visibly closes the loop -
   viewers who notice tend to rewatch the opening, which is worth more than any
   extra sentence.
5. Keep every claim faithful to the source below. Never invent numbers, names or
   motives that are not there. If the source marks something as uncertain, keep
   it uncertain rather than flattening it into a fact.
6. Plain spoken language, short sentences, contractions where natural.
7. Never use these overused AI-writing phrases: {blocklist}
8. {humanization}
9. Write the narration in {language}.

## Source story
{story}
""".strip()

# 增长指南 Rank 5：两行标题 + 两个关键词换成亮色。让模型把两个关键词单独
# 返回，而不是自己在正文里塞颜色标记——标记混在句子里很容易被模型写坏，
# 分开返回好解析得多。
TITLE_SYSTEM_PROMPT = """
# Role: On-Screen Title Writer

You write the 2-line title burned onto a short vertical video.

## Output format - mandatory, nothing else in the reply
LINE1: <at most 4 words>
LINE2: <at most 4 words>
KEY1: <one word appearing verbatim in LINE1 or LINE2>
KEY2: <a different word appearing verbatim in LINE1 or LINE2>

## Rules
1. The two lines together state the premise so a scroller gets it instantly.
2. Withhold the outcome. The title raises the question; the video answers it.
3. KEY1 and KEY2 are the two words carrying the most curiosity - they get
   recoloured on screen, so each must appear verbatim in LINE1 or LINE2.
4. No hashtags, no emoji, no quotation marks, no ending punctuation.
5. Write in {language}.

## The video narration
{script}
""".strip()


def beats_for_duration(target_seconds: int) -> int:
    """
    目标时长换算成节拍数。

    每个节拍连同它的画面大约 10-12 秒；再算上钩子和结尾，30 秒对应 3 拍、
    60 秒对应 5 拍、90 秒对应 7 拍。上下夹紧到 3-7：少于 3 拍不成故事，
    多于 7 拍观众会疲劳（增长指南 Rank 4 的 4-6 clip 区间说的也是这件事，
    只是它按"片段"计，这里按"节拍"计，一个节拍就是一个画面窗口）。
    """
    return max(3, min(7, round(target_seconds / 12)))


# 按标签切，而不是按行切。`llm.format_response()` 会对模型输出做清洗
# （去 markdown、按 \n\n 重组），实测标签会被挤成一行：
# "...found him.BEAT: Six young men..."。靠 splitlines() 解析必然失败，
# 用标签本身做边界则两种情况都能吃下。
_STORY_LABEL_RE = re.compile(
    r"(HOOK|BEAT|REVEAL)\s*:\s*(.*?)(?=(?:HOOK|BEAT|REVEAL)\s*:|$)",
    re.IGNORECASE | re.DOTALL,
)
_TITLE_LABEL_RE = re.compile(
    r"(LINE1|LINE2|KEY1|KEY2)\s*:\s*(.*?)(?=(?:LINE1|LINE2|KEY1|KEY2)\s*:|$)",
    re.IGNORECASE | re.DOTALL,
)


def parse_story_response(raw: str) -> dict:
    """把 LLM 返回的 HOOK/BEAT/REVEAL 解析成结构化的节拍。"""
    hook = ""
    reveal = ""
    beats: list[str] = []
    for label, text in _STORY_LABEL_RE.findall(raw):
        text = text.strip().strip('"').strip()
        if not text:
            continue
        label = label.upper()
        if label == "HOOK":
            hook = text
        elif label == "BEAT":
            beats.append(text)
        else:
            reveal = text
    if not hook or not beats or not reveal:
        raise RuntimeError(
            "could not parse HOOK/BEAT/REVEAL from the model output:\n" + raw[:1500]
        )
    return {"hook": hook, "beats": beats, "reveal": reveal}


def parse_title_response(raw: str) -> dict:
    """解析两行标题和两个高亮关键词。"""
    fields: dict[str, str] = {}
    for label, text in _TITLE_LABEL_RE.findall(raw):
        fields[label.upper()] = text.strip().strip('"').strip().rstrip(".")
    if not fields.get("LINE1") or not fields.get("LINE2"):
        raise RuntimeError("could not parse a 2-line title from:\n" + raw[:800])
    fields.setdefault("KEY1", "")
    fields.setdefault("KEY2", "")
    return fields


def _too_similar(a: str, b: str, threshold: float = 0.75) -> bool:
    """两句话是否几乎在说同一件事（用于挡住钩子和第一个节拍重复）。"""
    import difflib

    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio() >= threshold


def build_story_script(
    story: str,
    language: str,
    target_seconds: int,
    outro: str | None,
    hook: str | None,
) -> dict:
    """调用 LLM 把原始故事改写成钩子 + 节拍 + 结尾。"""
    from app.services import llm

    beats = beats_for_duration(target_seconds)
    word_budget = int(target_seconds * WORDS_PER_SECOND)
    system_prompt = STORY_SYSTEM_PROMPT.format(
        story=story.strip(),
        language=language,
        beats=beats,
        word_budget=word_budget,
        blocklist=ve.AI_TELL_BLOCKLIST,
        humanization=ve.HUMANIZATION_NOTE,
    )
    raw = llm.generate_script(
        video_subject="a true story",
        language=language,
        paragraph_number=1,
        video_script_prompt=(
            f"Write the narration now: one HOOK line, exactly {beats} BEAT lines, "
            "then one REVEAL line. Return only those labelled lines."
        ),
        custom_system_prompt=system_prompt,
    )
    parsed = parse_story_response(raw)

    if hook:
        # 日历/人工写好的钩子视为已把关，直接采用
        logger.info(f"hook (provided): {hook}")
        parsed["hook"] = hook.strip()

    # 这里**故意不调用** `ve.refine_hook()`。它是给"清单式"视频写的：拿第一条
    # 事实当上下文去重写钩子，在叙事流程里会稳定地把钩子改写成第一个节拍的
    # 复述，而且它自己的 prompt 里没有"不许铺陈场景"这条约束。实测两次都翻车，
    # 其中一次把
    #   "An archduke survived a grenade, only for a wrong turn to get him killed."
    # 改成了
    #   "Six young men lined a Sarajevo street to kill an empire's heir."
    # ——最值钱的前两秒从悬念变成了背景交代，还和 BEAT 1 撞车配了两遍画面。
    # STORY_SYSTEM_PROMPT 里的钩子规则比 refine_hook 严格，直接用它的输出。
    if parsed["beats"] and _too_similar(parsed["hook"], parsed["beats"][0]):
        logger.warning(
            "the hook restates the first beat, so the opening plays the same "
            "line twice; consider re-running or passing --hook. "
            f"hook={parsed['hook']!r} beat1={parsed['beats'][0]!r}"
        )

    for text in [parsed["hook"], *parsed["beats"], parsed["reveal"]]:
        tells = ve.find_ai_tells(text)
        if tells:
            logger.warning(f"AI-tell phrase slipped through: {tells} in: {text}")

    parsed["outro"] = (outro or "").strip()
    return parsed


def _colorize(line: str, keys: list[str], color: str) -> str:
    """把标题里的关键词换成亮色（ASS 行内 \\1c 标签）。"""
    from app.services.viral import _ass_color

    ass_color = _ass_color(color).rstrip("&") + "&"
    out = line
    for key in keys:
        if not key:
            continue
        # 只替换整词，避免 "war" 命中 "warning"
        out = re.sub(
            rf"(?<!\w)({re.escape(key)})(?!\w)",
            r"{\\1c" + ass_color + r"}\1{\\r}",
            out,
            count=1,
            flags=re.IGNORECASE,
        )
    return out


def inject_title_banner(
    ass_text: str,
    line1: str,
    line2: str,
    keys: list[str],
    duration: float,
    key_color: str = "#FF2D6F",
    video_width: int = 1080,
    video_height: int = 1920,
) -> str:
    """
    在已生成的 ASS 上叠一个常驻的两行标题（黑底 + 两个关键词换亮色）。

    增长指南 Rank 5 写的是"两行标题放在纯黑背景上"。这里做成**常驻顶部黑条**
    而不是开头的黑屏卡片：黑屏卡片会把最关键的前 2 秒烧掉，而指南自己又说
    前 2 秒决定一切——两条放一起只能这么解。常驻黑条既给了即时语境，又不占用
    钩子画面。

    直接改字符串而不是改 `viral.build_ass()`，是为了完全不动清单流程那条路径。
    """
    font_size = int(video_height * 0.030)
    band_top = int(video_height * 0.072)
    line_gap = int(font_size * 1.30)
    band_height = line_gap * 2 + int(font_size * 0.75)

    style = (
        f"Style: TitleBar,Anton,{font_size},&H00FFFFFF&,&H00FFFFFF&,&H00000000&,"
        f"&H00000000&,-1,0,0,0,100,100,0,0,1,0,0,5,40,40,0,1"
    )
    # 黑条本身：不透明黑，铺满整宽
    band = (
        f"Dialogue: 1,0:00:00.00,{ve_ass_time(duration)},TitleBar,,0,0,0,,"
        f"{{\\an7\\pos(0,{band_top})\\1c&H000000&\\alpha&H20&\\p1}}"
        f"m 0 0 l {video_width} 0 l {video_width} {band_height} l 0 {band_height}{{\\p0}}"
    )
    y1 = band_top + int(font_size * 0.85)
    y2 = y1 + line_gap
    text1 = _colorize(line1.upper(), keys, key_color)
    text2 = _colorize(line2.upper(), keys, key_color)
    ev1 = (
        f"Dialogue: 2,0:00:00.00,{ve_ass_time(duration)},TitleBar,,0,0,0,,"
        f"{{\\an5\\pos({video_width // 2},{y1})}}{text1}"
    )
    ev2 = (
        f"Dialogue: 2,0:00:00.00,{ve_ass_time(duration)},TitleBar,,0,0,0,,"
        f"{{\\an5\\pos({video_width // 2},{y2})}}{text2}"
    )

    lines = ass_text.splitlines()
    out: list[str] = []
    for line in lines:
        out.append(line)
        # 样式追加在最后一条 Style 之后，事件追加在 Format 行之后
        if line.startswith("Style: BarFill"):
            out.append(style)
        elif line.startswith("Format: Layer"):
            out.extend([band, ev1, ev2])
    return "\n".join(out) + "\n"


def ve_ass_time(seconds: float) -> str:
    """秒 -> ASS 时间戳 h:mm:ss.cc。"""
    if seconds < 0:
        seconds = 0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:05.2f}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--story-file",
        required=True,
        type=Path,
        help="原始故事文本。内容只作为线索：事实要另行核实，文字由本流程重写。",
    )
    parser.add_argument(
        "--target-seconds",
        type=int,
        default=60,
        help=(
            f"目标时长，{MIN_SECONDS}-{MAX_SECONDS} 秒。只有真正撑得住的故事才给到 "
            f"{MAX_SECONDS} 秒；没什么可展开的就做 {MIN_SECONDS} 秒，硬拉长必然掉留存。"
        ),
    )
    parser.add_argument(
        "--source-note",
        default="",
        help="线索出处（例如某个 Facebook 帖子）。只记进 result json 用于追溯。",
    )
    parser.add_argument("--episode", type=int, default=1)
    parser.add_argument("--series-name", default="Random But True Stories")
    parser.add_argument("--title", default=None, help="完整标题，直接用于发布元数据")
    parser.add_argument("--language", default="en-US")
    parser.add_argument("--voice-name", default="gemini:Puck-Male")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--hook", default=None, help="人工写好的钩子；不传则由 LLM 生成并精炼")
    parser.add_argument("--outro", default=None, help="结尾 CTA 口播；每集应当不同")
    parser.add_argument(
        "--segment-terms",
        default=None,
        help=(
            "按段钉死素材搜索词，JSON 对象：段序号 -> 逗号分隔关键词。"
            "段 0 是钩子，之后依次是各节拍，最后是 REVEAL（以及可选的结尾）。"
            "历史类故事几乎一定要用它——图库没有 1914 年的萨拉热窝。"
        ),
    )
    parser.add_argument("--highlight-color", default="#FFE500", help="字幕逐词高亮色")
    parser.add_argument("--title-key-color", default="#FF2D6F", help="标题关键词的亮色")
    parser.add_argument("--no-title-banner", action="store_true", help="不烧顶部两行标题")
    parser.add_argument("--words-per-caption", type=int, default=3)
    parser.add_argument("--whisper-model", default="base.en")
    parser.add_argument("--threads", type=int, default=ve.os.cpu_count() or 4)
    parser.add_argument("--dry-run", action="store_true", help="只出脚本和元数据，不渲染")
    parser.add_argument(
        "--from-dry-run",
        type=Path,
        default=None,
        help=(
            "读取一次 --dry-run 的 JSON 输出，直接用里面的脚本/标题/元数据渲染，"
            "跳过全部 LLM 生成。脚本每次生成都不一样，所以'先人工核对事实、再渲染'"
            "必须靠它才成立——否则渲染出来的是另一版没被核对过的文本。"
        ),
    )
    args = parser.parse_args(argv)

    if not MIN_SECONDS <= args.target_seconds <= MAX_SECONDS:
        parser.error(
            f"--target-seconds must be between {MIN_SECONDS} and {MAX_SECONDS} "
            f"(got {args.target_seconds})"
        )

    locked: dict | None = None
    if args.from_dry_run:
        locked = json.loads(args.from_dry_run.read_text(encoding="utf-8"))
        missing = [
            k for k in ("segments", "title_card", "metadata") if k not in locked
        ]
        if missing:
            parser.error(f"{args.from_dry_run} is missing keys: {missing}")
        if args.dry_run:
            parser.error("--from-dry-run and --dry-run are mutually exclusive")
        logger.info(f"using the locked script from {args.from_dry_run}")

    story = args.story_file.read_text(encoding="utf-8").strip()
    if not story and not locked:
        parser.error(f"{args.story_file} is empty")

    beats = beats_for_duration(args.target_seconds)
    logger.info(
        f"story episode {args.episode}: target {args.target_seconds}s -> "
        f"{beats} beats, ~{int(args.target_seconds * WORDS_PER_SECOND)} words"
    )

    if locked:
        spoken_segments = list(locked["segments"])
        parts = {"beats": spoken_segments[1:-1]}
    else:
        parts = build_story_script(
            story=story,
            language=args.language,
            target_seconds=args.target_seconds,
            outro=args.outro,
            hook=args.hook,
        )
        spoken_segments = [parts["hook"], *parts["beats"], parts["reveal"]]
        if parts["outro"]:
            spoken_segments.append(parts["outro"])
    script_text = " ".join(spoken_segments)
    word_count = len(script_text.split())
    estimated = word_count / WORDS_PER_SECOND
    logger.info(f"script ({word_count} words, ~{estimated:.0f}s): {script_text}")
    # 模型经常写不满词数预算（实测 75 秒目标只写了 134 词 ≈ 54 秒）。
    # 这不算错误——短一点通常反而留存更好——但必须说出来，否则会以为
    # --target-seconds 是被遵守的。
    if abs(estimated - args.target_seconds) > args.target_seconds * 0.2:
        logger.warning(
            f"script is ~{estimated:.0f}s against a --target-seconds of "
            f"{args.target_seconds}s. The model does not hit the word budget "
            "exactly; re-run or adjust --target-seconds if the gap matters."
        )

    term_overrides: dict[int, list[str]] = {}
    if args.segment_terms:
        for key, value in json.loads(args.segment_terms).items():
            parsed_terms = [t.strip() for t in value.split(",") if t.strip()]
            if not parsed_terms:
                parser.error(f"--segment-terms entry {key!r} has no usable terms")
            term_overrides[int(key)] = parsed_terms
        bad = sorted(i for i in term_overrides if not 0 <= i < len(spoken_segments))
        if bad:
            parser.error(
                f"--segment-terms index out of range: {bad}; this story has "
                f"segments 0..{len(spoken_segments) - 1}"
            )

    if locked:
        metadata = dict(locked["metadata"])
        title_card = dict(locked["title_card"])
    else:
        from app.services import llm

        metadata = llm.generate_social_metadata(
            video_subject="a true story",
            video_script=script_text,
            language="en",
            platform="youtube_shorts",
        )
        metadata["caption"] = ve.format_caption_paragraphs(metadata["caption"])

        title_raw = llm.generate_script(
            video_subject="on-screen title",
            language=args.language,
            paragraph_number=1,
            video_script_prompt=(
                "Write the 2-line title now. Return only the LINE1, LINE2, KEY1 and "
                "KEY2 lines."
            ),
            custom_system_prompt=TITLE_SYSTEM_PROMPT.format(
                script=script_text, language=args.language
            ),
        )
        title_card = parse_title_response(title_raw)
    if args.title:
        metadata["title"] = args.title
    logger.info(f"title card: {title_card}")

    if args.dry_run:
        print(
            json.dumps(
                {
                    "script": script_text,
                    "segments": spoken_segments,
                    "title_card": title_card,
                    "metadata": metadata,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    from app.services import topic_footage, viral

    task_id = str(uuid.uuid4())
    audio_path = ve.generate_audio_only(
        script_text=script_text,
        subject=f"{args.series_name} {args.episode}",
        voice_name=args.voice_name,
        task_id=task_id,
        root=args.root,
        threads=args.threads,
    )
    task_dir = audio_path.parent

    raw_words = viral.transcribe_word_timings(
        str(audio_path), model_size=args.whisper_model
    )
    if not raw_words:
        raise RuntimeError("no word timings produced; cannot build overlay")
    duration = max(word.end for word in raw_words)
    words = viral.align_script_to_words(script_text, raw_words)

    all_segments = viral.align_facts_to_words(
        spoken_segments, words, total_duration=duration
    )
    # playbook §6：相邻两段时间窗完全相同 = Whisper 复读，画面会全部挤到一点
    for a, b in zip(all_segments, all_segments[1:]):
        if abs(a.start - b.start) < 1e-6 and abs(a.end - b.end) < 1e-6:
            logger.warning(
                "two adjacent segments share identical timings - suspect a Whisper "
                "repeated-word loop; check the transcript before trusting the cut"
            )
            break

    segment_terms = ve.generate_segment_terms(
        spoken_segments, language=args.language, overrides=term_overrides
    )
    plans = [
        topic_footage.SegmentPlan(
            index=i, text=text, start=seg.start, end=seg.end, terms=terms
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

    # 故事没有"第 N 条"，计数器必须关掉；进度条保留
    ass_text = viral.build_ass(
        words=words,
        duration=duration,
        facts=None,
        highlight_color=args.highlight_color,
        words_per_caption=args.words_per_caption,
        show_counter=False,
        show_progress_bar=True,
    )
    if not args.no_title_banner:
        ass_text = inject_title_banner(
            ass_text,
            line1=title_card["LINE1"],
            line2=title_card["LINE2"],
            keys=[title_card.get("KEY1", ""), title_card.get("KEY2", "")],
            duration=duration,
            key_color=args.title_key_color,
        )
    ass_path = task_dir / "overlay.ass"
    ass_path.write_text(ass_text, encoding="utf-8")

    output_path = task_dir / "final-story.mp4"
    viral.burn_overlay(
        video_in=str(video_path),
        ass_file=str(ass_path),
        video_out=str(output_path),
        fonts_dir=str(PROJECT_ROOT / "resource" / "fonts"),
    )

    result = {
        "episode": args.episode,
        "format": "story",
        "video_file": str(output_path),
        "duration_seconds": round(duration, 2),
        "target_seconds": args.target_seconds,
        "beat_count": len(parts["beats"]),
        "source_note": args.source_note,
        "script": script_text,
        "segments": spoken_segments,
        "segment_terms": segment_terms,
        "segment_timings": [
            {"index": i, "start": round(s.start, 2), "end": round(s.end, 2)}
            for i, s in enumerate(all_segments)
        ],
        "title_card": title_card,
        "metadata": metadata,
    }
    (task_dir / "story-result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("STORY_RESULT")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
