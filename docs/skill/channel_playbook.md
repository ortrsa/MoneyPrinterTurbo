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

## 0. State as of 2026-08-07 07:10 Israel — read this first

A pinned summary for picking up a fresh session fast. Full rationale for every
line here is in the dated sections below and in `SKILL.md`; this is only the
"what's true right now" digest.

**Live/pending right now:**
- Ep20 (Facts 20, human body) is **published, public**, video id `MsvTGDudZ-U`.
  Its live YouTube title reads "Random But True Facts 19 👀" — a mislabel from
  a manual upload the owner did outside a session; owner declined the fix.
- Ep21 (D-Day crossword) is **published, public**, video id `S_zjnvbzZXw`.
- Ep22/build-key (pizza, retitled live to "Facts 20 👀") **published, public**,
  video id `yfuSDGdpTw4`, 16:30 slot 2026-08-06.
- Ep23/build-key (space facts, retitled live to "Facts 21 👀") **published,
  public**, video id `EtNhXZdSKZc`, 22:30 slot 2026-08-06.
- **Ep24 (big cats) and ep25 (weather phenomena)** — today's 09:00 build —
  are **approved by the owner (2026-08-07), awaiting the 16:30/22:30 publish
  jobs**. Both had real footage defects caught by post-render frame
  verification (not by pre-render probing) and fixed before delivery; full
  detail in `episode_log.csv` rows 24/25 and the dated §5c entry below.
  `storage/todays_uploads.json` already records both as `approved: true`,
  `published: false`, pointing at each episode's `result_json`. Live-title
  check already done at approval time: highest live "Facts N" is 21, so
  ep24/ep25's current titles ("Facts 22"/"Facts 23") are correct as-is — no
  retitling needed before publish.

**New capabilities added this session, both need conscious use, neither is
automatic yet:**
- **`docs/skill/ai-footage-fill/`** — generates a single AI B-roll clip
  (nano-banana first frame + Veo animation) for the one segment per episode
  where Pexels genuinely has nothing usable. Splices in via `--segment-clips`
  on either episode script. Credentials are live and working: Google Cloud
  project `ringed-rune-503816-b8`, OAuth token at `docs/skill/veo/token.json`
  (not a service-account key — the owner's choice, see the skill's own
  SKILL.md for the setup path). Image model is `gemini-2.5-flash-image`
  — the whole Gemini 3.x image tier ("Nano Banana 2" and siblings) 404s on
  this project despite being listed, confirmed by direct testing, not a
  guess. Video model is `veo-3.1-fast-generate-001`. **Not wired into the
  daily 09:00 flow** — the owner said keep the skill but don't default to
  using it until they say otherwise. First real (non-demo) use was ep21
  tonight: owner reviewed an all-Pexels cut against an AI-improved cut side
  by side and picked the AI-improved one.
- **`--narration-speed`** (default `1.1`) on both episode scripts — ~10%
  faster narration per owner feedback that pacing feels slow. Implemented as
  an ffmpeg atempo pass on the rendered audio, run *before* whisper
  transcription, so captions and every segment's footage window inherit the
  speed-up automatically — cut-to-cut rhythm is unchanged, the whole timeline
  just scales down slightly. This IS the new default for every future build,
  no flag needed. Gemini TTS (the actual voice in use) has no native rate
  control, which is why this had to happen at the audio-file level.

**2026-08-06 09:00 build.** Built ep22 (pizza, 16:30) and ep23 (space facts,
22:30). Both approved same day and published — see the live/pending bullets
above for video ids. Full build detail, including a real footage bug caught
and fixed in ep22 (two splice attempts — the first used a misidentified
file) and ep23's unusually clean frame-verification pass, is in
`episode_log.csv` rows 22/23.

**2026-08-07 09:00 build — done, awaiting owner approval.** Built ep24 (big
cats biology, first time this topic) for the **16:30 slot** and ep25
(weather phenomena, first time this topic) for the **22:30 slot** — both
fresh topics, calendar and §5a outlier list still exhausted. Both had real
footage defects caught only by post-render frame-by-frame verification, not
by pre-render probing, and both were fixed before the corrected version was
delivered to Telegram (the pipeline's own auto-send fired on the first,
still-defective render in both cases, same race condition as ep22 — a
follow-up message explicitly superseded the earlier send each time). Ep24:
the tiger-stripes segment had the tiger almost fully hidden behind
foreground foliage; fixed via clip splice, re-verified clean, recompressed
(53.2MB → 41.7MB). Ep25: the lightning segment was ~5s of near-solid black
(a 3s override clip gets *slowed*, not looped, to fill the segment window —
confirmed by reading `_build_override_clips` in `topic_footage.py`), fixed
by compositing real storm atmosphere with the flash clip at natural speed;
and the "Neptune and Uranus" payoff line was rendering recognizable Earth
and then the Moon — no real ice-giant footage exists in the Pexels catalog
under any tried term, so this was replaced with a stylized
hand-holding-Earth-against-a-large-blue-sphere clip that reads as an
explicit scale comparison rather than as wrong-but-confident Earth footage.
Full detail in `episode_log.csv` rows 24/25. **Both approved by the owner
2026-08-07** ("שתיהם מאושרים") — confirmed live titles top out at "Facts 21"
before recording approval, so ep24/ep25's current "Facts 22"/"Facts 23"
titles need no retitling this time. Awaiting the 16:30/22:30 publish jobs.

**Reconfirmed this session: Pexels search-result ordering is not stable
between calls of an identical query, even minutes apart** — this is now the
second session in a row where a fresh re-search of the exact term used in a
defective render returned a completely different top-3, none showing the
defect, which would have produced a false all-clear. The only reliable check
is extracting frames directly from the actual cached `vid-*.mp4` files
already present in the specific task directory being fixed, never a fresh
re-search assumed to still correspond by index.

**Same-morning correction — title numbers synced to what's actually live on
YouTube.** Owner asked to sync video numbers to the real channel state.
Pulled the actual upload playlist via the Data API (23 videos) rather than
trusting this file: the highest "Facts N" title that actually exists live
is **"Facts 19"** (ep20's mislabeled title — see above), and no video is
titled "Facts 20" or "21" yet. Ep22/ep23's `metadata.title` (the field
`upload_video.py` actually reads and uploads, not just the internal CSV
episode key) were retitled to **"Facts 20"** and **"Facts 21"** so the real
on-screen sequence continues 19→20→21 with no gap once approved — no
re-render needed, the episode number was never burned into any video frame,
only into the title/metadata. **The internal build-order episode key (22,
23 in `episode_log.csv`) is intentionally left unchanged** — that's a
durable ledger of build order including stories and dropped episodes, which
has never matched the viewer-facing "Facts N" sub-sequence 1:1 (e.g. ep17
and ep19 are stories with no "Facts N" title at all). **Going forward: before
titling any new facts episode, check the actual live channel for the
highest existing "Facts N" title rather than incrementing the internal
episode key** — they can and will drift apart again after any manual-upload
mislabel.

**The moa story (§7a) is script-locked and demo-verified, but NOT currently
rendered as a file** — the demo render itself was cleaned up after the owner
reviewed it, only the AI clip survives. Re-rendering is fast (script,
fact-check, footage terms and the AI clip are all already done, nothing to
redo) — from repo root:
```
uv run python docs/skill/story_episode.py \
  --story-file docs/skill/story_moa_lead.txt --episode <real_number> \
  --series-name "Random But True" \
  --title "Random But True: The Bird With No Wings At All" \
  --target-seconds 58 \
  --from-dry-run docs/skill/plans/locked_scripts/moa_locked.json \
  --segment-terms '{"0": "extinct bird forest", "1": "new zealand fern forest", "2": "misty forest floor mysterious", "3": "emu close up", "4": "coastline aerial forest ocean", "5": "forest fire burning", "6": "extinct bird forest", "7": "new zealand fern forest"}' \
  --segment-clips '{"0": "storage/ai_clips/moa_test.mp4", "6": "storage/ai_clips/moa_test.mp4"}' \
  --threads 4
```
Swap in the real episode number when it's actually story's turn next — the
`<real_number>` above is a placeholder, not the number to log it under.
**Caveat:** `storage/` is gitignored (same as every credential), so
`storage/ai_clips/moa_test.mp4` only survives if this exact environment
persists across sessions, not on a genuinely fresh clone. If that file is
missing when this is next needed, the locked script above is still valid —
just regenerate the one clip per `docs/skill/ai-footage-fill/SKILL.md`
(~$3, ~2 minutes) using the exact moa prompt logged in §7b below, then
re-run the render command above once it exists again.

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
  structure (post-specific / niche / broad), applied by hand at publish time
  because `generate_social_metadata` itself only emitted 3 flat tags then.
  **That code fix landed 2026-08-02** (see §5 below) — every episode built
  from now on gets 12 tiered tags automatically, no more hand-editing needed.
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

## 2f. Random But True Facts 11 — published 2026-08-01, results pending

First real test of §5's two untested hypotheses: cut to **25.7s** (well inside
the 25-30s target, well under the usual 50-60s) and the hook **opens directly
on the frog's face in the water**, no scene-setting line before the visual.
Topic: frog biology (skin breathing, third eyelid, eyeball-assisted
swallowing) — picked from §5a's unused-category shortlist (bat now used in
Facts 10, so frog was next).

**Planned facts were glass frog, wood frog (freeze-survival), and poison dart
frog — none of them survived footage probing.** Every specific-species query
(`glass frog transparent`, `poison dart frog colorful`, `wood frog winter
snow`, `red eyed tree frog`) returned the same two generic clips (a pond frog
floating, a frog on a lily pad) or, for `wood frog winter snow`, a literal log
in snow (word collision on "wood"). Same trap as sloths/wombats, now confirmed
for frogs as a genus, not just specific rare species. Facts were rewritten
around what the two real clips actually show — ordinary frog biology instead
of the exotic species — rather than rendering with a known-bad match.

