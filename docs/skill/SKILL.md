---
name: moneyprinterturbo-video
description: Use this skill whenever the user wants to create a finished video from a topic, title, idea, prompt, or script with MoneyPrinterTurbo. This includes short-form, voice-over, educational, marketing, social-media, and stock-footage videos. Also use it when the user mentions MoneyPrinterTurbo, provides this Skill URL, asks an AI agent to install or configure MoneyPrinterTurbo, needs missing API keys identified, wants a failed generation repaired, or wants a generated MP4 located and delivered. Use this skill when the expected outcome is a final video file, not setup instructions.
compatibility: Requires an AI agent with terminal, network, filesystem, and long-running command support. Supports macOS and Windows and uses uv exclusively.
metadata:
  author: "harry0703@hotmail.com"
  version: "3.0.0"
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

> **Working on the `@RBTfacts` "Random But True" channel? Read these two first.**
> - [`shorts_growth_guide.md`](shorts_growth_guide.md) — the **adopted strategy**,
>   ranked by impact. It governs length, hooks, titles, tags, cadence and topic
>   selection. Where it conflicts with our own measurements, both are stated.
> - [`channel_playbook.md`](channel_playbook.md) — the **measured analytics** for
>   this channel, which topics have and have not worked, and the production traps
>   already paid for.
>
> This file says how to build a video; the guide says what to aim for; the
> playbook says what actually happened. Update the playbook when new numbers
> arrive. Note the guide targets **≤20s and ≥70% stayed-to-watch**, which the
> current 6-fact/50-60s format does not meet — do not build a long episode on
> autopilot without checking that decision first.
>
> **Two flows exist. Pick the right one before writing anything:**
> - **List format** — `viral_episode.py`. N unrelated facts on one theme, `N/6`
>   counter, ~55s. Everything below describes this flow.
> - **Story format** — `story_episode.py`. One true story told as escalating
>   beats, 30–90s, no counter, with a burned-in 2-line title banner. Built for
>   narrative leads (a historical event, a true-crime case). See
>   [`channel_playbook.md`](channel_playbook.md) §7a for its rules, its two
>   known traps (`refine_hook` must not be used; scripts must be locked with
>   `--from-dry-run` before rendering or the fact-check is void), and the
>   copyright workflow when the lead comes from someone else's post.

0. **Research a proven topic before writing facts — do not invent from scratch.** Per the growth guide's Rank 3 (9.0/10), the highest-leverage step happens before a single fact is drafted: find a topic with a demonstrated track record in the niche and remake *that topic*, not a topic invented cold.
   - Search recently-active channels in the niche (e.g. "animal facts shorts channel viral") for ones with a visibly strong ratio of views to subscriber count or video count — that ratio is the signal a channel found something that works, not the channel's absolute size.
   - Within a promising channel, look for an **outlier**: a video running 5-10x that channel's typical view count. Its *topic* (dog temperament rankings, animal-strength comparisons, a specific species' odd behavior) is the proven element — never copy its script, footage, or wording, only the subject.
   - **Known tooling gap: this pipeline has no YouTube Data API access, so exact per-video view counts are not queryable from here.** `WebSearch`/`WebFetch` only surface channel-level aggregates and secondhand summaries (blog posts, vidIQ pages), not a sortable-by-views Shorts tab. Treat anything found this way as a *topic-category* signal ("ferocious dog breeds," "animal strength records" are reported as strong performers), not a verified outlier claim — record it as such rather than presenting it as measured. If precise per-video numbers matter for a decision, that requires the user to open the channel's Shorts tab sorted by "Popular" in a browser, or a YouTube Data API key wired into the pipeline; flag that gap explicitly rather than quietly substituting a weaker signal for it.
   - Cross-check any candidate topic/species against the "Species used so far" table in `channel_playbook.md` before committing, so a proven topic is a deliberate repeat or a genuine gap, not an accidental collision.
1. **Hook-first script, no preamble.** Generate the script with a `video_script_prompt` that forces it to open with the single most surprising or counter-intuitive part of the topic in the first sentence — no greetings, no "did you know," no scene-setting:
   ```text
   Open with the most surprising or counter-intuitive part of this fact in the very first sentence - no greeting, no preamble, no 'did you know' filler. Use short, punchy sentences with no filler words. Write in English.
   ```
   `docs/skill/viral_episode.py`'s `HOOK_PROMPT` goes further and offers the LLM one of three concrete hook shapes to pick from — a prediction-plus-stakes claim, a before/after compression, or a specific curiosity gap with a real payoff — rather than a vague "make it surprising" instruction. Naming the exact structure produces a noticeably punchier line than asking generically.
