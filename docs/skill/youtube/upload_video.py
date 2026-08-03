#!/usr/bin/env python3
"""
Upload a rendered episode to YouTube via the Data API.

HARD RULE: never run this without the channel owner's explicit, per-video
go-ahead on that specific video AND its upload kit (title/caption/tags) -
the --confirm flag exists to make that a structural requirement, not just
something to remember. Do not add a way to skip it.

Needs docs/skill/youtube/client_secret.json and token.json, and the token
must include the youtube.upload scope (see authorize_local.py's SCOPES). A
token generated before that scope was added will fail with 403 insufficient
permissions - re-run authorize_local.py locally to get a new one if so.

Usage::

    uv run python docs/skill/youtube/upload_video.py \
        --result-json storage/tasks/<id>/viral-result.json \
        --confirm

Uploads as public by default - this matches exactly what happens when the
owner uploads manually and hits Publish (their explicit choice, 2026-08-03:
"public immediately" over a private/unlisted staging step). Pass
--privacy unlisted/private to override for a specific video if ever wanted.

Also sets status.containsSyntheticMedia = true by default (the "Yes" answer
on Studio's "How this content was made" AI-disclosure screen) since every
video here uses AI (TTS) narration - matches how the owner already answers
that screen manually. Pass --no-synthetic-media-disclosure to override.

NOT supported here: Studio's "Related video" field (linking a Short to a
previous episode for cross-promotion) - could not confirm this is exposed
by the public Data API at all, so it is not faked. Add it manually in
Studio after upload if wanted, same as before.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

HERE = Path(__file__).parent
SKILL_DIR = HERE.parent
sys.path.insert(0, str(SKILL_DIR))

from send_to_telegram import build_caption_with_hashtags  # noqa: E402

CLIENT_SECRET_FILE = HERE / "client_secret.json"
TOKEN_FILE = HERE / "token.json"

TOKEN_URI = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"

# YouTube video category IDs - 24 = Entertainment, a reasonable default for
# facts/story Shorts. Override with --category-id if a specific upload
# warrants a different one (e.g. 27 = Education, 15 = Pets & Animals).
DEFAULT_CATEGORY_ID = "24"


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


def upload_video(
    access_token: str,
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    privacy_status: str,
    category_id: str,
    made_for_kids: bool,
    contains_synthetic_media: bool,
) -> dict:
    """Resumable upload: one POST to open the session, one PUT with the bytes.

    Single-shot PUT (no chunking/resume-on-failure) - fine for the sub-60MB
    files this pipeline produces over a stable connection. If large-file
    reliability ever becomes an issue, the resumable session's Location URL
    supports querying/resuming progress via Content-Range, not implemented
    here to keep this simple for now.
    """
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
            "containsSyntheticMedia": contains_synthetic_media,
        },
    }
    size = video_path.stat().st_size
    init_resp = requests.post(
        UPLOAD_URL,
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(size),
        },
        json=metadata,
        timeout=30,
    )
    init_resp.raise_for_status()
    upload_url = init_resp.headers["Location"]

    with video_path.open("rb") as f:
        video_bytes = f.read()
    put_resp = requests.put(
        upload_url,
        headers={"Content-Type": "video/mp4", "Content-Length": str(size)},
        data=video_bytes,
        timeout=900,
    )
    put_resp.raise_for_status()
    return put_resp.json()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--result-json",
        type=Path,
        required=True,
        help="viral-result.json / story-result.json to read video_file + metadata from",
    )
    parser.add_argument(
        "--video", type=Path, default=None, help="override the video file from result-json"
    )
    parser.add_argument(
        "--privacy", choices=["public", "unlisted", "private"], default="public"
    )
    parser.add_argument("--category-id", default=DEFAULT_CATEGORY_ID)
    parser.add_argument("--made-for-kids", action="store_true")
    parser.add_argument(
        "--no-synthetic-media-disclosure",
        dest="synthetic_media",
        action="store_false",
        default=True,
        help=(
            "every video here uses AI (TTS) narration, so the "
            "'How this content was made' AI disclosure is on (Yes) by "
            "default, matching how the owner answers it manually. Only pass "
            "this if a specific upload genuinely has none."
        ),
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        required=True,
        help=(
            "required. Only pass this after the channel owner has explicitly "
            "approved THIS video and its upload kit in the current conversation."
        ),
    )
    args = parser.parse_args(argv)

    if not CLIENT_SECRET_FILE.is_file() or not TOKEN_FILE.is_file():
        print(f"missing client_secret.json/token.json in {HERE}", file=sys.stderr)
        return 1

    result = json.loads(args.result_json.read_text(encoding="utf-8"))
    video_path = args.video or Path(result["video_file"])
    metadata = result.get("metadata", {})
    title = metadata.get("title", "")
    caption = metadata.get("caption", "")
    hashtags = metadata.get("hashtags", [])

    if not video_path.is_file():
        print(f"video file not found: {video_path}", file=sys.stderr)
        return 1
    if not title:
        print("no title in result json", file=sys.stderr)
        return 1

    description = build_caption_with_hashtags(caption, hashtags)
    tags = [h.lstrip("#") for h in hashtags]

    print(f"uploading {video_path} ({video_path.stat().st_size / 1024 / 1024:.1f} MiB)")
    print(f"title: {title}")
    print(f"privacy: {args.privacy}")

    access_token = get_access_token()
    response = upload_video(
        access_token,
        video_path,
        title=title,
        description=description,
        tags=tags,
        privacy_status=args.privacy,
        category_id=args.category_id,
        made_for_kids=args.made_for_kids,
        contains_synthetic_media=args.synthetic_media,
    )
    video_id = response.get("id")
    print(f"uploaded: https://youtube.com/shorts/{video_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
