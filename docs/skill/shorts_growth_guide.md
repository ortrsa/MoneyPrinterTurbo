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

> We currently generate **3 hashtags** plus a separate 5-item SEO tag string —
> under half the recommended count, and not tiered. Straightforward pipeline
> change in `generate_social_metadata`.

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

The guide and our own measurements agree on the diagnosis — retention in the
first seconds is everything — and disagree on almost nothing except **how long a
video should be**. That single number forces the biggest decision.

**Sub-20s is incompatible with the current episode design.** At 20 seconds you
get roughly 3 facts, not 6, which retires the `N/6` counter and the progress bar
in their present form. Against that: our own numbers are trending up *within* the
long format (36.4% → 40% → 51.6%), so the long format is not disproven — it is
merely still short of the 70% target after three attempts.

The honest read is that we have never tested short. Every retention figure we
own comes from 52–62s videos. The guide's central claim is that length itself is
the constraint, and we have no data contradicting it because we have never tried.

**Recommended: test it rather than assume.** Build the same topic twice — one
6-fact ~55s cut, one 3-fact ~18s cut — publish a day apart, compare
stayed-to-watch. That answers in 48 hours what argument cannot, and it is the one
experiment whose result changes everything downstream.

Caveat on measurement, carried over from the playbook: our recent videos land
387–867 views, which is enough for a stayed-to-watch percentage to mean
something, but a variant that gets seeded badly can still produce noise. Prefer a
clear gap (say 51% vs 70%) over a narrow one before concluding.
