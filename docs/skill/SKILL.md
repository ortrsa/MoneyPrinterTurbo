---
name: moneyprinterturbo-video
description: Use this skill whenever the user wants to create a finished video from a topic, title, idea, prompt, or script with MoneyPrinterTurbo. This includes short-form, voice-over, educational, marketing, social-media, and stock-footage videos. Also use it when the user mentions MoneyPrinterTurbo, provides this Skill URL, asks an AI agent to install or configure MoneyPrinterTurbo, needs missing API keys identified, wants a failed generation repaired, or wants a generated MP4 located and delivered. Use this skill when the expected outcome is a final video file, not setup instructions.
compatibility: Requires an AI agent with terminal, network, filesystem, and long-running command support. Supports macOS and Windows and uses uv exclusively.
metadata:
  author: "harry0703@hotmail.com"
  version: "1.4.0"
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

1. **Hook-first script, no preamble.** Pass a `--video-script-prompt` that forces the script to open with the single most surprising or counter-intuitive part of the topic in the first sentence — no greetings, no "did you know," no scene-setting. Example addition:
   ```text
   --video-script-prompt "Open with the most surprising or counter-intuitive part of this fact in the very first sentence - no greeting, no preamble, no 'did you know' filler. Use short, punchy sentences with no filler words. End on a line that loops back to the opening or invites the viewer to react/comment."
   ```
2. **Tight pacing.** Prefer `paragraph_number=1` (the default) and a short script over a long one — a Short that ends before it overstays its welcome retains better than one padded with extra sentences.
3. **Loop-able ending.** The closing line should call back to the opening or ask a question, since a viewer who rewatches the first second again counts as retained watch time.
4. **Always keep subtitles and background music on** (already the default) — both measurably help retention and accessibility.
5. **Generate a title, caption, and hashtags alongside the video.** `app/services/llm.py` already has `generate_social_metadata(video_subject, video_script, language, platform)` for this, but it is not wired into `cli.py`. Call it directly in a short Python snippet after the video finishes (read `script.json` from the task dir for `video_subject`/`script`, reuse the same configured LLM provider) and hand the title/caption/hashtags to the user together with the video file — do not make the user ask for these separately.
6. **Cross-post.** Suggest posting the same file to TikTok and Instagram Reels in addition to YouTube Shorts — it is outside this skill's scope to automate, but worth a one-line mention since it meaningfully expands reach for zero extra generation cost.
7. **This is a feedback loop, not a one-shot setting.** Point the user at YouTube Studio's retention graph after their first few videos — where viewers drop off is the most reliable signal for what to change next (usually the hook or the pacing), more reliable than any fixed template.

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
