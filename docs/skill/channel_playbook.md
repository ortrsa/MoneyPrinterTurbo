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

## 2d. Length experiment — built 2026-07-30, results pending

The growth guide's Rank 1 requires **≤20s**; every retention figure we own comes
from 52–62s videos, so length has never actually been tested. This experiment
isolates it.

**Design:** Facts 7 (57.1s, 6 facts) was split into two 3-fact shorts using the
*same already-fact-checked facts and same already-verified footage terms*, so the
only variable that moves is length.

| variant | length | facts | content |
|---|---|---|---|
| A (control) | 57.1s | 6 | the original Facts 7 |
| B — Facts 8 | 25.6s | 3 | axolotl, mantis shrimp, cuttlefish |
| C — Facts 9 | 25.6s | 3 | hedgehog, peacock, seahorse |

All three archived side by side in `/tmp/experiment_length/` with their
`viral-result.json`. The Facts 7 task directory was left fully intact.

**Reading the result:** publish B and C a day apart and compare stayed-to-watch
against the long-format baseline (Facts 5 at 51.6%, Facts 7 pending). 65–70%+ on
the shorts means the guide is right and the format changes. ~50% means length was
not the constraint and the real problem is elsewhere.

**Two honest caveats on this experiment:**

- **25.6s missed the ≤20s target.** Facts were capped at 14 words expecting
  ~4-5s each; Gemini TTS actually delivers 5–6.5s per fact. Hitting sub-20s needs
  ~10 words per fact or dropping the spoken outro. 25.6s vs 57.1s is still a real
  length test, just not a test of the guide's actual threshold.
- **Compression cost factual precision.** Facts 8's axolotl line became "regrow
  damaged brains and accept *any* organ transplants" — the verified claim is
  *parts* of the brain and transplants *from other axolotls*. Fourteen words left
  no room for the qualifiers. This is itself a finding about the short format:
  fewer words means less space to stay precise, so short episodes need their
  facts chosen for brevity rather than truncated after the fact.

## 2e. Random But True Facts 10 — published 2026-07-31, results pending

Topic: bats — the first episode built after adopting outlier-topic research
(§5a), though the six facts themselves were sourced and verified directly
rather than copied from a confirmed outlier video (see §5a's honest gap on
that). Kept the proven 50-60s/6-fact long format rather than pre-empting the
still-unresolved §2d length experiment: 54.1s, 6 facts.

Delivered file is `final-viral-fixed.mp4` in that task's `storage/tasks/`
directory — the footage-corrected render. The `final-viral.mp4` in the same
directory has the pigeon/duck contamination described in §6 and must not be
used or re-uploaded.

Upload kit used:
- Title: `Random But True Facts 10 👀`
- Hashtags: `#batfacts #vampirebats #tequilabat #animalfacts #wildlife #nature
  #shorts #viral #fyp` — first episode using the guide's Rank 7 three-tier
  structure (post-specific / niche / broad), applied by hand at publish time.
  `generate_social_metadata` itself still only emits 3 flat tags; that code
  fix is still open (§8).
- Pinned comment posted: "Bet you're never looking at a margarita the same way
  again 🦇🍹 Which animal should Random But True cover next — drop it below."

Still open from this episode: the two Veo prompts (a two-bats-roosting close-up
for the vampire-bat fact, a scale shot for the bumblebee-bat fact) were handed
to the user for extra footage variety but not yet generated as of this
writing — splice in once available, same technique as §6's fix.

No retention/view numbers yet. Update this section once Studio has a few
hours of data, following the §2b/§2c format — this is also another data point
for or against §2d's length question, since it's a long-format episode built
after the guide was adopted.

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

## 5a. Outlier topic research (adopted 2026-07-30)

Guide Rank 3 (9.0/10): stop inventing topics from scratch; find a niche channel's
proven outlier video and remake its *topic* with fresh clips and facts. Full
method now lives in `SKILL.md` step 0 — this entry records the first research
pass and its honest limits.

**What a general web search actually returned:** no per-video view counts (this
pipeline has no YouTube Data API access, and `WebSearch`/`WebFetch` only reach
channel-level aggregates and secondhand blog summaries). One concrete channel
data point surfaced repeatedly: **The Fact Animal**, ~130K subscribers and ~30M
views across 22 videos (≈1.4M views/video average) — a strong ratio, but that is
a channel average, not a verified outlier video, and no individual video's view
count could be confirmed from here.

