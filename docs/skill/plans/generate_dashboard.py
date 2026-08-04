#!/usr/bin/env python3
"""
Build the channel's evening-report dashboard as a single self-contained HTML
file, using real data only (Data API for current view/like counts, Analytics
API for retention where it has finalised).

Replaces the old wall-of-Telegram-text evening report (channel_playbook.md
Section: THE DAILY ROUTINE). The 20:00 job runs this, publishes the output
via the Artifact tool to a STABLE URL (same artifact, redeployed nightly --
the owner bookmarks one link), then sends a short Telegram digest pointing
at it instead of four long messages.

Usage::

    uv run python docs/skill/plans/generate_dashboard.py --out /path/to/dashboard.html

Topic/format metadata for older episodes is hand-maintained in EPISODE_META
below (this pipeline has no way to derive "what a video is about" from the
API) -- update it whenever episode_log.csv gets a new row.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import html
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "docs" / "skill" / "youtube"))
from fetch_channel_analytics import get_access_token  # noqa: E402

EPISODE_LOG = ROOT / "docs" / "skill" / "plans" / "episode_log.csv"

# video_id -> (episode label, topic, format). Hand-maintained -- see docstring.
EPISODE_META: dict[str, tuple[str, str, str]] = {
    "l-z-DmzP-6A": ("18", "Everyday objects", "facts"),
    "77Sx4bWjwgA": ("19", "The dollar / named after a valley", "story"),
    "Zu4n7UHvrDg": ("16", "Dogs", "facts"),
    "glOoMgY_--c": ("17", "Ferrari / Lamborghini / Pagani", "story"),
    "fnYLnTxsg4Y": ("13", "Ocean / deep sea", "facts"),
    "ScB_As-TQ4Y": ("12", "Animal strength", "facts"),
    "3ngQD1JbdAI": ("11", "Frog", "facts"),
    "aECYbohDjsE": ("10", "Bats", "facts"),
    "xHf6f-ildSE": ("9", "SHORT: hedgehog/peacock/seahorse", "facts-short"),
    "7jq91HsWFRY": ("8", "SHORT: axolotl/shrimp/cuttlefish", "facts-short"),
    "mFJ_FHlEv54": ("6", "Animal ensemble", "facts"),
    "Wdjj-D7PkIk": ("5", "Animal ensemble", "facts"),
    "BWQwmwyBaVk": ("AI4", "AI Unfiltered", "facts"),
    "q1WokT8ROLE": ("4", "Animal ensemble", "facts"),
    "gl6cF270Aa8": ("AI3", "AI Unfiltered", "facts"),
    "4gMCUJUhdZw": ("3", "(topic not recorded)", "facts"),
    "g4dTmbYAXd8": ("AI2", "AI Unfiltered", "facts"),
    "oCZTsQPSuT0": ("pre", "(pre-branding)", "facts"),
    "KjFM0JCJpNg": ("pre", "Flamingo (pre-branding)", "facts"),
    "OSwCQcCNf8k": ("pre", "(pre-branding test upload)", "facts"),
    "WjwadJphDcw": ("pre", "(pre-branding test upload)", "facts"),
}


def fetch_live_stats(token: str) -> list[dict]:
    H = {"Authorization": f"Bearer {token}"}
    ch = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={"part": "contentDetails", "mine": "true"},
        headers=H, timeout=30,
    ).json()
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    ids: list[str] = []
    page_token = None
    while True:
        params = {"part": "contentDetails", "playlistId": uploads, "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params=params, headers=H, timeout=30,
        ).json()
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        page_token = r.get("nextPageToken")
        if not page_token:
            break

    rows = []
    for i in range(0, len(ids), 50):
        v = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"part": "snippet,statistics,status", "id": ",".join(ids[i:i + 50])},
            headers=H, timeout=30,
        ).json()
        for it in v.get("items", []):
            st = it.get("statistics", {})
            rows.append({
                "id": it["id"],
                "title": it["snippet"]["title"],
                "published": it["snippet"]["publishedAt"],
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)),
                "comments": int(st.get("commentCount", 0)),
                "privacy": it["status"]["privacyStatus"],
            })
    rows.sort(key=lambda r: r["published"], reverse=True)
    return rows


def fetch_retention(token: str, days: int = 28) -> dict[str, float]:
    """video_id -> averageViewPercentage, for whatever Analytics has finalised."""
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    r = requests.get(
        "https://youtubeanalytics.googleapis.com/v2/reports",
        params={
            "ids": "channel==MINE",
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "metrics": "views,averageViewPercentage",
            "dimensions": "video",
            "sort": "-views",
            "maxResults": 50,
        },
        headers={"Authorization": f"Bearer {token}"}, timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    headers = [h["name"] for h in data.get("columnHeaders", [])]
    out = {}
    for row in data.get("rows", []):
        d = dict(zip(headers, row))
        out[d["video"]] = d["averageViewPercentage"]
    return out


def merge(live: list[dict], retention: dict[str, float]) -> list[dict]:
    out = []
    for r in live:
        ep, topic, fmt = EPISODE_META.get(r["id"], ("?", "(unmapped -- add to EPISODE_META)", "facts"))
        out.append({**r, "ep": ep, "topic": topic, "fmt": fmt, "ret": retention.get(r["id"])})
    return out


def read_open_items() -> dict:
    """Pull unbuilt/on-hold rows straight from episode_log.csv for the 'what's next' section."""
    if not EPISODE_LOG.is_file():
        return {"unbuilt": [], "on_hold": []}
    unbuilt, on_hold = [], []
    with open(EPISODE_LOG, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            status = row.get("status", "")
            if "ON HOLD" in status:
                on_hold.append(row)
            elif "not built" in status.lower() and "DROPPED" not in status and "STORY LEAD" not in status:
                unbuilt.append(row)
    return {"unbuilt": unbuilt, "on_hold": on_hold}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def fmt_age(published: str) -> str:
    pub = datetime.datetime.fromisoformat(published.replace("Z", "+00:00"))
    hours = (datetime.datetime.now(datetime.timezone.utc) - pub).total_seconds() / 3600
    if hours < 48:
        return f"{hours:.0f}h ago"
    return f"{hours / 24:.0f}d ago"


def retention_class(ret: float | None) -> str:
    if ret is None:
        return ""
    if ret >= 55:
        return "good"
    if ret >= 40:
        return "warn"
    return "bad"


def build_html(rows: list[dict], open_items: dict, generated_at: str) -> str:
    max_views = max((r["views"] for r in rows), default=1) or 1

    # Hero stats
    now = datetime.datetime.now(datetime.timezone.utc)
    published_recent = [
        r for r in rows
        if r["privacy"] == "public"
        and (now - datetime.datetime.fromisoformat(r["published"].replace("Z", "+00:00"))).days < 7
    ]
    MIN_VIEWS_FOR_RETENTION_HIGHLIGHT = 100
    best_retention = max(
        (r for r in rows if r["ret"] is not None and r["views"] >= MIN_VIEWS_FOR_RETENTION_HIGHLIGHT),
        key=lambda r: r["ret"], default=None,
    )
    top_views_7d = sorted(published_recent, key=lambda r: r["views"], reverse=True)[:1]
    pending_retention = [r for r in rows if r["ret"] is None and r["privacy"] == "public"]

    def stat_card(label: str, value: str, sub: str, tone: str = "") -> str:
        return f"""
        <div class="stat-card {tone}">
          <div class="stat-label">{esc(label)}</div>
          <div class="stat-value">{esc(value)}</div>
          <div class="stat-sub">{esc(sub)}</div>
        </div>"""

    hero = ""
    if top_views_7d:
        t = top_views_7d[0]
        hero += stat_card("Leading this week", f"{t['views']:,}", f"ep {t['ep']} — {t['topic']}", "accent")
    if best_retention:
        hero += stat_card(
            "Best retention on file", f"{best_retention['ret']:.1f}%",
            f"ep {best_retention['ep']} — {best_retention['topic']}", "good",
        )
    hero += stat_card("Awaiting real retention", str(len(pending_retention)), "too new for Analytics API", "warn")

    # Table rows
    table_rows = []
    for r in sorted(rows, key=lambda r: r["published"], reverse=True):
        bar_pct = max(2, round(100 * r["views"] / max_views))
        ret = r["ret"]
        ret_html = (
            f'<span class="pill {retention_class(ret)}">{ret:.0f}%</span>' if ret is not None
            else '<span class="pill pending">pending</span>'
        )
        privacy_dot = "" if r["privacy"] == "public" else '<span class="dot private" title="private / scheduled"></span>'
        table_rows.append(f"""
        <tr>
          <td class="ep">{esc(r['ep'])}{privacy_dot}</td>
          <td class="topic">{esc(r['topic'])}<span class="fmt">{esc(r['fmt'])}</span></td>
          <td class="views">
            <div class="bar-track"><div class="bar-fill" style="width:{bar_pct}%"></div></div>
            <span class="views-num">{r['views']:,}</span>
          </td>
          <td class="likes">{r['likes']}</td>
          <td class="ret">{ret_html}</td>
          <td class="age">{esc(fmt_age(r['published']))}</td>
        </tr>""")

    def open_row(row: dict, tag: str) -> str:
        return f'<li><span class="tag {tag}">{esc(tag)}</span> ep {esc(row.get("episode",""))} — {esc(row.get("topic","")[:60])}</li>'

    open_html = "".join(open_row(r, "on hold") for r in open_items["on_hold"]) + \
                "".join(open_row(r, "unbuilt") for r in open_items["unbuilt"])
    if not open_html:
        open_html = "<li class=\"muted\">Nothing queued — propose a fresh slate.</li>"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Random But True — Channel Dashboard</title>
<style>
  :root {{
    --ink: #14120f;
    --surface: #1e1b17;
    --surface-2: #262119;
    --border: #33291f;
    --paper: #f4efe6;
    --muted: #9a9184;
    --yellow: #ffe500;
    --pink: #ff2d6e;
    --good: #7fbf7a;
    --warn: #e8a33d;
    --bad: #e8604b;
  }}
  :root[data-theme="light"] {{
    --ink: #faf6ee;
    --surface: #ffffff;
    --surface-2: #f2ece0;
    --border: #e3d9c6;
    --paper: #201c16;
    --muted: #756c5e;
    --yellow: #c9a600;
    --pink: #d81b60;
    --good: #2f8f4e;
    --warn: #b9770e;
    --bad: #c8402c;
  }}
  @media (prefers-color-scheme: light) {{
    :root:not([data-theme="dark"]) {{
      --ink: #faf6ee; --surface: #ffffff; --surface-2: #f2ece0; --border: #e3d9c6;
      --paper: #201c16; --muted: #756c5e; --yellow: #c9a600; --pink: #d81b60;
      --good: #2f8f4e; --warn: #b9770e; --bad: #c8402c;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--ink);
    color: var(--paper);
    font-family: ui-sans-serif, "Segoe UI", "Avenir Next", system-ui, sans-serif;
    line-height: 1.45;
    padding: 20px 16px 48px;
  }}
  .wrap {{ max-width: 680px; margin: 0 auto; }}
  .masthead {{
    display: flex; align-items: baseline; justify-content: space-between;
    gap: 12px; margin-bottom: 4px; flex-wrap: wrap;
  }}
  .brand {{
    font-weight: 900; text-transform: uppercase; letter-spacing: -0.01em;
    font-size: 1.5rem;
  }}
  .brand em {{ color: var(--yellow); font-style: normal; }}
  .timestamp {{ color: var(--muted); font-size: 0.8rem; font-variant-numeric: tabular-nums; }}
  .subhead {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 22px; }}

  .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 26px; }}
  .stat-card {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
    padding: 12px 10px;
  }}
  .stat-card.accent {{ border-color: color-mix(in srgb, var(--yellow) 45%, var(--border)); }}
  .stat-card.good {{ border-color: color-mix(in srgb, var(--good) 45%, var(--border)); }}
  .stat-card.warn {{ border-color: color-mix(in srgb, var(--warn) 45%, var(--border)); }}
  .stat-label {{
    font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.04em;
    color: var(--muted); margin-bottom: 6px;
  }}
  .stat-value {{
    font-weight: 900; font-size: 1.5rem; font-variant-numeric: tabular-nums;
    letter-spacing: -0.01em;
  }}
  .stat-sub {{ font-size: 0.72rem; color: var(--muted); margin-top: 4px; }}

  h2 {{
    font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em;
    color: var(--muted); margin: 28px 0 10px; font-weight: 700;
  }}

  .table-scroll {{ overflow-x: auto; border-radius: 10px; border: 1px solid var(--border); }}
  table {{ width: 100%; border-collapse: collapse; min-width: 560px; background: var(--surface); }}
  th {{
    text-align: left; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.04em;
    color: var(--muted); padding: 8px 10px; border-bottom: 1px solid var(--border);
    position: sticky; top: 0; background: var(--surface);
  }}
  td {{ padding: 9px 10px; border-bottom: 1px solid var(--border); vertical-align: middle; font-size: 0.85rem; }}
  tr:last-child td {{ border-bottom: none; }}
  td.ep {{ font-weight: 800; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  td.topic {{ color: var(--paper); }}
  .fmt {{
    display: block; font-size: 0.65rem; color: var(--muted); text-transform: uppercase;
    letter-spacing: 0.03em; margin-top: 1px;
  }}
  td.views {{ min-width: 130px; }}
  .bar-track {{ background: var(--surface-2); border-radius: 4px; height: 6px; overflow: hidden; margin-bottom: 4px; }}
  .bar-fill {{ background: var(--yellow); height: 100%; border-radius: 4px; }}
  .views-num {{ font-variant-numeric: tabular-nums; font-size: 0.78rem; color: var(--muted); }}
  td.likes {{ font-variant-numeric: tabular-nums; color: var(--muted); }}
  .pill {{
    display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 0.72rem;
    font-weight: 700; font-variant-numeric: tabular-nums;
    background: var(--surface-2); color: var(--muted);
  }}
  .pill.good {{ background: color-mix(in srgb, var(--good) 22%, var(--surface-2)); color: var(--good); }}
  .pill.warn {{ background: color-mix(in srgb, var(--warn) 22%, var(--surface-2)); color: var(--warn); }}
  .pill.bad {{ background: color-mix(in srgb, var(--bad) 22%, var(--surface-2)); color: var(--bad); }}
  .pill.pending {{ font-style: italic; font-weight: 500; }}
  td.age {{ color: var(--muted); font-size: 0.78rem; white-space: nowrap; }}
  .dot.private {{
    display: inline-block; width: 7px; height: 7px; border-radius: 50%;
    background: var(--pink); margin-left: 5px; vertical-align: middle;
  }}

  ul.open-list {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }}
  ul.open-list li {{
    background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
    padding: 10px 12px; font-size: 0.85rem;
  }}
  .tag {{
    display: inline-block; font-size: 0.65rem; text-transform: uppercase; font-weight: 800;
    letter-spacing: 0.03em; padding: 1px 6px; border-radius: 4px; margin-right: 8px;
    background: var(--surface-2); color: var(--pink);
  }}
  .muted {{ color: var(--muted); }}

  footer {{ margin-top: 30px; color: var(--muted); font-size: 0.72rem; }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="masthead">
      <div class="brand">Random But <em>True</em></div>
      <div class="timestamp">{esc(generated_at)}</div>
    </div>
    <div class="subhead">Channel dashboard — live view/like counts (Data API) and finalised retention (Analytics API, ~2 day lag)</div>

    <div class="stats">{hero}</div>

    <h2>Every episode, most recent first</h2>
    <div class="table-scroll">
      <table>
        <thead><tr><th>Ep</th><th>Topic</th><th>Views</th><th>Likes</th><th>Retention</th><th>Age</th></tr></thead>
        <tbody>{"".join(table_rows)}</tbody>
      </table>
    </div>

    <h2>Open items</h2>
    <ul class="open-list">{open_html}</ul>

    <footer>Retention pill colors: green ≥55%, amber 40–54%, red &lt;40%. Pink dot = private/scheduled, not yet public.</footer>
  </div>
</body>
</html>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    token = get_access_token()
    live = fetch_live_stats(token)
    retention = fetch_retention(token)
    rows = merge(live, retention)
    open_items = read_open_items()

    now = datetime.datetime.now(datetime.timezone.utc)
    generated_at = now.strftime("%a %d %b, %H:%M UTC")

    html_out = build_html(rows, open_items, generated_at)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html_out, encoding="utf-8")
    print(f"wrote {args.out} ({len(html_out)} bytes, {len(rows)} episodes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
