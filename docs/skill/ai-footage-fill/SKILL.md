---
name: ai-footage-fill
description: Generate a single AI B-roll clip (nano-banana paints the first frame, Veo animates it, via Google Cloud Agent Platform - the 2026 name for Vertex AI) to fill ONE segment of a Random But True episode where the Pexels stock library genuinely has no usable footage - extinct animals, specific historical periods, physically impossible shots. Use this after probe_footage.py has been run and its frames looked at, when every candidate search term returns generic filler or footage that contradicts the narration. Also use when the user asks to "generate a clip with AI", mentions Veo, nano-banana, Agent Platform, Vertex video generation, or asks to fill a footage gap in an episode. This is a gap-filler for individual segments, NOT a footage source - the episode stays overwhelmingly Pexels.
compatibility: Requires google-genai and google-auth (already installed). Video needs a Google Cloud project with billing and a service-account key; image-only iteration also works with a free AI Studio API key. Cannot use the YouTube OAuth token.
---

# AI footage fill

A last-resort footage source for the one segment in an episode where stock video
genuinely does not have the thing being talked about.

## The rule this exists to serve

The channel's footage is Pexels. That is not a budget compromise, it is what
makes the videos look like videos rather than like AI slop, and the audience
notices the difference. So the bar for reaching for this skill is high, and the
question to ask is not "would a generated clip look nicer here?" but **"does the
stock library actually not have this?"**

Those are different questions. A merely mediocre Pexels clip is usually a
sign the search term is wrong, not that the library is empty — `channel_playbook.md`
§6 has a long history of terms that looked hopeless until they were rephrased
(`octopus` → `octopus underwater`, `blue jeans pocket` → `denim jeans texture`).
Re-probing costs thirty seconds. Generating costs real money and pulls the
episode a step away from the look that works.

**Generate only when all of these hold:**

1. `probe_footage.py` has been run on at least two or three genuinely different
   phrasings, and the frames have been *looked at* — not just counted. Pexels
   returns ~20 results for anything, including things it has no footage of.
2. Every candidate is either generic filler or actively contradicts the
   narration. Footage that contradicts the words is the real failure mode: a
   pink tongue under a line about blue-black tongues, an ambling dog under
   "fastest dog on Earth". That is worse than mediocre, it breaks trust.
3. The subject is one the library structurally cannot have: an extinct animal
   (moa, thylacine), a specific historical scene (a 1944 newspaper on a
   breakfast table), a physical impossibility, or a named object that only
   exists in one place.

**Do not generate** for a subject that merely has thin coverage. The documented
substitutions — a dolphin standing in for a sloth in a fact that names both, an
ostrich for a moa, golden retrievers for Newfoundlands in a water-rescue shot —
are legitimate and cheaper, and the playbook already accepts them.

## Budget gate

**One AI clip per episode is the working default. Two is the ceiling before
asking.** If an episode seems to need three or more, that is not a footage
problem, it is a topic problem: the episode is about something the visual
vocabulary of this channel cannot show, and the right move is to say so and
propose a different topic rather than to generate your way through it. Ask the
owner before generating a third clip in one episode.

Each clip is roughly a few dollars. Cheap once, not cheap daily.

## Credential setup

**The YouTube `token.json` cannot be used here.** It is a user OAuth token
carrying YouTube scopes; these APIs need entirely different credentials. There
is no way to pass one as the other.

### Naming, so the console does not look wrong

At Cloud Next 2026 Google renamed **Vertex AI** to the **Gemini Enterprise Agent
Platform**, and the console moved to
<https://console.cloud.google.com/agent-platform>. Searching the console for
"Vertex AI" now redirects there. The rename was branding only — the APIs, the
SDKs, the billing and the IAM roles were carried over unchanged, which is why
the code still passes `vertexai=True` and why the IAM role is still called
**Vertex AI User**. Those are not stale references; they are what the platform
still calls itself underneath.

### Two backends, and which one you need

| | `agent-platform` | `api-key` |
|---|---|---|
| where | Google Cloud, billing enabled | <https://aistudio.google.com/apikey> |
| first frame (nano-banana) | yes | yes, free tier |
| video (Veo) | **yes** | **no — paid tier only** |

