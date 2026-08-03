# Shorts growth guide (adopted strategy)

Provided by the channel owner 2026-07-29 and **adopted as the governing strategy**
for `@RBTfacts`. Ranked by the guide's own impact scores. Items 9 (AI editing
workflow) and 10 (fast branding) are deliberately excluded — the pipeline already
covers both.

Where a point conflicts with what this channel has actually measured, that is
called out inline. Adopting the guide does not mean pretending the conflicts
aren't there — it means changing course *and* knowing which parts are still
unproven for us.

Read alongside [`channel_playbook.md`](channel_playbook.md) (our measured
numbers) and [`SKILL.md`](SKILL.md) (how to build an episode).

---

## Rank 1 — The 2-second hook and view-to-swipe ratio · 10/10

*Source: Dan the Creator*

View-to-swipe is the metric the algorithm weights above all others. If viewers
swipe before watching, distribution stops immediately.

- **Target: ≥70% stayed-to-watch.** 80%+ is the multi-million-view band (a 12M
  short measured 86%).
- **Keep total length under 20 seconds** so viewers finish easily.
- **Land an intense visual or curiosity hook inside the first 2 seconds.**

> **⚠️ This is the single biggest change required, and it breaks our current
> format.** Our episodes run 52–62s with 6 facts. Our best measured retention is
> **51.6%** (Facts 5) — the trend across three animal episodes is 36.4% → 40% →
> 51.6%, genuinely improving but still ~20 points under the guide's floor. Six
> facts cannot fit in 20 seconds; roughly 3 can. Moving to sub-20s means
> abandoning the 6-fact structure, the `N/6` counter, and the progress bar as
> currently designed. See "What this means for our format" below.

## Rank 1b — The first-3-seconds construction formula · 9.5/10

*Source: owner-supplied tips, 2026-08-03. Formula: [Fast On-Screen Motion] +
[Bold Center Text] + [No-Pause Opening Line] = hard to swipe away.*

Same underlying metric as Rank 1 (view-vs-swipe in the first seconds), but
concrete construction rules instead of a target percentage. Checked each
claim against the actual code before writing anything down here — some of
this we already do, one piece is a real gap, one conflicts with an existing
rule and is **not** adopted silently.

**Already compliant, verified in `app/services/viral.py`:**
- **Dynamic word-highlight captions in yellow** — the guide's "words light
  up... yellow or green keeps the viewer's eyes locked in" is exactly
  `highlight_color: str = "#FFE500"` (a yellow), already the default.
- **Dead-center text placement, not bottom or right** — `caption_y_frac =
  0.5` and `\pos(video_width // 2, ...)` put captions dead center both axes.
  The guide's warned-against zones (bottom = YouTube's own captions/UI,
  right = Like/Share buttons) are already avoided by construction, not
  by luck.

