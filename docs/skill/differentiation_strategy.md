# Differentiation strategy — 2026-08-15

Written in response to the owner's question: *"if a viewer can't tell your
channel apart from another channel, your channel is in trouble. I want to stay
in the RBT niche but differentiate it meaningfully, for monetisation and
uniqueness. What do I do?"*

This file argues one position and states the evidence for it. It does not
replace `channel_playbook.md` (measured history) or `shorts_growth_guide.md`
(adopted tactics) — it argues that the channel's **identity**, not its tactics,
is the binding constraint right now.

---

## 1. The arithmetic — live pull, 2026-08-15

Data API, `channels.list?part=statistics&mine=true`:

| metric | value |
|---|---|
| videos | 42 |
| lifetime views | 26,661 |
| subscribers | **38** |
| view→sub conversion | **0.14%** |
| views / video | ~635 |
| subs / video | ~0.90 |
| current rate | ~1,300 views/day, ~1.8 subs/day |

**What that rate implies for the stated goal (1,000 subs):**

- 962 subscribers to go ÷ ~1.8/day = **~530 days**, i.e. reachable around
  early 2028 at the current format and cadence.
- Equivalently: ~673,000 more views at the current conversion rate.

**And for the Shorts monetisation route specifically:** YPP requires 1,000
subscribers **plus** either 4,000 valid public watch hours in 12 months *or*
**10M valid public Shorts views in 90 days**. 10M/90d is ~111,000 views/day.
The channel is at ~1,300/day — an **~85x gap**, not a gap that closes by
tuning a counter overlay. (Thresholds as of the last time they were checked;
confirm in Studio before acting on them.)

This is the honest framing of the owner's question: the channel is not
underperforming its niche, it is *performing exactly like its niche*, and the
niche's median outcome does not reach the goal. Incremental format tuning
cannot cover an 85x gap. Only a step change in what the channel *is* can.

## 2. The channel's own data already names the winner

From §10's full pull (2026-08-13), unchanged by anything since:

| format | avg retention | like-rate | subs/video |
|---|---|---|---|
| **STORY** (6 videos) | **63.4%** | **3.10%** | **1.50** |
| facts, pre-countdown (17) | 53.7% | 2.10% | 1.35 |
| facts, countdown (9) | 51.6% | 1.42% | 1.00 |

Story wins on every metric measured, and ep26 (moa) alone brought **+7
subscribers** — the single best converting video the channel has ever made.

Two things follow:

1. **The countdown-vs-listicle A/B test is optimising the losing branch.** It
   is a ±10% question inside a format that trails story by 12 retention points
   and 50% on subscriber conversion. Eight more episodes spent settling it is
   eight episodes not spent on the format that already won.
2. **Even story is not enough on its own.** At 1.50 subs/video and 2
   uploads/day, 1,000 subs is still ~320 days out. Story is the right vehicle;
   it still needs a reason for a viewer to choose *this* channel.

## 3. The diagnosis: substitutability

The channel is substitutable by construction:

- **A commodity format.** "6 facts about X, karaoke captions, stock footage,
  TTS narration" is the single most-cloned template on Shorts. Every element
  can be reproduced by a competitor in an afternoon — most of them are running
  the same open-source pipeline this channel runs.
- **A promise of nothing.** "Random" is an anti-brand. Subscribing is a bet on
  the next video; if the next video is unpredictable there is no bet to make.
  This is already written in §3/§5 of the playbook as the leading explanation
  for the zero-subscriber era, and the conversion rate has not moved since.
- **A title that promises nothing.** "Random But True Facts 33 🏛️" tells a
  viewer nothing about what they'd get by subscribing. The number aids
  channel-page binging (that part is real) but carries no promise.
- **No sensory signature.** Raw Pexels footage at default grade, a stock TTS
  voice, a generic caption style. Nothing lets a viewer recognise the channel
  in the feed before the words start.

There is also a **monetisation-policy** dimension: YouTube's inauthentic /
mass-produced content policy is aimed precisely at templated, automated,
indistinguishable uploads. Differentiation is not only a growth lever here, it
is insurance on the YPP review the channel is working toward.

## 4. The proposal — one strategy, six changes

**Keep the niche. Change what the channel promises, how it sounds, and how it
looks. Stop being a facts channel; become a daily archive of true events that
sound invented.**

The channel's best-performing content already *is* this — moa, great auk,
Wojtek, the Emu War, Antarctica, Inky the octopus. The proposal is to stop
treating those as an occasional format and make them the entire product.

### 4.1 Format: 100% story (STOP the A/B test)

One story per day, 40–70s. Facts episodes drop to a fallback used only when no
story lead is ready in time, not a scheduled half of output. Conclude the
countdown A/B as *decided by the pre-existing evidence* rather than running it
to n=4/arm.

### 4.2 Territory: a named, numbered archive

The unifying promise: **"this actually happened, and it sounds made up."**
Every episode is a numbered entry in an ongoing archive, not "Facts N".

- Titles name the story, not the series index: *"The bear that enlisted in the
  Polish army"*, not *"Random But True Facts 44"*.
