#!/usr/bin/env python3
"""
渲染之前先确认图库真的有对得上的素材。

一次渲染约六分钟，这个探针三十秒。跳过它的代价是实实在在的：一集动物
主题连续五次渲染都因为画面对不上被推翻。

结果数量说明不了任何问题——Pexels 对任何词都会返回约 20 条，"wombat"、
"sloth"、"animal digestion" 都是 20 条，但其中只有第一个真的有袋熊。
唯一可靠的判断方式是把首帧抠出来用眼睛看。

用法::

    uv run python docs/skill/probe_footage.py wombat "octopus underwater" sloth

然后逐个查看打印出来的 jpg，把确认可用的词用 --segment-terms 钉进
viral_episode.py，不要让 LLM 再改写。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terms", nargs="+", help="要试的搜索词")
    parser.add_argument("--out-dir", type=Path, default=Path("/tmp/probe_footage"))
    parser.add_argument(
        "--per-term",
        type=int,
        default=1,
        help="每个词看几条候选；排在后面的候选常常已经跑题，"
        "想确认整段而不只是第一个镜头时调大它",
    )
    args = parser.parse_args(argv)

    from imageio_ffmpeg import get_ffmpeg_exe
    from loguru import logger

    from app.models.schema import VideoAspect
    from app.services import material

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = get_ffmpeg_exe()
    frames: list[Path] = []

    for term in args.terms:
        items = material.search_videos_pexels(
            search_term=term, minimum_duration=1, video_aspect=VideoAspect.portrait
        )
        if not items:
            logger.warning(f"{term!r}: no results at all")
            continue

        slug = term.replace(" ", "_").replace("/", "_")
        for rank, item in enumerate(items[: args.per_term]):
            saved = material.save_video(video_url=item.url, save_dir=str(args.out_dir))
            if not saved:
                continue
            frame = args.out_dir / f"{slug}_{rank}.jpg"
            subprocess.run(
                [ffmpeg, "-nostdin", "-loglevel", "error", "-y",
                 "-ss", "1", "-i", saved, "-frames:v", "1",
                 "-vf", "scale=300:-1", "-q:v", "4", str(frame)],
                stdin=subprocess.DEVNULL, check=False,
            )
            if frame.is_file():
                frames.append(frame)

    print("\nLOOK AT THESE - result counts do not tell you whether the match is real:")
    for frame in frames:
        print(f"  {frame}")
    return 0 if frames else 1


if __name__ == "__main__":
    raise SystemExit(main())
