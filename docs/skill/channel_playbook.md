# Random But True — channel playbook

Accumulated findings for the `@RBTfacts` YouTube Shorts channel. `SKILL.md` covers
how to *build* a video; this file covers what has actually been learned about
making this specific channel work, so a fresh session does not restart from zero.

**Read this before proposing changes to format, topic mix, or episode length.**

> **Strategy note (2026-07-29):** [`shorts_growth_guide.md`](shorts_growth_guide.md)
> is now the adopted strategy and takes precedence on targets. It sets **≤20s
> length** and **≥70% stayed-to-watch**; our best measured figure is 51.6% at
> ~52s. The §5 strategy decisions below still hold on topic mix, but the length
> hypothesis in §5 is now a governing requirement rather than an idea to try
> eventually.

Measurements are dated. Anything not marked as measured is reasoning, and is
labelled as such — several conclusions below rest on very few data points, and
saying so is more useful than sounding confident.

---

## 1. Channel

- Handle `@RBTfacts`, name "Random But True". Faceless narrated facts, 9:16.
- Stated goal: **1000 subscribers** to reach monetisation.
- Format: 6 facts per episode, hook + facts + outro, karaoke captions, fact
  counter and progress bar. Built by `docs/skill/viral_episode.py`.

## 2. Measured performance — 2026-07-28 (28-day window)

Channel totals:

| metric | value |
|---|---|
| views | 2.4K |
| engaged views | 854 |
| likes | 60 |
| **subscribers** | **0** |
| stayed to watch | **33.1%** |
| swiped away | 66.9% |

Per video:

| video | views | note |
|---|---|---|
| 25 Jul (flamingo) | 1.4K | best performer; **36.4%** stayed, 500 engaged / 489 unique |
| 26 Jul | 837 | ~28% stayed (derived from channel average) |
| Random But True Facts 3 | 111 | |
| AI Unfiltered 3 | 40 | |
| AI Unfiltered 2 | 9 | |
| 25 Jul | 4 | |
| 25 Jul | 3 | |

## 2b. Random But True Facts 4 — first 6 hours (2026-07-28 19:51)

The animals episode, and the first video built with topic-matched footage.

| metric | value |
|---|---|
| views (6h) | 867, still climbing — curve had not flattened |
| **subscribers** | **+2** — the channel's first, ever |
| stayed to watch | ~40% (reported by user; best on the channel) |
| traffic source | 849 / 867 from the Shorts feed |
| retention curve | not yet processed |

**Why this matters more than the view count:** the channel had 0 subscribers from
2.4K lifetime views. This one video produced 2 from 867 (~0.23%). Still under the
0.5-2% benchmark, but zero to non-zero is a categorical change, not an
incremental one — it is the first evidence the content and CTA convert at all.

Velocity also differs in kind: the flamingo took roughly two days to reach 1.4K
and then flattened; this reached 867 in six hours and was still rising.

**Two changes moved at once, so causation is not available.** This episode is
both an animals topic (already the strongest) *and* the new synced-footage
format. The only single-variable comparison is against the flamingo — also
animals, old format — which gives 36.4% → 40%. A real improvement, but modest,
and possibly noise.

40% remains below the ~50% "average" mark. Better, not good.

**Next diagnostic:** once the retention curve processes (up to two days), it will
show *where* viewers leave. No video on this channel has previously had enough
views for that curve to render at all. It is the only thing that will
distinguish "the first second fails" from "they leave in the middle", and that
distinction decides whether the fix is the opening shot or the episode length.

## 2c. Random But True Facts 5 — first 5 hours (2026-07-29 13:37)

Third consecutive animals episode, second with topic-matched footage, first
after the elephant-fact correction (§6).

| metric | value |
|---|---|
| engaged views (5h) | 387 |
| stayed to watch | **51.6%** — first time on the channel above the ~50% "average" mark |
| swiped away | 48.4% |
| retention curve | not yet processed |

**Three animals episodes in a row, each better than the last:**

| video | stayed |
|---|---|
| flamingo (old format) | 36.4% |
| Facts 4 | ~40% |
| Facts 5 | **51.6%** |

A single win is a data point. A monotonic rise across three consecutive
same-topic videos is a trend, and this is the first evidence strong enough to
start calling the topic-narrowing hypothesis (§5) supported rather than merely
plausible.

**Still not fully separable:** format changes (synced footage, no caption
overlap), fact-quality (a shark/tree hook is unusually strong on its own), and
channel-level algorithm learning all moved together across these three videos.
None of the three can be credited in isolation yet.

## 3. What this data supports

**Retention is the bottleneck, not reach or titles.** 33.1% against commonly
cited benchmarks (70%+ strong, ~50% average, ~30% dies) is near the floor. The
flamingo's engaged-views curve rose for one day and went flat: the algorithm
tested it, two thirds left, it stopped pushing. Nothing was blocked — it just
did not earn more.

**Upload timing and format do not explain the spread.** Three videos published
on 25 July got 1.4K, 4 and 3 views — a 400x spread on one day. And AI Unfiltered
2 is *older* than AI Unfiltered 3 yet has fewer views. Whatever decides this is
per-video, and it happens in the first seconds.