2. **Block known AI-writing tells at the prompt, and check for them after.** LLM output tends toward a recognizable register — "here's the thing," "game-changer," "unlock," "delve," "in conclusion," and similar, plus paragraph-opening "However/Moreover/Overall" and uniform sentence length. `viral_episode.py`'s `AI_TELL_BLOCKLIST` and `HUMANIZATION_NOTE` are passed as explicit negative constraints inside `FACT_PROMPT` and `HOOK_PROMPT`, and `find_ai_tells()` re-checks the output afterward and logs a warning if one slips through anyway. Prevent at the prompt first; treat the check as a smoke detector, not an automatic rewriter — silently rewriting risks changing the meaning of a fact.
3. **Run the LLM-generated hook through one combined critique pass before accepting it.** `refine_hook()` sends the hook back to the LLM with five review angles folded into a single prompt — does this earn attention, is it factually solid, would a fast scroller actually stop, is it different from every other facts video, does every word pull weight — and gets back either the same hook unchanged or an improved one. This only runs on freely-generated hooks; a hook supplied via `--hook` (e.g. from the content calendar) is treated as already vetted and is used verbatim. Five separate LLM calls per episode would not be worth the latency for a 12-word sentence, so all five angles go in one request rather than five round-trips.
4. **Score a standalone video's title before publishing, but never score a series title.** This channel's series episodes use a fixed `"{series} {episode} 👀"` title by design (numbered titles aid channel-page loyalty over discovery — see Episode Format below), and that fixed title must never be scored or second-guessed by a heuristic built for one-off clickbait titles. For an actual one-off video (`--standalone`, no `--title`), `score_title()` grades the LLM's title on three 0-3 heuristics — does it contain a number, does it carry a high-arousal word, does it hold back the answer — and logs a warning below a 7/9 threshold. This is a heuristic signal to reconsider a weak title, not a hard gate: it does not stop generation.
5. **A written-per-episode closing CTA, appended verbatim.** Append the closing line yourself rather than letting the LLM phrase it, so it survives every generation unchanged.

   **Asking for a follow or a comment is explicitly allowed.** An earlier version of this file claimed platforms treat any follow/comment ask as engagement bait — that was wrong. YouTube permits asking viewers to like, comment or subscribe. What gets demoted is *templated, content-free* prompts ("subscribe if you agree", "comment YES"); classifiers score the caption, on-screen text and early comments together and shrink the test audience the more manufactured it reads. So ask directly, but tie the ask to this specific video.

   **Never reuse one CTA across episodes.** A fixed closing line makes a serialised channel feel automated and wastes the strongest conversion moment. Write a fresh one per episode that:
   - references something concrete from that video (a callback to fact 1 or the hook lands best),
   - rotates deliberately between **FOLLOW**, **COMMENT** and **BOTH**, chosen by what the content invites — a testable claim ("check which nostril you're breathing through") earns a comment ask; a topic with obvious series potential earns a follow ask,
   - can be playful or cheeky. Self-aware jokes about the feed work well in this genre, e.g. *"You're blind forty minutes a day. Don't spend the rest of it not following this page."*

   The month-1 calendar carries a per-episode `outro_line_spoken` and a `cta_type` column for exactly this; pass them through `--outro`. Keep `cta_type` populated so CTA style can be compared against subscriber conversion later.

   Because letting the LLM write its own closing line risks it dropping or rewording it, generate the script in two steps instead of one:
   - Call `llm.generate_script(video_subject=topic, video_script_prompt=<hook prompt above>, ...)` (or run the CLI once with `--stop-at script` using `--video-script-prompt`) to get the AI-written body.
   - Append the fixed CTA sentence to that text yourself (`script.strip() + " " + CTA`).
   - Pass the combined text back in via `--video-script "<body + CTA>"` for the actual generation run — `--video-script` skips LLM script generation entirely and uses the text verbatim, guaranteeing the CTA survives untouched in both narration and subtitles.
6. **Tight pacing.** Prefer `paragraph_number=1` (the default) and a short script over a long one — a Short that ends before it overstays its welcome retains better than one padded with extra sentences.
7. **Always keep subtitles and background music on** (already the default) — both measurably help retention and accessibility.
8. **Generate a title, caption, and hashtags alongside the video.** `app/services/llm.py` already has `generate_social_metadata(video_subject, video_script, language="en", platform="youtube_shorts")` for this, but it is not wired into `cli.py`. Call it directly in a short Python snippet (pass it the same body+CTA script used for generation) and hand the title/caption/hashtags to the user together with the video file as one packaged deliverable — do not make the user ask for these separately.

