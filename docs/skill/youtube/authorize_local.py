#!/usr/bin/env python3
"""
RUN THIS ON YOUR OWN COMPUTER, NOT IN THE REMOTE SESSION.

This is the one-time interactive step: it opens your browser, you log in as
the Google account that manages the Random But True channel and click
Allow, and it saves a token.json containing a refresh token next to this
script. That refresh token does not expire (unless you revoke access), so
this only needs to run once. Send the resulting token.json back so it can
be copied into docs/skill/youtube/token.json in the actual pipeline.

Setup on your machine (one time):
    pip install google-auth-oauthlib

Then put the client_secret.json you downloaded from Google Cloud Console
in the same folder as this script, and run:
    python authorize_local.py
"""
from __future__ import annotations

from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]

HERE = Path(__file__).parent
CLIENT_SECRET_FILE = HERE / "client_secret.json"
TOKEN_FILE = HERE / "token.json"


def main() -> None:
    if not CLIENT_SECRET_FILE.is_file():
        raise SystemExit(
            f"missing {CLIENT_SECRET_FILE} - put your downloaded "
            "client_secret.json next to this script first"
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    print(f"saved {TOKEN_FILE}")
    print("send this file's contents back so it can be wired into the pipeline")


if __name__ == "__main__":
    main()