**Titles are not the lever.** The two best videos have no title at all, just a
date. They beat every carefully-constructed series title on the channel. Effort
spent on title formatting was misallocated.

**The AI series is the weakest content on the channel.** 40 and 9 views, against
1.4K for an animal video and 111 for general science. Consistently at the bottom.

**People who stay, enjoy it.** 60 likes / 854 engaged ≈ 7%. That is a healthy
rate. The funnel breaks at the top, not in the content — which means the fix is
the opening, not the writing.

**Subscribers are downstream of retention.** Someone who leaves at second 2 never
hears a CTA at second 50. This held while the channel sat at 0 subscribers, and
the first conversions (§2b) arrived on its highest-retention video — consistent
with the same reading. Fix retention before rewriting CTAs again.

## 4. What this data does NOT support

Be strict about this; the temptation to over-read seven videos is strong.

- **Whether the synced-footage format helps is still unresolved.** Facts 4 is the
  first episode with real reach behind it (§2b), but it changed topic and format
  together. Against the flamingo — the one same-topic comparison — it is 36.4%
  → 40%: encouraging, not conclusive.
- **Whether animals beat other topics is now two data points**, both positive
  (flamingo 1.4K, Facts 4 867-plus). Better than one. Still not many.
- **The 70/50/30 retention benchmarks come from industry blogs, not YouTube.**
  Directionally useful, not authoritative. Do not quote them as official.

**The channel is in a closed loop:** low retention → low reach → too few views
per video to measure retention → nothing to learn from. A/B tests do not
currently produce readable results, because a variant that gets 9 views tells
you nothing. Until reach recovers, judge changes on the channel-level number
across 8-10 videos, not per video.

## 5. Strategy decisions

**One theme per episode — already in place, keep it.** All six facts share a
subject so each builds on the last.

**The channel is too scattered — narrow it.** Five parallel topics (AI, objects,
body, hacks, random) means the recommendation system cannot converge on an
audience, and every upload starts cold. It also plausibly explains 0
subscribers: subscribing is a bet on the next video, and if the next video is
unpredictable there is no bet to make. 1.4K people watched a flamingo and none
subscribed, because nothing signalled what they would get next.

**Saturation matters less here than intuition suggests.** In search you compete
for a ranked slot. In a Shorts feed you are matched against interest profiles —
so a "common" topic means a large, well-defined audience the algorithm already
knows how to find, which helps a channel with no audience. A very niche topic
gives it a small pool to test against. The real cost of a saturated topic is a
higher quality bar, not worse distribution.

**Topic shortlist, ranked by stock-footage availability** (a hard constraint,
see §6):

| topic | audience | Pexels coverage |
|---|---|---|
| ocean / deep sea | very broad | excellent |
| food | broadest | best available |
| money and prices | broad | good |
| everyday objects | broad | excellent |
| space | very broad | good, more saturated |
| exotic animals | broad | **poor — avoid** |

Keep animals in the mix — it is the only thing that has demonstrably worked —
but restrict to species with real coverage (sharks, octopus, birds, dogs, cats),
never wombats or sloths.

**Untested hypotheses worth trying,** in order:

1. **Shorten to 25-30s.** 52-57s is a lot of runway when two thirds already
   leave early. Also halves the cost of every experiment.
2. **Open on the strange image, not a sentence describing it.** Current hooks
   are statements *about* a fact ("Wombats produce cube-shaped droppings, and
   scientists needed years to explain it"). A close-up of the thing before a
   word is spoken is the stronger opening.

## 6. Production rules learned the hard way

Full detail in `SKILL.md`; the short version:

- **Probe the stock library before rendering** — `docs/skill/probe_footage.py`.
  Thirty seconds versus a six-minute render. Skipping it cost five consecutive
  rejected renders of one animals episode.
- **Result counts are worthless.** Pexels returns ~20 hits for any query,
  including ones with no matching footage. Only looking at frames tells you.
  Zero "black filler" warnings is likewise not evidence of correct footage.
- **Sample every cut when verifying, not one frame per segment.** Judging a
  three-cut segment by its midpoint hides two thirds of what shipped.
- Recurring failure modes: a common word with a dominant other meaning
  (`octopus` → carpaccio), a species the library lacks (sloth → sloth *bears*),
  and any year in a query (`1956 summer workshop` → nothing).
- Pin verified terms with `--segment-terms` so the LLM cannot overwrite them.
- **Fact-check claims with real web search before rendering, not after — and
  when a correction is needed, verify the actual spoken script, not just the
  generated caption/description.** On Facts 5, "elephants are the only mammal
  that can't jump" was false (sloths, hippos, rhinos can't either). The fix
  attempt removed "only" from the source fact text and re-rendered; the
  per-fact rewrite prompt (`FACT_PROMPT`) silently reintroduced "only mammals"
  anyway, because deleting a claim leaves room for the model to reinvent it.
  The regenerated video's *caption* (written separately by
  `generate_social_metadata`) happened to avoid the error, which briefly masked
  the fact that the narration and burned-in captions still had it. What
  actually fixed it: giving the model the correcting fact explicitly ("neither
  can sloths, hippos, or rhinos") instead of just deleting the wrong claim, so
  there was no room to reinvent it, and then grepping
  `viral-result.json["segments"]` — the literal spoken text — for the banned
  phrase before treating the fix as done.
- **Check the species list below before picking facts for a new animal
  episode.** Flamingo was the channel's best-performing video (36.4% retention,
  §2), then reappeared as a fact in Facts 6 with no one having checked whether
  it had been used already. Not wrong to reuse a proven subject, but it should
  be a deliberate choice, not a repeat nobody tracked.