**Veo cannot be driven from a free API key.** Google's free Veo access is
through the web UIs (Flow, the Gemini app) — watermarked, and not scriptable, so
it cannot feed this pipeline. If the goal is a finished clip, the
`agent-platform` backend with billing is the only route.

Worth knowing: a **new Google Cloud account's $300 free trial credit does apply**
to Agent Platform usage, Veo included. If that credit is unused, it covers a lot
of 8-second clips at these prices.

The `api-key` backend still earns its place: the prompt → first-frame loop is
where most of the iteration happens, and doing that for free before paying to
animate is the cheaper order of operations.

### Setup for `agent-platform` (needed for video)

Steps 1-3 are the same regardless of which credential form is used below:

1. Create or pick a project at <https://console.cloud.google.com/agent-platform>
   and attach a **billing account**. Note the **project ID**, not the display
   name.
2. Enable the **Vertex AI API** (may be listed as Agent Platform) for it.
3. Confirm model access. Veo is gated per-project on some accounts; if it is not
   granted this surfaces later as `PERMISSION_DENIED` or `404` on the model
   name, not as an auth error.

Then pick **one** of two credential forms — the script checks for an OAuth
token first, falling back to a service-account key, so either is sufficient and
having both is not necessary:

**A. OAuth token** (mirrors the `docs/skill/youtube/authorize_local.py` flow
already used for YouTube — familiar if that one is set up):

4. In the same project, go to APIs & Services → Credentials → Create
   Credentials → OAuth client ID → Application type **Desktop app**, and
   download the JSON.