8a. **Both `viral_episode.py` and `story_episode.py` deliver the upload kit to Telegram automatically** once a real (non-`--dry-run`) render finishes, via `docs/skill/send_to_telegram.py`. Requires `[telegram]` `bot_token`/`chat_id` in `config.toml` (gitignored — create a bot via @BotFather, message it once, read the chat_id from `https://api.telegram.org/bot<token>/getUpdates`). Sends five separate messages: the video, then title/caption+hashtags/tags(plain, no `#`)/pinned-comment each as a "label:" message followed by a "content" message, so a phone user can long-press-copy just the content. Pass `--pinned-comment "..."` when you have one — the pipeline does not generate this field itself. `--no-telegram` skips delivery (e.g. for test renders); delivery failures are logged as warnings and never fail an otherwise-successful render.

8b. **Inbound side: `docs/skill/check_telegram_inbox.py` polls for new topic/story messages sent to the same bot,** idempotently (state in `storage/telegram_state.json`, gitignored). **This is manual-only by design — not on a schedule.** Run it only when the channel owner explicitly asks for a check. When it returns non-empty, treat every message as a full episode to build end-to-end (fact-check independently even if the message carries its own sources, pick list vs. story format by content, verify footage and output as usual) — see `channel_playbook.md` §9 for the full handoff, including why the scheduled version was attempted and shelved.
9. **Cross-post.** Suggest posting the same file to TikTok and Instagram Reels in addition to YouTube Shorts — it is outside this skill's scope to automate, but worth a one-line mention since it meaningfully expands reach for zero extra generation cost.

10. **Views do not equal subscribers — hand over the conversion steps too.** A healthy Shorts view-to-subscriber rate is roughly **0.5-2%**, so a video needs volume before subscriber counts move; do not let the user read a low number as failure. What actually converts, in rough order of impact at under 1,000 subscribers:
   - **A series format** — structured multi-episode series report meaningfully higher subscriber conversion than one-off videos. This is already the channel's format; say so, because it is the main lever.
   - **A pinned comment posted immediately after publishing**, giving a concrete reason to subscribe (what the next episode covers, when it lands). Deliver suggested pinned-comment text with the upload kit.
   - **Replying to every comment early on.** At this scale personal replies convert unusually well, and early engagement also feeds the algorithm.
   - **A playlist per series** on the channel page, so a viewer who clicks through immediately sees there is more.
   - **A consistent schedule** — consistency is associated with materially faster subscriber growth than sporadic posting.
11. **This is a feedback loop, not a one-shot setting.** Point the user at YouTube Studio's retention graph after their first few videos — where viewers drop off is the most reliable signal for what to change next (usually the hook or the pacing), more reliable than any fixed template.

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
3. **Close on a direct but content-specific CTA** (see Shorts Virality Guidelines item 5 for the full rule). Asking for a follow or comment is allowed and is the strongest conversion moment in the video — what fails is a generic, reused line. Write a new one per episode, tie it to that episode's content, and rotate FOLLOW / COMMENT / BOTH. Keep it to one line: a long outro with no reason to stay is a documented drop-off cause.
4. **Captions: 3 words per screen, centered, Anton, active word in yellow.** Base white, `#FFE500` highlight, black outline ~9% of font size, font size ~6% of frame height. Highlight fires ~60ms before the word (reading outruns listening). Subtitling research puts the comfortable ceiling at 160-200 WPM — keep narration under it. The specific claim that karaoke captions beat static ones on retention is **unverified marketing copy**, but it is the universal convention across CapCut/Submagic/Opus Clip.
5. **Counter and progress bar are a bet, not a proven win.** No published A/B test exists for them in short video. The supporting evidence is the endowed-progress effect (34% vs 19% completion — in a loyalty-card field experiment, not video). None of the named facts channels visibly use them, so treat this as a differentiator to test, not table stakes.
6. **Footage matches the fact being spoken (`--footage-mode synced`, the default).** Each spoken segment gets its own LLM-generated Pexels search terms, and its clips are laid into that segment's exact whisper-derived time window — so when fact 3 is about voice cloning, the screen shows a microphone, not leftover footage from fact 1. Terms are de-duplicated across the episode (both the search phrases and the resulting clip URLs), because near-identical facts otherwise all resolve to the same "person typing on laptop" shot. Search terms must name a *filmable scene* — concrete objects, people doing things, real places. Abstract prompts ("technology concept", "innovation") return generic blue circuit-board filler, which is why the prompt bans them. `--footage-mode generic` restores the old behavior: one global `--video-terms` pool of satisfying B-roll (kinetic sand, slime, hydraulic press) with no relationship to the narration. Prefer `synced`; generic is a fallback for topics too abstract to film.
7. **Numbered series title** (`Random But True Facts 2 👀`). Numbering aids channel-page binging and loyalty; it is **not** a discovery lever, since Shorts recommendation favors recent uploads. What converts a numbered series into subscribers is a consistent recognizable format, not the number.
8. **Frame 1 is the thumbnail.** Custom Shorts thumbnails do not appear in the swipe feed — only in search/grid/shelf placements. Judge the opening frame on retention-after-view, not click appeal. The general thumbnail-legibility rules (≤3 visual elements, high contrast, readable at a glance, bold sans-serif text ≤4 words) still apply to that first frame — our karaoke caption design (3 words, Anton, black outline on white/yellow) already satisfies these by construction. One rule genuinely does not transfer: "a face with a shocked expression" boosts click-through in face-forward content, but this channel is deliberately faceless B-roll, so there is no face to add — don't force one in.
9. **Trend-jacking is deliberately out of scope for now.** Tying facts to breaking news/trending topics is a plausible future format (discussed and shelved per the user), not something to build speculatively into this pipeline.
10. **Cost model: keep it near zero.** Pexels footage, Gemini TTS, and local whisper are free or negligible; spend on Veo image-to-video clips only for hero shots. Cross-post the same file to TikTok and Reels — no extra generation cost.

