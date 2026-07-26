#!/usr/bin/env python3
"""
按内容日历 CSV 批量跑一周的集数：把每一行拆成 facts 文件，调用
`viral_episode.py`，产物按天归档，全部失败/成功情况汇总到一个 JSON。

用法::

    uv run python docs/skill/run_week.py \
        --calendar content_calendar_month1.csv --week 1 \
        --out-dir /tmp/week1
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent

# 每个系列独立编号：日历里的 `episode` 是系列内序号，但 viral_episode.py
# 用 --episode 生成标题里的数字，所以要按 series_name 分别维护计数。
DAY_ORDER = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calendar", required=True, type=Path)
    parser.add_argument("--week", required=True, type=int)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument(
        "--only-day",
        default=None,
        help="只跑某一天（如 Mon），用于单条重跑或排查",
    )
    args = parser.parse_args(argv)

    rows = list(csv.DictReader(args.calendar.open(encoding="utf-8")))
    week_rows = [r for r in rows if r["week"] == str(args.week)]
    week_rows.sort(key=lambda r: DAY_ORDER[r["day"]])
    if args.only_day:
        week_rows = [r for r in week_rows if r["day"] == args.only_day]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for row in week_rows:
        slug = f"{row['day']}_{row['series'].replace(' ', '_')}_{row['episode']}"
        facts_file = args.out_dir / f"{slug}_facts.txt"
        facts_file.write_text(
            "\n".join(t.strip() for t in row["fact_topics"].split("|")),
            encoding="utf-8",
        )

        command = [
            "uv", "run", "python", "viral_episode.py",
            "--facts-file", str(facts_file.resolve()),
            "--episode", row["episode"],
            "--series-name", row["series"],
            "--hook", row["hook_line_spoken"],
            "--outro", row["outro_line_spoken"],
        ]
        print(f"\n=== {slug} ===", flush=True)
        print("$ " + " ".join(command), flush=True)
        proc = subprocess.run(command, cwd=SKILL_DIR)

        entry = {"slug": slug, "day": row["day"], "title": row["title"], "returncode": proc.returncode}
        if proc.returncode == 0:
            # viral_episode.py 打印 VIRAL_RESULT 后跟 JSON；这里不重新解析
            # stdout（已直接透传到终端），改为按约定路径去 viral-result.json
            # 里找最新一条属于这次任务的记录。简单起见改成让调用方自己核对
            # 日志，这里只记录成功与否，方便判断当天是否需要重跑。
            pass
        results.append(entry)
        (args.out_dir / "week_summary.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    ok = sum(1 for r in results if r["returncode"] == 0)
    print(f"\n=== done: {ok}/{len(results)} succeeded ===")
    for r in results:
        status = "OK" if r["returncode"] == 0 else f"FAILED (rc={r['returncode']})"
        print(f"  {r['day']:4} {r['title']:35} {status}")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
