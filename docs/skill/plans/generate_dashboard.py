#!/usr/bin/env python3
"""
Build the channel's evening-report dashboard as a single self-contained HTML
file, using real data only:

- Data API  : live view/like counts, subscriber count, thumbnails (inlined
              as base64 data URIs -- the Artifact CSP blocks remote images)
- Analytics : finalised retention per video, channel views-per-day, and
              per-video daily views for the trajectory ("race") chart

Replaces the old wall-of-Telegram-text evening report. The 20:00 job runs
this, publishes the output via the Artifact tool to a STABLE URL (same file
path every night => same URL -- the owner bookmarks one link), then sends a
short Telegram digest pointing at it.

Usage::

    uv run python docs/skill/plans/generate_dashboard.py --out /path/to/dashboard.html
    uv run python docs/skill/plans/generate_dashboard.py --out ... --no-thumbs   # faster test run

Topic/format metadata is hand-maintained in EPISODE_META below (no API can
tell you what a video is *about*) -- add a line for every new upload.

Known API traps (learned the hard way, see SKILL.md 8f):
- Analytics `reports` 400s without a `sort` param when dimensions=video is
  combined with multiple metrics; always raise_for_status() so a malformed
  query can't masquerade as "no data yet".
- Analytics daily data is FROZEN a few days behind. The race chart therefore
  anchors each line's final point to the LIVE Data-API view count, so brand
  new videos still show an honest trajectory.
"""
from __future__ import annotations

import argparse
import base64
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
TODAYS_UPLOADS = ROOT / "storage" / "todays_uploads.json"

ANALYTICS_URL = "https://youtubeanalytics.googleapis.com/v2/reports"
IL_OFFSET = datetime.timedelta(hours=3)  # IDT; winter is +2, only affects "today" labels

# video_id -> (episode label, topic, format). Hand-maintained -- see docstring.
EPISODE_META: dict[str, tuple[str, str, str]] = {
    "DsoMMdBDb7Q": ("24", "Big cats biology (retitled 'Facts 22' to match live sequence)", "facts"),
    "EtNhXZdSKZc": ("23", "Space facts (retitled 'Facts 21' to match live sequence)", "facts"),
    "yfuSDGdpTw4": ("22", "Pizza toppings (retitled 'Facts 20' to match live sequence)", "facts"),
    "S_zjnvbzZXw": ("21", "D-Day crossword panic (WWII story)", "story"),
    "MsvTGDudZ-U": ("20", "Human body (live title reads 'Facts 19' -- known mislabel, declined fix)", "facts"),
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

# Episode labels that count as "the branded numbered run" for scoreboards
# (pre-branding uploads and the AI-Unfiltered side series would skew medians).
def is_branded(ep: str) -> bool:
    return ep not in ("pre", "?") and not ep.startswith("AI")


# --------------------------------------------------------------------------- data


def fetch_channel_stats(token: str) -> dict:
    r = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={"part": "statistics", "mine": "true"},
        headers={"Authorization": f"Bearer {token}"}, timeout=30,
    )
    r.raise_for_status()
    return r.json()["items"][0]["statistics"]


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


def _analytics(token: str, **params) -> list[list]:
    base = {
        "ids": "channel==MINE",
        "startDate": (datetime.date.today() - datetime.timedelta(days=28)).isoformat(),
        "endDate": datetime.date.today().isoformat(),
    }
    base.update(params)
    r = requests.get(
        ANALYTICS_URL, params=base,
        headers={"Authorization": f"Bearer {token}"}, timeout=30,
    )
    r.raise_for_status()
    return r.json().get("rows", [])


def fetch_retention(token: str) -> dict[str, float]:
    """video_id -> averageViewPercentage, for whatever Analytics has finalised."""
    rows = _analytics(
        token, metrics="views,averageViewPercentage",
        dimensions="video", sort="-views", maxResults=50,
    )
    return {vid: avg for vid, _views, avg in rows}


