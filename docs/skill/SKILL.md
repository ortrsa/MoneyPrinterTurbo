---
name: moneyprinterturbo-video
description: Use this skill whenever the user wants to create a finished video from a topic, title, idea, prompt, or script with MoneyPrinterTurbo. This includes short-form, voice-over, educational, marketing, social-media, and stock-footage videos. Also use it when the user mentions MoneyPrinterTurbo, provides this Skill URL, asks an AI agent to install or configure MoneyPrinterTurbo, needs missing API keys identified, wants a failed generation repaired, or wants a generated MP4 located and delivered. Use this skill when the expected outcome is a final video file, not setup instructions.
compatibility: Requires an AI agent with terminal, network, filesystem, and long-running command support. Supports macOS and Windows and uses uv exclusively.
metadata:
  author: "harry0703@hotmail.com"
  version: "2.0.0"
  upstream: "https://github.com/harry0703/MoneyPrinterTurbo"
---

# MoneyPrinterTurbo Video Generation

The user only needs to provide a video topic or script. Complete installation, configuration reuse, generation, waiting, and final MP4 delivery automatically. Do not stop after giving instructions or commands.

## Required Behavior

1. Ask the user only for required API credentials that are missing, rejected, or unusable. Combine all required credentials into one request.
2. Do not ask for confirmation before installing, generating, waiting, using defaults, or returning the result.
3. Do not create or repeatedly update a detailed plan for a standard generation request. Send one short progress update and execute.
4. Run the helper as one foreground command with a timeout of at least 20 minutes.
5. Never poll with `sleep`, `echo`, `ps`, repeated `ls`, or repeated `tail`. If the terminal returns a resumable session ID, continue waiting on that same session.
6. Do not read the full log after success. Read only the short reported error or the relevant log tail after failure.
7. Never print API keys, tokens, the full `config.toml`, or credential-bearing configuration fragments.

## Defaults

Unless the user requests otherwise, generate one Chinese `9:16` portrait video with Pexels footage, the default Chinese Edge TTS voice, subtitles, and background music. Install MoneyPrinterTurbo under the user's home directory.

## Shorts Virality Guidelines

There is no guaranteed-viral setting, but these defaults measurably improve retention on short-form platforms. Apply them unless the user's request already specifies its own script, hook, or tone.

1. **Hook-first script, no preamble.** Generate the script with a `video_script_prompt` that forces it to open with the single most surprising or counter-intuitive part of the topic in the first sentence — no greetings, no "did you know," no scene-setting:
   ```text
   Open with the most surprising or counter-intuitive part of this fact in the very first sentence - no greeting, no preamble, no 'did you know' filler. Use short, punchy sentences with no filler words. Write in English.
   ```
2. **Fixed English closing line, appended verbatim.** Whatever the closing line is, append it yourself rather than letting the LLM phrase it, so it survives every generation unchanged.

   **Default is now a next-episode cliffhanger, not a follow/comment CTA.** Meta's and TikTok's policies treat "follow for more", "like for part 2" and "comment X" as engagement bait, so the previous fixed CTA below is kept only as an opt-in:
   ```text
   The last one still breaks my brain - episode <N+1> goes even further.
   ```
   Legacy CTA, use only if the user explicitly asks for it (`--outro` on `viral_episode.py`):
   ```text
   Follow for more wild facts, and comment which one surprised you the most!
   ```
   Because letting the LLM write its own closing line risks it dropping or rewording it, generate the script in two steps instead of one:
   - Call `llm.generate_script(video_subject=topic, video_script_prompt=<hook prompt above>, ...)` (or run the CLI once with `--stop-at script` using `--video-script-prompt`) to get the AI-written body.
   - Append the fixed CTA sentence to that text yourself (`script.strip() + " " + CTA`).
   - Pass the combined text back in via `--video-script "<body + CTA>"` for the actual generation run — `--video-script` skips LLM script generation entirely and uses the text verbatim, guaranteeing the CTA survives untouched in both narration and subtitles.
3. **Tight pacing.** Prefer `paragraph_number=1` (the default) and a short script over a long one — a Short that ends before it overstays its welcome retains better than one padded with extra sentences.
4. **Always keep subtitles and background music on** (already the default) — both measurably help retention and accessibility.
5. **Generate a title, caption, and hashtags alongside the video.** `app/services/llm.py` already has `generate_social_metadata(video_subject, video_script, language="en", platform="youtube_shorts")` for this, but it is not wired into `cli.py`. Call it directly in a short Python snippet (pass it the same body+CTA script used for generation) and hand the title/caption/hashtags to the user together with the video file as one packaged deliverable — do not make the user ask for these separately.
6. **Cross-post.** Suggest posting the same file to TikTok and Instagram Reels in addition to YouTube Shorts — it is outside this skill's scope to automate, but worth a one-line mention since it meaningfully expands reach for zero extra generation cost.
7. **This is a feedback loop, not a one-shot setting.** Point the user at YouTube Studio's retention graph after their first few videos — where viewers drop off is the most reliable signal for what to change next (usually the hook or the pacing), more reliable than any fixed template.

