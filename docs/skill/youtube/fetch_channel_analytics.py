#!/usr/bin/env python3
"""
Query the channel's real YouTube Analytics: per-video views, watch time,
and average-view-percentage (retention) for a date range.

Needs docs/skill/youtube/client_secret.json and docs/skill/youtube/token.json
(the latter produced once by authorize_local.py, run on a machine with a
browser -- see that script's docstring). Both are gitignored. Once token.json
exists, this script is fully headless: it mints a fresh access token from the
refresh token on every run via a plain HTTPS POST, no browser needed.

Usage::

    uv run python docs/skill/youtube/fetch_channel_analytics.py
    uv run python docs/skill/youtube/fetch_channel_analytics.py --days 90 --max-results 50

Replaces the guesswork in channel_playbook.md section 5a ("no per-video view
counts, this pipeline has no YouTube Data API access") with real numbers.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import requests

HERE = Path(__file__).parent
CLIENT_SECRET_FILE = HERE / "client_secret.json"
TOKEN_FILE = HERE / "token.json"

TOKEN_URI = "https://oauth2.googleapis.com/token"
ANALYTICS_URL = "https://youtubeanalytics.googleapis.com/v2/reports"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def get_access_token() -> str:
    client = json.loads(CLIENT_SECRET_FILE.read_text(encoding="utf-8"))["installed"]
    token_data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    resp = requests.post(
        TOKEN_URI,
        data={
            "client_id": client["client_id"],
            "client_secret": client["client_secret"],
            "refresh_token": token_data["refresh_token"],
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_video_metrics(access_token: str, days: int, max_results: int) -> list[dict]:
    end = date.today()
    start = end - timedelta(days=days)
    resp = requests.get(
        ANALYTICS_URL,
        params={
            "ids": "channel==MINE",
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "metrics": "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage",
            "dimensions": "video",
            "sort": "-views",
            "maxResults": max_results,
        },
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    headers = [h["name"] for h in data.get("columnHeaders", [])]
    return [dict(zip(headers, row)) for row in data.get("rows", [])]


def fetch_titles(access_token: str, video_ids: list[str]) -> dict[str, str]:
    if not video_ids:
        return {}
    resp = requests.get(
        VIDEOS_URL,
        params={"part": "snippet", "id": ",".join(video_ids)},
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    resp.raise_for_status()
    return {item["id"]: item["snippet"]["title"] for item in resp.json().get("items", [])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--max-results", type=int, default=25)
    args = parser.parse_args(argv)

    if not CLIENT_SECRET_FILE.is_file() or not TOKEN_FILE.is_file():
        print(
            f"missing {CLIENT_SECRET_FILE.name} and/or {TOKEN_FILE.name} in "
            f"{HERE} - run authorize_local.py on a machine with a browser first",
            file=sys.stderr,
        )
        return 1

    access_token = get_access_token()
    videos = fetch_video_metrics(access_token, days=args.days, max_results=args.max_results)
    if not videos:
        print("no data returned (date range may have no views, or channel too new)")
        return 0

    titles = fetch_titles(access_token, [v.get("video", "") for v in videos if v.get("video")])

    print(f"last {args.days} days, top {len(videos)} videos by views:\n")
    print(f"{'title':<45}{'views':>8}{'avg%':>8}{'avg_dur_s':>11}")
    for v in videos:
        vid = v.get("video", "?")
        title = titles.get(vid, vid)[:44]
        print(
            f"{title:<45}{v.get('views', 0):>8}"
            f"{v.get('averageViewPercentage', 0):>8.1f}"
            f"{v.get('averageViewDuration', 0):>11}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