def fetch_channel_daily(token: str) -> list[tuple[datetime.date, int]]:
    rows = _analytics(token, metrics="views", dimensions="day", sort="day")
    out = [(datetime.date.fromisoformat(d), int(v)) for d, v in rows]
    # trim the leading dead days before the channel's first view
    while out and out[0][1] == 0:
        out.pop(0)
    return out


def fetch_watch_minutes(token: str) -> int:
    rows = _analytics(token, metrics="estimatedMinutesWatched")
    return int(rows[0][0]) if rows else 0


def fetch_video_daily(token: str, video_id: str) -> list[tuple[datetime.date, int]]:
    rows = _analytics(
        token, metrics="views", dimensions="day", sort="day",
        filters=f"video=={video_id}",
    )
    return [(datetime.date.fromisoformat(d), int(v)) for d, v in rows]


def fetch_thumb(video_id: str) -> str | None:
    """mqdefault jpg inlined as a data URI; None for private/missing (404)."""
    try:
        r = requests.get(f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg", timeout=15)
        if r.ok and r.headers.get("content-type", "").startswith("image/"):
            return "data:image/jpeg;base64," + base64.b64encode(r.content).decode()
    except requests.RequestException:
        pass
    return None


def merge(live: list[dict], retention: dict[str, float]) -> list[dict]:
    out = []
    for r in live:
        ep, topic, fmt = EPISODE_META.get(r["id"], ("?", "(unmapped -- add to EPISODE_META)", "facts"))
        out.append({**r, "ep": ep, "topic": topic, "fmt": fmt, "ret": retention.get(r["id"])})
    return out


def read_open_items() -> dict:
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


def read_todays_slots() -> dict:
    """Slot approval/publish state, if the 13:00 job has written it today."""
    try:
        data = json.loads(TODAYS_UPLOADS.read_text(encoding="utf-8"))
        today_il = (datetime.datetime.now(datetime.timezone.utc) + IL_OFFSET).date().isoformat()
        if data.get("date") == today_il:
            return data.get("slots", {})
    except (OSError, ValueError):
        pass
    return {}


# --------------------------------------------------------------------------- shaping


def pub_dt(row: dict) -> datetime.datetime:
    return datetime.datetime.fromisoformat(row["published"].replace("Z", "+00:00"))


def cumulative_series(
    daily: list[tuple[datetime.date, int]], row: dict, now: datetime.datetime,
) -> list[tuple[float, int]]:
    """(age_in_days, cumulative_views) points: analytics dailies where they
    exist, anchored to the live Data-API count as the final truth-point."""
    published = pub_dt(row)
    pts: list[tuple[float, int]] = [(0.0, 0)]
    total = 0
    for day, v in daily:
        day_end = datetime.datetime.combine(
            day + datetime.timedelta(days=1), datetime.time.min, tzinfo=datetime.timezone.utc,
        )
        if day_end <= published:
            continue
        total += v
        pts.append((round((day_end - published).total_seconds() / 86400, 2), total))
    age_now = (now - published).total_seconds() / 86400
    if row["views"] >= total:
        pts.append((round(age_now, 2), row["views"]))
    return pts


def nice_ceil(v: float) -> int:
    if v <= 0:
        return 1
    mag = 10 ** (len(str(int(v))) - 1)
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * mag:
            return int(m * mag)
    return int(10 * mag)


def short(n: float) -> str:
    if n >= 1000:
        s = f"{n / 1000:.1f}".rstrip("0").rstrip(".")
        return f"{s}K"
    return f"{int(n)}"


def median(vals: list[float]) -> float:
    if not vals:
        return 0
    s = sorted(vals)
    m = len(s) // 2
    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def fmt_age(published: str, now: datetime.datetime) -> str:
    hours = (now - datetime.datetime.fromisoformat(published.replace("Z", "+00:00"))).total_seconds() / 3600
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


# --------------------------------------------------------------------------- svg charts


def svg_daily_chart(daily: list[tuple[datetime.date, int]], upload_days: set[datetime.date]) -> str:
    if len(daily) < 2:
        return '<p class="muted">Not enough finalised days yet for a chart.</p>'
    W, H, L, R, T, B = 640, 190, 40, 14, 14, 30
    ymax = nice_ceil(max(v for _, v in daily))
    x0, x1 = daily[0][0].toordinal(), daily[-1][0].toordinal()
    span = max(x1 - x0, 1)

    def X(d: datetime.date) -> float:
        return round(L + (d.toordinal() - x0) / span * (W - L - R), 1)

    def Y(v: float) -> float:
        return round(T + (1 - v / ymax) * (H - T - B), 1)

    line = " ".join(f"{X(d)},{Y(v)}" for d, v in daily)
    area = f"{X(daily[0][0])},{Y(0)} {line} {X(daily[-1][0])},{Y(0)}"
    grid = ""
    for frac in (0.5, 1.0):
        gy = Y(ymax * frac)
        grid += (
            f'<line x1="{L}" y1="{gy}" x2="{W - R}" y2="{gy}" class="grid"/>'
            f'<text x="{L - 6}" y="{gy + 4}" class="axis" text-anchor="end">{short(ymax * frac)}</text>'
        )
    marks = "".join(
        f'<path d="M{X(d) - 4},{H - 8} L{X(d) + 4},{H - 8} L{X(d)},{H - 15} Z" class="upmark"/>'
        for d in sorted(upload_days) if daily[0][0] <= d <= daily[-1][0]
    )
    last_d, last_v = daily[-1]
    return f"""<svg viewBox="0 0 {W} {H}" role="img" aria-label="Channel views per day">
      {grid}
      <polygon points="{area}" class="areafill"/>
      <polyline points="{line}" class="areaLine"/>
      <circle cx="{X(last_d)}" cy="{Y(last_v)}" r="4" class="dot"/>
      <text x="{X(last_d) - 8}" y="{Y(last_v) - 9}" class="dotlabel" text-anchor="end">{short(last_v)}</text>
      {marks}
      <text x="{L}" y="{H - 4}" class="axis">{daily[0][0].strftime("%d %b")}</text>
      <text x="{W - R}" y="{H - 4}" class="axis" text-anchor="end">{last_d.strftime("%d %b")}</text>
    </svg>"""


RACE_WINDOW_DAYS = 5.0  # Shorts live or die in their first days; a longer axis
                        # just flattens the decisive early curve into a corner


def clip_series(points: list[tuple[float, int]], window: float) -> list[tuple[float, int]]:
    """Keep points inside the window, interpolating one point exactly at the
    boundary if the line crosses it, so clipped lines still reach the edge."""
    kept = [p for p in points if p[0] <= window]
    beyond = [p for p in points if p[0] > window]
    if kept and beyond:
        (x0, y0), (x1, y1) = kept[-1], beyond[0]
        t = (window - x0) / (x1 - x0)
        kept.append((window, round(y0 + t * (y1 - y0))))
    return kept


def svg_race_chart(lines: list[dict]) -> str:
    """lines: [{label, cls, points [(age_days, cum_views)]}] newest-first."""
    lines = [
        {**ln, "points": clip_series(ln["points"], RACE_WINDOW_DAYS)}
        for ln in lines
    ]
    lines = [ln for ln in lines if len(ln["points"]) >= 2]
    if not lines:
        return '<p class="muted">No trajectory data yet.</p>'
    W, H, L, R, T, B = 640, 250, 40, 56, 14, 26
    xmax = max(1.0, max(p[0] for ln in lines for p in ln["points"]))
    ymax = nice_ceil(max(p[1] for ln in lines for p in ln["points"]))

    def X(a: float) -> float:
        return round(L + a / xmax * (W - L - R), 1)

    def Y(v: float) -> float:
        return round(T + (1 - v / ymax) * (H - T - B), 1)

    grid = ""
    for frac in (0.5, 1.0):
        gy = Y(ymax * frac)
        grid += (
            f'<line x1="{L}" y1="{gy}" x2="{W - R}" y2="{gy}" class="grid"/>'
            f'<text x="{L - 6}" y="{gy + 4}" class="axis" text-anchor="end">{short(ymax * frac)}</text>'
        )
    ticks = "".join(
        f'<text x="{X(d)}" y="{H - 6}" class="axis" text-anchor="middle">d{d}</text>'
        for d in range(0, int(xmax) + 1, max(1, int(xmax // 5) or 1))
    )
    paths, labels = "", ""
    used_y: list[float] = []
    for ln in lines:
        pts = " ".join(f"{X(a)},{Y(v)}" for a, v in ln["points"])
        paths += f'<polyline points="{pts}" class="race {ln["cls"]}"/>'
        la, lv = ln["points"][-1]
        ly = Y(lv)
        while any(abs(ly - u) < 13 for u in used_y):  # nudge overlapping end labels
            ly -= 13
        used_y.append(ly)
        labels += (
            f'<text x="{X(la) + 6}" y="{ly + 4}" class="racelabel {ln["cls"]}">'
            f"{esc(ln['label'])}</text>"
        )
    return f"""<svg viewBox="0 0 {W} {H}" role="img" aria-label="Views by days since publish, per episode">
      {grid}{ticks}{paths}{labels}
    </svg>"""


# --------------------------------------------------------------------------- html

CSS = """
  :root {
    --ink: #14110c;
    --surface: #1e1a14;
    --surface-2: #272117;
    --border: #352c1e;
    --paper: #f4efe6;
    --muted: #9c9284;
    --yellow: #ffe500;
    --pink: #ff2d6e;
    --good: #8fce7f;
    --warn: #eab04c;
    --bad: #ef6a50;
    --chart-grid: #352c1e;
  }
  :root[data-theme="light"] {
    --ink: #faf6ee; --surface: #ffffff; --surface-2: #f2ece0; --border: #e3d9c6;
    --paper: #221d15; --muted: #756c5e; --yellow: #b89900; --pink: #d81b60;
    --good: #2f8f4e; --warn: #b9770e; --bad: #c8402c; --chart-grid: #e8dfcd;
  }
  @media (prefers-color-scheme: light) {
    :root:not([data-theme="dark"]) {
      --ink: #faf6ee; --surface: #ffffff; --surface-2: #f2ece0; --border: #e3d9c6;
      --paper: #221d15; --muted: #756c5e; --yellow: #b89900; --pink: #d81b60;
      --good: #2f8f4e; --warn: #b9770e; --bad: #c8402c; --chart-grid: #e8dfcd;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--ink); color: var(--paper);
    font-family: ui-sans-serif, "Segoe UI", "Avenir Next", system-ui, sans-serif;
    line-height: 1.45; padding: 20px 14px 56px;
  }
  .wrap { max-width: 720px; margin: 0 auto; }
  .masthead { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
  .brand { font-weight: 900; text-transform: uppercase; letter-spacing: -0.015em; font-size: 1.6rem; }
  .brand em { color: var(--yellow); font-style: normal; }
  .timestamp { color: var(--muted); font-size: 0.78rem; font-variant-numeric: tabular-nums; }
  .subhead { color: var(--muted); font-size: 0.88rem; margin: 2px 0 20px; }

  .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
  @media (max-width: 520px) { .stats { grid-template-columns: repeat(2, 1fr); } }
  .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 11px 12px; }
  .stat-card.accent { border-color: color-mix(in srgb, var(--yellow) 50%, var(--border)); }
  .stat-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); margin-bottom: 4px; }
  .stat-value { font-weight: 900; font-size: 1.45rem; font-variant-numeric: tabular-nums; letter-spacing: -0.01em; }
  .stat-sub { font-size: 0.7rem; color: var(--muted); margin-top: 2px; }

  h2 { font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.07em; color: var(--muted); margin: 30px 0 10px; font-weight: 700; }
  h2 .accentbar { display: inline-block; width: 16px; height: 8px; background: var(--yellow); margin-right: 8px; border-radius: 2px; }

  .takeaways { display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }
  .takeaways li { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--yellow); border-radius: 8px; padding: 10px 13px; font-size: 0.9rem; }
  .takeaways li strong { color: var(--yellow); font-weight: 800; }

  .chart-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px 12px 8px; }
  .chart-note { color: var(--muted); font-size: 0.72rem; margin: 6px 4px 4px; }
  svg { width: 100%; height: auto; display: block; }
  .grid { stroke: var(--chart-grid); stroke-width: 1; }
  .axis { fill: var(--muted); font-size: 11px; font-variant-numeric: tabular-nums; }
  .areafill { fill: var(--yellow); fill-opacity: 0.14; }
  .areaLine { fill: none; stroke: var(--yellow); stroke-width: 2.25; stroke-linejoin: round; }
  .dot { fill: var(--yellow); }
  .dotlabel { fill: var(--paper); font-size: 12px; font-weight: 700; font-variant-numeric: tabular-nums; }
  .upmark { fill: var(--pink); }
  .race { fill: none; stroke-width: 1.6; stroke-linejoin: round; stroke: #8a7f6d; opacity: 0.55; }
  .race.hot { stroke: var(--yellow); stroke-width: 2.6; opacity: 1; }
  .race.hot2 { stroke: var(--pink); stroke-width: 2.2; opacity: 1; }
  .racelabel { fill: #8a7f6d; font-size: 11px; font-weight: 700; }
  .racelabel.hot { fill: var(--yellow); }
  .racelabel.hot2 { fill: var(--pink); }

  .scoreboard { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
  @media (max-width: 520px) { .scoreboard { grid-template-columns: 1fr; } }
  .score-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 11px 13px; }
  .score-card h3 { margin: 0 0 6px; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; }
  .score-card h3.story { color: var(--pink); }
  .score-card h3.facts { color: var(--yellow); }
  .score-row { display: flex; justify-content: space-between; font-size: 0.82rem; padding: 2px 0; }
  .score-row .k { color: var(--muted); }
  .score-row .v { font-variant-numeric: tabular-nums; font-weight: 700; }

  .eps { display: grid; gap: 8px; }
  .ep-card {
    display: grid; grid-template-columns: 88px 1fr auto; gap: 12px; align-items: center;
    background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 10px 12px 12px; color: inherit; position: relative; overflow: hidden;
  }
  .ep-card:hover { border-color: color-mix(in srgb, var(--yellow) 40%, var(--border)); }
  .card-link { position: absolute; inset: 0; z-index: 1; }
  .watch {
    position: relative; z-index: 2; text-decoration: none;
    font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 800;
    padding: 1px 7px; border-radius: 999px; background: var(--surface-2); color: var(--muted);
  }
  .watch:hover { color: var(--yellow); }
  .thumb, .thumb-ph { width: 88px; height: 50px; border-radius: 6px; object-fit: cover; display: block; }
  .thumb-ph {
    background: linear-gradient(135deg, var(--surface-2), var(--border));
    display: flex; align-items: center; justify-content: center;
    color: var(--yellow); font-weight: 900; font-size: 0.9rem;
  }
  .ep-main { min-width: 0; }
  .ep-title { font-weight: 800; font-size: 0.92rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .ep-title .num { color: var(--yellow); }
  .ep-meta { display: flex; gap: 8px; align-items: center; margin-top: 3px; flex-wrap: wrap; }
  .chip { font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.04em; font-weight: 800; padding: 1px 7px; border-radius: 999px; background: var(--surface-2); color: var(--muted); }
  .chip.story { color: var(--pink); }
  .age { color: var(--muted); font-size: 0.72rem; }
  .ep-nums { text-align: right; font-variant-numeric: tabular-nums; }
  .ep-views { font-weight: 900; font-size: 1.05rem; }
  .ep-likes { color: var(--muted); font-size: 0.74rem; }
  .pill { display: inline-block; margin-top: 3px; padding: 1px 8px; border-radius: 999px; font-size: 0.7rem; font-weight: 700; background: var(--surface-2); color: var(--muted); font-variant-numeric: tabular-nums; }
  .pill.good { background: color-mix(in srgb, var(--good) 22%, var(--surface-2)); color: var(--good); }
  .pill.warn { background: color-mix(in srgb, var(--warn) 22%, var(--surface-2)); color: var(--warn); }
  .pill.bad { background: color-mix(in srgb, var(--bad) 22%, var(--surface-2)); color: var(--bad); }
  .pill.pending { font-style: italic; font-weight: 500; }
  .pill.queued { background: color-mix(in srgb, var(--pink) 20%, var(--surface-2)); color: var(--pink); font-style: normal; font-weight: 700; }
  .bar-rail { position: absolute; left: 0; right: 0; bottom: 0; height: 3px; background: transparent; }
  .bar-rail i { display: block; height: 100%; background: var(--yellow); opacity: 0.75; }

  ul.open-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
  ul.open-list li { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; font-size: 0.85rem; }
  .tag { display: inline-block; font-size: 0.63rem; text-transform: uppercase; font-weight: 800; letter-spacing: 0.03em; padding: 1px 6px; border-radius: 4px; margin-right: 8px; background: var(--surface-2); color: var(--pink); }
  .muted { color: var(--muted); }
  footer { margin-top: 34px; color: var(--muted); font-size: 0.72rem; line-height: 1.6; }
"""


def build_takeaways(rows: list[dict], subs: int, now: datetime.datetime) -> list[str]:
    """Honest, computed-from-data bullets -- no adjectives the numbers don't earn."""
    out = []
    week = [
        r for r in rows
        if r["privacy"] == "public" and (now - pub_dt(r)).days < 7
    ]
    if week:
        t = max(week, key=lambda r: r["views"])
        out.append(
            f"<strong>Ep {esc(t['ep'])} ({esc(t['topic'])})</strong> leads the last 7 days "
            f"with {t['views']:,} views."
        )
    best = max(
        (r for r in rows if r["ret"] is not None and r["views"] >= 100),
        key=lambda r: r["ret"], default=None,
    )
    if best:
        out.append(
            f"Retention record: <strong>{best['ret']:.1f}%</strong> — "
            f"ep {esc(best['ep'])} ({esc(best['topic'])}). That is the bar new episodes are judged against."
        )
    facts_views = [r["views"] for r in rows if r["fmt"] == "facts" and is_branded(r["ep"]) and r["privacy"] == "public"]
    story = [r for r in rows if r["fmt"] == "story" and r["privacy"] == "public"]
    if story and facts_views:
        s = max(story, key=lambda r: r["views"])
        med = median(facts_views)
        ret_txt = f"{s['ret']:.0f}% retention" if s["ret"] is not None else "retention not finalised yet"
        vs = "above" if s["views"] > med else "below"
        out.append(
            f"Story format check: ep {esc(s['ep'])} sits at <strong>{s['views']:,}</strong> views, "
            f"{vs} the {med:,.0f} facts median; {ret_txt} — verdict "
            f"{'in' if s['ret'] is not None else 'still open'}."
        )
    total_views = sum(r["views"] for r in rows)
    if subs:
        out.append(
            f"<strong>{subs}</strong> subscribers on {total_views:,} total views "
            f"({subs / max(total_views, 1) * 100:.2f}% conversion — the healthy Shorts range is 0.5–2%, "
            f"so growth here follows volume)."
        )
    return out


def build_html(
    rows: list[dict], open_items: dict, chan: dict, watch_min: int,
    daily: list[tuple[datetime.date, int]], race_lines: list[dict],
    thumbs: dict[str, str], slots: dict, now: datetime.datetime,
) -> str:
    max_views = max((r["views"] for r in rows), default=1) or 1
    subs = int(chan.get("subscriberCount", 0))
    takeaways = "".join(f"<li>{t}</li>" for t in build_takeaways(rows, subs, now))

    upload_days = {pub_dt(r).date() for r in rows if r["privacy"] == "public"}
    daily_svg = svg_daily_chart(daily, upload_days)
    race_svg = svg_race_chart(race_lines)

    # format scoreboard over the branded run only
    score_cards = ""
    for fmt, cls in (("facts", "facts"), ("story", "story"), ("facts-short", "")):
        grp = [r for r in rows if r["fmt"] == fmt and is_branded(r["ep"]) and r["privacy"] == "public"]
        if not grp:
            continue
        rets = [r["ret"] for r in grp if r["ret"] is not None]
        ret_txt = f"{sum(rets) / len(rets):.0f}% <span class='muted'>(n={len(rets)})</span>" if rets else "—"
        score_cards += f"""
        <div class="score-card">
          <h3 class="{cls}">{esc(fmt)}</h3>
          <div class="score-row"><span class="k">episodes</span><span class="v">{len(grp)}</span></div>
          <div class="score-row"><span class="k">median views</span><span class="v">{median([g["views"] for g in grp]):,.0f}</span></div>
          <div class="score-row"><span class="k">avg retention</span><span class="v">{ret_txt}</span></div>
        </div>"""

    # episode cards
    slot_by_episode = {
        str(v.get("episode", "")): (slot, v) for slot, v in slots.items() if isinstance(v, dict)
    }
    cards = ""
    for r in rows:
        pct = max(2, round(r["views"] / max_views * 100))
        thumb = (
            f'<img class="thumb" src="{thumbs[r["id"]]}" alt="" loading="lazy">'
            if thumbs.get(r["id"])
            else f'<span class="thumb-ph">{esc(r["ep"])}</span>'
        )
        fmt_chip = f'<span class="chip {"story" if r["fmt"] == "story" else ""}">{esc(r["fmt"])}</span>'
        if r["privacy"] != "public":
            slot_info = slot_by_episode.get(str(r["ep"]))
            when = f"today {slot_info[0]}" if slot_info else "awaiting its slot"
            nums = f'<span class="pill queued">queued · {esc(when)}</span>'
        else:
            ret = r["ret"]
            pill = (
                f'<span class="pill {retention_class(ret)}">{ret:.0f}% ret</span>'
                if ret is not None else '<span class="pill pending">ret pending</span>'
            )
            nums = (
                f'<div class="ep-views">{r["views"]:,}</div>'
                f'<div class="ep-likes">{r["likes"]} likes</div>{pill}'
            )
        studio = f"https://studio.youtube.com/video/{esc(r['id'])}/analytics/tab-overview/period-default"
        cards += f"""
        <div class="ep-card">
          <a class="card-link" href="{studio}" target="_blank" rel="noopener"
             aria-label="Open ep {esc(r["ep"])} in YouTube Studio analytics"></a>
          {thumb}
          <div class="ep-main">
            <div class="ep-title"><span class="num">Ep {esc(r["ep"])}</span> · {esc(r["topic"])}</div>
            <div class="ep-meta">{fmt_chip}<span class="age">{fmt_age(r["published"], now)}</span>
              <a class="watch" href="https://www.youtube.com/shorts/{esc(r["id"])}" target="_blank" rel="noopener">▶ watch</a></div>
          </div>
          <div class="ep-nums">{nums}</div>
          <span class="bar-rail"><i style="width:{pct}%"></i></span>
        </div>"""

    open_lis = "".join(
        f'<li><span class="tag">on hold</span> ep {esc(i.get("episode", "?"))} — {esc(i.get("topic", ""))}</li>'
        for i in open_items["on_hold"]
    ) + "".join(
        f'<li><span class="tag">unbuilt</span> ep {esc(i.get("episode", "?"))} — {esc(i.get("topic", ""))}</li>'
        for i in open_items["unbuilt"]
    )
    open_html = f'<h2><span class="accentbar"></span>Pipeline</h2><ul class="open-list">{open_lis}</ul>' if open_lis else ""

    il_now = (now + IL_OFFSET).strftime("%a %d %b, %H:%M")
    return f"""<title>Random But True — Channel Dashboard</title>
<style>{CSS}</style>
<div class="wrap">
  <div class="masthead">
    <div class="brand">Random But <em>True</em></div>
    <div class="timestamp">{il_now} Israel time</div>
  </div>
  <div class="subhead">Live counts from the Data API · retention &amp; daily curves from the Analytics API (finalised days only, ~2-day lag)</div>

  <div class="stats">
    <div class="stat-card accent">
      <div class="stat-label">Subscribers</div>
      <div class="stat-value">{subs:,}</div>
      <div class="stat-sub">channel total</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total views</div>
      <div class="stat-value">{sum(r["views"] for r in rows):,}</div>
      <div class="stat-sub">all videos, live</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Watch time</div>
      <div class="stat-value">{watch_min / 60:,.1f}h</div>
      <div class="stat-sub">last 28 days</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Videos</div>
      <div class="stat-value">{len([r for r in rows if r["privacy"] == "public"])}</div>
      <div class="stat-sub">public ({len(rows)} total)</div>
    </div>
  </div>

  <h2><span class="accentbar"></span>What the numbers say</h2>
  <ul class="takeaways">{takeaways}</ul>

  <h2><span class="accentbar"></span>Channel views per day</h2>
  <div class="chart-card">
    {daily_svg}
    <p class="chart-note">▲ pink markers = upload days · finalised Analytics days only, the last ~2 days aren't in yet</p>
  </div>

  <h2><span class="accentbar"></span>The race — every episode at the same age</h2>
  <div class="chart-card">
    {race_svg}
    <p class="chart-note">Cumulative views over each episode's first {int(RACE_WINDOW_DAYS)} days. Yellow = newest episode, pink = second newest — read whether the new one is tracking above or below the pack at the same age. Line ends anchored to live counts.</p>
  </div>

  <h2><span class="accentbar"></span>Format scoreboard <span class="muted">(branded episodes only)</span></h2>
  <div class="scoreboard">{score_cards}</div>

  <h2><span class="accentbar"></span>Every episode, newest first</h2>
  <div class="eps">{cards}</div>

  {open_html}

  <footer>
    Retention pills: green ≥55% · amber 40–54% · red &lt;40% · “pending” = Analytics hasn't finalised it yet (~2 days).
    Yellow bar under each card = views relative to the channel's top video. Clicking a card opens that video's
    YouTube Studio analytics (channel owner only); “▶ watch” opens the public video.
    Regenerated nightly at 20:00 by the evening-report job — same URL every night.
  </footer>
</div>
"""


# --------------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--no-thumbs", action="store_true", help="skip thumbnail fetching (faster test runs)")
    args = parser.parse_args(argv)

    now = datetime.datetime.now(datetime.timezone.utc)
    token = get_access_token()

    chan = fetch_channel_stats(token)
    live = fetch_live_stats(token)
    retention = fetch_retention(token)
    daily = fetch_channel_daily(token)
    watch_min = fetch_watch_minutes(token)
    rows = merge(live, retention)

    # race chart: branded public episodes -- top 5 by views + the 3 newest
    branded = [r for r in rows if is_branded(r["ep"]) and r["privacy"] == "public"]
    chosen = {r["id"]: r for r in sorted(branded, key=lambda r: r["views"], reverse=True)[:5]}
    for r in branded[:3]:
        chosen[r["id"]] = r
    race_rows = sorted(chosen.values(), key=lambda r: r["published"], reverse=True)
    race_lines = []
    for i, r in enumerate(race_rows):
        vid_daily = fetch_video_daily(token, r["id"])
        cls = "hot" if i == 0 else ("hot2" if i == 1 else "")
        race_lines.append({
            "label": f"ep{r['ep']}", "cls": cls,
            "points": cumulative_series(vid_daily, r, now),
        })

    thumbs: dict[str, str] = {}
    if not args.no_thumbs:
        for r in rows:
            uri = fetch_thumb(r["id"])
            if uri:
                thumbs[r["id"]] = uri

    doc = build_html(
        rows, read_open_items(), chan, watch_min, daily, race_lines,
        thumbs, read_todays_slots(), now,
    )
    args.out.write_text(doc, encoding="utf-8")
    print(
        f"wrote {args.out} ({len(doc.encode()):,} bytes, {len(rows)} episodes, "
        f"{len(thumbs)} thumbnails, {len(race_lines)} race lines)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