## Viral Episode Pipeline (preferred path)

For this channel's facts episodes, prefer the one-shot pipeline over hand-assembling steps:

```bash
uv run python docs/skill/viral_episode.py --facts-file facts.txt --episode 2
```

It generates hook + per-fact scripts, renders a subtitle-free base video, derives word-level timings with faster-whisper, and burns an ASS overlay with karaoke captions, a fact counter and a progress bar. `--dry-run` prints the script and metadata without rendering. Add `--outro "<text>"` to override the default cliffhanger close.

Design notes that matter if you modify it:

- **Word timings come from whisper, not the TTS.** Gemini/OpenAI TTS return no timestamps, and Edge TTS's `WordBoundary` needs a WebSocket that is blocked in some sandboxes. `app/services/viral.py::transcribe_word_timings` re-derives timings from the rendered audio with `faster-whisper` (`base.en`, CPU, a few seconds for a 50s clip). Do not add a paid TTS purely to get timestamps.
- **Captions are ASS burned by ffmpeg, not MoviePy.** Per-word coloring inside one line is impossible with MoviePy's single-color `TextClip`; ASS `\1c` inline overrides handle it, and libass renders in one C pass instead of compositing hundreds of Python clips. Always pass `--no-subtitle-enabled` to the base render or you get two stacked subtitle layers.
- **`PlayResX/PlayResY` must equal the output resolution**, or libass rescales font size, outline and margins — the most common ASS burn bug.
- **Fact boundaries use sequence alignment, not word counts.** `align_facts_to_words` diffs the known script against the whisper tokens; a single insertion would shift every later boundary if we split by count. It always returns one segment per input so callers can slice off the hook and outro positionally.

## Episode Format (research-backed defaults)

Modeled on BrainBlud (~596K subscribers, ~188M views) plus retention research. Where evidence is thin, this says so — do not present these as proven numbers to the user.

1. **6 facts, target 45-55s.** The 50-60s bucket shows the highest average views (~4.1M) at ~76% completion, and completion rate still beats duration in the ranking signal. At 150-170 WPM that is ~125-140 words, which fits 6 facts plus hook and outro. Note honestly: **no A/B data exists on 5 vs 7 vs 10 facts** — 6 is derived from the length target, not measured.
2. **Hook in the first sentence, ≤12 words.** TikTok's own guidance: ~65% of viewers who watch 3 seconds watch 10+. Use Loewenstein's information-gap model — name a *specific* gap ("the third one still isn't explained"), never a vague tease, and make sure the payoff lands or the hook backfires.
3. **Close on a specific cliffhanger, not a generic CTA.** Meta's and TikTok's policies treat "follow for more" / "comment YES" as engagement bait. Point at the next episode instead. Keep the outro to one line — a long outro with no reason to stay is a documented drop-off cause.
4. **Captions: 3 words per screen, centered, Anton, active word in yellow.** Base white, `#FFE500` highlight, black outline ~9% of font size, font size ~6% of frame height. Highlight fires ~60ms before the word (reading outruns listening). Subtitling research puts the comfortable ceiling at 160-200 WPM — keep narration under it. The specific claim that karaoke captions beat static ones on retention is **unverified marketing copy**, but it is the universal convention across CapCut/Submagic/Opus Clip.
5. **Counter and progress bar are a bet, not a proven win.** No published A/B test exists for them in short video. The supporting evidence is the endowed-progress effect (34% vs 19% completion — in a loyalty-card field experiment, not video). None of the named facts channels visibly use them, so treat this as a differentiator to test, not table stakes.
6. **Generic "satisfying" B-roll, unrelated to the facts.** Pass `--video-terms` explicitly with categories like kinetic sand, slime, hydraulic press, soap cutting, paint pouring. Rotate terms between episodes so consecutive videos don't reuse footage.
7. **Numbered series title** (`Random But True Facts 2 👀`). Numbering aids channel-page binging and loyalty; it is **not** a discovery lever, since Shorts recommendation favors recent uploads. What converts a numbered series into subscribers is a consistent recognizable format, not the number.
8. **Frame 1 is the thumbnail.** Custom Shorts thumbnails do not appear in the swipe feed — only in search/grid/shelf placements. Judge the opening frame on retention-after-view, not click appeal.
9. **Cost model: keep it near zero.** Pexels footage, Gemini TTS, and local whisper are free or negligible; spend on Veo image-to-video clips only for hero shots. Cross-post the same file to TikTok and Reels — no extra generation cost.

