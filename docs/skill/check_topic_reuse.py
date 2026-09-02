#!/usr/bin/env python3
"""
Check a candidate topic (and its individual facts) against every episode
ever made, BEFORE locking a script.

WHY THIS EXISTS. On 2026-08-31 the owner caught a repeated fact: "there's a
fact that repeats itself with the bees from previous videos." Investigating
showed it was worse than one fact -- ep45 was already a bees/honeybees
episode, and TWO of ep81's three facts duplicated it. The same pass turned
up more history: ep20's "yawning contagion" later became all of ep75, and
ep33 "ancient Rome" overlapped ep79's gladiators. The pre-build check had
only ever looked at topic-mix CATEGORY BALANCE (ANIMAL/EVERYDAY/HISTORY
counts) and recent topics -- never at whether this exact subject or fact had
already been used.

Greps are easy to forget and easy to do too narrowly, so this makes the
check mechanical. It searches the WHOLE log, not just recent rows, and it
searches every column (a topic can hide inside an older multi-topic
episode's key_subjects rather than its topic field).

SUBSTRING FALSE POSITIVES ARE REAL: "owl" matches "howl", "sloth" matches
"cloth". This tool reports word-boundary matches separately from loose
substring matches so a scary-looking hit can be dismissed on sight instead
of scaring you off a perfectly good topic.

Usage::

    uv run python docs/skill/check_topic_reuse.py wolf wolves
    uv run python docs/skill/check_topic_reuse.py --topic "alpha wolf" \\
        --fact "captive" --fact "David Mech" --fact "1999 paper"

Exit code is 0 when nothing is found, 1 when there is any word-boundary
hit -- so it can gate a build script if that is ever wanted.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

LOG = Path(__file__).resolve().parent / "plans" / "episode_log.csv"


def search(rows: list[dict], term: str) -> tuple[list, list]:
    """Return (word-boundary hits, loose substring-only hits)."""
    exact, loose = [], []
    pattern = re.compile(r"\b" + re.escape(term.lower()) + r"\b")
    for row in rows:
        blob = " ".join(v or "" for v in row.values()).lower()
        if term.lower() not in blob:
            continue
        where = [k for k, v in row.items() if v and term.lower() in v.lower()]
        entry = (row.get("episode", "?"), row.get("topic", "")[:60], where)
        (exact if pattern.search(blob) else loose).append(entry)
    return exact, loose


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("terms", nargs="*", help="bare terms to check")
    p.add_argument("--topic", action="append", default=[],
                   help="the candidate topic (repeatable)")
    p.add_argument("--fact", action="append", default=[],
                   help="a distinctive keyword from one fact (repeatable)")
    p.add_argument("--log", type=Path, default=LOG)
    args = p.parse_args(argv)

    terms = args.terms + args.topic + args.fact
    if not terms:
        p.error("give at least one term, --topic or --fact")

    with args.log.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"checking {len(terms)} term(s) against {len(rows)} logged episodes\n")

    any_exact = False
    for term in terms:
        exact, loose = search(rows, term)
        if exact:
            any_exact = True
            print(f"  [USED]  {term!r} -- {len(exact)} episode(s):")
            for ep, topic, where in exact:
                print(f"            ep {ep}: {topic}   (in: {', '.join(where)})")
        elif loose:
            print(f"  [~]     {term!r} -- no whole-word match; "
                  f"{len(loose)} substring-only hit(s), most likely false "
                  f"positives (e.g. owl/howl):")
            for ep, topic, _ in loose[:4]:
                print(f"            ep {ep}: {topic}")
        else:
            print(f"  [CLEAR] {term!r} -- no prior use anywhere")

    print()
    if any_exact:
        print("At least one term has been used before. Either pick a different\n"
              "topic, or build only from facts that are genuinely new -- and say\n"
              "so explicitly in the episode_log row. Do NOT write '(FIRST time\n"
              "this topic)' unless this check came back clear.")
    else:
        print("Nothing found. Safe to proceed -- and '(FIRST time this topic)'\n"
              "is now a verified claim rather than an assumption.")
    return 1 if any_exact else 0


if __name__ == "__main__":
    raise SystemExit(main())