- **A verified footage term is not a verified footage *pool*.** `probe_footage.py`
  and manual checks only look at each term's *first* result. `download_segment_materials`
  pulls up to `MAX_CLIPS_PER_TERM` (3) per term, and on Facts 7 both "cuttlefish"
  and "mantis shrimp" had a real animal at result 0 but sea turtles, a stingray,
  a fish school, and a seafood market scene scattered through results 1-2 of the
  *same* pinned terms. Two of eight segments ended up on the wrong animal despite
  every term having been individually confirmed good. Some species (this pair,
  alongside sloth) simply do not have deep, clean coverage on Pexels no matter
  which synonym is tried - the honest fix was checking every unique candidate
  clip across all pinned terms, not just each term's top hit, and when only one
  clip out of six actually showed the right animal, splicing that single clip
  into the segment's exact window directly (`ffmpeg` trim + concat, matching
  resolution/fps, replacing only the video stream so the full original audio
  stays untouched and in sync) rather than gambling on another full render.
- **A Whisper transcription can silently corrupt an otherwise-correct episode.**
  On the same Facts 7 render, the narration said "hearts" twice (heart
  regeneration, then again a sentence later). `faster-whisper`, conditioning
  each segment on previously transcribed text by default, got stuck on the
  second occurrence and transcribed the following ~30 seconds of real,
  perfectly good narration as the word "hearts" repeated roughly thirty times.
  That collapsed the back half of the word-level timeline to a single
  timestamp, and every fact after it got squeezed into a zero-duration window -
  a pure transcription bug, unrelated to facts or footage, that would have been
  invisible without checking `segment_timings` for duplicate/zero-length
  windows. Fixed for good by passing `condition_on_previous_text=False` to
  `transcribe_word_timings()` (`app/services/viral.py`). If a future episode's
  `segment_timings` ever shows two adjacent entries with identical start/end,
  suspect this same failure mode again - check `segments` for large repeated-word
  runs before assuming the footage or facts are at fault.

### Species used so far

| species | episode |
|---|---|
| flamingo | standalone video (old format), Facts 6 |
| wombat, sea otter, cow, crow, octopus, dolphin | Facts 4 |
| shark, cat, dog, honeybee, elephant/rhino/hippo/sloth (named, not shown), Adelie penguin (African penguin footage) | Facts 5 |
| owl, giraffe, sea turtle, butterfly, kangaroo | Facts 6 (flamingo repeated, see above) |
| axolotl, mantis shrimp, cuttlefish, hedgehog, peacock, seahorse | Facts 7 |
| owl, giraffe, sea turtle, butterfly, kangaroo, flamingo | Facts 6 |

Update this table whenever a new animal episode is built.

## 7. Working agreement

**Ship the video, then report what is weak.** Do not silently iterate toward
perfection. On 2026-07-28 a single request for one episode became five renders;
each failure was real, but the user should have been given the choice after the
first or second, along with the option to accept a good-enough cut.

**Watch for optimising the measurable instead of the important.** That same day,
substantial effort went into footage-topic matching — measurable, verifiable —
while the actual problem (67% leaving in two seconds) went untouched. Production
quality is already adequate. The opening is not.

**Division of labour.** The mechanical parts — generation, quality checks,
measurement, reporting — are well suited to automation. Two decisions are not,
and should stay with the user: **what the video is about**, and **what the first
two seconds look like**. Those are where human judgement genuinely outperforms.

**On running the channel autonomously** (asked and answered 2026-07-28):
technically straightforward — YouTube Data API uploads, Analytics API reads,
~6 uploads/day within default quota. But it would likely not produce virality:
the feedback loop is far too slow and noisy for the number of experiments
needed, breakouts are heavy-tailed and substantially luck, and there is no
real-time cultural sense for trend-jacking. It would also amplify the
optimise-the-measurable failure above. Separately, fully automated daily
templated uploads sit exactly in the profile YouTube scrutinises under its
inauthentic / mass-produced content policy — a real risk when the goal is
monetisation.

## 8. Open items

- Five unpublished week-1 videos still carry the caption-overlap bug (~2.3s of
  overprinted text each). Re-burn is ~1 minute per video, no footage re-render.
  Two already-published videos would cost their view counts to replace.
- Sloth fact in Random But True Facts 4 shows a dolphin, which the script names.
  Veo would provide a real sloth for roughly one clip's cost.
- Content calendar still built around the old five-topic mix. Rebuilding it
  around the §5 shortlist has not been done.
