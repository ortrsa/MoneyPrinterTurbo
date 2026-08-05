#!/usr/bin/env python3
"""
Generate one AI B-roll clip: nano-banana paints the first frame, Veo animates it.

WHY TWO STAGES INSTEAD OF TEXT-TO-VIDEO. Veo can go straight from text, but then
the opening frame is a lottery - and the opening frame is exactly what matters
here, because these clips are spliced into a segment whose first instant the
viewer judges. Painting the frame first makes that instant reviewable BEFORE any
video money is spent: look at the PNG, and if the composition is wrong, re-roll
the image (cheap) rather than the video (not cheap).

WHAT THIS IS FOR. This is a gap-filler, not a footage source. The channel's
footage comes from Pexels; this exists for the specific case where a segment
names something the stock library genuinely does not have (an extinct animal, a
period scene, a physical impossibility) and every probed term returns filler or
something that contradicts the narration. See SKILL.md for the judgement call.

AUTH. Two backends, because they have different costs and different ceilings:

  agent-platform  Google Cloud, the console at console.cloud.google.com/
                  agent-platform. This is Vertex AI under its 2026 name - the
                  SDK still takes vertexai=True and the API is unchanged, only
                  the branding moved. Needs a project with billing enabled and
                  a credential: either an OAuth token (docs/skill/veo/token.json,
                  produced by docs/skill/veo/authorize_local.py - run locally,
                  see SKILL.md) or a service-account key
                  (docs/skill/veo/service_account.json). Either is enough; the
                  OAuth token is tried first. This is the backend that can run
                  Veo.

  api-key         The Gemini Developer API, with a key from aistudio.google.com.
                  Simpler, and its free tier covers image generation - so the
                  prompt-to-first-frame loop can be iterated at no cost. It does
                  NOT cover Veo: video generation is paid-tier only, and a free
                  key will be refused at the animate step.

Neither can use the YouTube OAuth token: that carries YouTube scopes and reaches
neither backend, no matter how it is passed.

Config lives in config.toml under [google_ai] (the older [vertex] section is
still read, for anything written before the rename). Credentials never come from
the command line - they would end up in shell history and in the process list.

Usage::

    # 0. one-time: check credentials work, spends nothing
    uv run python docs/skill/ai-footage-fill/scripts/generate_ai_clip.py --probe

    # 1. see the plan and the cost, spends nothing
    uv run python docs/skill/ai-footage-fill/scripts/generate_ai_clip.py \
        --prompt "a moa, a giant wingless bird, standing in dense New Zealand forest" \
        --out storage/ai_clips/moa.mp4 --dry-run

    # 2. actually generate (--confirm is required; it is the cost gate)
    uv run python docs/skill/ai-footage-fill/scripts/generate_ai_clip.py \
        --prompt "..." --out storage/ai_clips/moa.mp4 --confirm

    # 3. image only, to iterate on composition before paying for video
    uv run python docs/skill/ai-footage-fill/scripts/generate_ai_clip.py \
        --prompt "..." --out storage/ai_clips/moa.mp4 --image-only --confirm

The clip is written silently on purpose (generate_audio=False): the pipeline
replaces the audio track with the narration anyway, so generated audio would be
paid for and then discarded.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

# Defaults are deliberately overridable from config.toml and the CLI: Google
# renames and retires these model IDs on its own schedule, and a rename should
# be a one-line config edit, not a code change.
DEFAULT_IMAGE_MODEL = "gemini-2.5-flash-image"
DEFAULT_VIDEO_MODEL = "veo-3.1-generate-preview"
DEFAULT_LOCATION = "us-central1"
DEFAULT_DURATION = 8
DEFAULT_ASPECT = "9:16"
DEFAULT_RESOLUTION = "1080p"

# Rough list-price estimate, only used to print a number before spending.
# Veo is billed per second of output video; treat this as an order-of-magnitude
# figure for the confirmation prompt, not an invoice.
APPROX_VIDEO_USD_PER_SECOND = 0.40
APPROX_IMAGE_USD = 0.04

POLL_SECONDS = 10
POLL_TIMEOUT_SECONDS = 900

# Veo refuses some prompts outright, and a refusal still costs a round trip and
# looks like a bug if it is not named. These are the things it reliably rejects
# for this channel's subject matter.
PROMPT_GUARDRAILS = """\
Write the prompt as a filmable scene, not as a fact or a caption. Name the
subject, the camera framing, the lighting and the motion. Avoid: real named
people, brand logos, on-screen text or numbers (Veo renders text as garbled
glyphs and it collides with our burned-in captions anyway), graphic injury, and
anything that reads as a news or documentary clip of a real event."""


def load_ai_config(overrides: dict) -> dict:
    """Merge config.toml [google_ai] with CLI overrides; CLI wins.

    [vertex] is still read as a fallback so config written before the 2026
    rename keeps working - the section moved, the meaning did not.
    """
    import tomllib

    config_path = REPO_ROOT / "config.toml"
    section: dict = {}
    if config_path.exists():
        with open(config_path, "rb") as handle:
            parsed = tomllib.load(handle)
            section = parsed.get("google_ai") or parsed.get("vertex") or {}

    # Infer the backend from whichever credential is actually present, so the
    # common case needs no explicit setting: a project implies Agent Platform,
    # a bare API key implies the Developer API.
    backend = section.get("backend")
    if not backend:
        backend = "agent-platform" if section.get("project") else "api-key"

    merged = {
        "backend": backend,
        "project": section.get("project"),
        "location": section.get("location", DEFAULT_LOCATION),
        "service_account_file": section.get(
            "service_account_file", "docs/skill/veo/service_account.json"
        ),
        "token_file": section.get("token_file", "docs/skill/veo/token.json"),
        "api_key": section.get("api_key"),
        "image_model": section.get("image_model", DEFAULT_IMAGE_MODEL),
        "video_model": section.get("video_model", DEFAULT_VIDEO_MODEL),
    }
    for key, value in overrides.items():
        if value:
            merged[key] = value
    return merged


def build_client(config: dict):
    """Authenticate to whichever backend is configured.

    Every failure here is a setup problem with a specific fix, so each one says
    what to do rather than surfacing a raw library traceback.
    """
    from google import genai

    backend = config["backend"]
    if backend not in ("agent-platform", "api-key"):
        raise SystemExit(
            f"Unknown backend {backend!r}. Use 'agent-platform' or 'api-key'."
        )

    if backend == "api-key":
        if not config.get("api_key"):
            raise SystemExit(
                "No API key configured.\n"
                "Get one from https://aistudio.google.com/apikey, then add to "
                "config.toml:\n\n"
                "  [google_ai]\n"
                '  backend = "api-key"\n'
                '  api_key = "..."\n\n'
                "Note this backend can generate images on the free tier but NOT "
                "video -\nVeo is paid-tier only. For video use the "
                "agent-platform backend."
            )
        return genai.Client(api_key=config["api_key"])

    if not config.get("project"):
        raise SystemExit(
            "No Google Cloud project configured.\n"
            "Add this to config.toml:\n\n"
            "  [google_ai]\n"
            '  backend = "agent-platform"\n'
            '  project = "your-gcp-project-id"\n'
            f'  location = "{DEFAULT_LOCATION}"\n'
        )

    credentials = _load_agent_platform_credentials(config)

    # vertexai=True is still correct after the Agent Platform rename: the
    # console branding changed, the SDK flag and the API did not.
    return genai.Client(
        vertexai=True,
        credentials=credentials,
        project=config["project"],
        location=config["location"],
    )


def _resolve(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else REPO_ROOT / path


def _load_agent_platform_credentials(config: dict):
    """Load whichever credential is on disk: OAuth user token, or a
    service-account key. Two forms, one purpose - both end up as a
    google.auth Credentials object and the caller does not need to care
    which kind it got.

    OAuth is checked first because it is the path this channel's owner
    chose (it mirrors the YouTube authorize_local.py flow they already
    know), but either works interchangeably.
    """
    token_path = _resolve(config["token_file"])
    if token_path.exists():
        from google.oauth2.credentials import Credentials as UserCredentials

        try:
            return UserCredentials.from_authorized_user_file(
                str(token_path),
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        except Exception as exc:
            raise SystemExit(
                f"Could not read the OAuth token at {token_path}: {exc}\n"
                "It should be the token.json produced by "
                "docs/skill/veo/authorize_local.py, kept verbatim - it carries "
                "its own client_id/client_secret, nothing else needs to travel "
                "with it."
            ) from exc

    key_path = _resolve(config["service_account_file"])
    if key_path.exists():
        from google.oauth2 import service_account

        try:
            return service_account.Credentials.from_service_account_file(
                str(key_path),
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        except Exception as exc:
            raise SystemExit(
                f"Could not read the service-account key at {key_path}: {exc}\n"
                "It should be the JSON key file downloaded from Google Cloud, "
                "kept verbatim."
            ) from exc

    raise SystemExit(
        f"No credential found for the agent-platform backend.\n"
        f"Checked for an OAuth token at {token_path}\n"
        f"and a service-account key at {key_path}\n\n"
        "See docs/skill/ai-footage-fill/SKILL.md ('Credential setup') for how to "
        "get either one. The YouTube token.json cannot be used here - it carries "
        "YouTube scopes, not cloud-platform."
    )


def probe(config: dict) -> int:
    """Verify credentials reach the backend without generating anything."""
    print(f"backend        {config['backend']}")
    if config["backend"] == "agent-platform":
        print(f"  project      {config['project']}")
        print(f"  location     {config['location']}")
        token_path = _resolve(config["token_file"])
        key_path = _resolve(config["service_account_file"])
        if token_path.exists():
            print(f"  credential   OAuth token at {token_path}")
        elif key_path.exists():
            print(f"  credential   service-account key at {key_path}")
        else:
            print(f"  credential   NONE FOUND (checked {token_path} and {key_path})")
    else:
        key = config.get("api_key") or ""
        print(f"  api key      {'set (' + key[:6] + '...)' if key else 'MISSING'}")
        print("  note         image generation only; Veo needs agent-platform")
    print(f"  image model  {config['image_model']}")
    print(f"  video model  {config['video_model']}")
    print()

    client = build_client(config)
    try:
        models = list(client.models.list())
    except Exception as exc:
        print(f"FAILED to reach the API: {exc}\n", file=sys.stderr)
        if config["backend"] == "agent-platform":
            print(
                "Common causes, in the order worth checking:\n"
                "  - the Vertex AI / Agent Platform API is not enabled on this "
                "project\n"
                "  - the service account is missing the 'Vertex AI User' role\n"
                "  - the project has no billing account attached\n"
                "  - Veo / nano-banana access has not been granted for this "
                "project",
                file=sys.stderr,
            )
        else:
            print(
                "Common causes:\n"
                "  - the API key is wrong, or was revoked\n"
                "  - the key's project has not enabled the Generative Language API",
                file=sys.stderr,
            )
        return 1

    print(f"Authenticated. {len(models)} models visible to this project.")

    # Reachability is not the same as entitlement: Veo in particular is often
    # gated per-project, and finding that out now beats finding it out mid-build.
    names = " ".join(getattr(m, "name", "") or "" for m in models)
    for label, model_id in (
        ("image", config["image_model"]),
        ("video", config["video_model"]),
    ):
        stem = model_id.split("/")[-1]
        mark = "visible" if stem in names else "NOT LISTED"
        print(f"  {label:5} {stem:34} {mark}")
    print(
        "\n'NOT LISTED' is not always fatal - some models are callable without "
        "appearing\nin models.list() - but if generation later fails with a 404 "
        "or PERMISSION_DENIED,\nthis is the reason: request access for that model "
        "on this project."
    )
    return 0


def generate_first_frame(client, config: dict, prompt: str, aspect: str) -> bytes:
    """Paint the opening frame with nano-banana."""
    from google.genai import types

    image_prompt = (
        f"{prompt}\n\n"
        "Cinematic still photograph, single clear subject, uncluttered "
        "background, strong natural lighting, shallow depth of field, "
        "photorealistic. No text, no words, no numbers, no watermarks, no logos."
    )

    response = client.models.generate_content(
        model=config["image_model"],
        contents=image_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio=aspect),
        ),
    )

    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else []) or []:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                return inline.data

    # A refusal comes back as an empty-but-successful response, which is
    # confusing unless it is named as a refusal.
    raise SystemExit(
        "The image model returned no image. This is usually a safety refusal "
        "rather than an outage.\n" + PROMPT_GUARDRAILS
    )


def generate_video(
    client,
    config: dict,
    prompt: str,
    image_bytes: bytes,
    aspect: str,
    resolution: str,
    duration: int,
) -> bytes:
    """Animate the frame with Veo and wait for the long-running operation."""
    from google.genai import types

    motion_prompt = (
        f"{prompt}\n\n"
        "Slow, steady camera movement. Natural realistic motion. "
        "Continuous single shot, no cuts, no transitions, no text overlays."
    )

    operation = client.models.generate_videos(
        model=config["video_model"],
        prompt=motion_prompt,
        image=types.Image(image_bytes=image_bytes, mime_type="image/png"),
        config=types.GenerateVideosConfig(
            aspect_ratio=aspect,
            resolution=resolution,
            duration_seconds=duration,
            number_of_videos=1,
            # The pipeline overwrites the audio track with narration, so paying
            # Veo to synthesise audio would be spending money on something that
            # is discarded a step later.
            generate_audio=False,
            enhance_prompt=True,
        ),
    )

    print(f"Veo job submitted ({operation.name}). Polling...", flush=True)
    waited = 0
    while not operation.done:
        if waited >= POLL_TIMEOUT_SECONDS:
            raise SystemExit(
                f"Veo job still running after {POLL_TIMEOUT_SECONDS}s. It may yet "
                f"finish - resume it with operation name:\n  {operation.name}"
            )
        time.sleep(POLL_SECONDS)
        waited += POLL_SECONDS
        operation = client.operations.get(operation)
        print(f"  ...{waited}s", flush=True)

    if operation.error:
        raise SystemExit(f"Veo job failed: {operation.error}")

    response = operation.response
    videos = getattr(response, "generated_videos", None) or []
    if not videos:
        filtered = getattr(response, "rai_media_filtered_reasons", None)
        raise SystemExit(
            "Veo returned no video. "
            + (f"Filtered: {filtered}\n" if filtered else "")
            + PROMPT_GUARDRAILS
        )

    video = videos[0].video
    if video.video_bytes:
        return video.video_bytes
    if video.uri:
        # Vertex hands back a URI when the result is staged rather than inlined;
        # the SDK's download knows how to authenticate against it.
        return client.files.download(file=video)
    raise SystemExit("Veo returned a video object with neither bytes nor a URI.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--prompt", help="the scene to film, as a filmable description")
    parser.add_argument("--out", type=Path, help="where to write the .mp4")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    parser.add_argument("--aspect", default=DEFAULT_ASPECT)
    parser.add_argument(
        "--resolution",
        default=DEFAULT_RESOLUTION,
        help="1080p or 720p. If Veo rejects 1080p for this aspect ratio, retry at 720p; "
        "the pipeline upscales to 1080x1920 either way.",
    )
    parser.add_argument(
        "--backend",
        choices=["agent-platform", "api-key"],
        help="agent-platform (Google Cloud, can run Veo) or api-key (AI Studio, "
        "images only). Inferred from config.toml when omitted.",
    )
    parser.add_argument("--project", help="override config.toml [google_ai] project")
    parser.add_argument("--location", help="override config.toml [google_ai] location")
    parser.add_argument("--image-model")
    parser.add_argument("--video-model")
    parser.add_argument(
        "--probe",
        action="store_true",
        help="verify credentials and model visibility, generate nothing",
    )
    parser.add_argument(
        "--image-only",
        action="store_true",
        help="stop after the first frame, so composition can be judged before "
        "paying for video",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the plan and estimated cost without calling the API",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="required for any run that actually spends money",
    )
    args = parser.parse_args(argv)

    config = load_ai_config(
        {
            "backend": args.backend,
            "project": args.project,
            "location": args.location,
            "image_model": args.image_model,
            "video_model": args.video_model,
        }
    )

    if args.probe:
        return probe(config)

    if not args.prompt or not args.out:
        parser.error("--prompt and --out are required (or use --probe)")

    # Fail before the image is generated rather than after: on the api-key
    # backend the image would succeed and only the animate step would be
    # refused, which wastes a generation and reads like a bug.
    if config["backend"] == "api-key" and not args.image_only:
        parser.error(
            "The api-key backend cannot generate video - Veo is paid-tier only.\n"
            "Either add --image-only to iterate on the first frame for free, or "
            "switch to\nthe agent-platform backend (Google Cloud project with "
            "billing) for the full clip."
        )

    est = APPROX_IMAGE_USD + (
        0 if args.image_only else APPROX_VIDEO_USD_PER_SECOND * args.duration
    )
    print("Plan")
    print(f"  prompt      {args.prompt}")
    print(f"  out         {args.out}")
    print(f"  image model {config['image_model']}  ({args.aspect})")
    if not args.image_only:
        print(
            f"  video model {config['video_model']}  "
            f"({args.aspect}, {args.resolution}, {args.duration}s, silent)"
        )
    print(f"  est. cost   ~${est:.2f} (list-price estimate, not an invoice)")
    print()

    if args.dry_run:
        print("Dry run - nothing generated, nothing spent.")
        return 0

    if not args.confirm:
        # The gate is structural rather than an "are you sure?" prompt so that an
        # unattended run can never quietly spend money.
        print(
            "Refusing to generate without --confirm.\n"
            "Re-run with --confirm once the plan above looks right.",
            file=sys.stderr,
        )
        return 1

    client = build_client(config)
    out_path = args.out if args.out.is_absolute() else REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image_path = out_path.with_suffix(".png")

    print("Painting first frame...", flush=True)
    image_bytes = generate_first_frame(client, config, args.prompt, args.aspect)
    image_path.write_bytes(image_bytes)
    print(f"  wrote {image_path} ({len(image_bytes) / 1024:.0f} KB)")

    if args.image_only:
        print("\nImage only. Look at it, then re-run without --image-only to animate.")
        return 0

    print("Animating...", flush=True)
    video_bytes = generate_video(
        client,
        config,
        args.prompt,
        image_bytes,
        args.aspect,
        args.resolution,
        args.duration,
    )
    out_path.write_bytes(video_bytes)
    print(f"  wrote {out_path} ({len(video_bytes) / 1024 / 1024:.1f} MB)")

    # Provenance sits next to the clip because months later "is this shot real
    # footage or generated?" has to be answerable from the file alone.
    sidecar = out_path.with_suffix(".json")
    sidecar.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "prompt": args.prompt,
                "image_model": config["image_model"],
                "video_model": config["video_model"],
                "aspect": args.aspect,
                "resolution": args.resolution,
                "duration_seconds": args.duration,
                "audio": False,
                "first_frame": image_path.name,
                "ai_generated": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  wrote {sidecar}")
    print("\nLook at the clip before splicing it in - a plausible prompt can still")
    print("yield a bad take, exactly like a plausible Pexels term can.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