### Probe the stock library before rendering, not after

**Always do this before an episode whose facts name specific animals, objects, places or historical periods.** A render takes about six minutes; a probe takes thirty seconds. Skipping it once cost five consecutive rejected renders of a single animals episode.

For each fact whose subject might be rare, search Pexels directly, download the top result, extract one frame, and look at it:

```python
from app.services import material
from app.models.schema import VideoAspect
r = material.search_videos_pexels("wombat", minimum_duration=1, video_aspect=VideoAspect.portrait)
material.save_video(video_url=r[0].url, save_dir="/tmp/probe")
```

Then `ffmpeg -ss 1 -i clip.mp4 -frames:v 1 out.jpg` (the binary lives under `.venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/`) and read the image. Pass every verified term to `--segment-terms` so the LLM cannot overwrite it.

**Result counts prove nothing.** Pexels returns roughly 20 results for any query, including ones it has no real footage for — `wombat`, `sloth` and `animal digestion` all returned about 20. Only looking at frames distinguishes a real match from fuzzy filler. For the same reason, zero "black filler" warnings in the log is not evidence the footage is right.

Three failure modes worth probing for specifically:

- **A common word with a dominant other meaning.** `octopus` returns octopus *carpaccio* as often as the animal — a plate of food under a fact about octopus intelligence. Qualify it: `octopus underwater`.
- **A species the library simply lacks.** No wording finds tree sloths; `sloth` returns sloth *bears* in a zoo. Either pick a different fact, use an adjacent subject the script already names (a fact comparing sloths to dolphins can legitimately show a dolphin), or generate the shot with Veo.
- **A year or date in the query.** Stock is tagged by what is in the shot, never by when an event happened. Describe the period's look instead.

When verifying the finished render, sample **every cut**, not one frame per segment. A segment of three cuts judged on its midpoint hides two thirds of what shipped — that mistake made a correct octopus segment look like a failure.

### Shot pacing: what transfers from the 6-step transformation formula

The widely-circulated 6-step viral formula (Declare → Assessment → Isolate → Process → Build → Reveal) was written for **transformation/restoration** videos, where one object visibly changes over 60 seconds. A facts compilation has no single object and no transformation, so most of it cannot be applied literally. The parts that genuinely transfer:

- **Declare (0-3s) → the opening shot must be readable instantly.** This is the one step that transfers unchanged. The hook segment's search terms carry an extra constraint requiring a clean scene, single clear subject, strong lighting, uncluttered background — if the viewer spends half a second parsing the composition, the hook's words are already gone.
- **Isolate → keep cuts short.** The formula's 1-1.5s rapid cuts are too fast here: each fact runs 6-11 seconds and the viewer needs long enough to connect picture to claim. `plan_cuts()` targets ~3s and splits each fact's window into equal cuts (typically 2-4), which keeps visual density high without making the footage unreadable. Equal splitting also structurally prevents the sub-second tail sliver that `plan_clip_duration()` fixes on the generic path.
- **Reveal → close the loop.** The outro segment gets its own terms rather than trailing off on whatever clip was last, so the final seconds are deliberate.

What does **not** transfer: Assessment (macro shots of calipers and measurement tools), Process (time-lapse of a chemical/mechanical change), and Build (reassembly with satisfying clicks) all presuppose a physical object being worked on. Do not fabricate a fake "measurement" or "before/after" beat for a facts video — there is nothing being transformed, and the mismatch reads as filler. The before/after retention trick at the end (viewers rewinding to re-check the change, pushing watch time past 100%) likewise has no equivalent here.

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
