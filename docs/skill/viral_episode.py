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
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger  # noqa: E402

from app.services import viral  # noqa: E402

# 研究结论：50-60 秒档位在事实类短视频里平均表现最好，而完播率仍是核心指标。
# 按 150-170 WPM 的口播语速，约 50 秒对应 125-140 个词，正好放得下 6 条事实。
DEFAULT_FACT_COUNT = 6

FACT_PROMPT = (
    "Rewrite this fact as ONE or TWO short punchy sentences for a rapid-fire facts "
    "compilation video. Open directly with the surprising claim - no greeting, no "
    "'did you know', no preamble, no filler words. Keep it under 25 words. "
    "Write in {language}."
)

HOOK_PROMPT = (
    "Write a single opening hook sentence, at most 12 words, for a short video that "
    "lists {count} surprising facts. It must create a specific curiosity gap and "
    "promise the payoff - not a vague tease. Do not greet the viewer. Do not use "
    "'did you know'. Return only the sentence, in {language}."
)

# 明确要求关注/评论是被允许的，被压制的是"点赞就关注"这类模板化空话。
# 但同一句结尾反复用会让系列显得自动化，所以正确做法是每集在内容日历里
# 单独写一句、并轮换 FOLLOW / COMMENT / BOTH。这里的默认值只是兜底，
# 调用方应当始终通过 --outro 传入当集专属文案。
DEFAULT_OUTRO = (
    "Follow this page so episode {next_episode} actually reaches you."
)


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    logger.info("$ " + " ".join(command[:6]) + (" ..." if len(command) > 6 else ""))
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True)


def build_scripts(
    raw_facts: list[str],
    language: str,
    episode: int,
    outro: str | None = None,
    hook: str | None = None,
) -> dict:
    """调用项目内的 LLM 服务，把原始事实改写成口播稿并生成钩子。"""
    from app.services import llm

    fact_lines = []
    for fact in raw_facts:
        line = llm.generate_script(
            video_subject=fact,
            language=language,
            paragraph_number=1,
            video_script_prompt=FACT_PROMPT.format(language=language),
        ).strip()
        logger.info(f"fact: {line}")
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

    resolved_outro = outro or DEFAULT_OUTRO.format(next_episode=episode + 1)
    return {"hook": hook, "facts": fact_lines, "outro": resolved_outro}


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
        "--dry-run",
        action="store_true",
        help="只生成脚本和元数据，不渲染视频",
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
    )
    spoken_segments = [parts["hook"], *parts["facts"], parts["outro"]]
    script_text = " ".join(spoken_segments)

    title = args.title or f"{args.series_name} {args.episode} \U0001F440"
    from app.services import llm

    metadata = llm.generate_social_metadata(
        video_subject=f"{len(raw_facts)} surprising true facts",
        video_script=script_text,
        language="en",
        platform="youtube_shorts",
    )
    metadata["title"] = title  # 系列标题固定，不让 LLM 自由发挥

    if args.dry_run:
        print(json.dumps({"script": script_text, "metadata": metadata}, indent=2, ensure_ascii=False))
        return 0

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
    audio_path = task_dir / "audio.mp3"

    raw_words = viral.transcribe_word_timings(
        str(audio_path), model_size=args.whisper_model
    )
    if not raw_words:
        raise RuntimeError("no word timings produced; cannot build overlay")
    duration = max(word.end for word in raw_words)
    # 字幕文字取自脚本原文，Whisper 只负责提供时间：避免识别错误或
    # `[Music]` 这类非语音标注被直接烧进画面
    words = viral.align_script_to_words(script_text, raw_words)

    # 钩子和结尾不计入"第 N 条事实"，所以先把它们一起参与对齐，再只取中间的事实区间
    all_segments = viral.align_facts_to_words(
        spoken_segments, words, total_duration=duration
    )
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
        "script": script_text,
        # 保留分段与区间，便于只重跑叠加层而不必重新渲染底片
        "segments": spoken_segments,
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
