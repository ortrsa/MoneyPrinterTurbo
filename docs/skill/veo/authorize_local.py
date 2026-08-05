#!/usr/bin/env python3
"""
RUN THIS ON YOUR OWN COMPUTER, NOT IN THE REMOTE SESSION.

Same pattern as docs/skill/youtube/authorize_local.py: this opens your browser,
you log in as the Google account that has the "Vertex AI User" role (or is
Owner/Editor) on the GCP project set up for AI clip generation, click Allow,
and it saves a token.json containing a refresh token next to this script. That
refresh token does not expire (unless you revoke access), so this only needs
to run once. Send the resulting token.json back so it can be copied into
docs/skill/veo/token.json in the actual pipeline.

WHY A SEPARATE TOKEN FROM THE YOUTUBE ONE. Scopes are requested per-token, not
per-app, so in principle one token could carry both the YouTube scopes and
this one. Keeping them separate means a problem with one (revoked, expired,
project deleted) can never take the other down with it, and it makes clear at
a glance which credential is doing what.

Setup on your machine (one time):
    pip install google-auth-oauthlib

Then:
1. In the SAME Google Cloud project where you enabled the Vertex AI API and
   attached billing, go to APIs & Services -> Credentials -> Create
   Credentials -> OAuth client ID -> Application type "Desktop app".
   Download the resulting JSON.
2. Put it in this same folder as client_secret.json (this folder, not the
   youtube/ one - it must belong to the project that has Vertex AI enabled).
3. Run:
    python authorize_local.py
4. Send back the token.json this prints - it is self-contained (refresh
   token + client id/secret together), so nothing else needs to travel with
   it.
"""
from __future__ import annotations

from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

# cloud-platform is intentionally broad - Vertex/Agent Platform does not
# expose a narrower scope for image + video generation specifically. This is
# the same scope a service-account key would carry for this purpose.
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

HERE = Path(__file__).parent
CLIENT_SECRET_FILE = HERE / "client_secret.json"
TOKEN_FILE = HERE / "token.json"


def main() -> None:
    if not CLIENT_SECRET_FILE.is_file():
        raise SystemExit(
            f"missing {CLIENT_SECRET_FILE} - put the client_secret.json you "
            "downloaded from the Vertex-enabled project's OAuth client next to "
            "this script first"
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    print(f"saved {TOKEN_FILE}")
    print("send this file's contents back so it can be wired into the pipeline")


if __name__ == "__main__":
    main()