**Candidate topic categories reported (secondhand, unverified) as strong
performers in this niche:** ferocious dog breeds/temperament rankings, animal
strength comparisons, bat behavior oddities, frog abilities, sloth statistics.
Treat these as directional leads, not proof — the honest gap above still stands.
Against the species table below: `dog` and `sloth` (named, not shown) have
already appeared (Facts 5), so a dog or sloth episode would be a deliberate
repeat with a new angle, not virgin territory; bat and frog are unused.

**If a real go/no-go on a specific outlier claim is ever needed:** that requires
either the user checking a channel's Shorts tab sorted by "Popular" in a
browser, or wiring a YouTube Data API key into this pipeline. Say so rather than
treating a blog-post summary as equivalent.

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
- **Order the pinned terms so the verified-good one is FIRST.** The first term in
  a segment's list is the primary — it is exempt from cross-segment URL de-dup and
  supplies the opening cut, the one that plays while the fact is actually spoken.
  Pinning `cuttlefish swimming,common cuttlefish,cuttlefish` put a term whose top
  result is a *sea turtle* in the primary slot and shipped the turtle again, even
  though `common cuttlefish` (the verified one) was right there in position two.
  Same mistake twice, once in Facts 7 and again in Facts 8.
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
  **Confirmed again on Facts 10**, before rendering rather than after: the raw
  fact said the bumblebee bat is "arguably the smallest mammal on Earth, by
  body length" (the honest phrasing — the Etruscan shrew is smaller by mass);
  `FACT_PROMPT`'s dry-run rewrite dropped the qualifier and turned it into "it's
  tied as the absolute smallest mammal on Earth" — a false, invented absolute.
  Caught in the `--dry-run` script text before any TTS/render cost was spent,
  fixed by rewriting the raw fact to state the correction explicitly ("the
  smallest bat... but not by weight, since the Etruscan shrew is lighter"),
  which the rewrite preserved intact on the next pass. `--dry-run` is worth
  running as a matter of course before every real render for exactly this
  check, not just when a correction is already suspected.
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
- **Bats are close to a total Pexels gap, worse than sloth.** Building Facts 10,
  roughly 20 candidate search terms were probed (`bat`, `vampire bat`, `bat
  flying`, `bat hanging upside down`, `bumblebee bat`, `bat teeth`, `bat wing
  membrane`, `tiny bat`, and more) and only **two** returned a real bat: one
  close-up of flying foxes hanging in a tree, one wide shot of a colony
  emerging at dusk. Every other term resolved to Halloween paper-bat
  decorations, a kid in vampire-fang makeup, a Halloween pumpkin prop, a
  baseball bat (word collision), an owl, a chicken, or a praying mantis. Pinning
  the two good terms still wasn't enough: `download_segment_materials`'
  9-clip-per-segment pool for `gray headed flying fox,fruit bat,megabat` also
  contained a flock-of-pigeons-in-a-plaza clip and a ducks-on-a-pond clip, and
  random selection put one or both into 4 of the episode's 6 fact segments
  despite every pinned term's rank-0 result being a real bat. Caught only by
  sampling frames across the *rendered output*, not by re-checking the search
  terms — the terms were never wrong, the pool behind them was contaminated.
  Fixed with the same splice technique as the Facts 7 cuttlefish case, looping
  the one verified close-up clip to cover all four contaminated segments. Two
  Veo prompts were handed to the user for future variety (a moodier
  two-bats-roosting shot for the vampire-bat fact, a scale shot for the
  bumblebee-bat fact) but not yet generated as of this writing.
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
| axolotl, mantis shrimp, cuttlefish | Facts 8 (length experiment, split from Facts 7) |
| hedgehog, peacock, seahorse | Facts 9 (length experiment, split from Facts 7) |
| bat (flying fox / megabat footage) | Facts 10 |

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

## 7a. The story format — a second flow, added 2026-08-01

A parallel content format, requested by the channel owner and built as
`docs/skill/story_episode.py`. It does **not** replace the list format; both
flows coexist and neither touches the other's code path.

**What it is.** One true story, 30–90 seconds, told as escalating beats instead
of N unrelated facts. Source stories come from wherever (the owner's example was
a Facebook page, "עובדות לא חשובות"), used strictly as a *topic lead*.

**Structural differences from `viral_episode.py`, and why:**

| | list format | story format |
|---|---|---|
| counter | `N/6` | **off** — "3/6" mid-story tells the viewer how much is left and dismantles the suspense |
| progress bar | on | on — it says "nearly there", which helps retention |
| length | ~55s fixed by 6 facts | 30–90s, set by how much the story can carry |
| segments | independent facts | beats, each ending on an open loop |
| title | none burned in | **2-line banner, 2 keywords in pink** (guide Rank 5) |

**On the guide's ≤20s rule:** deliberately not applied here. A narrative needs
room to set up and pay off a turn; at 20s the hook never gets cashed. The owner
specified 30–90s and that governs this flow. §2d's length experiment covers the
list format only.

**On the guide's 6-phase Declare/Assessment/Isolate/Process/Build/Reveal
structure:** it was written for restoration/transformation videos and mostly
does not transfer. "Assessment" with digital calipers has no analogue in the
assassination of Franz Ferdinand. Only two phases map cleanly — **Declare → the
hook**, and **Reveal → the payoff plus a callback to the opening image** (the
callback is the part worth keeping; it drives rewatches). The middle phases were
replaced with narrative escalation.

**The title banner is a persistent top band, not an opening card.** The guide
says "2 lines on a pure black background"; a black card at the head of the video
would burn the first 2 seconds, which the same guide calls the single most
important metric. A persistent band gives instant context without costing the
hook.

**Two bugs found while building it, both worth remembering:**

- **`refine_hook()` is actively harmful in narrative context.** Built for the
  list format, it takes the first fact as context and reliably rewrites the hook
  into a restatement of it — and its own prompt carries no rule against
  scene-setting. It twice replaced a strong hook ("An archduke survived a
  grenade, only for a wrong turn to get him killed") with background exposition
  that duplicated beat 1, which also meant the same sentence got footage twice.
  It is not called in this flow. Tuning the similarity threshold would have
  papered over a step that was systematically wrong for this format.
- **A regenerated script invalidates its own fact-check.** The narration is
  re-rolled on every run, so the text that gets rendered was never the text that
  was verified. `--from-dry-run` locks an approved script and renders exactly
  that. Verify-then-render does not hold together without it.

**Measured narration speed** (script words ÷ final duration):

| episode | words | seconds | words/sec |
|---|---|---|---|
| Facts 7 (list) | 152 | 57.14 | 2.66 |
| Facts 10 (list) | 145 | 54.12 | 2.68 |
| Story 1 (narrative) | 135 | 44.74 | **3.02** |

Narrative runs ~13% faster than list content — a list pauses between facts, a
story is one continuous line. `WORDS_PER_SECOND` is set to 2.9 for this flow.
Note the model does not hit the word budget exactly: a 75s target produced a 45s
video, so `--target-seconds` steers rather than sets, and the script warns when
the gap exceeds 20%.

**Footage for historical stories works, but only atmospherically.** There is no
Pexels footage of Sarajevo in 1914, and per §6 a year in a query returns
nothing. What worked for Story 1 was evocative rather than literal: an empty
cobblestone European street, a vintage convertible, a shallow rocky river (for
the assassin who jumped into 10cm of water), old film strips for the hook and
outro, a war memorial for the payoff. All nine segments verified frame-by-frame
after render. Pin these with `--segment-terms`; the LLM will not find them.

**Two adjacent segments sharing a primary term replay the identical clip.** The
first pinned term is exempt from cross-segment URL de-dup (§6) so that a subject
appearing in consecutive lines still gets the right footage — but the cost is
that the *same clip* restarts mid-scene, which reads as a stutter. On Story 1
segments 2 and 3 both pinned `vintage car`, and the same Mercedes played twice,
spotted immediately by the channel owner. This is common in narrative, where
consecutive beats often concern the same car or person.

The fix that works is **one clip slowed to fill the merged window**, not two
plays: take the first segment's cut, apply `setpts=<merged_window/clip_len>*PTS`,
and splice it across both windows (Story 1: 3.94s of footage stretched by 2.081
to cover 10.34–18.54, i.e. 0.48x). Slow motion also suits a tension beat better
than a repeat. `story_episode.py` now warns when adjacent segments share a
primary term; the de-dup logic itself was left alone because it is shared with
the list flow.

**The model puts the payoff in the hook and then has nothing to reveal.** On
Story 2 (Mercedes) the generated hook was "Mercedes-Benz was named after a Jewish
girl whose grandfather was a famous rabbi" — both reveals spent in the opening
two seconds. It also produced a beat that was a rhetorical question about
something two earlier beats had already answered, and dropped the single most
striking fact (the grandfather's name was Adolf) entirely. This is the recurring
failure of the format: the prompt asks for the most shocking element up front,
and the model reads that as "state the conclusion". Expect to restructure the
beat order by hand and re-lock with `--from-dry-run`; the model is reliable at
producing *material* and unreliable at ordering it. Check specifically that the
hook withholds something and that the reveal actually lands the best fact.

**Titles are a monetisation decision, not just a hook decision.** Story 2's
generated title was "How a Jewish girl's name ended up on Nazi fighter planes" —
accurate, and the strongest possible hook, but YouTube limits ads on war and
Nazi-related content even when it is historical and factual. Since the channel's
stated goal is monetisation, the shipped title was "The Girl Behind the Mercedes
Name": curiosity-driven, no flag words, with the wartime facts still stated
plainly in the narration. Flag this trade-off to the owner rather than silently
picking either side.

**Sensitive topics: cite what the subject documents about itself.** Story 2's
wartime claims are all sourced from Mercedes-Benz Group's own corporate history
pages, which is stated in the narration ("Mercedes-Benz documents all of it
today"). That turns a potential accusation into a citation and is the right
default whenever a story implicates a named, living organisation. The source
file also carried an explicit instruction not to imply the naming was a trick or
a cover-up, and not to editorialise about the modern company.

**Copyright, since the source is other people's posts** (asked and answered
2026-08-01): facts and historical events are not copyrightable, but the specific
wording of a post is — regardless of whether the author is anonymous, posting in
a group, or unaffiliated with any organisation. Anonymity makes it unenforceable
in practice, not permissible. The workflow is therefore: use the post as a topic
lead, re-verify the facts against independent sources, and write the narration
from scratch. `--source-note` records the lead in `story-result.json`. Images
attached to such posts (Story 1's lead carried an NBC News photo) are separately
protected and must not be reused.

**Re-verification is not optional, and it caught a real error on the first
try.** The generated narration for Story 1 described Princip as "hungry" outside
the delicatessen — nodding at the widely repeated story that he was buying a
sandwich, which is a documented myth. Fixed by stating the correction explicitly
in the source file rather than deleting the claim (same technique as §6's
elephant fact), then grepping the locked script for `sandwich|hungry|food|eating`
before rendering.

## 8. Open items

- Five unpublished week-1 videos still carry the caption-overlap bug (~2.3s of
  overprinted text each). Re-burn is ~1 minute per video, no footage re-render.
  Two already-published videos would cost their view counts to replace.
- Sloth fact in Random But True Facts 4 shows a dolphin, which the script names.
  Veo would provide a real sloth for roughly one clip's cost.
- Content calendar still built around the old five-topic mix. Rebuilding it
  around the §5 shortlist has not been done.
- **No YouTube Data API access from this pipeline.** §5a's outlier-topic research
  had to rely on secondhand web summaries instead of real per-video view counts.
  A read-only Data API key (or the user manually sorting a channel's Shorts by
  "Popular") would let future topic research verify an actual outlier instead of
  a reported channel average.
- **Facts 10 (bats) published 2026-07-31** — awaiting first-hours numbers
  (§2e). It's a long-format (54.1s/6-fact) episode, so its retention reads as
  another data point on the still-unresolved §2d length question, not just its
  own result.
- Two Veo prompts are outstanding and not yet generated by the user: a real
  sloth hero shot for Facts 4's dolphin-substitution gap (§6, two variants
  given), and two bat-variety shots for Facts 10 (a two-bats-roosting close-up,
  a bumblebee-bat-scale shot). Splice in via the §6 technique once received.
- `generate_social_metadata` still only emits 3 flat hashtags; Facts 10 used a
  hand-written 3-tier set instead (§2e). The Rank 7 code fix itself is still
  undone.

## 9. Sourcing stories from other people's posts — what is and isn't ours

Story leads increasingly come from Facebook pages like *עובדות לא חשובות*. The
line that matters:

- **Facts and events are not copyrightable.** Who shot Franz Ferdinand, in what
  order the assassins failed, what a court found — nobody owns those.
- **The specific wording of someone's post is.** Copyright attaches automatically
  the moment someone writes original text, and it does **not** depend on the
  author being named, being an official page, or being identifiable. "It's just
  some anonymous person in a group" changes only how enforceable it is, not
  whether copying is legitimate.
- **Images attached to a post are separately owned** (a news photo credited to
  NBC stays NBC's). Never reuse them; source footage independently.

**The workflow this implies, and it is the same one already used for facts:**
treat the post as a *topic lead* only, re-verify the claims against independent
sources, then write the narration from scratch. `story_episode.py --source-note`
records where the lead came from in `story-result.json` so it can be traced
later. Re-verification is not just legal hygiene — posts like these are often
wrong on details, so it is a quality step too.

## 10. Story format (`story_episode.py`) — added 2026-08-01

A second, parallel flow to `viral_episode.py`, for narrative true stories rather
than fact lists. Nothing about the list format changed; both scripts coexist.

**Differences that matter, and why:**

| | list format | story format |
|---|---|---|
| length | 50–60s (6 facts) | 30–90s, set by `--target-seconds` |
| counter | `N/6` shown | **off** — a counter tells the viewer "3 left", which deflates narrative tension |
| progress bar | on | on (it says "nearly there", which helps retention) |
| segments | independent facts | hook → escalating beats → reveal, each beat ending on an open loop |
| title | metadata only | **2-line on-screen banner**, 2 keywords recoloured (guide Rank 5) |

**Three interpretation calls, stated openly:**

1. **30–90s over the guide's "≤20 seconds".** Set by the channel owner. A
   narrative cannot land a turn in 20s — the hook never gets paid off. The §2d
   length experiment therefore says nothing about this format.
2. **The 6-phase Declare/Assessment/Isolate/Process/Build/Reveal structure was
   written for restoration videos** (measuring rust with a caliper). Only
   *Declare* → hook and *Reveal* → loop-closure transfer; the middle is replaced
   with narrative escalation. Pretending the rest maps would have produced
   nonsense for a story about an assassination.
3. **"2-line title on a pure black background" is built as a persistent top
   banner, not an opening black card.** A black card would burn exactly the
   first 2 seconds the same guide calls decisive. A banner gives instant context
   without costing the hook.

**Three bugs found while building it, all fixed, all worth remembering:**

- **`video_script_prompt` is capped at 2000 characters** (`MAX_SCRIPT_PROMPT_LENGTH`).
  A story pasted into the prompt fills it, so the output-format instructions got
  silently truncated away and the model returned prose. Long prompts must go via
  `custom_system_prompt` (cap 8000), which *also* replaces the default system
  prompt — necessary here, because the default one forbids "any formatting",
  fighting the required `HOOK:/BEAT:/REVEAL:` labels.
- **`llm.format_response()` reflows the reply**, so labels can arrive glued into
  one line (`...found him.BEAT: Six young men...`). Parse by regex on the labels,
  never by `splitlines()`. Same function also strips anything in parentheses
  (`re.sub(r"\(.*\)", "")`, greedy) — worth knowing before writing narration
  that relies on them.
- **`refine_hook()` must not be reused here.** It takes the first fact as
  context, so on a story it reliably rewrites the hook into a restatement of
  beat 1, and its own prompt has no rule against scene-setting. It twice turned
  a strong hook into background exposition — once replacing *"An archduke
  survived a grenade, only for a wrong turn to get him killed"* with *"Six young
  men lined a Sarajevo street to kill an empire's heir"*, which both wasted the
  opening and duplicated the next segment's footage. The story prompt's own hook
  rules are stricter; its output is used unrefined, with a similarity check left
  in as a warning only.

**Known limits, unresolved:**

- The model undershoots the word budget (a 75s target produced ~60s). A warning
  fires above 20% deviation; there is no retry loop.
- **Historical stories are a footage problem waiting to happen.** Pexels has
  nothing for "Sarajevo 1914", and §6 already documents that years in queries
  match nothing. Expect to pin `--segment-terms` with *atmospheric* rather than
  literal shots (period-looking streets, old cars, rivers), or to generate
  hero shots. This has not been tested on a real render yet.