- The entry number stays (it drives binging), but subordinate to the story:
  `Entry 44 — The bear that enlisted in the Polish army`.
- Narrow the topic pool to what the archive can plausibly contain — historical
  absurdities, extinct/lost things, true crime, forgotten records — and stop
  drawing from open "random facts" space. Narrower is the point: it lets the
  recommendation system converge on an audience, which unpredictable topics
  actively prevent.

### 4.3 A house look, applied to every frame

The cheapest recognisability lever available, and the one the competition
structurally does not do: a **fixed grade applied to all footage, Pexels and
AI alike** — one colour curve, light grain, a soft vignette, consistent title
card. Implemented as a single ffmpeg filter pass at the end of the existing
render (no re-architecture, no per-episode cost), it makes any frame of any
episode identifiable as this channel's before a word is spoken. Raw ungraded
stock footage is the visual signature of automation; a consistent grade is the
visual signature of a show.

### 4.4 A fixed voice and two fixed rituals

- **One voice, permanently.** Never rotate it. The voice is the channel's
  strongest audio identity and currently the most interchangeable thing about
  it.
- **A cold open used in every single episode** — three or four words, spoken
  over frame 1, e.g. *"This actually happened."* Rituals are what make a
  serialised channel feel like a show rather than a feed of clips.
- **A fixed sign-off**, distinct from the CTA, that names tomorrow's entry.

### 4.5 End on a real open question; pin the counter-theory

Comment volume is the channel's worst metric (10 comments across 25 videos at
last count). Generic asks ("which is your favourite?") produce nothing. What
produces comments in this genre is an **unresolved** ending — the part nobody
knows — plus a pinned comment stating the strongest competing explanation.
This replaces the disagreement-CTA convention on facts episodes with something
that works in story format, where the channel's best content lives.

### 4.6 Serialise deliberately

- One two-part story per week, part 2 the next day, stated explicitly at the
  end of part 1.
- A single playlist ("The Archive") so a channel-page visitor sees a body of
  work, not 42 loose clips.
- The outro names tomorrow's entry by title. Subscribing has to buy something
  specific.

## 5. Monetisation — the route matters more than the format

**Shorts ad revenue is not a business at any scale this channel will reach
soon.** Shorts RPM runs roughly $0.01–0.15 per 1,000 views; even 10M views in
90 days (the YPP threshold itself) is a few hundred dollars. Planning around
it is planning around the worst-paying surface on the platform.

Three routes that are actually reachable, in order of leverage:

1. **Long-form compilations, built from episodes that already exist.** Eight to
   ten finished stories, stitched with connective narration, becomes a 10–12
   minute video at near-zero marginal cost — the assets are already rendered
   and paid for. This matters twice: long-form RPM is 20–100x Shorts RPM, and
   the **4,000 watch hours in 12 months** route is far more reachable than 10M
   Shorts views in 90 days. Rough shape: a 10-minute video holding 3 minutes of
   average view duration needs ~80,000 views *spread over a year* to clear
   4,000 hours — against ~111,000 views *per day* for the Shorts route. This is
   the single highest-ROI unexploited asset the channel owns.
2. **Cross-post every episode to TikTok, Instagram Reels and Facebook Reels.**
   Zero extra generation cost, independent monetisation programmes, and a hedge
   against a single algorithm.
3. **Fan funding before ads.** YouTube's lower tier (around 500 subscribers,
   plus recent uploads and a smaller watch-hour/views bar) unlocks memberships
   and Super Thanks well before the full YPP ad threshold. At 38 subscribers
   that is still the nearer milestone, and it should be the one on the wall.

## 6. Test protocol and kill criteria

Run the new identity for **14 consecutive story episodes** (~2 weeks at one
story/day), all six changes applied together. Deliberately *not* a
single-variable test: the claim under test is that an identity is more than the
sum of its mechanics, and testing the grade alone or the cold open alone would
measure nothing.

**Baseline to beat** — the existing 6-story cohort: 63.4% retention, 3.10%
like-rate, 1.50 subs/video.

**Read at 14 episodes:**

| result | reading | action |
|---|---|---|
| subs/video ≥ 2.5 and retention ≥ 63% | identity is the lever | commit; build the long-form compilation |
| subs/video 1.5–2.5 | real but insufficient | keep the identity, attack topic selection next |
| subs/video < 1.5 | identity was not the constraint | revert to plain story; the constraint is topic/hook quality |

Judge on subs/video and retention. **Views are the wrong metric here** — an
identity change is a bet on conversion, and views will lag it either way.

## 7. What to stop doing

- **Stop the countdown/listicle A/B test.** Its question is smaller than the
  gap between facts and story that the data has already measured.
- **Stop "Facts N 👀" titles.** They promise nothing and are the most
  substitutable surface on the video.
- **Stop treating story as the occasional variant.** It is the product.
- **Stop planning around Shorts ad revenue.** Plan around watch hours and
  cross-platform.
- **Stop shipping ungraded stock footage.** It is the visual fingerprint of the
  exact category the channel is trying to escape.