**Real, unverified gap:** the guide's "Hook Text" (a distinct 3-5 word
summary card, separate from the flowing spoken captions) is **only built
for the story format** (`story_episode.py`'s 2-line title card, matches
Rank 5). `viral_episode.py` (facts format — the channel's main output) has
no equivalent; the hook's on-screen text is just the same word-by-word
karaoke captions used for every other line. Worth testing a short static
title card for facts episodes too, not yet built.

**Real, unverified claim — needs checking, not assumed either way:** no
silence-trimming step was found in `viral_episode.py`'s audio pipeline.
`segment_timings[0].start` always reads `0.0`, but that is a property of how
segments get assigned, not confirmation the TTS audio itself has zero
lead-in silence before the first word. Worth a direct check (load
`audio.mp3` from a recent task dir, look at the waveform/silence before the
first detected word) before either claiming compliance or building a trim
step.

**Not adopted — conflicts with an existing explicit rule, flagging instead
of silently overriding:** the guide's negativity-bias/imperative hook
templates ("Stop doing X if you want Y," "The biggest mistake people make
with X") are statements, not questions. The channel owner explicitly ruled
hooks must be phrased as a question (`HOOK_PROMPT` in `viral_episode.py`,
logged in this file and `channel_playbook.md` §5) after multiple "Did you
know" episodes shipped. These two rules are incompatible as written. If the
owner wants to test a negativity-bias angle, it would need to be phrased as
a question-form variant of the template (e.g. "Are you making the biggest
mistake with X?") rather than adopting the imperative form outright — this
is a topic/hook decision reserved for the owner per §7's division of labor,
not something to change unilaterally.

**Not adopted — real structural change, needs the owner's decision:** the
seamless-loop technique (last line grammatically continues into the first
line, so a re-watch reads as one continuous sentence and can push measured
retention past 100%) is a genuinely new, non-conflicting idea, but it
changes what the outro *is* — currently every outro is a FOLLOW/COMMENT/BOTH
CTA (see `channel_playbook.md` §5's outro rotation), and a loop-closing line
can't simultaneously be a CTA in the way we currently write one. Worth
testing on one episode as an explicit experiment, not a silent default
change to `OUTRO`/hook generation.

## Rank 2 — Account warm-up and human verification · 9.5/10

*Sources: Kellan Henneberry, Dan the Creator*

Brand-new accounts that immediately upload at volume get flagged as bots and land
in "0-view jail."

- **Warm up first:** 2–3 weeks (or ≥30 min/day for 2 consecutive days) using the
  account as a normal viewer — watching, liking, commenting in-niche.
- **Enable features:** YouTube Studio → Settings → Channel → Feature Eligibility;
  verify the phone number to unlock Intermediate Features.

> Warm-up is moot — the channel is live and past that stage. **Feature
> eligibility is still worth confirming**, and it costs two minutes. Worth noting
> our lowest-performing videos (9, 4, 3 views) came from days with multiple
> uploads on a young channel, which is consistent with this concern even if not
> proof of it.

## Rank 3 — Outlier topic selection and proven proof of concept · 9.0/10

*Source: Kellan Henneberry*

Don't invent topics from scratch. Use content with a demonstrated track record.

- Find recently created channels in high-growth niches.
- Look for **outliers** — videos with 5–10× that channel's baseline (e.g. 30M on
  a channel averaging 200k).
- Remake the winning *topic* with your own fresh clips.

> **We have been doing the opposite** — inventing every topic, then fact-checking
> and footage-probing it ourselves. That is why animal episodes cost 3–5 renders
> each. This is a real process change: research the topic's proven performance
> *before* writing facts.

## Rank 4 — Aggressive fluff trimming and the 4–6 clip sweet spot · 8.5/10

*Source: Kellan Henneberry*

- **4–6 clips maximum.** Under 4 feels lazy; over 6 causes fatigue and drop-off.
- Cut each clip to its **5–10 second peak moment** only.
- Add sound effects (Vine boom), light voiceover, text transition effects.

> Our episodes currently use **17–21 cuts** (2–3 per segment across 8 segments).
> That is 3–4× the stated ceiling. Note the guide's clip count is written for
> ranking/compilation formats where each clip *is* the content; for narrated
> facts a "clip" is B-roll under continuous voiceover, so the numbers aren't
> strictly comparable. But at sub-20s the counts converge anyway — a 20s video at
> ~3s/cut is 6 cuts, exactly in range. **We have no sound effects at all**; that
> is a genuine, cheap gap.

## Rank 5 — Clean high-contrast title formatting, no hashtags in title · 8.0/10

*Sources: Kellan Henneberry, Dan the Creator*

- **2-line on-screen title** over a pure black background.
- **Recolor the 2 most important keywords** in a vibrant pop colour (pink/red).
- **Never put `#hashtags` in the YouTube title field** — it burns curiosity
  real-estate. Put 3 subtle hashtags in the description instead.

> **We are actively violating the hashtag rule right now.** Live titles read
> `Random But True Facts 5 #facts`, `Random But True Facts 4 #facts`,
> `AI Unfiltered 3 #artificialintelligence #facts #scie…`. Editing a title is
> free and does **not** reset views or reach — this is the cheapest fix available.
> The 2-line black-background title card is a new video element we do not build;
> our current opening frame is B-roll with a karaoke caption over it.

## Rank 6 — Disciplined posting cadence and US-time distribution · 7.5/10

*Sources: Kellan Henneberry, Dan the Creator*

- **Post only during US waking hours, 06:00–22:00 US time**, spacing multiple
  daily uploads across morning / afternoon / evening.
- Ramp: **week 1** 1/day → **weeks 2–3** 2/day → **week 4+** 3/day.
- **5/day only after crossing 1,000,000 views in 48 hours.**

> Our calendar is built on **Israel local time**, which is UTC+3 — 7–10 hours
> ahead of US time zones. A 20:00 Israel slot is 13:00 ET / 10:00 PT, which lands
> inside the window; an 07:30 Israel slot is 00:30 ET, which is dead. **The
> calendar needs re-anchoring to US hours.** Current cadence (~2/day) matches the
> weeks 2–3 step, so the rate itself is fine.

## Rank 7 — The 3-tier SEO tag formula · 7.0/10

*Source: Dan the Creator*

**9–12 tags total**, split three ways:

1. **Post-specific (3–4)** — the exact content: `#wombatfacts`, `#sharkfacts`
2. **Niche-specific (3–4)** — the category: `#animals`, `#science`, `#nature`
3. **Broad viral (3–4)** — mass reach: `#viral`, `#shorts`, `#fyp`

> **Implemented 2026-08-02.** `generate_social_metadata(platform="youtube_shorts")`
> now returns 12 hashtags (was 3), and the prompt explicitly instructs the
> 3-tier split above. Verified live: a test call returned
> `#challengerdeep #deepoceanfacts #abyssalzone #deepseafacts` (post-specific),
> `#oceanography #marinebiology #sciencefacts #ocean` (niche), `#shorts #viral
> #trending #exploration` (broad) — 12 tags, all three tiers present. Both
> `viral_episode.py` and `story_episode.py` already call this function with no
> other changes needed, so every episode built from now on gets this
> automatically. `send_to_telegram.py` already forwarded the full hashtag list
> to both the caption and the separate YouTube "Tags" field, so nothing there
> needed to change either — see `SKILL.md` 8c.

## Rank 8 — The 48-hour delete-and-reupload fix · 6.5/10

*Source: Dan the Creator*

The Shorts algorithm sometimes fails to seed a video at all, leaving a good video
flat.

- If a quality short is **under 100 views after 48 hours** on an established
  channel: delete it.
- Tweak the title, hook, or thumbnail frame and **reupload on a different day**.
- Cited proof: a video stuck at 47 views became ~6M after delete-tweak-reupload.

> **We have four immediate candidates**: AI Unfiltered 2 (9 views), AI Unfiltered
> 3 (40), and two others at 4 and 3 views. All are well under 100 and well past
> 48 hours. Honest caveat: the guide frames this as an algorithmic *glitch* fix,
> but our AI-topic videos may simply be underperforming on topic — the playbook
> shows AI is the channel's weakest category. Reuploading a weak topic likely
> just fails again. Reupload the ones whose topic we believe in.

---

## What this means for our format

**Updated 2026-08-03 — this section was written before the test it called
for existed. It now does; the answer changed the conclusion.**

The guide and our own early measurements agreed on the diagnosis — retention
in the first seconds is everything — but the guide's central claim was that
*length itself* is the retention constraint, sub-20s vs. our 52-62s format.
That was untested when this section was first written (see the superseded
text in git history if needed). It has since actually been tested:

**Real result (real YouTube Analytics data, not estimated): long format
(6-fact, ~52-58s) beat short format (3-fact, ~25s) on both retention AND
raw views.** Long format averaged 45.8% stayed-to-watch / 724 views across 9
videos; short format (Facts 8 + Facts 9, the two episodes actually built at
~25s) averaged 41.4% / 275 views. Short format's sample is thin (n=2), so
this isn't the last word, but it's a real, clear-gap result — not a hunch —
and it points the opposite direction from the guide's central claim.

**Conclusion: keep the 6-fact/50s+ format as the default.** Do not re-run
the sub-20s experiment without a new, specific reason — the original
"maybe length is the whole problem" hypothesis this section existed to test
has been tested and did not hold up for this channel. The guide's other
points (first-3-seconds construction, hashtag tiers, posting cadence, etc.)
remain independently useful regardless of this one disagreement — see Rank
1b above for the parts of "the first seconds matter" that don't depend on
total video length.

Caveat on measurement, carried over from the playbook: our recent videos land
387–1400+ views, which is enough for a stayed-to-watch percentage to mean
something, but a variant that gets seeded badly can still produce noise. The
45.8% vs 41.4% gap here is real but not huge — keep growing the sample
(`docs/skill/youtube/fetch_channel_analytics.py`) rather than treating this
as fully settled after one comparison.