### Fallback: MoviePy captions without the overlay

If the ASS overlay path is unavailable (no ffmpeg with libass, or whisper cannot run), fall back to the built-in caption path: set `subtitle_words_per_chunk = 3` in `config.toml`'s `[app]` section and pass `--subtitle-position center --font-size 110`. This gives large centered few-word captions but **no** per-word highlighting, counter or progress bar.

## Execution

### 1. Locate the helper

Resolve `SKILL_DIR` from this `SKILL.md` file. The helper is the adjacent `mpt_agent.py`. Set the terminal tool's working directory to `SKILL_DIR` and invoke the helper by its relative filename. Do not put the absolute helper path in the command, and do not run an extra `ls` or `dir` check.

This is required on Windows because some agent terminal validators remove backslashes from absolute paths embedded in commands. Using `mpt_agent.py` with `workdir=SKILL_DIR` avoids that failure and works on both macOS and Windows.

If the client loaded only the remote `SKILL.md`, download the helper from the official repository to a temporary directory, then use that temporary directory as the command working directory:

```text
https://raw.githubusercontent.com/harry0703/MoneyPrinterTurbo/main/docs/skill/mpt_agent.py
```

### 2. Run the helper

Do not run a separate `uv --version` preflight. Run the helper directly. If the shell explicitly reports that uv is missing, install uv and retry the same helper command once.

macOS uv installation:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell uv installation:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Use this foreground command with `workdir=SKILL_DIR` and a timeout of at least 20 minutes:

```bash
uv run --no-project --python 3.11 python mpt_agent.py --subject "<video topic>"
```

On Windows, do not try absolute backslash paths, absolute forward-slash paths, or copies in the workspace before this relative command. If a terminal tool reports `referenced_script_path_missing`, verify that its working directory is exactly `SKILL_DIR` and retry the relative command once. Do not cycle through path variants.

Do not use Docker, Conda, system pip, or a manually managed virtual environment.

## Exit Handling

### Exit code 0: deliver the result

Successful output has this form:

```text
MPT_RESULT
VIDEO_FILE=<absolute path>/final-1.mp4
TASK_DIR=<absolute path>/storage/tasks/<task_id>
LOG_FILE=<absolute path>/run-<task_id>.log
RESULT_FILE=<absolute path>/latest-result.json
```

`mpt_agent.py` emits `VIDEO_FILE` only after confirming that the file exists and is non-empty. Do not run another `ls`, `stat`, or file validation command.

If the terminal reports `exitCode=0` but truncates the output or returns a history-file reference without `MPT_RESULT`, do not infer failure and do not inspect old logs. Read this file once:

```text
~/MoneyPrinterTurbo/.agent-logs/moneyprinterturbo-video/latest-result.json
```

Treat `status=completed` as success. Return only the absolute video path and a concise description, for example:

```text
The video is ready.
Topic: ...
Video file: /absolute/path/to/final-1.mp4
Summary: Chinese portrait video with voice-over, subtitles, and background music.
```

### Exit code 10: request credentials once

`MPT_NEEDS_INPUT` includes only the required fields, recommended LLM providers and signup links, custom OpenAI-compatible requirements, and the Pexels signup link. Ask only for the listed values and do not request credentials already found in `config.toml`.

After the user responds, rerun the same foreground command with only the required environment variables:

```text
MPT_LLM_PROVIDER
MPT_LLM_API_KEY
MPT_LLM_BASE_URL
MPT_LLM_MODEL_NAME
MPT_PEXELS_API_KEY
```

### Exit code 1: repair or report

Use `MPT_ERROR` and `LOG_FILE` to repair a recoverable problem and retry once. Ask the user only if the repair requires a new API key. If the retry fails, report the failed stage, a short error, and the log path.

A terminal-tool path validation error is not a video-generation failure because the helper did not start. Correct the working directory and retry the relative command once. Never ask the user to copy `mpt_agent.py`, run commands manually, or confirm whether the agent should continue.

## Configuration and Background Fallback

The helper may read the complete local `config.toml` to reuse existing settings, but it must never print its contents. It reuses a working LLM provider automatically and validates configured Pexels keys through the authenticated My Collections endpoint before generation.

Use background mode only if the agent platform cannot wait for a foreground process. Wait for the platform's process-completion notification without polling, then read `latest-result.json` once.

## Scope

- Support macOS and Windows only.
- Use uv and the MoneyPrinterTurbo CLI only.
- Do not start Docker, WebUI, or API services.
- Do not run multiple video jobs concurrently.
- Pass additional video requirements after `--`. Run `cli.py --help` once only when an unfamiliar option must be verified.