5. On your own machine (not the remote session — it has no browser to complete
   Google's consent screen): `pip install google-auth-oauthlib`, put the
   downloaded file next to `docs/skill/veo/authorize_local.py` as
   `client_secret.json`, and run `python authorize_local.py`. It opens a
   browser, you click Allow, and it writes `token.json`.
6. Send that `token.json` back to be placed at `docs/skill/veo/token.json`
   (gitignored — it is a billable credential and must never be committed).
   The Google account used in step 5 needs the **Vertex AI User** role (or
   Owner/Editor) on the project.

**B. Service-account key** (no browser needed, but a second identity to manage):

4. Create a **service account**, grant it the **Vertex AI User** role, download
   a **JSON key**.
5. Put the key at `docs/skill/veo/service_account.json` (gitignored, same
   reason as above).

Either way, add to `config.toml`:

```toml
[google_ai]
backend = "agent-platform"
project = "your-project-id"
location = "us-central1"
```

### Setup for `api-key` (free, images only)

```toml
[google_ai]
backend = "api-key"
api_key = "..."
```

### Verify — spends nothing

```bash
uv run python docs/skill/ai-footage-fill/scripts/generate_ai_clip.py --probe
```

It reports whether auth works and whether each model is visible. Fix whatever it
flags before building an episode around it.

Model IDs live in `[google_ai]` (`image_model`, `video_model`) precisely because
Google renames and retires them; a rename should be a config edit, not a code
change. The older `[vertex]` section is still read as a fallback.

## Workflow

The AI clip is spliced into an otherwise normal build. Nothing about the
existing flow changes — the episode is still scripted, fact-checked, probed and
rendered exactly as always, and this fills one hole in it.

### 1. Write the prompt as a filmable scene

The prompt describes a **shot**, not a fact. Name the subject, the framing, the
lighting and the motion. This matters for the same reason Pexels search terms
must name a filmable scene: "animal digestion" returns blue circuit boards, and
an abstract video prompt produces an equally abstract result.

Veo reliably refuses or mangles: real named people, brand logos, on-screen text
or numbers (it renders text as garbled glyphs, and it would collide with the
burned-in captions anyway), graphic injury, and anything framed as documentary
footage of a real event.

**Weak:** `the extinction of the moa`
**Strong:** `a huge flightless bird, taller than a man, with shaggy brown
feathers and no wings at all, standing still in dense misty New Zealand forest
at dawn, low camera angle looking up, soft light through tree ferns`

### 2. Generate the first frame alone, and look at it

```bash
uv run python docs/skill/ai-footage-fill/scripts/generate_ai_clip.py \
  --prompt "<the shot>" --out storage/ai_clips/<name>.mp4 \
  --image-only --confirm
```

Read the PNG it writes. This step exists because the opening frame is what the
viewer judges in the instant the segment starts, and re-rolling an image is far
cheaper than re-rolling a video. If the composition is wrong — subject too
small, cluttered background, wrong species — fix the prompt and repeat here.
Do not animate a frame you would not have accepted as a Pexels result.

This stage runs on the free `api-key` backend, so the iteration that actually
takes several attempts is the one that costs nothing. Add `--backend api-key` if
config.toml defaults to `agent-platform`.

### 3. Animate it

```bash
uv run python docs/skill/ai-footage-fill/scripts/generate_ai_clip.py \
  --prompt "<the shot>" --out storage/ai_clips/<name>.mp4 --confirm
```

8 seconds, 9:16, silent, starting on the approved frame. `--dry-run` first
prints the plan and an estimated cost without calling the API; `--confirm` is
required for anything that spends money.

The clip is generated silent on purpose: the pipeline replaces the audio track
with the narration, so generated audio would be paid for and discarded.

### 4. Verify the clip like any other footage

Watch it. Sample frames across its length, not just the first — the same rule
that applies to stock footage applies here, and a good first frame does not
guarantee a good take. Veo drifts: subjects morph, extra limbs appear, motion
stutters at the end. A bad take is a re-roll, not something to ship.

### 5. Splice it into the render

Pass `--segment-clips` alongside the usual `--segment-terms`. The keyed segment
skips Pexels entirely and plays this clip as one continuous shot; every other
segment is untouched.

```bash
uv run python docs/skill/viral_episode.py \
  --facts-file facts.txt --episode 22 \
  --segment-terms '{"0": "...", "1": "...", ...}' \
  --segment-clips '{"3": "storage/ai_clips/moa.mp4"}' \
  --threads 4
```

Segment indices are the same ones `--segment-terms` uses: 0 is the hook, 1..N
are the facts (or story beats), the last is the outro. Both `viral_episode.py`
and `story_episode.py` accept it. Bad indices and missing files are rejected
before the render starts.

Overridden segments play as a **single continuous shot** rather than being cut
into ~3s pieces. Stock clips get cut up because a stock clip is only loosely
related to the sentence and cutting raises density; a shot generated for this
exact sentence is already on-topic, and chopping it would just produce jump cuts
within one continuous take.

### 6. Verify the finished render, then log it

Check the spliced segment in the final MP4 — especially that it does not look
tonally alien next to the Pexels shots around it. A generated clip that reads as
obviously synthetic next to real footage is worse than a substituted-subject
stock clip, because it makes the whole episode look generated.

Record in `episode_log.csv`'s `outcome_note`: which segment was AI-generated,
the prompt, and **why stock footage could not cover it** — that last part is what
makes the decision reviewable later, and what will show whether these clips help
or hurt retention. The render's `*-result.json` also carries
`ai_generated_segments` for the same reason.

## Disclosure

`upload_video.py` already sets `containsSyntheticMedia = true` on every upload
because the narration is AI TTS, so an AI-generated shot needs no additional
flag. Worth knowing that the disclosure is already correct rather than assuming
it needs changing.

## When it does not work

- **`PERMISSION_DENIED` / `404` on the model name** — the project does not have
  access to that model. Auth is fine; entitlement is not. Request access, or set
  a different `video_model` in `config.toml`.
- **Video refused on a free API key** — expected, not a bug: Veo is paid-tier
  only. The script blocks this before generating the image so the refusal does
  not arrive halfway through and look like a failure.
- **Empty response, no error** — almost always a safety refusal, not an outage.
  Reread the prompt against the refusal list above.
- **1080p rejected for 9:16** — retry with `--resolution 720p`. The pipeline
  scales to 1080x1920 anyway.
- **Job still running after 15 minutes** — the script prints the operation name
  and stops waiting. The job may still finish; Veo latency is variable.