**`refine_hook()` produced a near-duplicate of fact 1 in the list format, not
just the story format.** §7a documented this failure mode for
`story_episode.py` and explicitly disabled the call there; this is the first
confirmed case of the same failure in `viral_episode.py`'s list flow. The
auto-generated hook ("Frogs breathe entirely through their skin, drinking
oxygen straight from water.") was nearly word-for-word fact 1 ("Frogs breathe
right through their skin, absorbing oxygen straight from the water.") spoken
back to back. `_too_similar()` exists in `viral.py` but evidently didn't fire
here, or isn't wired into `refine_hook`'s own gate the way it is in
`build_story_script`. Fixed by passing `--hook` manually (skips
`refine_hook()` entirely, same escape hatch the story flow uses by design).
**Worth checking `viral.py`'s `refine_hook` similarity gate against
`_too_similar()`'s threshold** — this may be a real bug, not a one-off.

**Channel owner feedback after publishing the 3-fact/25.7s cut: it didn't
work, revert to the standard 6-fact recipe.** Rebuilt as 6 facts (added: eyes
on top of the head letting a frog see while submerged, the drinking-patch
skin-absorption fact, and the "a group of frogs is an army" collective noun).
Also tightened the third-eyelid fact's wording — the first draft implied frogs
"hunt" underwater with it, but frogs mainly catch prey via tongue-flick at the
water's edge or on land. **So the 25-30s/open-on-image experiment from §5 is
inconclusive from one data point** — do not treat this single owner reaction
as a verdict on short-form vs. long-form generally; it may have been this
specific cut, topic, or hook rather than duration itself.

**A stock-footage pool can contain a bad clip that recurs across every query,
not just a specific search term.** A third real Pexels clip for this
account's frog coverage — a frog barely visible under thick pond algae —
surfaced in the `frog eye close up` pool at the 3rd-candidate position
(`probe_footage.py --per-term 2` only shows the top 2, so it was invisible
during probing). It then showed up for **two different segments** despite
using different search terms, because `download_segment_materials` pulls 3
clips per segment and both segments' term happened to include it in their
pool. Probing more candidates (`--per-term 3`) would have caught this, but
even then — this account's frog coverage is genuinely only 3 clips total, one
of them weak, and no search-term rewording avoids it since it appears in
nearly every frog query's top-3. Accepted as a minor, known limitation rather
than blocking further (2 brief cuts out of 55s), same class of issue as the
sloth/wombat gaps.

**A caption anomaly is not automatically a whisper bug — check the render's
own logged script before diagnosing, not an earlier dry-run's.** The 6-fact
render's fact 6 ended in the awkwardly-phrased "...goes by that fierce
military title." The word "title." burned into the caption looked exactly
like the `condition_on_previous_text` hallucination class already documented
above (a plausible-sounding word substituting for real speech at a segment
boundary). It was diagnosed as exactly that, "fixed" by hand-editing the
`.ass` overlay to replace it with reconstructed words ("unit in the wild")
matching a *different, earlier* generation of fact 6 seen in that episode's
own dry-run log — and re-burned locally via `viral.burn_overlay`'s ffmpeg
command (no TTS needed, since `combined-synced.mp4` + `overlay.ass` +
`audio.mp3` all survive in the task dir). Caught before delivery by grep-ing
this specific render's own `fact:` log lines and `viral-result.json`, which
both confirmed "title." was the model's actual chosen wording, correctly
transcribed — not a transcription error. The edit was reverted before
sending. **Net lesson: local ASS re-burn (no API calls) is a legitimate,
fast way to patch a genuine caption bug without a full re-render — but verify
the anomaly against that exact render's own script log first, since every run
regenerates fresh text and an earlier run's wording is not evidence of what
this run's audio actually says.**

**Gemini's free-tier TTS quota (`gemini-2.5-flash-tts`) hard-caps at 10
requests/day and was exhausted mid-session** after repeated re-renders across
Facts 11's two format attempts plus the Ferrari and pizza episodes earlier the
same day. `RESOURCE_EXHAUSTED` on `generate_content_free_tier_requests`,
`GenerateRequestsPerDayPerProjectPerModel-FreeTier`, quota value 10. The
API's `retryDelay` field said 49s, which is misleading for a *daily* quota —
do not trust it as an actual reset time. **This blocks any further new
narration generation for the rest of the day** (existing renders can still be
locally re-burned/re-encoded/compressed without hitting this). Flag it to the
user early if the day's work involves more than a handful of full renders;
enabling billing on the Gemini API key is the only way around it, same
constraint already hit once today for image generation (see the pizza
episode's Picsart/Nano-Banana credit conversation).

**With Gemini TTS quota exhausted, the fallback of passing a plain
`--voice-name` (e.g. `en-US-AriaNeural`) to route around `gemini:`-prefixed
voices to `edge_tts` was tried and also failed in this remote session** —
`edge_tts stream timed out after 30s`, three retries, all timed out. This is
the exact WebSocket-blocked-in-some-sandboxes limitation SKILL.md's Viral
Episode Pipeline section already warns about (Edge TTS's `WordBoundary` needs
a WebSocket some sandboxes block) — now confirmed to apply to *this*
environment specifically, not just a theoretical caveat. **Net effect: with
Gemini's daily TTS quota gone, there was no working TTS path left in this
session at all** — not just Gemini, but also its documented fallback. If this
happens again: check whether the *current* remote environment blocks
`edge_tts`'s WebSocket before assuming the voice-name workaround will save a
render; it may not, and the two failures compound to a hard stop for new
narration until either Gemini quota resets, billing is enabled, or a
different environment (e.g. the user's own machine, which is what this
skill's `mpt_agent.py` path targets by design) is used instead.

No retention/view numbers yet.

## 2g. Random But True Facts 13 (ocean) — published 2026-08-02, results pending

Built from the ep12-18 content calendar (§5, three-criteria framework),
question-form hook per the diversity fix below: "What if the strangest thing
in the ocean isn't even alive?" 6 facts, completion-compulsion structure —
the brine-pool/underwater-lake fact (the single most surprising one) held for
last, with the hook and outro both referencing it so leaving early costs the
viewer the payoff.

Two footage-mapping bugs caught and fixed before rendering (source:
`docs/skill/plans/build_calendar.py`'s draft `segment_terms`, not yet
probed):
- Segments 0/1/2 (hook + facts 1/2) all shared the identical term "deep ocean
  underwater dark" — adjacent-repeat stutter risk. Diversified to "deep ocean
  underwater dark" / "deep sea trench dark blue" / "whale underwater".
- The payoff fact (brine pools) was mapped to "whale underwater" — a visual
  non-sequitur for a fact about underwater lakes/shorelines. Reassigned to
  "ocean waves aerial drone", which echoes the fact's own "coastlines and
  waves" language.
- Probed and **rejected** "underwater brine pool lake" as a search term
  outright — Pexels returns generic aquarium content, not real brine pools.
  Same class of gap as sloths/wombats/glass-frogs: some real phenomena simply
  have no matching stock footage in this account's tier, and the fix is to
  pick a search term for the *visual echo* of the fact rather than a literal
  (and unfilmable) match.

Render was 58.78s / 52.2MB, over Telegram's 50MB limit — compressed locally
via ffmpeg (`-c:v libx264 -b:v 5500k -maxrate 6000k -bufsize 10000k -preset
medium -c:a aac -b:a 128k`) to 36.3MB, one frame re-verified post-compression
to confirm no visible quality loss. Delivered via `send_to_telegram.py` plus
the script sent as a separate Telegram text message, per the established
two-message pattern.

No retention/view numbers yet.

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

**LLM PROVIDER OUTAGE, 2026-08-04 — survived, and the fixes are permanent.**
Gemini returned `503 UNAVAILABLE` ("experiencing high demand") for hours.
Three separate lessons came out of it, all worth keeping:

**1. A 503 is MODEL-specific, not key-specific. Change the model, not the
key.** The owner supplied a fresh API key mid-outage; it produced byte-identical
errors, because the overload is on the model. Diagnostic that actually works:
list the models the key can reach (`GET /v1beta/models`) and test candidates
until one returns 200. `gemini-3.5-flash-lite` was dead while
`gemini-3.1-flash-lite`, `gemini-flash-latest` and `gemini-3-flash-preview` all
answered instantly. Fix was one line in `config.toml`. **Do not swap keys to
chase a 503** — and note the old key reached those same working models, so the
key swap would have achieved nothing. (Separately: `gemini-2.0-flash` returns
429 RESOURCE_EXHAUSTED, a different failure — quota, not overload.)

**2. `viral_episode.py` was making an LLM call whose result it threw away.**
The audio stage shells out to `cli.py`, and `task.py` only skips
`llm.generate_terms()` when `video_terms` is non-empty. In synced mode those
terms are never used (each segment gets its own, and `--stop-at audio` never
downloads footage) — but the call still happened, and during the outage it
killed renders that were otherwise completely fine: script written, TTS
working, footage pinned. Fixed by passing `--video-terms` explicitly in
`generate_audio_only`. This removes one pointless round-trip from **every**
render, outage or not.

**3. `--pre-written` is the escape hatch when the text model is down but TTS
is up.** Those are independent services and they fail independently — TTS was
healthy the entire time. The flag makes `viral_episode.py` treat each line of
the facts file as finished spoken copy and skip the LLM entirely. Facts 18 was
built this way, hand-written end to end. **When using it, the facts file must
contain readable finished sentences, not the usual model-directed notes like
"keep this LAST".** Metadata also degrades in this mode
(`generate_social_metadata` falls back to a heuristic that dumps the whole
script into the caption), so title/caption/tags need hand-writing too.

**Story-format test integrity, same day.** The dollar story first rendered at
74.7s. Ferrari was 55.8s and nothing on this channel has been tested past 63s.
Shipping it long would have confounded the very thing it exists to measure —
whether stories outperform facts — so it was trimmed to 48.2s by cutting the
one beat that merely restated an earlier point. **When an episode's purpose is
to test variable X, do not let variable Y drift at the same time.** Also
caught pre-render: the generated script called "thal" a *mountain pass* (it
means *valley*), which was both wrong and a leak of the payoff one beat early.
Both fixes locked with `--from-dry-run`.

**Evening report 2026-08-03 — two measurement findings that change how to
read this channel.** First successful firing of the session-bound routine.

**FINDING 1: the Analytics API is not just lagged, it is FROZEN between
finalised days — do not use it for anything recent.** The 20:00 pull
returned byte-identical numbers to the 09:00 pull: all 14 videos, same view
counts, eleven hours apart. Not one view moved on a live channel, which is
impossible. The Analytics API serves finalised daily snapshots, so "last 28
days ending today" really means "through roughly two days ago". **For
anything published in the last ~48h, use the Data API's
`videos.list?part=statistics` instead** — that returns live view/like/comment
counts (it is what Studio shows). The evening report now pulls both: Data
API for current counts, Analytics API for retention on older videos. Getting
this wrong would mean reporting a day-old episode as having zero traction
when it actually had a thousand views.

**FINDING 2: like-rate is a usable same-day proxy for retention, which the
Analytics API cannot give us for two days.** Ranking every episode by
likes/views lines up strikingly well with the retention we do have:

| episode | views | likes | like-rate | known retention |
|---|---|---|---|---|
| Facts 4 | 1,161 | 43 | **3.70%** | **81.6%** (best ever) |
| Facts 6 | 903 | 28 | 3.10% | 42.2% |
| Facts 5 | 1,029 | 26 | 2.53% | 42.2% |
| Ferrari (story) | 518 | 12 | 2.32% | pending |
| Facts 13 ocean | 599 | 13 | 2.17% | pending |
| Facts 10 bats | 916 | 18 | 1.96% | 52.0% |
| Facts 11 frogs | 866 | 16 | 1.85% | pending |
| Facts 12 strength | 1,123 | 19 | 1.69% | pending |
| Facts 9 (short) | 586 | 3 | **0.51%** | 48.4% |
| Facts 8 (short) | 26 | 0 | 0% | 34.4% |

Facts 4 tops both lists; the short-format episodes sit at the bottom of
both. Treat like-rate as a leading indicator to act on the same day, then
confirm with real retention when it lands — **but do not treat it as
proven**: n is small and Facts 10 (1.96% like-rate, 52.0% retention) already
sits out of order versus Facts 5 and 6. It is a hint, not a law.

**Reach and resonance are not the same thing, and views alone mislead.**
Facts 12 took the most views of the week (1,123) *and* the worst like-rate of
the batch (1.69%). Judging it on views would have marked it the week's
winner; on engagement it is the weakest recent episode.

**Not concluded, deliberately: whether the ocean topic shift hurt.** Facts 13
(599) vs Facts 12 (1,123) invites blaming the move off animals — but they
published at 18:10 and 22:00, different slots, so time-of-day is an
unresolved confound. Ep16 (dogs, i.e. back to animals, in the same 22:30
slot as ocean) is the cleaner comparison; read it tomorrow before drawing
any topic conclusion.

**First-story verdict is NOT in yet.** Ferrari at 518 views in 3.6h is the
fastest start measurable here, but Shorts front-load views so an early-hours
pace always flatters against an older video's lifetime average. Comparing
144 views/hour (Ferrari, 3.6h) to 49/hour (Facts 12, 23h) is not
like-for-like. Wait for the 24h mark before deciding anything about the
story format — and specifically before building Inky.


**THE DAILY ROUTINE, adopted 2026-08-03, architecture updated 2026-08-04.**
The owner set a fixed operating rhythm and asked for it to run on scheduled
wake-ups. Five Routines now exist (created via `create_trigger`, **bound to
the persistent session** — see the failure below for why that is not
optional). Their prompts still begin by re-reading these docs, because
context gets compacted:

| Israel time | UTC cron | Job |
|---|---|---|
| 09:00 | `0 6 * * *` | Build the day's TWO episodes, send both + full upload kits to Telegram, ask for approval. **Uploads nothing.** |
| 13:00 | `0 10 * * *` | Check Telegram inbox. Apply corrections if any; **record approval** into `storage/todays_uploads.json` if approved; nudge and stop if no reply. **Uploads nothing** (changed 2026-08-04, see below). |
| 16:30 | `30 13 * * *` | Read `storage/todays_uploads.json` — if the 16:30 slot is approved and not yet published, upload it live as public **right now**. Otherwise skip and notify. |
| 22:30 | `30 19 * * *` | Same as 16:30, for the 22:30 slot. |
| 20:00 | `0 17 * * *` | Generate + publish `docs/skill/plans/generate_dashboard.py`'s HTML dashboard (same URL every night), send one short Telegram digest pointing at it plus the key takeaway, log conclusions to this file, revise the plan if the calendar is running dry. |

**Direct-publish-at-slot-time, not `--publish-at` scheduling (owner
request, 2026-08-04):** "I'm still thinking we should post in the same time
we want it. Not a scheduled post." Until this point, 13:00 called
`upload_video.py --publish-at <UTC time>`, which uploads immediately as
`private` and lets YouTube itself flip it public at the given timestamp —
technically correct, but not what the owner pictured when they said "upload
at 16:30." Replaced with real wall-clock publishing: 13:00 now only writes
approval state (`storage/todays_uploads.json`, gitignored via `/storage/`,
one day's data — `{"date", "slots": {"16:30": {"approved", "result_json",
"episode", "published"}, "22:30": {...}}}`), and two new Routines fire at
the literal slot times and upload with `--confirm --privacy public` (no
`--publish-at`) only if that slot is approved for today and not already
published. The hard rule carries over unchanged: no slot is ever uploaded
without the owner's prior explicit approval of that exact rendered
version — the two new jobs check `approved: true` before doing anything,
and skip with a Telegram notice otherwise. `upload_video.py --publish-at`
itself was not removed — still there for genuine one-off scheduling, just
no longer what the daily Routines use.

**FAILURE — the first 13:00 firing did nothing, 2026-08-03. Root cause: the
Routines were created with `create_new_session_on_fire: true`.** The fired
session came up with `/home/user` empty — no repo, no clone anywhere on
disk. It correctly refused to act and reported clearly, and took no
irreversible action, but the whole job was a no-op.

**The deeper reason fresh-session mode can never work for this channel, and
the thing to actually remember:** even if the repo *had* cloned, the job
would still have failed, because **every credential this pipeline needs is
gitignored by design** — `config.toml` (Gemini + Pexels keys, Telegram bot
token and chat_id), `docs/skill/youtube/client_secret.json`, and
`docs/skill/youtube/token.json`. A fresh clone reaches none of them, and
they cannot be recovered from git. So a fresh-session Routine could not
generate a script, fetch footage, message Telegram, or upload — it could
only read the docs. The mode was chosen for "robustness against this
session dying", which had the trade-off exactly backwards: it traded a
*possible* future failure for a *guaranteed* immediate one.

Fixed same day by deleting all three and recreating them **session-bound**
(the default mode — omit `create_new_session_on_fire`), so each firing
resumes this session, which holds both the repo and the gitignored
credentials. Cost of the fix: session-bound Routines cannot carry
completion push-notifications (the server rejects `notifications` for
them). That is an acceptable loss — every job's real deliverable goes to
Telegram anyway, which is the channel the owner actually reads.

**Generalised rule: a scheduled job that needs credentials must run
somewhere those credentials already exist.** Before choosing fresh-session
mode for anything here, check what the job needs to touch; if the answer
includes any gitignored file, fresh-session is wrong. Today's two already
scheduled uploads were unaffected — `status.publishAt` lives on YouTube's
servers, so once a video is scheduled it publishes regardless of whether
any session is alive (verified via the API after the fix, both still
private with correct publishAt timestamps).

Owner's words: "אתה קם ב 9 בבוקר כל יום ושולח לי לטלגרם 2 סרטונים שעתידים
להתפרסם ב 16:30 וב 22:30 (לאחר אישור שלי) ואת ריט העלאה... בערב באזור 20:00
כל יום אתה שולח לי את הלוז המעודכן לכל השבוע... המטרה שלנו ביחד היא להביא
לערוץ יוטיוב הכי מוצלח שאפשר."

Why 13:00 and not later: it leaves 3.5 hours before the 16:30 slot, so a
correction can actually be rebuilt and re-sent rather than rushed. **An
unapproved video is never uploaded, even if the slot is about to pass** —
missing a slot is recoverable, publishing something the owner didn't approve
is not.

**⚠️ CRON IS UTC AND DOES NOT FOLLOW ISRAELI DST.** These five expressions
are correct for IDT (UTC+3, ~late March to late October). When Israel falls
back to IST (UTC+2) in late October, **every job will fire one hour late in
local terms** (09:00 becomes 10:00, 16:30 becomes 17:30, etc). Fix then by
shifting each cron back an hour (`0 7`, `0 11`, `30 14`, `30 20`, `0 18`) via
`update_trigger` — do not delete and recreate, that loses the run history.

**Both publish slots are genuinely well-placed for a US audience**, checked
rather than assumed: 16:30 IDT = 09:30 ET / 06:30 PT, and 22:30 IDT = 15:30
ET / 12:30 PT. Both sit inside the guide's Rank 6 window (06:00-22:00 US
time), which the old Israel-anchored calendar did not. This resolves the
"calendar needs re-anchoring to US hours" gap flagged in
`shorts_growth_guide.md` Rank 6.

**THE UPLOAD-FLOW RULE — sequencing is deliberate, never random.** Owner:
"אנחנו נעלה גם עובדות בפורמט של ה 6 עובדות וגם סיפורים אבל צריך שתהיה זרימה
בין העלאות ולא להעלות בצורה רנדומלית." Concrete and checkable:

1. **Stories run roughly 1 in every 4-5 uploads, never back-to-back.** The
   6-fact format is the channel's identity and its measured performer;
   stories are the change of pace, not the new default. Revisit this ratio
   once the first stories have real retention data — not before.
2. **Never two consecutive uploads from the same topic category.** Rotate
   across animals / ocean / food / everyday objects / cars / people.
3. **The two same-day slots must differ on at least one axis** — format or
   category. Two animal-facts episodes on the same day is exactly the
   "random" feel the owner is asking to avoid.
4. **Check `episode_log.csv`'s `key_subjects` column before finalising a
   topic.** Never reuse a specific subject (a species, a brand, a person)
   that appeared in the last 5 episodes. This is the whole reason that
   column exists.

**Known constraint at adoption time: 2 videos/day burns the calendar in ~2
days.** After the Ferrari story publishes, only 4 episodes remain (14 Inky,
15 pizza, 16 dogs, 18 objects) — and 14 is deliberately on hold pending
Ferrari's numbers, while 15 is flagged weak-as-built. That is roughly two
days of runway against a plan that consumes two per day. The §7 "propose a
new plan at ≤2 remaining" threshold is therefore already effectively met;
a fresh slate of topics and story leads is needed immediately, not later.

**Standing risk, already documented in §7, now directly live:** fully
automated daily templated uploads sit in the profile YouTube scrutinises
under its inauthentic / mass-produced content policy — a real risk given
monetisation is the goal. Two mitigations are structurally in place: every
single upload passes through the owner's explicit approval (nothing
publishes unreviewed), and topics/hooks are varied by the flow rule above
rather than templated. Worth revisiting if the channel ever gets a policy
warning.

**Story-format sequencing, decided 2026-08-03** (owner: "I have all the video
I want till 13. Now let's update our videos plan and think about the stories
part — I still didn't upload the stories"):

Facts 1-13 are all confirmed live on the channel (per the owner's Studio
screenshot). The Ferrari/Lamborghini/Pagani story episode, by contrast, was
fully built back on 2026-08-01 but **never actually uploaded** — meaning the
channel has zero real retention data on the story format at all, despite the
three-criteria framework (§5) predicting stories should score higher on
completion compulsion than facts lists. That's a hypothesis no episode has
tested yet.

Fixed and re-delivered it same-day: retitled to the branded
`Random But True: The Insult That Built Lamborghini` (was still under the
old "Rival Origins" working title), regenerated hashtags through the now-live
3-tier formula (was still on the old 3-flat-tag output), compressed
52.86MB→33.4MB for Telegram's limit, verified frames post-compression, wrote
a fresh pinned comment, delivered with script as a separate message.

**Decision: upload this NEXT, ahead of anything still in the Facts 14+
build queue, regardless of its "episode 17" slot in the calendar CSV.** It
costs nothing to prioritize — it's already fully rendered — and it's the
only way to get a real data point on whether stories actually outperform
facts lists for this channel, rather than continuing to guess from the
framework's reasoning alone. **Do not build or upload Inky (the second
planned story, was ep14) until Ferrari's real numbers are in** — building a
second unproven-format episode before the first one reports back would
repeat the same mistake as the original 3-fact-format experiment (shipped
before checking whether short format worked, had to be reverted). Given the
Analytics API's ~24-48h processing lag (see the lesson below), expect
Ferrari's real retention to be readable roughly 1-2 days after the owner
uploads it to YouTube.

**Update, same day: uploaded via the API rather than manually, and
scheduled rather than published immediately.** Owner asked for scheduled
upload support and to schedule this specific video for 16:30 Israel time.
Added `--publish-at` to `upload_video.py` (RFC3339 UTC timestamp) — checked
the actual API requirement before implementing rather than assuming:
`status.publishAt` requires `privacyStatus: private` at upload time, and
YouTube itself flips the video to public at that timestamp, confirmed via
search, not guessed. The script forces `privacy_status` to `"private"`
whenever `--publish-at` is set, regardless of what `--privacy` says.
Uploaded with `--publish-at 2026-08-03T13:30:00Z` (16:30 IDT, confirmed
Israel is UTC+3 in August and that this was still ~8 hours in the future at
upload time) — video id `glOoMgY_--c`, currently private, will auto-publish
at that timestamp. First video this channel has ever uploaded through the
API instead of by hand.

**Real YouTube Analytics access landed 2026-08-03** — `docs/skill/youtube/`
(setup detailed in §8) finally replaced the stale manual-screenshot numbers
in §2 with a live per-video pull. First real read, 14 videos, 28/90-day
windows identical (i.e. this is literally every video published so far):

- **Facts 4** (wombat/otter/cow/crow/octopus/dolphin) is the standout: 81.6%
  average-view-percentage, far above everything else. Worth studying what's
  different about its hook/pacing/footage.
- **AI Unfiltered is confirmed the weakest topic**, not just suspected: 131,
  34, and 11 views across its three episodes. Deprioritize AI topics.
- **The long-vs-short length question (§2d, previously unresolved) has a
  real-data answer now, though the short-format sample is thin (n=2):**
  long format (6-fact, ~52-58s) averaged 45.8% retention / 724 views across
  9 videos; short format (3-fact, ~25s) averaged 41.4% retention / 275 views
  across Facts 8 and 9. Long format wins on both axes. This matches the
  owner's own qualitative call after the 3-fact experiment ("the recipe
  didn't work, revert to 6") — now with numbers behind it. Keep 6-fact/50s+
  as the default.
- **Facts 8 vs Facts 9 is a same-format natural experiment**: identical
  3-fact/~25s format, but Facts 8 (axolotl/mantis shrimp/cuttlefish) got 23
  views while Facts 9 (hedgehog/peacock/seahorse) got 527. Confirms topic
  choice, not format, drove that gap.

**Lesson learned the same session — do not misread Analytics API processing
lag as "not uploaded."** The initial pull showed no data at all for Facts
11, 12, 13, or the Ferrari story episode, which was reported to the owner as
"these may not be uploaded yet." Owner corrected this with a YouTube Studio
screenshot: 11/12/13 are live and performing well (Facts 12: **1K views in
10 hours**, notably faster than anything else in the dataset took days to
reach). The real cause: **the YouTube Analytics API does not populate a
video's row until roughly a day or more after upload** — Facts 11/12/13 were
all under 24h old at pull time. Studio's own view/like/comment counts are
visible immediately; the Analytics API's per-video breakdown (views,
averageViewPercentage, averageViewDuration) is what lags. **Before reporting
a video as "missing/not published" based on an Analytics API pull, check its
upload age first** — anything under ~24-48h old may simply not have
propagated yet, distinct from actually not existing. Facts 1, 2, 7, and the
Ferrari/Lamborghini story episode are still unconfirmed either way (they
predate the lag window, so if published they should have appeared) — owner
is checking further down the Studio content list.

**Two follow-up fixes to the hashtag work, same day (2026-08-02):**

1. **Caption gets only 3 hashtags, not all 12.** After the 3-tier fix below
   shipped, the owner asked for episodes 12/13's tags refreshed. Sending the
   full 12-tag list appended to the caption was wrong — Rank 5 already says
   "3 subtle hashtags in the description," and 12 there reads as spam. Fixed
   in `send_to_telegram.py`: added `CAPTION_HASHTAG_COUNT = 3`;
   `build_caption_with_hashtags` now slices `hashtags[:3]` instead of the
   full list. The full 9-12 still go, unabridged, to the separate "tags:"
   Telegram message meant for YouTube Studio's Tags field — that field is
   supposed to hold all of them, only the caption needed trimming.
2. **Manual/ad-hoc Telegram sends must follow the same one-thing-per-message
   rule the pipeline already uses, no exceptions.** The manual delivery of
   ep12/ep13's refreshed tags crammed intro text + the `#`-caption version +
   the plain-Tags-field version into a single message per episode. Owner:
   "why I ask you to send separate messages in Telegram because I need to
   copy it... if you send all in one message, it's very hard hard for me to
   copy." `send_to_telegram.py`'s `send_labelled_field` already does this
   correctly (label message, then content-only message) for scripted
   deliveries — the mistake was only in a hand-rolled `curl` send that didn't
   reuse that pattern. Documented as a hard rule in `SKILL.md` 8d so it isn't
   repeated: every copyable thing sent by hand gets its own label message and
   its own content message, never bundled with anything else.

**3-tier hashtag formula, implemented in code 2026-08-02** (owner restated the
guide's Rank 7 rule verbatim and asked to make sure the pipeline actually uses
it, not just documents it as a gap):

> Using the correct tag structure helps YouTube feed your short to the exact
> audience most likely to watch it through to the end. Apply 9 to 12 total
> tags split into three categories: (1) Post-Specific Tags (3-4) — describe
> the exact video content; (2) Niche-Specific Tags (3-4) — broad category
> tags; (3) Broad Viral Tags (3-4) — mass-reach tags.

This had been sitting in `shorts_growth_guide.md` as Rank 7 (7.0/10) since the
guide research pass, flagged as a gap: the pipeline only emitted 3 flat,
untiered hashtags, and Facts 10 worked around it with a hand-written tag list
at publish time rather than a pipeline fix. Implemented for real this time in
`app/services/llm.py`:
- `SOCIAL_PLATFORMS["youtube_shorts"]["hashtag_count"]` raised from 3 to 12
  (4+4+4 tiers). Other platforms' entries (`tiktok`, `instagram_reels`,
  `facebook_reels`) left untouched — this channel only publishes to YouTube
  Shorts, no reason to change behavior nobody uses.
- `build_social_metadata_prompt` now appends an explicit tier instruction
  (post-specific / niche-specific / broad-viral, in that order, 3-4 each)
  whenever a platform's `hashtag_count >= HASHTAG_TIER_MIN_COUNT` (9) — kept
  conditional so low-count platforms don't get forced into padding 3-5 tags
  into three artificial buckets.
- `DEFAULT_SOCIAL_HASHTAGS` (the no-LLM fallback) extended from 8 to 12 items
  so the fallback path also satisfies the new count; it stays generic/flat
  since the fallback has no per-episode topic to draw post-specific tags from.

Verified live (see `shorts_growth_guide.md` Rank 7 for the exact output).
Both `viral_episode.py` and `story_episode.py` already call
`generate_social_metadata(platform="youtube_shorts")`, and
`send_to_telegram.py` already forwards the full hashtag list to both the
caption and YouTube Studio's separate "Tags" field — so this took effect for
every future episode with no other file changes. Owner asked for episodes 12
and 13's tags specifically regenerated and sent to Telegram right after this
landed, so those two already-published episodes got new 12-tag sets too
(their `viral-result.json` `metadata.hashtags` were updated to match); no
other already-published episode has been retroactively re-tagged.

**Three-criteria niche/episode-selection framework, adopted 2026-08-02**
(channel owner supplied it from an external source, with a timestamped
breakdown, and asked to fix episodes 13+ if the current slate didn't already
satisfy it — full CSV lives at `docs/skill/plans/content_calendar_ep12_18.csv`,
per-episode assessment in its `criteria_fit` column):

1. **Universal Relatability** — content must be instantly understood by
   anyone on Earth, no prior knowledge or language required (food, animals,
   cleaning/restoration are the framework's own named examples).
2. **Emotional Hook / Absurdity** — the viewer's reaction is "why would they
   put this much effort into something so small" — a creator visibly
   over-investing psychic effort on an everyday goal.
3. **Completion Compulsion** — a clear statement in the first second that
   creates a commitment to see the outcome, driving retention toward 80%+ on
   60s Shorts.

**Honest fit assessment, not uniform compliance — two of the three criteria
behave very differently for this channel:**

- **#1 is already satisfied.** Ocean, food, dogs and everyday objects are
  all inside the framework's own named categories; no change needed here.
- **#2 is structurally unreachable for the facts format, and this document
  says so rather than faking it.** The criterion describes a creator
  visibly toiling on screen; this is faceless stock-footage narration, with
  no creator to display effort. `SKILL.md`'s Shot Pacing section already
  reached the same conclusion independently, unprompted by this framework
  ("do not fabricate a fake before/after for a facts video — the mismatch
  reads as filler"). **The story format is the one place it transfers**,
  because the absurd effort can belong to the *subject* rather than a
  creator — Inky the octopus mounting a patient escape for the simple goal
  of reaching the sea is exactly this shape. Ep 14 (Inky) is flagged in the
  CSV as the single best-fit episode across the whole slate, hitting all
  three criteria at once where the facts episodes hit at most two. This is
  a real argument for a higher story ratio than the 3:1 originally proposed
  two sections below — but do not flip on an untested framework alone; it's
  a hypothesis to weigh against ep 14's actual retention once published,
  same evidentiary bar as everything else in this section.
- **#3 is the real, fixable gap — and plausibly explains the 33% retention
  already logged in §3.** A 6-fact list with independent facts and a hook
  that spends the best fact immediately hands the viewer full value by
  fact 1; leaving early costs them nothing. Fixed in the CSV for eps 13, 16
  and 18 by restructuring (not reformatting): the hook now names a payoff
  without revealing it, and the single most surprising fact is moved to the
  final slot so it closes the loop the hook opened (ocean → brine pools;
  dogs → Chaser's 1,000-word vocabulary; objects → the fuel-gauge arrow,
  which is also the strongest comment-bait in the batch because it's
  immediately self-verifiable). Ep 12 shipped before this rule existed and
  is deliberately left as-is in the CSV as the **control** — compare its
  retention against 13/16/18 to see whether the restructure actually moves
  the number, since ep 13 also changes topic at the same time and so isn't
  a clean isolated test on its own; ep 16 (dogs, no topic change) is the
  cleaner second data point.

**Blending story episodes into the facts-only channel: roughly 1 story per
4 videos, animal-subject stories first** (channel owner request, 2026-08-01
— "most videos up to 11 are animal facts, I want to start mixing in stories
like the one we built, but not too sharp a transition; what should the next
videos be, and how do I combine story-format with the 6-fact format"). The
channel has been 100% animal facts through Facts 11; the one story episode
built so far (Ferrari/Lamborghini/Pagani, §7a) was a separate one-off under
its own series name ("Rival Origins"), not folded into this channel's
rhythm. Decision:

- **Facts stay the dominant format — do not alternate 1:1.** §3/§5 already
  established that topic-scattering plausibly explains the channel's original
  zero-subscriber problem (unpredictable next-video content gives nothing to
  subscribe to). A story every ~4th video keeps facts as the channel's clear
  identity while still introducing variety. Re-evaluate the ratio once a few
  stories have retention data — this is a starting point, not a fixed rule.
- **The first 1-2 story episodes should be animal/nature-subject stories,
  not a subject-matter jump like Ferrari/Lamborghini.** Introduce one
  variable at a time: format changes (list → narrative) without also
  changing topic domain, so it reads as a natural extension of "surprising
  animal facts" rather than a second, unrelated show. Candidates identified
  so far, both real and already escalating in structure: **Inky the
  octopus's 2016 tank escape** (ties back to octopus from Facts 4) and **the
  coelacanth's 1938 rediscovery** after being presumed extinct for 65 million
  years. Only branch into non-animal story subjects (Ferrari etc.) after the
  animal-subject bridge episodes are out and the format itself is validated
  with the audience.
- **Brand stories under the same "Random But True" identity going forward**
  (e.g. `Random But True: Inky's Escape`) instead of a separate series name,
  so it reads as the same channel occasionally changing gears rather than a
  spin-off. The already-published Ferrari video keeps its "Rival Origins"
  title as-is (already shipped); this naming convention applies to stories
  built from here on. The already-built Ferrari/Lamborghini/Pagani episode
  should still get used — slot it in as a story once the animal-subject
  bridge story(s) have run, not wasted.
- **Superseded by the 2026-08-01 follow-up below: topic (not just format)
  should diversify too.** The channel owner's next message clarified that
  "all the facts are still about animals, I want to vary that too" — so
  topic rotation within the numbered Facts series is now part of the plan,
  not just interleaving story episodes. Revised slate, changing only one
  variable (format or topic) per step so no single transition is sharp:

  | # | type | topic | why here |
  |---|---|---|---|
  | 12 | Facts | animal strength comparisons | still animals, keeps momentum |
  | 13 | Facts | **ocean/deep sea facts** | first topic shift — gentlest bridge, sea creatures are still "animals" but a new environment |
  | 14 | Story | **Inky the octopus's escape** | continues straight from ep.13's ocean theme; story format debuts on an already-primed topic |
  | 15 | Facts | **food** (rebrand the already-built pizza episode, §2 pending) | first fully non-animal topic, already produced |
  | 16 | Facts | dog breed temperament | back to animals — not a one-way departure |
  | 17 | Story | Ferrari/Lamborghini/Pagani | second story, format + topic diversification both established by now |
  | 18 | Facts | everyday objects or money/prices | continue the §5 topic shortlist |

  **This is a hypothesis, not proven** — animals are the only topic with any
  retention data on this channel (§3). Facts 13 and 15 are the next real data
  points on whether non-animal topics hold up here, same evidentiary status
  as the other untested items in this section.

**Hooks must be phrased as a question to the viewer, not a flat statement**
(channel owner feedback, 2026-08-01, after watching Facts 11 — "the opening
isn't good, it should start with something like 'did you know' or a
question-style opener; not always literally 'did you know', but every time
some form of question"). This **reverses** an earlier rule in this same
document and in `SKILL.md` that explicitly banned "did you know" and required
a flat declarative opener (e.g. Facts 11's actual hook: "Frogs use their own
eyeballs to swallow food.") — that rule is now wrong per direct owner
feedback and has been replaced. `viral_episode.py`'s `HOOK_PROMPT` and
`HOOK_CRITIQUE_PROMPT` (used by `refine_hook()`) were both updated to require
a question form, varying the exact phrasing across episodes rather than
reusing the same one ("Did you know...?", "Ever wonder why...?", "What if I
told you...?", "Guess what...?", etc.) while still keeping the older,
still-valid constraint: the question must name a specific curiosity gap with
a real payoff, not a vague tease. **Not yet applied to `story_episode.py`**
(its `STORY_SYSTEM_PROMPT` still explicitly bans "did you know" and expects a
statement-style shock-opener, e.g. "An archduke survived a grenade, only for
a wrong turn to get him killed.") — the owner's feedback followed a list-format
video, and a narrative hook's job (state the story's most shocking beat) may
not translate cleanly to question form. Revisit if the owner gives the same
feedback on a story-format episode; do not assume it carries over silently.

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

## 5b. Evening report redesign — dashboard (adopted 2026-08-04)

Owner: "the report you send, it's a lot of text. Maybe we can do something
nicer like HTML or suggest something else. I don't know" — left the concrete
design open. Built `docs/skill/plans/generate_dashboard.py`: pulls live
Data API view/like counts + Analytics API retention, merges with a
hand-maintained `EPISODE_META` dict (video_id → episode/topic/format — the
API has no way to know what a video is *about*), writes one self-contained
HTML file. Published via the `Artifact` tool to a stable URL, **redeployed
to the same file path every night** so the owner bookmarks one link instead
of getting a new one daily. The 20:00 job now sends one short Telegram
message (link + 2-3 sentence takeaway) instead of four long messages.

Three real bugs caught before shipping the first version, worth remembering
because they're generic mistakes, not dashboard-specific ones:
- `ROOT = Path(__file__).resolve().parents[2]` climbed to `docs/`, not the
  repo root — off-by-one on the parent count is an easy silent failure
  that still imports fine right up until a script two directories deeper
  tries to reach a sibling package. Always count parents against the
  actual file depth, don't assume.
- The Analytics API's `reports` endpoint returns a 400 (not en empty
  result) when `dimensions=video` is combined with more than one metric
  and no `sort` param — but the code was doing `.get("rows", [])` on the
  response without checking status first, so the 400 silently became "0
  rows", which looked exactly like "nothing has finalised yet" instead of
  "the query itself is malformed." Every retention pill showed "pending"
  on the first run because of this alone. Lesson: `.raise_for_status()`
  before trusting an empty collection means "no data" instead of "error."
- The initial "best retention on file" hero stat surfaced 128.8% off a
  12-view video — a real number, but statistical noise, not a signal
  worth highlighting. Added a `views >= 100` floor before a video is
  eligible for that specific highlight card (the full table still shows
  every video's real retention regardless of view count — the floor is
  only for what gets promoted to a hero stat).

**v2, same day (owner: "make the dashboard 10X better").** Rebuilt around
the questions a creator actually asks, not just a numbers list:
- **Race chart** — cumulative views over each episode's *first 5 days*,
  every line at the same age, newest episode in brand yellow, second
  newest in pink, the pack in grey. This is the single most useful chart
  on the page: it answers "is today's video tracking above or below the
  pack at the same age" the moment it's opened. Windowed to 5 days on
  purpose — a full-age axis flattened the decisive early curve into the
  corner. Because Analytics dailies freeze ~2 days behind, each line's
  final point is anchored to the LIVE Data-API count, so brand-new videos
  still show an honest trajectory (a straight line to "now" when no
  finalised days exist yet).
- **Channel views-per-day area chart** with pink markers on upload days.
- **Real thumbnails** inlined as base64 data URIs (the Artifact CSP blocks
  `i.ytimg.com`; ~6.5KB each, ~140KB total, fine under the 16MB cap).
  Private/queued videos 404 on the thumb endpoint → branded placeholder.
- **Format scoreboard** (facts vs story vs facts-short): episode count,
  median views, avg finalised retention, computed over the branded run
  only — `pre`/`AI` uploads would skew the medians.
- **Auto-computed takeaways** — leader of the week, retention record,
  story-vs-facts-median check, subscriber-conversion note. All phrased
  from the numbers; no adjective the data doesn't earn.
- Episode rows are now phone-first cards (thumb / title / numbers) that
  link to the video — no horizontal-scroll table at all.
- **Verify rendering with Playwright, not headless `--screenshot`**: the
  bare `chromium --headless --screenshot --window-size=430,...` flow laid
  the page out at a wider default width and cropped, which looks exactly
  like a horizontal-overflow bug. Playwright with a real 390px viewport
  proved scrollWidth == clientWidth. Don't chase phantom overflow from
  cropped screenshots.
- The 20:00 job MUST regenerate to the exact same scratchpad path and
  republish from it — the stable URL is bound to the file path; `--out`
  anywhere else mints a new URL and silently breaks the owner's bookmark
  (the trigger prompt now hardcodes both the path and the URL).

**2026-08-04 20:00 report.** Ep 18 published on time (16:30 IDT, 633 views
21h in). Ep 19 (dollar story) queued for 22:30 tonight — first video to go
through the new direct-publish-at-slot-time flow end to end. Ep 12 still
leads the week (1,138 views). Ep 17's retention (the story-format go/no-go
data point) is still "pending" at 28h — Analytics needs ~48h to finalise,
so no call on Inky yet; check again tomorrow evening.

**Facts-topic calendar is now exhausted.** `content_calendar_ep12_18.csv`
covered episodes 12-18; all are built. The §5a outlier-research candidate
list (dog, strength, bat, frog, sloth) is also now fully used — every one
of those has shipped. Story-side runway is fine (2 fact-checked leads ready:
D-Day crossword, moa bird), but there is currently no next FACTS topic
queued for the 09:00 build. Flagged to the owner in tonight's Telegram
digest with an ask for topics; if none arrive before 09:00, do fresh
outlier-topic research (SKILL.md step 0 method) rather than block the
build on a reply.

## 5c. Retention-first self-improvement log (adopted 2026-08-04)

Owner instruction, verbatim: "when you send me a summary, also take notes
for yourself to improve for the next videos... always self improve, it's
very important to notice the retention not only the views." Views measure
reach; retention measures whether the episode itself is good — a video can
lead the week on views (algorithm placement, luck, time of day) while
quietly being the weakest thing on the channel by retention, and vice
versa. **Every entry here must end in a concrete action for the next
build, not just an observation** — "X happened" is not a lesson, "next
time do Y because X happened" is.

**Process:** the 20:00 job appends an entry whenever a video's retention
newly finalises (crosses from "pending" to a real number). The 09:00 job
reads this section before picking topics/structure and applies at least
one open action if one is live. Entries close out (marked RESOLVED) once
a later episode actually tests the hypothesis.

**Backfilled entries, 2026-08-04, from confirmed Analytics API data
(averageViewPercentage; small-n outliers like the 12-view 129% and the
4-5 view pre-branding test uploads are excluded as noise, not signal):**

1. **Ep 4 (81.6%) vs ep 5 / ep 6 (42.2% each) — same format, same "animal
   ensemble" topic category, ~2x retention gap, still not fully
   explained.** Ep 4's hook opens on a concrete strange image stated
   plainly ("wombats produce cube-shaped droppings, and scientists needed
   years to explain it") rather than a question. This is already the
   basis of the production rule in §6 below ("open on the strange image,
   not a sentence describing it") — so the *hook-shape* hypothesis is
   captured and supposedly in use. **Open action:** the last several
   episodes (16, 17, 18, 19) all use question-form or statement-form hooks
   inconsistently without logging *why* — starting now, log each episode's
   hook shape (question vs strange-image-statement) next to its retention
   in this table once data lands, so this 2-episode comparison can finally
   grow into a real sample instead of staying anecdotal.
2. **Ep 10 bats (50%) vs ep 11 frog (38%) — both built after the
   three-criteria completion-compulsion restructure, same execution
   approach, 12-point gap.** The restructure alone is not sufficient;
   something about the species/topic itself still moves the number. Ep
   11's footage was logged at build time as the weakest-coverage batch on
   file ("generic pond/tree frog footage only — glass frog, wood frog,
   poison dart frog have no real Pexels coverage"), while bats had punchier
   individual facts (vampire bat / tequila). **Open action:** rate footage
   specificity 1-5 per episode BEFORE render (not just "probed / not
   probed" pass-fail) and log that rating here against the eventual
   retention — testing whether generic/stock-feeling footage measurably
   costs retention independent of the fact content itself.
3. **AI Unfiltered (32-35% avg across 3 episodes) confirmed as the
   channel's weakest category — RESOLVED, action already taken:**
   deprioritized since the finding, no AI-topic episode has since been
   queued. Keep it deprioritized; this is a closed loop, not an open one.
4. **Sample size discipline:** every comparison above is n=1 or n=2 per
   side. Treat all open actions as hypotheses being tested across future
   episodes, not settled rules — do not silently start treating "open on
   the strange image" as proven just because it is repeated often; it
   still only has ep 4 as direct support.

**Pending, watch for retention landing:** eps 12/13/16/18 (facts) and 17/19
(stories) all still show "pending" as of tonight — each is a real data
point for the open hypotheses above the moment Analytics finalises it
(~48h after publish). Ep 17 in particular is the channel's first-ever
story-format retention number; log it here the moment it lands, not just
in the evening Telegram digest.

**2026-08-06 20:00 report — five episodes finalized at once (11, 12, 13, 16,
17), and the clean completion-compulsion test finally lands.**

- **Ep16 (dogs, 40.41%) vs ep12 (animal strength, 40.93%, the designated
  CONTROL) is the clean, same-topic-category comparison the playbook has
  been waiting for since 2026-08-02**: completion-compulsion restructure
  (withheld payoff, hook that doesn't reveal it) with NO topic change, and
  the two numbers are statistically indistinguishable (a 0.5-point gap).
  **RESOLVED: the completion-compulsion restructure does not measurably
  move retention by itself** — at least not on this comparison, against
  the three-criteria framework's own prediction.
- This reframes ep13's standout **59.68%** (ocean, also restructured,
  second-best on the channel after ep4): since the *same* restructure
  produced nothing on ep16, ep13's real driver was more likely the ocean
  **topic** itself, not the structural fix. **Concrete action for the next
  build: stop treating the completion-compulsion restructure as a
  retention lever on its own — weight topic selection and novelty over
  hook/payoff structure**, and don't expect a future restructured episode
  to reproduce ep13's jump just because it's restructured.
- **Ep17 (Ferrari/Lamborghini story) finalized at 48.45%** — the channel's
  first-ever story-format retention number, **resolving the "first-story
  verdict is NOT in yet" flag from §5**. 48.45% sits slightly above the
  45.8% long-format facts average (§5) — a mild positive first signal for
  the story format, but n=1; keep testing as ep19/ep21 land.
- **Ep11 (frog, 40.38%) also finalized** — another mid-40s number,
  consistent with the broader pattern that most non-ep4 episodes cluster
  in the low-to-mid 40s regardless of hook shape or topic tweaks; ep4's
  81.6% remains the channel's unexplained outlier.

**Still pending as of tonight:** ep18 (everyday objects), ep19 (dollar
story, right at the ~48h edge, likely finalizes tomorrow), ep20 (human
body), ep21 (D-Day story), ep22 (pizza, published today). Log each the
moment it lands.

**2026-08-05 09:00 build — both open actions applied.** Ep 20 (human body
facts) used a deliberate strange-image-statement hook (not a question) to
grow the ep4-vs-ep5/6 comparison in item 1 above, and rated footage
specificity 1-5 per segment before delivery per item 2 (avg ~4.6/5 — see
`episode_log.csv` row 20 for the per-segment breakdown). Both are now real
data points waiting on retention to land, not just logged intentions.

**2026-08-05 owner feedback — pacing feels slow, not dramatically, but noticeably.**
Verbatim: today's viewers are impatient; the video's own footage-cut pace should
stay exactly as-is (cuts must keep following the speech, don't decouple them),
but narration and captions should run a bit faster. Implemented as a ~10%
narration speed-up (`--narration-speed`, default `1.1`, in both
`viral_episode.py` and `story_episode.py` — see their commit for why this had
to happen at the audio-file level via ffmpeg rather than through Gemini TTS's
own rate control, which the code confirms is not implemented for that
provider). Because the speed-up runs before whisper transcription, captions and
every segment's footage window inherit it automatically — the cut-to-cut rhythm
is unchanged, only the whole timeline scales down a little, exactly matching
what the owner asked for. This is now the default for every future build, no
extra flag needed. `narration_speed` is recorded in each render's result JSON
so a later retention comparison can actually test whether the faster pace
helped — treat "did pacing move retention" as a new §5c-style hypothesis once
a few episodes at 1.1x have real numbers.

**2026-08-06 09:00 build — both open actions applied again, plus a new
observation.** Ep22 (pizza) and ep23 (space) both used question-form hooks
(no deviation this time — ep20's one-off statement-form test stands as its
own data point, not a new default) and both got footage specificity rated
1-5 per segment before delivery (ep22 avg ~4.3/5, ep23 avg ~4.0/5 — see
`episode_log.csv` rows 22/23 for the per-segment breakdown). **New
observation worth tracking as its own hypothesis:** ep23's lower average
wasn't a search failure — space has more segments that are structurally
unphotographable (Venus, a neutron star) than a typical animal or food
episode, so a topic's *ceiling* on this rating may vary by category. Don't
read a sub-4.5 average as automatically weaker footage work without checking
whether the topic itself caps it lower.

**2026-08-07 09:00 build — both open actions applied again, plus the
category-ceiling hypothesis gets a second, stronger data point.** Ep24 (big
cats) and ep25 (weather) both used question-form hooks and both got footage
specificity rated 1-5 per segment before delivery (ep24 avg ~4.3/5, ep25 avg
~3.8/5 — see `episode_log.csv` rows 24/25). Ep25's average is the lowest of
any facts episode built this session, and for the same structural reason
flagged for ep23: hail and ice-giant planets are close to unphotographable
as real stock footage (confirmed by exhausting 4-6 distinct search terms for
each with zero genuine matches), not a search-effort problem. This is now
two facts episodes in a row (ep23, ep25) where the category itself — not
search quality — set the visible ceiling, which starts to look like a real
pattern rather than one outlier: **topic categories built mostly from
abstract/astronomical/extinct/rare subjects should be expected to average
noticeably below 4.5/5 on this rating, and that alone should not trigger
extra search effort past 4-6 well-chosen terms.** Also newly confirmed this
build: a too-short `--segment-clips` override does not loop to fill its
segment window, it gets *speed-scaled* (slowed down) by
`_build_override_clips` in `topic_footage.py` — a 3s clip stretched across
an 8s segment plays in slow motion with long near-black stretches before and
after its one bright moment, which reads as dead air, not as intentional
pacing. When an override clip is meaningfully shorter than its segment,
prefer compositing it with a second real clip (concatenate to roughly the
segment's duration) over relying on the built-in slowdown.

**2026-08-07 — owner flagged ep21 (D-Day crossword) as underperforming;
investigated, no fixable cause found, second data point for a real
"unexplained flop" pattern.** 27 views after ~1.5 days live vs 600-1500+ for
every other video published that same week, including both immediate
siblings. Checked and ruled out: technical/metadata setup is identical in
kind to well-performing STORY siblings (duration, privacy, embeddability,
`#shorts` tag, category, description all normal). Retention data isn't
available yet — too few views for Analytics to finalize a number, so the
actual drop-off point can't be diagnosed from here. Impressions/CTR (the one
metric that would distinguish "never shown" from "shown and swiped past") is
YouTube Studio-only and not exposed by the public Analytics API — not
checkable from this environment; the owner would need to check Studio
directly for a real answer on that specific question. Compared opening-frame
energy against the channel's only other severe outlier (Facts 8, 26 views) —
inconclusive: Facts 8's thumbnail isn't obviously weaker than the
well-performing Facts 9's, so "weak thumbnail" doesn't hold up as a clean
discriminator across the two data points available. **This is now N=2 for
"thoroughly-checked severe outlier, no findable technical or content
cause"** — most consistent with the Shorts algorithm simply not
distributing the video, which happens somewhat unpredictably and
disconnected from production quality. Not yet enough data to act on (both
outliers happen to be story/off-format-adjacent picks, but n=2 is too thin
to blame format), but worth tracking rather than assuming every future flop
has a fixable root cause — and worth checking Studio's impressions panel
specifically the next time this happens, since that's the one diagnostic
this environment can't reach on its own.

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
- **A thin stock library causes visible ping-pong, not just a wrong species.**
  Facts 12's dung-beetle opener (segments 0+1, same "dung beetle" search term)
  and its gorilla closer (segments 6+7, same "gorilla" term) each only had 2
  real matching clips in this account's tier. The renderer fills each
  segment's time window by cycling `clip_paths[cut_index % len(clip_paths)]`
  starting over from index 0 in every segment — so two adjacent segments
  sharing the same term pool visibly flip A→B→A→B→A. The owner caught this
  immediately as "back to the first video, then the second, then back
  again," even without knowing the mechanism. Fix: give adjacent segments
  that cover the same subject *different* search terms so their candidate
  pools (and therefore their cut order) differ, and prefer terms whose own
  top-2/3 results are each real matches — probe several phrasings
  (`probe_footage.py --per-term 4`+) until you find ones that don't surface
  the same bad/irrelevant clip (e.g. "dung beetle" and "scarab beetle" both
  ranked a market-crate-of-harvested-insects clip at position 1; "black
  beetle macro" and "ground beetle" did not).
- **A footage-only bug in an already-delivered episode does not require a
  full re-render.** `viral_episode.py` has no `--from-dry-run` lock (facts
  format), so a full re-run re-calls the LLM for every fact's wording and
  burns a fresh TTS quota slot — overkill and risky (wording drift) for a
  pure b-roll fix. Instead reuse the task dir's existing `audio.mp3` and
  `overlay.ass` untouched: rebuild `SegmentPlan`s from the saved
  `viral-result.json`'s `segments`/`segment_timings`, override only the
  broken segments' `terms`, call `topic_footage.build_synced_footage(...)`
  with the *same* `task_id` (so it reuses cached downloads) to get a new
  `combined-synced.mp4`, then re-burn the untouched `overlay.ass` with
  `viral.burn_overlay(...)` to a new `final-viral.mp4`. Zero TTS/LLM calls,
  captions stay perfectly aligned since the audio never changed. Used this
  to fix Facts 12 in ~3 minutes instead of a ~6-minute full re-render.
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
| frog (generic pond/tree frog footage only -- glass frog, wood frog, poison dart frog have no real Pexels coverage in this tier) | Facts 11 |

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

**The YouTuber mandate, 2026-08-03** (owner: "from now on you are more than
just a video creator you are a youtuber!"). This is a *scoped* expansion of
the role above, not the full-autonomy scenario rejected two paragraphs up —
the two decisions reserved for the owner (topic, first-two-seconds) are
unchanged, and every publish still requires their explicit go-ahead. What's
new is being proactive about everything else instead of only reacting to a
build request:

1. **Propose the next plan before the current one runs out.** When the
   content calendar (`docs/skill/plans/content_calendar_ep*.csv`) has 2 or
   fewer un-built episodes left, or when real data shows the current plan's
   assumptions were wrong (a whole topic category underperforming, a format
   choice not paying off), raise a revised plan unprompted rather than
   waiting to be asked. Ground it in `episode_log.csv` (below) and whatever
   real Analytics data is available — not just the three-criteria framework
   in the abstract.
2. **Build on request, upload only on permission.** Build a video any time
   asked, no extra confirmation needed for the build itself. Uploading is
   different — `upload_video.py` structurally requires `--confirm`, and that
   flag only gets passed after the owner has approved that specific video
   and its upload kit in that conversation. See `SKILL.md` 8e.
3. **Log everything — failures and successes alike, in enough detail to
   actually prevent a repeat.** This has been this file's convention since
   the first session; it's now an explicit standing rule, not just a habit.
   A failure log entry that only says "didn't work" is useless to a future
   session — say what was tried, what broke, and what the fix was (see any
   `## 2x` episode section or the `§6` production-rules list for the
   expected level of detail).
4. **Check `docs/skill/plans/episode_log.csv` before proposing a new topic.**
   One row per episode: topic, key subjects/species, format, outcome, and a
   pointer to the full narrative writeup in this file. Built 2026-08-03 from
   everything known at the time (14 uploaded videos' real stats, the
   species-used table, every build note already in this file) — **update it
   every time an episode is built, delivered, uploaded, or gets real
   retention data**, the same way `content_calendar_ep*.csv` gets updated as
   episodes move through the pipeline. This is the fast dedup check; this
   file's prose entries are for the full story when more context is needed.

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

**Title banner and progress bar position, corrected 2026-08-04 (owner feedback on
the dollar/valley episode):** commit `61a9c69` (2026-08-01) had pinned the title
band flush to `y=0` and the progress bar to a 4.5%-from-bottom margin. On an
actual phone the band flush to the top edge sits under the status bar/notch and
the app's own top overlay, and the bar that close to the bottom sits under
YT Studio's UI chrome — both were confirmed hidden in a screenshot the owner
sent. Reverted the title band to its original offset (`band_top =
video_height * 0.072`, the position used before that commit) and increased the
progress-bar bottom margin from `0.045` to `0.085` in
`docs/skill/story_episode.py`'s `inject_title_banner()` /
`move_progress_bar_to_bottom()`. Applies to future renders only — do not
re-render or replace already-published videos over this.

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

**A probed-and-rejected term can still end up pinned — check the pin list
against the rejections.** `classic car hood ornament` was probed for Story 2,
looked at, and rejected on sight: it returns the Rolls-Royce Spirit of Ecstasy,
a winged figure, not a Mercedes star. It was then pinned anyway for the outro
segment, where the narration says "that hood star" — so the one line asking the
viewer to picture a Mercedes star showed a Rolls-Royce instead. Probing only
helps if the rejections are carried forward into the pin list; write the
rejected terms down rather than keeping them in your head.

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

## 7b. ai-footage-fill in practice — prompts and results, 2026-08-05

`docs/skill/ai-footage-fill/` (own SKILL.md has the judgement rules and
credential setup). This section is the practical log: what was actually
generated, what the prompts were, and how each one turned out — so a repeat
need for similar footage (another extinct animal, another period-costume
shot) can start from a known-good prompt instead of guessing from zero.

**Backend confirmed working:** Google Cloud project `ringed-rune-503816-b8`,
OAuth token at `docs/skill/veo/token.json` (the owner's choice over a
service-account key — mirrors the already-familiar
`docs/skill/youtube/authorize_local.py` flow). `gemini-2.5-flash-image` for
the first frame, `veo-3.1-fast-generate-001` for the 8s animation. Verify any
time with `uv run python docs/skill/ai-footage-fill/scripts/generate_ai_clip.py --probe`.

**Model note, checked directly rather than assumed:** the entire Gemini 3.x
image tier — `gemini-3.1-flash-image` ("Nano Banana 2"),
`gemini-3.1-flash-image-preview`, `gemini-3.1-flash-lite-image` ("Nano Banana
2 Lite"), `gemini-3-pro-image` ("Nano Banana Pro") — all show up in
`models.list()` for this project but every one 404s on an actual call. Listed
is not the same as enabled. Re-probe after requesting access if this matters
later; don't re-try the same four names expecting a different result without
that.

**Three clips generated so far, all verified frame-by-frame before use:**

1. **Moa** (`storage/ai_clips/moa_test.mp4`, ~$3.24, for the moa story's hook
   + reveal-callback, §7a) — prompt: *"a moa, a huge flightless bird with
   shaggy brown feathers and no wings at all, standing still in dense misty
   New Zealand forest at dawn, low camera angle looking up, soft light
   through tree ferns"*. First try, no re-roll needed. Clean across 5 sampled
   frames spanning the full 8s, no morphing or extra limbs.
2. **1940s schoolboy** (`storage/ai_clips/schoolboy_1944.mp4`, ~$3.24, ep21's
   reveal segment) — prompt: *"a young boy about 13 years old wearing a 1940s
   British school uniform, grey tweed blazer, flat cap, white collared shirt,
   standing in an old stone school corridor with tall arched windows, soft
   natural light, black and white vintage photograph style, period-accurate
   1940s England, no modern objects"*. Replaced a Pexels clip of a modern kid
   in a modern library that evoked nothing about 1944. First try.
3. **1944 crossword** (`storage/ai_clips/crossword_1944.mp4`, ~$3.24, ep21's
   hook + callback) — prompt: *"a close-up of hands filling in a vintage
   1940s newspaper crossword puzzle grid with a pencil, black and white,
   English newsprint texture, period-accurate World War Two era style, soft
   window light, no legible text visible, shallow depth of field"*. Replaced
   a real Pexels crossword clip that had readable Spanish headline text in
   frame — the AI version's whole point was legible-English-or-no-text,
   which "no legible text visible" in the prompt achieved directly. First
   try.

**Pattern worth naming:** all three succeeded on the first attempt once the
prompt named a concrete subject, a specific camera framing, and explicit
lighting/style words — the same discipline the Pexels search-term rules
already ask for (§6, "must name a filmable scene"). None needed a second
image-only pass before animating. Small sample (n=3), but zero re-rolls out
of three is worth recording as a data point for how much prompt iteration to
budget next time.

**Cost so far:** ~$0.12 across 3 first-frame images (image-only iteration is
cheap, use it) + ~$9.72 across 3 full 8s animations ≈ **$9.84 total**, all
against the owner's Google Cloud trial credit.

## 8. Open items

- Five unpublished week-1 videos still carry the caption-overlap bug (~2.3s of
  overprinted text each). Re-burn is ~1 minute per video, no footage re-render.
  Two already-published videos would cost their view counts to replace.
- Sloth fact in Random But True Facts 4 shows a dolphin, which the script names.
  Veo would provide a real sloth for roughly one clip's cost.
- Content calendar still built around the old five-topic mix. Rebuilding it
  around the §5 shortlist has not been done.
- ~~YouTube Analytics access — setup in progress~~ **Live as of 2026-08-03.**
  `docs/skill/youtube/` (all gitignored except the two `.py` scripts) holds
  `client_secret.json` + `token.json` (owner completed the one-time local
  OAuth authorization) and `fetch_channel_analytics.py`, which is fully
  headless from here on — mints a fresh access token from the refresh token
  on every run, no more manual steps. Also needed **YouTube Data API v3**
  enabled (separate from Analytics/Reporting) for title lookups, since the
  Analytics report only returns video IDs — that's enabled now too. First
  real read's findings are in §5 above. Two things worth remembering for
  next time: (1) title lookup failing is a *soft* failure in the script (see
  §6) so the numbers still print even if Data API v3 ever gets disabled
  again; (2) **do not read "missing from an Analytics API pull" as "not
  published"** without checking upload age first — see the processing-lag
  lesson in §5. Verifying a *competitor's* outlier video's public view count
  (§5a's original ask) is still a separate, simpler task (just a YouTube
  Data API key, no OAuth) — not set up, raise it separately if still wanted.
- **Upload capability added 2026-08-03.** Owner asked whether the pipeline
  could publish directly instead of them uploading by hand — "only after I
  confirm them and the upload kit." Added `docs/skill/youtube/upload_video.py`
  (see `SKILL.md` 8e for the full rule) and a `youtube.upload` scope to
  `authorize_local.py`'s `SCOPES`. **The existing `token.json` predates this
  scope** — the owner needs to re-run `authorize_local.py` locally (one more
  browser consent, same as the first time) and send back the new token
  before any upload can actually succeed; the old read-only token will 403
  on `videos.insert` until then. Asked the owner to decide public-immediately
  vs. private/unlisted-staging as the upload default (a real, hard-to-reverse
  judgment call, not something to decide unilaterally) — **they chose public
  immediately**, matching their manual workflow exactly. The `--confirm`
  flag is the only safety rail after that; it is a discipline mechanism for
  future sessions reading this file, not a technical guarantee, since
  whichever agent constructs the command is also the one that would pass it
  — the real requirement is still: never invoke this script without the
  owner's explicit go-ahead on that specific video, stated in that
  conversation.
- **Two upload-flow details caught from the owner's own screenshots of their
  manual process, same day.** They pointed out they always do two more things
  when uploading by hand: answer Yes on the "Was AI used..." disclosure
  screen, and set a "Related video" link to the previous episode. Checked
  both against the actual API before implementing either — did not assume:
  (1) `status.containsSyntheticMedia` is a real field, added to the Data API
  in October 2024, confirmed via web search; wired into `upload_video.py`,
  defaulted `true` since every video here has AI TTS narration, matching how
  the owner already answers that screen. (2) Studio's "Related video" field
  — could not confirm any public Data API exposure for it at all; rather
  than guess a field name and risk a silent no-op or a failed upload, left
  it unimplemented and documented as a manual post-upload step. **If this
  becomes annoying enough to matter, look again before assuming it's
  impossible** — this was one search pass, not exhaustive.
- **Facts 10 (bats) published 2026-07-31** — awaiting first-hours numbers
  (§2e). It's a long-format (54.1s/6-fact) episode, so its retention reads as
  another data point on the still-unresolved §2d length question, not just its
  own result.
- Two Veo prompts are outstanding and not yet generated by the user: a real
  sloth hero shot for Facts 4's dolphin-substitution gap (§6, two variants
  given), and two bat-variety shots for Facts 10 (a two-bats-roosting close-up,
  a bumblebee-bat-scale shot). Splice in via the §6 technique once received.
- ~~`generate_social_metadata` still only emits 3 flat hashtags~~ **Fixed
  2026-08-02** — now emits 12 tiered tags for `youtube_shorts`. See §5.


## 9. Telegram delivery, and picking this project back up in a fresh session

**Deliverables now go to Telegram automatically, not just to the chat.** Both
`viral_episode.py` and `story_episode.py` send the finished upload kit to a
Telegram bot as soon as a real (non-`--dry-run`) render finishes — see SKILL.md
8a for the mechanics. Setup already done, nothing to redo:

- Bot created via @BotFather, `bot_token` and `chat_id` live in `config.toml`'s
  `[telegram]` section. `config.toml` is gitignored, so **a fresh clone or a
  fresh session in this same checkout still has it** — nothing needs
  re-entering unless the repo is re-cloned from scratch, in which case ask the
  channel owner for the token again rather than creating a second bot.
- Five messages per delivery: video, then title / caption(+`#`hashtags at the
  end, the YouTube description convention) / plain-text comma-separated tags
  (no `#`, matching YouTube Studio's actual Tags field — deliberately different
  formatting from the caption's hashtags, both were explicitly requested) /
  pinned-comment. Each field sends as a "label:" message followed by a
  content-only message, so a phone user can long-press-copy just the content.
- Pass `--pinned-comment "..."` to either script when one exists — the
  pipeline does not generate this field on its own, matching the existing rule
  that a pinned comment must be written fresh per episode, never reused.

**Inbound side exists but is intentionally not scheduled.** The channel owner
can message the bot with a topic or a story lead (plain text, or a forwarded
post with its own source links). `docs/skill/check_telegram_inbox.py` polls for
new messages since the last check and returns them as JSON, exactly once each —
state persists to `storage/telegram_state.json` (gitignored, runtime state) and
is written *before* any downstream processing, so a crash mid-build loses a
message rather than ever re-triggering it. Verified live: two real messages
sent back-to-back both came back in one call, in order, and a second
consecutive call correctly returned empty.

**A scheduled Routine (3x/day, 9/13/20 Israel time) was built and then
deliberately not activated** — `create_trigger` failed repeatedly with
`MCP error -32003: MCP tool call requires approval` even after the owner
approved a UI prompt each time, so the routine was never actually created. The
owner then asked to hold off on automatic checks entirely: **checks happen only
when explicitly requested**, in this same conversation. If automatic scheduling
comes up again, the exact prompt and cron expression (`0 6,10,17 * * *`, UTC,
anchored to Israel Daylight Time — needs a 1-hour shift after Israel's clocks
change back, ~late October) are preserved in this session's history and can be
reconstructed; the manual alternative is creating the routine directly at
`claude.ai/code/routines` with that same content.

**When asked to check manually:** run `check_telegram_inbox.py`, and for every
message in `new_messages`, run the *full* process this file and SKILL.md
document — fact-check independently (even when the message already carries
source links, per §7a's copyright section: verify anyway, and never reuse an
attached image), choose list vs. story format by the content's shape, lock a
story script with `--from-dry-run` before rendering, probe and pin footage,
verify the rendered output frame-by-frame, and write a fresh pinned comment.
Two real messages arrived during testing (an Alfa Romeo → Ferrari →
Lamborghini → Pagani lineage story, and a world pizza-toppings list) and were
marked read by the idempotency test *without* being built — they will not
resurface on their own; building them requires being asked again with their
content, or re-sending them to the bot.

**For a fresh session picking this project up:** read this file and
`SKILL.md` in full before doing anything — they hold the format guide, the
measured numbers, the production traps already paid for, and now the delivery
mechanics. The short version: two build flows exist (`viral_episode.py` for
fact lists, `story_episode.py` for narrative stories, see §7a), both fact-check
before rendering and verify footage frame-by-frame after, both now deliver to
Telegram automatically, and Telegram inbound is available but must be
triggered manually, not on a schedule.
