# Random But True — channel playbook

Accumulated findings for the `@RBTfacts` YouTube Shorts channel. `SKILL.md` covers
how to *build* a video; this file covers what has actually been learned about
making this specific channel work, so a fresh session does not restart from zero.

**Read this before proposing changes to format, topic mix, or episode length.**

> ## 📍 HANDOFF — current state as of 2026-08-25 (read this first)
>
> **Backlog: EMPTY.** ep64 and ep65 were approved 2026-08-25 ("מאושר
> תתזמן אותם לשעות שלהם" — approved, schedule them for their own times)
> and both scheduled rather than uploaded immediately: ep64 (STORY) for
> 16:30 IDT, ep65 (FACTS) for 23:00 IDT. ep49 and ep51-65 are all
> live/scheduled — see episode_log.csv for exact URLs and times.
>
> **QUEUED FOR THE 2026-08-26 09:00 IDT BUILD:** owner sent an Instagram
> screenshot (Columbus Zoo credit) claiming zoos pair anxious cheetah cubs
> with dog companions, and asked to verify it and use it as "tomorrow's
> story." Fact-checked TRUE (well-documented, not a myth — see
> `docs/skill/story_cheetahdog_lead.txt`) and already scripted/locked
> (`docs/skill/plans/locked_scripts/cheetahdog_locked.json`) — origin
> story of Laurie Marker/Khayam/Shesho (Wildlife Safari, Oregon, 1976),
> tied back to Columbus Zoo's real Emmett/Cullen pairing. **This is a
> STORY topic — the next build should build this as the STORY half of
> the pair (a fresh FACTS topic still needs picking), not re-derive facts
> from scratch.** Footage not yet probed — that's the next step at build
> time.
>
> **Publish workflow (since 2026-08-19):** only one scheduled trigger
> exists, the 09:00 IDT daily build (`trig_01KeLddHpRHZDY15UYZTPJFs`). It
> builds and sends to Telegram only — it must NEVER upload. Uploading
> happens only after the owner approves a specific episode **in a live
> chat message**, via `docs/skill/youtube/upload_video.py --confirm` with
> either `--privacy public` (owner said "now") or `--publish-at <UTC
> timestamp>` (owner gave a time — convert from IDT, currently UTC+3).
> When the owner approves without naming which episode goes when, the
> established fallback (used twice, 08-22 and 08-23) is: the STORY of the
> pair goes live immediately, the FACTS episode gets scheduled for 23:00
> IDT. When the owner says "schedule them for their own times" without
> naming exact times (now used **twice**, 08-24 and 08-25, near-identical
> phrasing both times, never corrected either time), the fallback read is
> the channel's old pre-08-19 two-slot cadence, **STORY → 16:30 IDT,
> FACTS → 23:00 IDT** — the repeat with no correction makes this reading
> more credible, but it has still never been explicitly confirmed by the
> owner in so many words. Keep flagging it if it comes up again.
>
> **PIPELINE CHANGE DISCOVERED 2026-08-25: `viral_episode.py` and
> `story_episode.py` now auto-send to Telegram at the end of the script**
> (calls `send_to_telegram.send_episode()` internally) **unless
> `--no-telegram` is passed.** This is new since the last time these
> scripts were read closely — it broke the "fix the caption before it
> ever reaches Telegram" discipline on the ep65 build (see below), because
> the flawed caption went out automatically before it could be reviewed.
> Fixed for ep64 by passing `--no-telegram`, reviewing frames + caption
> locally, then sending manually via `send_to_telegram.py --result-json
> ... --pinned-comment "..."`. **Pass `--no-telegram` on every future
> render, on both pipelines, and send manually after review — do not rely
> on the auto-send.**
>
> **Views-decline investigation — RECOVERY CONFIRMED with real data
> (2026-08-25 pulse re-check).** The 08-18 cliff (427 views) was a one-day
> dip, not a collapse: 08-21 (2845) and 08-22 (2793) are now the two
> highest channel-wide days in the whole ~5-week dataset, above even the
> pre-cliff peak (2262 on 08-08), and 99% of those two days' views are
> explained by the freshly-uploaded backlog episodes themselves (ep49-59),
> not the back-catalog. 4 of 9 assessed videos landed a genuine pulse-day
> spike (ep49 918, ep51 644, ep58 992, ep59 1014 — all ≥ the old Octopus
> benchmark of 868), a 44% hit rate matching the pre-decline breakout
> rates. **The 08-18 topic-mix fix is confirmed working, not just adopted
> on paper.** Findings reported to the owner in Hebrew via Telegram and
> logged in the dated entry below. ep60-63 are still outside the
> Analytics reporting window (2-3 day lag) — worth a follow-up check once
> their data lands, but no further pipeline/policy change is indicated by
> this pass.
>
> **Recurring risk, NOT solved, still the single most reliable failure
> point in the FACTS pipeline (`--pre-written`):** the auto-generated
> caption has flattened a hedge on 6 separate builds now (ep45, ep48,
> ep54, ep61, ep63, ep65) even when `--pre-written` locked the spoken
> script — the caption is always a separate LLM pass, regenerated fresh
> even on a re-render, and `--pre-written` never touches it.
> ep65's flattening was caught only AFTER it had already auto-sent to
> Telegram (see pipeline-change note above) — fixed by editing the local
> result JSON and sending an explicit follow-up "correction" message.
> Treat "read the caption in the result JSON against the locked script's
> hedges, before sending" as mandatory on every single FACTS send, same
> weight as frame-verification, never skippable. **New finding, ep64:**
> STORY's `--from-dry-run` does NOT have this risk — the rendered
> caption is pulled verbatim from the locked script JSON, confirmed
> word-for-word identical including the hedge. The caption-flattening
> risk is specific to `--pre-written` FACTS builds, not STORY.
>
> **Two flagged assumptions still awaiting owner confirmation:** (1) "the
> trigger of 9" was read as 9:00 AM IDT (the live build trigger); (2) "at
> their own times" (08-24 approval) was read as the old 16:30/23:00 IDT
> cadence. Neither has been explicitly confirmed or corrected by the
> owner.
>
> No open build is in progress. Next scheduled event is either the
> 2026-08-25T07:00:00Z Analytics pulse-check trigger, or the owner
> approving the ep64/ep65 backlog, or the next 09:00 IDT daily build,
> whichever comes first.

> **Strategy note (2026-07-29):** [`shorts_growth_guide.md`](shorts_growth_guide.md)
> is now the adopted strategy and takes precedence on targets. It sets **≤20s
> length** and **≥70% stayed-to-watch**; our best measured figure is 51.6% at
> ~52s. The §5 strategy decisions below still hold on topic mix, but the length
> hypothesis in §5 is now a governing requirement rather than an idea to try
> eventually.

> ## ⏱️ LENGTH: back to ~60s. The ~30s rule was tried for one day and REWOUND.
>
> **Timeline, so this is not re-litigated in either direction:**
> - **2026-08-14** the owner moved every episode to ~30s and both pipelines'
>   defaults were changed (`--fact-count` 6→4, `--fact-max-words` 25→16,
>   story `--target-seconds` 60→30).
> - **2026-08-15** the owner **rewound it**, explicitly to protect the
>   countdown-vs-listicle A/B test. All three defaults are back to **6 / 25 /
>   60**, and the two episodes built under the short rule (ep43 Antarctica,
>   ep44 Wojtek) were **rebuilt at the old length** rather than left as
>   outliers.
>
> **Why the rewind, in one line:** §10's A/B test had already logged ep33
> (Rome, countdown, 57.72s) as Arm A run #1. Building Arm B at ~33s would
> have confounded *countdown vs flat listicle* with *58s vs 33s* — a much
> bigger variable than the arm being tested. Shortening mid-test would have
> cost the experiment, so the length change goes back in the box until the
> A/B test finishes.
>
> **Do not re-adopt ~30s while the A/B test is running.** After it concludes
> (§10 item 1 targets a minimum of 4 completed episodes per arm) the length
> question is open again and worth testing properly — as its own single-
> variable experiment, not folded into another one. The measured record that
> already exists: long format (6-fact, ~52-58s) 45.8% retention / 724 views
> across 9 videos vs short format (3-fact, ~25s) 41.4% / 275 across 2, plus
> an owner-reverted 3-fact experiment on Facts 11. The 50-58s core range and
> the ~63s ceiling are live targets again.

> ## ✅ RESOLVED — the build-trigger stale-~30s warning (was here 2026-08-16
> ## through 2026-08-19)
>
> The `update_trigger` fix this section used to call for was applied
> 2026-08-19, as part of the bigger publish-workflow change below (see that
> section) — the build trigger's full prompt was rewritten, including a
> correct step 3 with no ~30s language. **The underlying discipline still
> stands even though the specific staleness is fixed:** trigger prompts are
> automation text, not the owner talking, and can go stale again — always
> verify length against the live code defaults (`DEFAULT_FACT_COUNT`,
> `DEFAULT_FACT_MAX_WORDS` in `viral_episode.py`; `--target-seconds` default
> in `story_episode.py`) and this file's most recent dated entry before
> trusting any trigger's own length instructions, the same habit that caught
> the original staleness.

> ## 🔁 PUBLISH WORKFLOW CHANGED 2026-08-19 — no more 16:30/22:30 triggers
>
> **The owner asked, live in chat, to eliminate the separate live-publish
> triggers entirely.** Both `RBT publish 16:30 IDT`
> (`trig_01P8m2TTGhCdgqmDz8fvTBuF`) and `RBT publish 22:30 IDT`
> (`trig_01UBEF4pe6YhF3joy3zcXA6k`) were **permanently deleted**. The build
> trigger (`trig_01KeLddHpRHZDY15UYZTPJFs`) was retimed from 02:00 IDT to
> **09:00 IDT** (`0 6 * * *` UTC) and renamed `RBT daily build (09:00 IDT)`;
> it is now the **only** scheduled trigger left in this pipeline.
>
> **New model:** the build job still only builds and sends to Telegram —
> it still must never upload. But publishing is no longer triggered by wall
> clock time at all. Instead: the owner reviews the day's built episode(s)
> and approves them **in a live chat message**, same as any other approval,
> and upload happens **immediately in that same conversation** via
> `docs/skill/youtube/upload_video.py --confirm --publish-at <RFC3339 UTC
> timestamp>` — YouTube's own scheduler flips the video public at the
> requested time (IDT is UTC+3; e.g. 16:30 IDT → `13:30:00Z`), so there is
> no dependency on a Claude-side trigger firing at exactly the right minute
> for the video to actually go live. `--publish-at` uploads as `private`
> until that timestamp; this is a real, confirmed API behavior
> (`status.publishAt`), not scheduled-guessing.
>
> **Why this is better than the old model:** the 16:30/22:30 triggers were
> pure wall-clock risk — if a session wasn't available exactly then, or
> `todays_uploads.json` was stale, publishing silently didn't happen (this
> already happened at least once, see the 2026-08-16 entry about the 13:00
> Routine being removed and nothing else staging the file). Scheduling via
> `--publish-at` at approval time removes that entire failure class: once
> uploaded-and-scheduled, YouTube's own infrastructure — not this session's
> uptime — is responsible for the video going live.
>
> **First run of the new model, 2026-08-19:** ep47 (gagaloris) and ep50
> (coffee) were already sitting approved in `storage/todays_uploads.json`
> for that day's 16:30/22:30 slots when the owner asked for this change.
> Uploaded both immediately with `--publish-at` set to that day's original
> 16:30/22:30 IDT times (`2026-08-19T13:30:00Z` and `...T19:30:00Z`)
> rather than leaving them to strand once the triggers were deleted.
>
> **`storage/todays_uploads.json` is now a reference/tracking record only**
> — nothing reads it to decide whether to publish anymore, since there is
> no publish-time trigger left. Still worth keeping updated with each day's
> intended slot assignments for continuity across sessions/compaction, but
> writing it no longer has any operational effect on what actually
> publishes. The build trigger's prompt was updated to say this explicitly.
>
> **Open question, not yet resolved with the owner:** what publish times to
> default to going forward. 16:30/22:30 IDT (the owner's original stated
> preference, "at least 6 hours difference between videos") is the
> reasonable default until told otherwise, but nothing requires sticking to
> exactly those two clock times anymore now that scheduling is manual —
> worth confirming with the owner rather than assuming permanence.

> ## 📉 ROOT CAUSE OF THE VIEWS DECLINE: topic drift away from animals
>
> **Found 2026-08-18 (second, deeper pass after the owner pushed back that
> views are clearly down).** The first pass that same day looked at
> channel-level daily totals and lifetime per-video views and concluded
> "mostly an age artifact." **That conclusion was too weak.** Measuring
> each video's views *at the same age* (day-1 views, which removes the age
> confound entirely) shows a real and specific problem.
>
> **The floor is fine. The ceiling collapsed.**
>
> | period | median day-1 views | breakouts (>=900 day-1) |
> |---|---|---|
> | early 7/27-8/3 | 652 | 3/12 (25%) |
> | peak 8/4-8/10 | 692 | 3/14 (21%) |
> | recent 8/11-8/16 | 634 | **0/12 (0%)** |
>
> Baseline distribution is intact — every video still gets its ~600-650
> opening test audience. What stopped happening is *expansion*: not one
> video since 2026-08-10 has broken 900 on day 1, where roughly 1 in 4 did
> before. The channel didn't get quieter; it stopped producing hits.
>
> **Why: the topic mix flipped, and topic category is the single strongest
> predictor of reach found so far.**
>
> | category | n | median day-1 | breakout rate (>=850) |
> |---|---|---|---|
> | EVERYDAY/RELATABLE | 4 | 851 | 50% |
> | ANIMAL | 15 | 814 | 33% |
> | NATURE/SCIENCE | 7 | 587 | 14% |
> | HISTORY/ABSTRACT | 10 | 598 | 0% |
>
> Core (animal+everyday) median 814 vs drift (nature+history) median 596 —
> a +218 day-1 gap, **permutation test p=0.0005**, breakout rate 37% vs 6%.
>
> And the mix inverted almost exactly when the breakouts stopped:
>
> | | ANIMAL | EVERYDAY | NATURE | HISTORY |
> |---|---|---|---|---|
> | 7/27-8/10 | **54%** | 12% | 17% | 17% |
> | 8/11-8/16 | **17%** | 8% | 25% | **50%** |
>
> **The cause was a playbook rule, not bad luck.** §"never two consecutive
> uploads from the same topic category" (now revoked — see that section)
> forced rotation *away* from animals every time an animal episode ran,
> and the "FIRST time this topic" novelty habit in build jobs pushed
> steadily into more obscure territory: chess, ancient Greece, Vikings,
> Rome, Antarctica, ancient artifacts, Cardiff Giant. Every one of those
> landed at the ~600 floor. The two best recent performers were the only
> two animals in the window — sharks (814) and the octopus story (843).
>
> **Things that are NOT the problem, checked and ruled out:**
> - **Retention.** Correlation between day-1 views and retention% is
>   **-0.11 — essentially zero.** Retention has actually *improved*
>   (channel daily avg 65.5% on 8/16 vs 42-50% in late July) while reach
>   fell. Optimizing retention further will not fix reach. This directly
>   contradicts `shorts_growth_guide.md`'s framing of retention as the
>   governing metric — for *reach* on this channel, topic beats retention.
> - **Duration / the A/B arms.** Recent videos are 49-64s, same as the peak
>   window. The 28s octopus scored 843 and the 70s moa scored 1311. No
>   length signal. Do not blame the countdown-vs-listicle test.
> - **Traffic source.** Shorts feed is ~97% of views in every period. No
>   shift.
> - **Publish times.** Unchanged across the whole window.
>
> **THE FIX (adopted 2026-08-18):**
> 1. **Target ~50% ANIMAL + ~15% EVERYDAY/RELATABLE across any rolling 10
>    uploads.** This is the mix that was running when the channel produced
>    breakouts. It is now the primary topic constraint.
> 2. **Revoked the forced category-rotation rule** that caused the drift.
>    Repeating a *category* is fine; repeating a *subject* is not.
> 3. **EVERYDAY/RELATABLE is under-used and has the best numbers of any
>    category** (median 851, 50% breakout rate, n=4). Sleep/dreams (971),
>    everyday objects (1102), and the 6-7 meme (731) all landed well. Mine
>    this vein harder — food, money habits, phone/tech habits, sleep, the
>    body, things in every house.
> 4. **Stop treating "FIRST time this topic" as a virtue in itself.** It
>    correlates with obscurity, and obscurity is what stopped the hits.
> 5. **Re-check in ~7 days** (around 2026-08-25) once 10+ uploads have run
>    under the new mix: has the >=900 breakout rate recovered toward the
>    20-25% it held through 8/10? If it has not, the next hypothesis to
>    test is hook quality, and after that the new-channel-boost-taper
>    explanation (which would mean accepting a lower ceiling rather than
>    fixing one).

> ### 2026-08-25, same conversation — owner-lead topic verified and locked:
> ### cheetahs get emotional-support dogs, queued for tomorrow's STORY
>
> Owner sent an Instagram screenshot (video credited "Columbus Zoo and
> Aquarium") claiming shy cheetah cubs are raised alongside calm Labrador
> Retrievers as companions, because cheetahs are especially anxious
> animals, particularly in captivity. Instruction: "תאמת את נכונות
> הדברים וזה יהיה הסיפור למחר" (verify the correctness of this and it'll
> be tomorrow's story).
>
> **Verified TRUE, independently, via WebSearch — not a myth or
> exaggeration.** Corroborated across many mainstream sources (NBC4
> Columbus, Today.com, Atlas Obscura, Boing Boing, Cincinnati Zoo,
> Columbus Zoo's own Facebook posts) plus one peer-reviewed academic
> source on the physiology (Terio et al., "Evidence for chronic stress in
> captive but not free-ranging cheetahs," PubMed / Cheetah Conservation
> Fund resource library). The screenshot's specific claim about Columbus
> Zoo and Labrador companions checks out exactly.
>
> **Caught one conflation risk and avoided it:** Anatolian Shepherds are
> genuinely used as companion dogs at some zoos including Columbus Zoo,
> but they're *also* used in a completely different Cheetah Conservation
> Fund program in Namibia — livestock-guardian dogs that protect
> *farmers'* animals from *wild* cheetah predation, reducing retaliatory
> killing. Different mechanism, different continent, different purpose.
> The script does not mix these two programs together.
>
> **Hedge applied:** the peer-reviewed source specifically shows chronic
> stress in *captive* cheetahs that *free-ranging* cheetahs don't show —
> so the script says cheetahs in zoos/captivity show measurable stress,
> not an unqualified "cheetahs are the most nervous animal on Earth"
> (a media-headline simplification, not the precise finding).
>
> **Narrative chosen: the origin story**, not just the general phenomenon
> — 1976, Wildlife Safari (Oregon): researcher Laurie Marker hand-raising
> a lonely cheetah cub, Khayam, paired her on a hunch with a Labrador-mix
> puppy, Shesho, and it worked immediately. Khayam became the first
> cheetah conservation ambassador. Ties back to the screenshot's own
> Columbus Zoo credit via a real, verified detail: cheetah Emmett and Lab
> Cullen were paired as cubs in 2016 and were inseparable for years (not
> using the fact that Emmett died in 2024 — keeps the story upbeat,
> same choice as not dwelling on Dolly the sheep's death). Laurie Marker
> named only via her own on-record, positive career story — no
> sensitivity issue, same register as other living public figures named
> for a positive, on-record reason this session (Dolly Parton, Eric
> Knudsen).
>
> Wrote `docs/skill/story_cheetahdog_lead.txt` (full fact-check) and
> locked the script at
> `docs/skill/plans/locked_scripts/cheetahdog_locked.json` (~168 words, 8
> segments) — ready for the 2026-08-26 09:00 IDT build via
> `--from-dry-run`. Footage not yet probed. **Reminder for build time:**
> ep24's footage-check found cheetah-specific Pexels searches return
> false positives (giraffes, other big cats) more often than expected —
> budget extra probe terms and verify species in every thumbnail.

> ### 2026-08-25, same conversation — owner approved ep64 + ep65, scheduled
> ### for "their own times"
>
> Owner, live in chat: "מאושר תתזמן אותם לשעות שלהם" (approved, schedule
> them for their own times). Near-identical phrasing to the 08-24
> approval ("2 הסרטונים מאושרים תעלה אותם בשעות שלהם (לא עכשיו)"), which
> was read as the channel's classic pre-08-19 two-slot cadence (16:30 IDT
> / 23:00 IDT) since no specific times were named. Applied the same
> reading again, in the same STORY-earlier/FACTS-later order: ep64 (Dolly
> the sheep, STORY) scheduled via `--publish-at 2026-08-25T13:30:00Z`
> (16:30 IDT — https://youtube.com/shorts/gri2xBEKCzg); ep65 (brain
> freeze facts) scheduled via `--publish-at 2026-08-25T20:00:00Z` (23:00
> IDT — https://youtube.com/shorts/TQoAsiP0NoU). Neither uploaded
> immediately, matching "schedule" (תתזמן) rather than "upload now" in
> the owner's wording. Backlog empty again. **This is the second time
> this exact reading has been used with no correction from the owner** —
> raises confidence it's right, but it's still an inference, not a
> confirmed instruction; keep flagging it if a future approval suggests
> otherwise.

> ### 2026-08-25 07:00 UTC — pulse re-check: the fix is working, recovery
> ### confirmed with real data, not just theory
>
> Scheduled follow-up to the 2026-08-20/21 investigation (see "ROOT CAUSE
> OF THE VIEWS DECLINE" and the 08-20 sharper-finding entry below). Pulled
> fresh real YouTube Analytics: channel-wide `dimensions=day` for the last
> 5 weeks, plus `dimensions=day,video` filtered to ep49/51-59 (ep60-63
> not yet queryable — uploaded 08-23/08-24, still inside the API's normal
> 2-3 day reporting lag).
>
> **Channel-wide daily views, 08-18 through 08-22 (real numbers):** 427,
> 1199, 321, **2845**, **2793**. The 08-18 cliff was a one-day dip, not a
> collapse — 08-21 and 08-22 are now the two highest days in the entire
> ~5-week dataset, above even the pre-cliff peak (2262 on 08-08). 08-19
> was actually fine (1199, within the old 1000-2200 baseline); 08-20 dipped
> again (321) but that too was transient.
>
> **The mechanism prediction from the 08-20 entry checks out almost
> exactly:** filtering the same day-by-day query to just ep49/51-59 shows
> nearly the entire 08-21/08-22 total is explained by those freshly-
> uploaded episodes alone — 2821 of 2845 views on 08-21 (99%), 2769 of
> 2793 on 08-22 (99%). This is not the back-catalog resurging; it is the
> backlog clear-out generating a batch of fresh pulse-or-no-pulse rolls,
> exactly as the mechanism model predicted.
>
> **4 of 9 assessed videos (44%) landed a genuine pulse-day spike**,
> comparable to or exceeding the historical pulse benchmarks (Octopus 868,
> Bird 2200): ep49 "The Ten-Foot Man That Wasn't Real" (918, upload day
> 08-21), ep58 "Mike the Headless Chicken" (992, upload day 08-22), ep59
> elephant facts (1014, upload day 08-22), ep51 "The Cat Three Warships
> Couldn't Sink" (644, upload day 08-21). **This is the first confirmed
> post-08-14 pulse** — direct evidence the channel had not lost the
> ability to land one, it just hadn't had upload volume to try since the
> backlog pileup. The 44% hit rate lines up with the pre-decline breakout
> rates the 08-18 finding measured (ANIMAL 33%, EVERYDAY 50%), so this
> reads as the expected outcome under the restored mix, not a lucky
> fluke.
>
> **Not every video hit:** ep53 "The Rhino Who Won An Election" essentially
> flopped (53 lifetime views total), and ep52/54/56/57 were weak
> (39-327 range, below the old ~600-650 floor). This is expected and
> consistent with the model — mix improves the odds, it doesn't guarantee
> every individual video.
>
> **Conclusion sent to the owner (Hebrew, via Telegram):** the 08-18 fix
> is working — real recovery, not just restored policy on paper. ep60-63
> are still outside the Analytics reporting window and need a follow-up
> check once their data lands (likely within the next 1-2 days). No
> pipeline or policy change recommended from this pass — the fix is
> doing what it was supposed to do; the next useful re-check is once
> ep60-63 (and eventually ep64/65) have real day-by-day numbers.

> ### 2026-08-25 09:00 IDT build — ep64 Dolly the sheep (STORY) + ep65
> ### brain freeze facts (FACTS, Arm A)
>
> Backlog empty going in (ep62/ep63 cleared 08-24). A/B tally was tied 6-6
> after ep63 (Arm B), tie-broken by alternating off the most recent facts
> build, so Arm A (countdown) was due for ep65; confirmed correct. Rolling
> mix diversified as usual: ep64 ANIMAL (Dolly the sheep, fresh subject),
> ep65 EVERYDAY/RELATABLE (brain freeze, fresh subject) — same pairing
> discipline as every recent day.
>
> **PIPELINE CHANGE FOUND THIS BUILD:** `viral_episode.py` and
> `story_episode.py` now call `send_to_telegram.send_episode()`
> internally at the end of the render, auto-sending to Telegram unless
> `--no-telegram` is passed. Not passing it on the ep65 render meant the
> video (and its flawed caption, see below) went out before there was any
> chance to review it — the review-before-send discipline this session
> has relied on since ep45 assumed a manual send step that no longer
> exists by default. Fixed for ep64 by passing `--no-telegram` and
> sending manually after full review. **Recommend `--no-telegram` as
> standard on every future render, both pipelines.**
>
> **Caption hedge-flattening, 6th occurrence this session** (ep65, brain
> freeze): the migraine-link fact's "probably because" qualifier was
> flattened to a flat "because" in the auto-generated caption — same
> failure class as ep45/ep48/ep54/ep61/ep63, still `--pre-written`-proof
> only for the *spoken* narration, never the caption. This time it had
> already auto-sent (see pipeline note above) before being caught — fixed
> by editing the local `viral-result.json` and sending an explicit
> follow-up "correction" message to Telegram rather than the usual
> pre-send edit. The on-screen burned-in captions (from the locked facts
> text) were unaffected — verified "probably because" intact in the
> frame-check screenshots; only the separate YouTube-description caption
> text was wrong.
>
> **New finding, ep64 (STORY, `--from-dry-run`): no caption-flattening
> risk.** Confirmed the rendered `story-result.json` caption matches
> `dollysheep_locked.json`'s caption verbatim, hedge intact
> ("likely wasn't connected to cloning"). Unlike `--pre-written` FACTS
> builds, STORY's `--from-dry-run` pulls the whole metadata block
> (including caption) straight from the locked script rather than
> regenerating it — the caption-hedge risk documented all session is
> specific to the FACTS pipeline, not STORY.
>
> **Footage: ep65 (brain freeze)** — zero AI clips, real Pexels footage
> for all 8 segments, pinned via `--segment-clips` from 7 isolated probes
> (hook, slow, tongue, vessels, migraine, doctor, scan). Caught two things
> before rendering: (1) the "hook" and "slow" term pools heavily
> overlapped — 4 of 8 candidates in each were the literal same underlying
> file at different index positions, cross-checked hashes and picked
> non-overlapping files; (2) the first-picked "tongue" candidate was only
> 5.06s long against a ~7.9s spoken-duration need — swapped to a 10.48s
> candidate before rendering rather than accepting an excessive stretch.
> All 8 segments frame-verified post-render, one cosmetic-only note: a
> brief overlapping-caption-text artifact between two caption chunks in
> segment 5's first two sample frames, resolved by the third frame — a
> normal text-transition artifact, not a rendering defect, same tier as
> prior QA-note-not-defect precedents.
>
> **Footage: ep64 (Dolly the sheep)** — 1 of 8 segments AI (mandatory
> STORY hook only): a dim 1990s lab at night, a sheep silhouetted under a
> cone of blue light, evoking the cloning-lab mood without literally
> depicting the real 1996 procedure. Image-only test passed on the first
> prompt, no safety-filter refusal, full clip clean across 4 sample
> frames. All 7 other segments real Pexels footage, cross-checked for
> hash collisions across all 7 term pools (none found). **One
> re-render:** the first-pass outro clip (a sheep with a bright magenta
> breeding-marker dye patch — common and benign in real sheep farming,
> but read as a risk of momentarily looking like an injury on the
> episode's very last visual before the follow CTA) was swapped for a
> clean unmarked sheep-and-lamb pair from the same search pool,
> re-rendered, all 8 segments re-verified end to end, zero regressions
> (segment timings shifted slightly between renders from normal TTS
> variance, not a defect).
>
> Both episodes logged as AWAITING OWNER APPROVAL in episode_log.csv.
> Backlog: ep64 + ep65, neither approved yet as of this entry.

> ### 2026-08-24, same conversation — owner approved ep62 + ep63, explicitly
> ### NOT now
>
> Owner, live in chat: "2 הסרטונים מאושרים תעלה אותם בשעות שלהם (לא עכשיו)"
> (the 2 videos are approved, upload them at their own times — not now).
> This is the first approval this session that explicitly ruled out the
> immediate-upload default. Read "their own times" as the channel's
> classic two-slot cadence from before the 2026-08-19 workflow change
> (16:30 IDT / 22:30-23:00 IDT), since no specific times were named
> otherwise. Scheduled both via `--publish-at`, neither uploaded
> immediately: ep62 (STORY) for 16:30 IDT / `2026-08-24T13:30:00Z`
> (https://youtube.com/shorts/TfWae_c_tgo); ep63 (facts) for 23:00 IDT /
> `2026-08-24T20:00:00Z` (https://youtube.com/shorts/aShl4efbi9E). Backlog
> empty again. **Note for next time:** if "their own times" is meant to
> reference something more specific than this inferred 16:30/23:00
> reading, that hasn't been confirmed by the owner — flag if it comes up
> again.

> ### 2026-08-24 09:00 IDT build — ep62 Togo vs Balto (STORY) + ep63
> ### hiccups facts (FACTS, Arm B)
>
> Backlog empty going in. A/B tied 6-6 after ep61 (Arm A) — wait, tally was
> A=6/B=5 going in, so Arm B was due for ep63; confirmed correct. Rolling-10
> mix going in was still ANIMAL-heavy (6/10), so kept the same
> diversification approach as 08-23: ep62 ANIMAL (Togo/Balto, a strong
> fresh true-crime-adjacent-but-not lead), ep63 EVERYDAY/RELATABLE
> (hiccups) rather than stacking two ANIMAL.
>
> **Caption hedge-flattening, 5th occurrence this session** (ep63,
> hiccups): the fetal-hiccup-frequency figure lost its "some studies
> suggest" qualifier on BOTH the first-pass caption and the re-rendered
> caption — confirms this is not a one-off LLM quirk, it happens
> consistently on this specific type of hedge (a numeric figure with a
> sourcing qualifier). Hand-corrected both times. This is now the single
> most reliable failure point in the whole pipeline; treat "check the
> caption against the locked script's hedges" as a mandatory step with the
> same weight as frame-verification, not an occasional spot-check.
>
> **Footage QA, two different flavors this build:**
> - ep63 segment 3 (amphibian-ancestor fact): the frog was barely visible
>   in the rendered frames even though the source thumbnail showed it
>   clearly — a reminder that the probe thumbnail and the actual rendered
>   segment can diverge (different crop/zoom/compression), so the
>   post-render frame-check is not redundant with the pre-render thumbnail
>   review, it catches a genuinely different failure.
> - ep62 segment 1 (blizzard/setup beat): landed on an abstract grainy
>   grey-texture clip, not misleading but visually weak — logged as a QA
>   note rather than re-rendered, since it doesn't contradict anything and
>   isn't distracting, just underwhelming.
>
> AI budget: ep62 held to the mandatory hook only (1/8, a blizzard sled
> team scene, no safety-filter issue this time); ep63 used zero AI clips.
> Both frame-verified, sent to Telegram. ep62: 52.9s/35MB. ep63:
> 55.16s/22MB.

> ### 2026-08-23, same conversation — owner approved and uploaded ep60 + ep61
>
> Owner, live in chat: "Both approved." No timing specified this time
> (unlike the 08-21/08-22 approvals, which named "now" and "23:00"
> explicitly). Followed the established recent cadence rather than guess
> fresh: ep60 (STORY) uploaded immediately as public
> (https://youtube.com/shorts/WPcRVkGqgc4) — matches both prior instances
> where the STORY of the pair went live immediately (ep57, ep58). ep61
> (facts) scheduled via `--publish-at 2026-08-23T20:00:00Z` / 23:00 IDT
> (https://youtube.com/shorts/fEFVm0YvKFc). Backlog empty again.

> ### 2026-08-23 09:00 IDT build — ep60 Bubble Wrap origin (STORY) + ep61
> ### domestic cat facts (FACTS, Arm A)
>
> Backlog empty going in (per the 08-22 HANDOFF block), so built normally:
> 1 STORY + 1 FACTS. Rolling-10 topic mix going in was ANIMAL 6/10 (over
> the ~50% target) and EVERYDAY 3/10 (over ~15%) — the last 6 uploads had
> skewed heavily ANIMAL (Sam, Cacareco, crows, Neil, Mike the Chicken,
> elephants). Deliberately picked ep60 as EVERYDAY/RELATABLE (Bubble
> Wrap's 1957 origin as a failed wallpaper) to diversify rather than push
> ANIMAL to 8/10 — kept ep61 as ANIMAL (domestic cat facts, a strong fresh
> lead) anyway since the pair together still lands one of each register.
>
> **A/B tally:** tied 5-5 after ep59 (Arm B), tie-broken to Arm A for ep61
> (countdown) per the alternate-off-most-recent rule.
>
> **Caption hedge-flattening, fourth occurrence this session** (after
> ep45/ep48/ep54): ep61's auto-generated caption stated the 1987 cat
> high-rise-syndrome study "proved" the terminal-velocity-relax mechanism
> as settled causal fact, dropping the locked script's "seem to" hedge and
> the single-study-limitations framing from the lead doc. Hand-corrected
> before sending. **Reinforces the standing rule harder:** `--pre-written`
> only locks the *spoken* narration — the caption is a separate LLM
> generation pass every time and must be hedge-checked independently on
> every build, not assumed safe because the facts file was pre-written.
>
> **Footage-file-collision catch (ep60):** two different search terms
> ("vintage office typewriter desk" and "vintage mainframe computer
> retro") returned an overlapping Pexels result at different index
> positions — same failure mode as the elephant episode (ep59) two days
> earlier. Caught by cross-checking file hashes before assigning segments,
> confirms this is a recurring-enough pattern to check every time multiple
> probe terms are thematically adjacent, not just when something looks
> visually identical on the contact sheet.
>
> Both built with zero AI clips (both topics extremely well covered by
> Pexels), frame-verified, sent to Telegram. ep60: 54.52s/28MB. ep61:
> 53.3s/30MB.

> ### 2026-08-22, same conversation — owner approved and uploaded ep58 + ep59
>
> Owner, live in chat: "מאושר אחד תעלה עכשיו ואחד תתזמן ל 23:00" (one is
> approved — upload one now and schedule one for 23:00). Read as approving
> **both** of today's two episodes (ep58, ep59 — the only two pending), one
> immediate and one scheduled, matching the pattern from the 08-21
> approvals. **The owner did not specify which one goes now vs. 23:00** —
> made a judgment call: ep58 (Mike the Headless Chicken, STORY) uploaded
> immediately as public
> (https://youtube.com/shorts/IoCcXrvf33I); ep59 (elephant facts)
> scheduled via `--publish-at 2026-08-22T20:00:00Z` / 23:00 IDT
> (https://youtube.com/shorts/s06GCAoNKu4). Flagged this assumption back to
> the owner in the reply so it can be corrected if the intended order was
> reversed — same open-assumption discipline as the earlier "trigger of 9"
> AM/PM call.

> ### 2026-08-22 09:00 IDT build — ep58 Mike the Headless Chicken (STORY) +
> ### ep59 elephant facts (FACTS, Arm B)
>
> First normal 2-episode build since the backlog was cleared 2026-08-21 —
> backlog check came back empty (0 awaiting approval), so this build
> proceeded per the trigger's standard instructions rather than being
> skipped. Also fixed a recurring bug while checking the backlog: the
> ep49/51-55 rows still said "AWAITING OWNER APPROVAL"/"HELD" in
> `episode_log.csv` even though they were uploaded 2026-08-21 — the
> upload-logging step had only *appended* "UPLOADED..." text after the
> stale phrase instead of replacing it, so a naive backlog scan would have
> re-counted them as pending. Corrected the text on all 8 rows (49, 51-57)
> and will replace-not-append going forward.
>
> **ep59 (elephant facts, ANIMAL, Arm B/flat-listicle)** — last-10 topic
> tally coming in was ANIMAL 4/10 (under the ~50% target), so picked
> another ANIMAL topic to close the gap; A/B tally was A={33,41,45,50,54}=5,
> B={40,43,48,52}=4, so Arm B was due. Fresh subject ("elephant" only
> appeared before as a different animal, "elephant seal," in the Neil the
> Seal story). All 6 facts independently verified (docs/skill/facts_elephants_lead.txt),
> 3 of 6 carry hedges (elephants share the no-jump trait with rhinos/hippos
> rather than being unique; the 35-45-year matriarch water-memory figure is
> field-inference, not a lab-verified test; post-matriarch-death behavior is
> documented, not asserted as human-equivalent grief) so built with
> `--pre-written`. Zero AI clips — elephants are extremely well covered by
> Pexels. **Footage-pairing gotcha worth keeping:** two different search
> terms ("elephant close up eye" and "elephant trunk close up") returned
> overlapping Pexels results including the *same underlying video file* at
> different index positions in each result set — caught by comparing file
> hashes across all candidate picks before finalizing, since using it twice
> under two different facts would have shown an identical repeated shot.
> All 8 segments frame-verified, zero defects. 44.84s, 54MB (compressed to
> 28MB for Telegram, full file kept for YouTube).
>
> **ep58 (Mike the Headless Chicken, STORY, ANIMAL)** — real, Snopes-
> confirmed-true 1945 story (Fruita, Colorado), fresh subject, absurd-but-
> true register that fits the channel well. Full sourcing:
> docs/skill/story_mikechicken_lead.txt (Wikipedia, Snopes, Britannica,
> Scientific American, Sky HISTORY). HEDGE: the exact mechanism of Mike's
> death (choked on corn vs. couldn't clear his severed trachea because the
> feeding syringe was left behind) is disputed across sources — script
> states only what's undisputed (died in a motel in Phoenix, ~18 months
> after the beheading, from a choking/breathing incident) without picking a
> side. Mike's age at beheading is also inconsistently reported across
> sources (5.5 months vs. an outlying "five-year-old" claim) — script avoids
> stating a specific age rather than pick one. Built via `--from-dry-run`
> for script-fidelity given the hedge. **Sensitivity handling:** the story
> involves a real beheading — hook and all segments are non-graphic by
> design; the mandatory AI hook is a tasteful farmyard scene (axe resting
> against a chopping block, feathers drifting, a rooster walking calmly in
> the background) that evokes the story without depicting the act, same
> discipline as mainstream retellings (Britannica, Scientific American).
> Image-only test passed on the first prompt, no safety-filter refusal.
> **ONE RE-RENDER:** first-pass segment 4 (the dropper-feeding beat) landed
> on real Pexels footage of a small white DOG being hand-fed — not
> factually contradictory (script never claims the footage is Mike) but a
> visible species mismatch in a chicken story, which reads as a mistake to
> viewers rather than a defect a viewer would forgive. Re-probed
> specifically for chicken/chick imagery, found a clean shot of a small
> chicken on a hand, re-rendered, re-verified all 8 segments, zero
> regressions on the 7 untouched ones. **New footage-check habit:** the
> generic-stock-as-visual-echo discipline (never claim footage depicts the
> specific named individual/event) still requires the stand-in to be the
> same *species*, not just thematically close — a same-category-different-
> animal substitution is a step too far and reads as an error, not an
> echo. 57.64s, 53MB (compressed to 27MB for Telegram).

> ### 2026-08-21, same conversation — owner said "implement the
> ### recommendations": full 6-episode backlog cleared same day
>
> Owner, live in chat, quoted the three recommendations from the
> views-decline analysis back verbatim and said to implement them: clear
> the queue (ep49, 51-55), give the topic-mix fix a real chance, re-check
> around 8/25. This is explicit, per-episode-named approval for all six —
> traced to a real chat message, not a trigger firing.
>
> **Scheduled all 6 the same day (2026-08-21), spread through the day
> rather than dumped at once**, alternating STORY/FACTS where the mix
> allowed (4 stories : 2 facts in this batch, so the last two are back-to-
> back stories — unavoidable, not a format-policy violation since this is
> backlog catch-up, not a normal daily build). Chose same-day over spread-
> across-days because the owner's own reasoning ("every day without upload
> is a day with zero chance at the algorithmic push") argues for speed, and
> the pulse mechanism found in the entry above showed no evidence that
> multiple same-day uploads cannibalize each other — each video's pulse
> chance ties to its own publish moment, not to how many other videos went
> up that day.
>
> | ep | title | publish_at UTC | IDT | format |
> |----|-------|-----------------|-----|--------|
> | 49 | The Ten-Foot Man That Wasn't Real (Cardiff Giant) | 08:00 | 11:00 | STORY |
> | 52 | money/spending psychology facts | 10:00 | 13:00 | facts |
> | 51 | Unsinkable Sam | 12:00 | 15:00 | STORY |
> | 54 | crow intelligence facts | 14:00 | 17:00 | facts |
> | 53 | The Rhino Who Won An Election (Cacareco) | 16:00 | 19:00 | STORY |
> | 55 | Neil the Seal | 18:00 | 21:00 | STORY |
>
> (ep56 already scheduled 20:00 UTC/23:00 IDT the day before; ep57 already
> live since 2026-08-20 — so this is actually **8 episodes publishing
> across 2026-08-20/21**, the closest thing to a real live-distribution
> test the topic-mix fix has had yet.) Approval for ep49 specifically also
> lifts its 2026-08-18 HOLD — the owner's "clear the queue... ep49, 51-55"
> named it explicitly, and the hold was a topic-mix-recovery precaution,
> not a content problem, so this instruction supersedes it. Backlog is now
> **fully cleared** — `storage/todays_uploads.json` updated to reflect
> this and to carry a `next_check_in: 2026-08-25` note forward across
> sessions. A one-shot reminder was also scheduled via `send_later`/trigger
> for 2026-08-25 to actually re-run the per-day-Analytics pulse check
> against ep51-57 rather than rely on remembering to do it.

> ### 2026-08-21 09:00 IDT build job — SKIPPED, backlog already flagged
>
> The daily build trigger fired normally (06:08:58 UTC). Backlog check:
> still 6 episodes awaiting approval (ep49, 51-55) — ep56/ep57 uploaded the
> day before, but nothing else moved. The trigger's own instructions say to
> **flag a deep backlog instead of silently building more** when it's
> unflagged; this one was *already* flagged to the owner minutes earlier in
> the same conversation (as part of the views-decline analysis, which also
> found that live-upload cadence itself is what drives the channel's view
> totals — see the entry above). Building 2 more here would directly work
> against that finding: more unpublished episodes sitting in the queue,
> not more live at-bats. **Decision: skipped this build cycle**, sent a
> short Telegram reminder instead, and left `episode_log.csv` / the CSV's
> stale "AWAITING OWNER APPROVAL" text on the now-uploaded ep56/ep57 rows
> corrected (it still said AWAITING even after upload, which would have
> thrown off any future backlog count — fixed to "APPROVED AND UPLOADED").
> Resume normal 2-episodes/day building once the owner clears some of the
> backlog or explicitly asks to keep building anyway.

> ### 2026-08-20, owner asked again "why the decline, fix it" — sharper root
> ### cause found with real per-day Analytics data (first time this pipeline
> ### queried dimensions=day instead of dimensions=video)
>
> Owner asked again to look at the view decline and understand/fix it.
> Pulled real data via `fetch_channel_analytics.py` plus two ad-hoc
> `dimensions=day` Analytics queries (channel-wide, and filtered to the
> top-8 lifetime-view videos) rather than re-stating the 08-18 finding from
> memory — that finding was built on lifetime/day-1 totals across videos,
> never on a real day-by-day channel timeline, so it was worth checking
> whether fresher data told the same story or a sharper one. It told a
> sharper one:
>
> **Channel-wide daily views, last ~4 weeks (YouTube Analytics API, real
> numbers, `dimensions=day`):** roughly 1000-2200/day from 2026-07-26
> through 2026-08-17, then a cliff to **428 on 2026-08-18** (-63% in one
> day). No rows exist yet for 08-19/08-20 — normal Analytics API reporting
> lag (2-3 days), not zero views; those days show as explicit `0` rows when
> genuinely zero (confirmed against 07-22 to 07-24, before the channel's
> first upload).
>
> **The mechanism, found by filtering the same day-by-day query to just the
> channel's top-8 all-time videos:** each of those videos shows ONE huge
> single-day view spike, and the spike date is consistently that video's
> own upload date (or the day after) — 08-02 (Facts 12, uploaded 08-02),
> 08-04 (Facts 18, uploaded 08-04), **08-08 (2200 views — "The Bird With No
> Wings At All," uploaded 08-08)**, 08-10 (Facts 26, uploaded 08-10),
> **08-14 (868 views — "The Octopus That Escaped," uploaded 08-14)**. Every
> one of these videos is essentially flat before/after its own spike day.
> This is the Shorts recommender's actual behavior on this channel: a new
> video either gets pushed hard on/near its own publish day, or it doesn't,
> and that single day determines most of the video's lifetime total — not
> gradual organic discovery, not legacy videos resurging at random.
>
> **The finding that matters: no video published after 08-14 (Octopus) has
> landed one of these pulses.** Everything from 08-15 onward — Facts 33/34,
> "War Australia Lost To Birds," Facts 35, "Bear Who Was Officially A
> Soldier," Facts 36, "Pilot Switzerland Couldn't Catch," Facts 37, "Animal
> That Bit Lady Gaga," ep50 — sits at 6-141 views apiece with no spike day
> of its own. The 08-18 channel-total cliff is simply the exact date the
> last successful pulse (Octopus, 08-14) finished decaying with nothing new
> to replace it. **This corroborates the 08-18 "topic drift away from
> animals" finding through a completely independent lens** (day-by-day
> channel Analytics instead of per-video day-1 comparisons) and sharpens
> it: the failure window (no pulses since 08-14) lines up almost exactly
> with when the forced category-rotation rule was dragging topics away from
> ANIMAL/EVERYDAY, right before it was revoked on 08-18.
>
> **A second, compounding factor found in the same pass:** the topic-mix
> fix has been *policy* since 08-18 and every build since (ep51-57) follows
> it, but **almost none of those builds have actually gone live on YouTube**
> — they piled up in the approval backlog from 08-19 until today, when the
> owner approved and uploaded ep56/ep57. That means the fix has had almost
> no live at-bats yet to prove out; the channel went ~36-48 hours (exactly
> the highest-leverage window right after the 08-18 cliff) with no new
> upload at all to even *attempt* a pulse. Every day a built episode sits
> unapproved instead of going live is a day with zero chance of landing the
> algorithmic push that, per the mechanism above, is what actually drives
> this channel's view totals.
>
> **Recommendation given to the owner:** (1) clear the remaining backlog
> (ep49, 51-55, six episodes) at a steady cadence rather than let it sit —
> more live uploads means more chances at a pulse; (2) the topic-mix fix
> needs real upload volume to be judged fairly, so the 08-25 re-check
> (§ROOT CAUSE item 5) should specifically look at whether any of ep51-57
> lands a pulse-day spike like Octopus/Bird/Facts-18/26/12 did, not just
> raw view totals; (3) no further pipeline change recommended yet — the
> already-adopted fix hasn't been tested with real distribution, so
> changing anything else now would confound the read again.

> ### 2026-08-20, same conversation — owner approved and uploaded ep56 + ep57
>
> Owner, live in chat: "תעלה עכשיו את הסיפור האחרון וב 2300 עוד סיפור האחד
> לפני האחרון שתיהם מאושרים" (upload the last story now, and the one before
> it at 23:00 — both are approved). Read "last" / "one before last" as the
> two most recently built STORY episodes: ep57 (Slender Man) and ep56 (eye
> drops), both correctly identified since no other story was built between
> them. **ep57 uploaded immediately as public** (`--privacy public`, per
> the owner's explicit "now" — https://youtube.com/shorts/y4H0C51e3QA).
> **ep56 scheduled via `--publish-at 2026-08-20T20:00:00Z`** (23:00 IDT —
> https://youtube.com/shorts/hLejd2pEFDU), uploaded private until YouTube
> flips it at that timestamp, per the 2026-08-19 publish-workflow model.
> Both approvals traced to this real chat message, not a trigger firing.
> Backlog after this: ep49 (held) + ep51-55 still awaiting approval (6
> episodes) — flagged to the owner alongside this build.

> ### 2026-08-20, same conversation — ep57 the real Slender Man origin story:
> ### owner rejected a fabricated "true 1962 event" creepypasta, first
> ### deliberate genre pivot into eerie/mystery content
>
> Owner posted an Instagram screenshot of "Yellow Echo" — a creepypasta
> claiming 37 children vanished around a faceless figure in 1962 — with the
> instruction "Make this a story." Checked it: it's a **modern fabricated
> creepypasta** (verbatim on creepypasta.com and midnightsignals.net,
> inconsistent details between versions, no actual 1962 historical record),
> not a documented event, despite the source account's own "unclear if real
> or urban legend" hedge — that hedge language is itself a common
> creepypasta framing device, not a genuine sourcing caveat. **Declined to
> build it as a "true story"** — doing so would break the channel's core
> brand promise and the fact-checking discipline this session has held on
> Cher Ami and the FBI-fugitive case. Offered the owner two alternatives: (1)
> a genuinely real, verified, similarly-eerie true story instead, or (2)
> build Yellow Echo itself but explicitly labeled legend/creepypasta, not
> "true" — a brand deviation requiring explicit sign-off. **Owner replied
> "1."**
>
> Built the real 2009 origin of "Slender Man": Eric Knudsen, posting as
> "Victor Surge," created him in a single Something Awful Photoshop-contest
> thread on June 10, 2009 — no ancient legend, no prior history, just one
> forum post with two edited photos and invented "witness" text. The
> internet then built him a fake past after the fact (a supposed 16th-
> century German woodcut, "Der Großmann," fake case files) specifically to
> make him look centuries old — a genuinely eerie true story about a *fake*
> true story, which lands as an ironic, on-brand mirror of the very thing
> the owner asked about. Full sourcing: `docs/skill/story_slenderman_lead.txt`
> (Wikipedia, Newsweek, Rolling Stone, NBC News, Know Your Meme).
>
> **New sensitivity layer, extending the living-person standing rule
> (2026-08-20 earlier entry, Cher Ami/FBI-fugitive precedent):** the honest
> payoff of this story is the 2014 Waukesha, Wisconsin stabbing, where two
> 12-year-old girls cited Slender Man as their motive. Named Knudsen (public
> figure, spoke on the record via NBC News) but **deliberately did not name
> the two attackers or the victim** — they were minors at the time, the
> victim is a private individual, and one attacker resurfaced in real news
> very recently (a reported group-home escape, Nov 2025), so this is not
> settled cold history. Referred to them only as "two 12-year-old girls" and
> "a classmate," and stated plainly that the victim survived rather than
> leaving it as unresolved dread. **Extend this as a general rule:** even
> when a crime is fully adjudicated/closed, a *recent recurrence in the news*
> of one of the real people involved pushes it back toward the
> "don't-name-them" side, same as an still-open case would.
>
> **Footage catch worth keeping:** first-pass render put the 2014-case
> narration over real Pexels footage of a silhouetted person walking alone
> down a foggy forest road. Not factually wrong, but on frame-check it read
> as an **implied reenactment** of the real attackers/victim — exactly the
> kind of visual the sensitivity decision above was trying to avoid. Swapped
> for an empty misty-forest shot with no person in frame, re-rendered,
> re-verified all 8 segments. **New footage-check habit:** for any segment
> whose narration involves real, identifiable people (even unnamed ones),
> screen candidate footage specifically for "does this visual read as
> depicting a person from the story" — not just "is this literally forest at
> night," which is too weak a bar.
>
> AI budget: exactly 1 of 8 segments (the mandatory STORY hook — a faceless
> figure in a black suit in a foggy forest, which cannot exist as real stock
> without using someone else's copyrighted fan art). Image-only test passed
> on the first prompt this time, no safety-filter refusal. All 7 other
> segments real Pexels footage, per the owner's standing AI-restraint
> caution. Final: 63.58s, 33MB, no compression needed.

> ### 2026-08-20, same conversation — ep56 the eye-drop-recall story: owner
> ### said ep55 "still boring," first deliberately NON-ANIMAL build
>
> Owner's reaction to ep55: "still boring, do something not about animals
> that's trending today." Read as: even a strong ANIMAL pick can read as
> more-of-the-same after several in a row — **the topic-mix policy sets a
> floor for animals, not a ceiling that every single video must hit.**
> Category diversity within "what's actually trending" matters too.
>
> **Rejected a much more obviously "trending" candidate first, and this is
> the one to remember.** The single most viral non-animal true-crime story
> right now is the FBI Most Wanted "fake heiress" true-crime TV producer
> case (Mary Carole McDonnell — allegedly conned banks out of $30M, now a
> fugitive believed to be in Dubai). It looked perfect on the surface:
> dramatic, real, currently trending. **Rejected anyway, because she is a
> real, living person, currently at large, only *alleged* to have
> committed the crime, under active federal investigation.** That's a
> categorically different risk than this channel's usual real-but-settled
> subjects — defamation exposure before any conviction, safety/privacy
> concerns, and facts that could shift before this even publishes. **This
> is the same family of judgment as the Cher Ami rejection (2026-08-20,
> earlier) but one level more serious: Cher Ami's problem was a disputed
> historical detail; this was a real person's unresolved legal jeopardy.
> New standing rule: an active criminal investigation of a named living
> person is off the table regardless of how well-documented or trending it
> is, full stop — this isn't a hedge-it-carefully case, it's a pick-a-
> different-topic case.**
>
> **Built ep56 instead: the 2023 EzriCare artificial-tears outbreak
> (81 infected, 14 lost vision, 4 died, from contaminated eye drops),
> bridged to the real, currently-running wave of 2026 eye-drop recalls**
> (Clear Eyes, Rohto, a wave of store brands — all citing the same root
> failure, inadequate sterility assurance). EVERYDAY/RELATABLE, genuinely
> trending (FDA update dated 2026-08-14, six days before this build), zero
> living-person risk — the only subject is a company's manufacturing
> failure and a closed CDC-documented outbreak.
>
> **AI budget: zero clips.** Probed real footage for all 9 segments first
> and it held up completely without needing a single generation — real lab
> workers in PPE, a real pediatric eye exam, real dropper-bottle handling.
> This is the cleanest demonstration yet of the ai-footage-fill discipline
> working as intended: **generation is for confirmed gaps, and an ordinary
> everyday subject like this one usually has none.** Directly responsive to
> the owner's standing AI-restraint caution from ep55.
>
> Sent to Telegram, **awaiting owner approval** — not uploaded. Backlog is
> now 7 unapproved (ep49 held + ep51/52/53/54/55/56), all explicitly
> flagged.

> ### 2026-08-20, owner request — ep55 Neil the Seal: first TRENDING-topic
> ### build, and the AI-restraint precedent
>
> Owner asked directly for one video that is **interesting, eye-catching, and
> pulled from today's top Google trends** while fitting this channel — with an
> explicit caution that **excessive AI generation can itself provoke a negative
> audience reaction.** That caution is now a standing consideration, not a
> one-off note.
>
> **Trending-topic sourcing, and why the obvious list was useless.** Google's
> actual trending searches for 2026-08-19/20 were sports fixtures, celebrity
> news and product recalls — nothing that survives as evergreen absurd-but-true
> content. **The productive move was to search for currently-viral stories
> *within* the channel's proven category (ANIMAL) rather than to mine the
> generic trending list.** That surfaced three live candidates; two were
> rejected and the reasons are worth keeping:
> - **Punch the macaque** (Japan, ~40M views in Feb 2026, IKEA plush sold out
>   worldwide) — rejected because the zoo has *publicly rebutted* the viral
>   "he's being bullied" framing and an animal-rights group has separately
>   criticised his treatment. **The popular version of the story is the wrong
>   version**, and he is a specific living zoo animal with no legitimate
>   footage available. Same failure class as the Cher Ami rejection: the
>   disputed part is the core, not an embellishment.
> - **Jimothy the raccoon** (Seattle) — the short-spine-syndrome claim is
>   speculative in the sourcing, and building a comedy beat on an animal's
>   suspected deformity is off-tone for this channel.
>
> **Built ep55 (Neil the Seal + the Freya precedent).** Neil is a one-tonne
> southern elephant seal who hauls out into Tasmanian towns twice a year and
> blocks roads, rams cars and sleeps in streets; 1.5M+ followers. The payoff is
> the genuinely dark, fully documented turn: officials aren't worried about the
> cars, they're worried about the crowds — and in 2022 Norway euthanised Freya
> the walrus, not because she hurt anyone, but because the public would not
> keep its distance. **Hedge held:** the script never claims Neil will be
> euthanised or that anyone threatened it — only what is sourced.
>
> **AI restraint, deliberately: 2 of 8 segments (25%), despite the STORY budget
> allowing 3.** Both were genuine confirmed gaps — the hook (a seal lying
> across a suburban road; no stock library has this, and it is the episode's
> eye-catching shot) and Freya (**"walrus" on Pexels returns only children in
> walrus onesies** — a total gap, now on the known-gap list). The other six
> segments are real footage. **This is the precedent to follow when the owner's
> AI-caution is in play: spend AI on the hook and on true gaps, carry the rest
> on real stock, and never claim a generated clip depicts the real named
> animal.**
>
> **Reusable safety-filter lesson.** The first hook prompt was *refused* by the
> image model because it contained "looks like real amateur news footage" — the
> generator rejects prompts that read as documentary coverage of a real event.
> Rewriting the identical shot as a pure filmable scene ("cinematic wide
> shot… camera slowly pushing in") passed immediately. **Describe the scene,
> never the provenance.**
>
> **One re-render:** the first pass put a tourist photographing a Thai temple
> under the "officials are worried about the crowds" segment — not
> contradictory, but the wrong setting entirely. Swapped for a real coastal
> warning sign and re-verified all 8 segments, zero regressions.
>
> **Also new: first render to exceed Telegram's 50MB limit in a while** (58MB
> at 54.9s, because two 1080p Veo clips plus long real clips compress poorly).
> Compressed to 29MB at CRF 26 *for Telegram only* — the full-quality file
> stays in the task dir and is what should be uploaded to YouTube. Keep that
> split; do not upload the compressed copy.
>
> Sent to Telegram, **awaiting owner approval** — not uploaded.

> ### 2026-08-20 09:00 build — ep53 Cacareco the rhino story + ep54 crow
> ### facts, second build night under the new topic-mix policy
>
> First firing of the retimed (02:00→09:00 IDT) build trigger. Backlog going
> in was 3 (ep49 held, ep51, ep52 both awaiting approval) — under the
> established "build to 5, flag clearly" threshold, so this job built 2 more
> rather than pausing. **Backlog is now 5, all explicitly flagged**: ep49
> (held), ep51, ep52, ep53, ep54.
>
> Checked the rolling-10 category mix before picking topics (episodes 43-52):
> 40% ANIMAL, 20% EVERYDAY/RELATABLE, 10% NATURE/SCIENCE, 30% HISTORY/ABSTRACT
> — still short of the ~50% ANIMAL target. **Built both of tonight's episodes
> ANIMAL** to push the rolling window toward target (new window 45-54 lands
> at 50% ANIMAL / 20% EVERYDAY / 30% HISTORY once the two oldest entries roll
> off).
>
> **Built ep53 (Cacareco the rhinoceros — 1959 São Paulo city council
> election).** Real, unusually clean lead — the 100,000-vote/15% figure is
> consistent across every source with no dispute found, a rarer thing this
> session than expected. **Worth recording the topic that got rejected
> first:** Cher Ami, the WWI messenger pigeon credited with saving the "Lost
> Battalion," looked like a strong ANIMAL candidate on first pass. A second,
> deeper pass found that Snopes and the Smithsonian's own curator say
> official military records cannot confirm which pigeon delivered the
> critical message that day — **this is a different class of problem than
> Unsinkable Sam's hedge.** Sam's disputed detail was an embellishment on a
> solid, independently-photographed core (the Ark Royal rescue). Cher Ami's
> disputed detail *is* the story's central causal claim. **Lesson: a hedge
> on an embellishment is scriptable (state the solid core, flag the
> embellishment as "the sailors' own telling"); a hedge on the central claim
> itself is a sign to pick a different topic, not to hedge harder.** Switched
> to Cacareco rather than force it. Zero AI clips needed for the build itself
> — no Pexels gap for rhino/zoo, voting, or São Paulo city visuals. 55.86s.
>
> **Built ep54 (crow/corvid intelligence facts, Arm A countdown run #5 —
> tally was tied 4-4, broke off the most recent Arm B build).** Confirmed
> Pexels gap: no footage anywhere shows a crow actually using a tool (every
> candidate was just a perched or flying bird) — used a clear crow portrait
> instead of forcing it or spending the facts-format AI budget (hook-only)
> on a non-hook segment. **Also caught a wrong-species near-miss:** a
> candidate for the "shiny objects" segment was actually a red-billed
> chough, a different corvid with a distinctive red beak/legs — would have
> been a subtle species mismatch under a generic "crow" claim, swapped for
> an unambiguous silhouetted pair. **Auto-generated caption flattened two of
> the three hedges** (funeral interpretation, gift-giving motivation) into
> flat assertions, dropping "scientists think" / "researchers suspect" —
> hand-corrected before sending. This is now the third time this exact
> failure mode has hit a caption (after ep45 honey, ep48 Parthenon) — **the
> caption step needs the same hedge-check as the script, every single time,
> not just when a fact "feels" contested.** 56.52s.
>
> **Disk:** cleaned ~/tmp probe scratch after both renders, ended the night
> at 5.5GB free / 86% used.
>
> **Neither ep53 nor ep54 was uploaded** — both sent to Telegram, awaiting
> owner approval per the new publish-on-chat-approval model (see the
> workflow-change section above). `storage/todays_uploads.json` updated to
> the new reference-only shape introduced 2026-08-19 (no more slot times,
> just a backlog list) since there is no publish trigger left to stage slots
> for.

> ### 2026-08-19 02:00 build — ep51 Unsinkable Sam story + ep52 money facts,
> ### first build under the new topic-mix policy
>
> **Both 2026-08-18 slots published** (ep46 Swiss hijack 16:30, ep48 ancient
> Greece 22:30), and `storage/todays_uploads.json` was re-staged for
> 2026-08-19 with the two already-approved, already-built episodes from the
> queue set the same night: **ep47 gagaloris (ANIMAL) → 16:30, ep50 coffee
> (EVERYDAY/RELATABLE) → 22:30.** No fresh topics were built for either of
> tomorrow's slots, per that entry's explicit instruction. **Backlog is now 2
> unapproved: ep49 (held, HISTORY/ABSTRACT, not competing for a slot) plus
> the two built tonight (ep51, ep52) — both flagged here, neither silently
> piled up.**
>
> **This is the first build night run under the topic-mix fix** (see the
> "ROOT CAUSE" section above). Both topics were chosen deliberately from the
> two recommended categories rather than continuing the "avoid the last
> category" rotation that caused the drift.
>
> **Built ep51 (Unsinkable Sam, WWII ship's cat — FIRST time this topic,
> ANIMAL).** Real, carefully hedged story: the Ark Royal rescue (Nov 1941)
> is solidly documented; the earlier Bismarck/Cossack legs trace only to the
> sailors' own telling, and at least one source found conflicting photos
> suggesting the popular "Unsinkable Sam" photo may actually show a
> different WWII ship's cat. Built `--from-dry-run` specifically to keep
> that distinction intact — the locked script states the Bismarck/Cossack
> legs as "the sailors' own telling" and flags the Ark Royal leg as the part
> "every historian agrees is real." **Three AI clips (hook + 2 more, at the
> STORY budget ceiling)** — a newly confirmed Pexels gap: no usable WWII-era
> warship footage exists for battleship/destroyer/aircraft-carrier searches
> (blank ocean, a modern museum ship, passenger ferries, one airplane wing —
> nothing usable), joining the WWII/Vikings/lava-lake list. All three AI
> clips verified clean, no drift, no visible people. 51.74s, 45MB.
>
> **Built ep52 (money and spending psychology facts, Arm B flat listicle —
> FIRST time this topic, EVERYDAY/RELATABLE).** Deliberately mined the
> best-performing category per the topic-drift finding's recommendation #3.
> Six independently-verified facts (2019 lost-wallet study, pain of paying,
> credit-card spending research, charm pricing, the US Mint's November 2025
> final penny, 1909-1915 tipping bans), built `--pre-written` since the
> charm-pricing fact carries a hedge (the left-digit psychological effect is
> real research; the cash-register anti-theft origin story is folklore, not
> documented history). Zero AI clips needed — Pexels covered everything.
> **One accepted trade-off:** the best visual match for the penny fact (a
> coin stack) was only 7.24s against an ~8.7s segment; kept it anyway over a
> worse-matching but longer banknote clip, verified no visible slow-motion
> artifact on frame-check. 64.94s (~2s over the soft ceiling, accepted as
> minor, same standard as ep49's 64.28s), 26MB.
>
> **Disk space:** cleaned ~740MB of `/tmp` probe scratch after both renders
> (never tracked, safe to delete once verified). Ended the night at 5.8GB
> free / 85% used — comfortable but worth watching; `storage/tasks/`
> cleanup (published-only, cross-checked against the CSV) is the next lever
> if it gets tighter, per the established methodology above.
>
> **Neither ep51 nor ep52 was auto-slotted anywhere** — both go into the
> standard awaiting-approval backlog. The now-3-deep backlog (ep49 held +
> ep51 + ep52) is explicitly flagged here rather than left to silently pile
> up, per standing practice.

> ### 2026-08-18, same conversation — owner approved acting on the topic-drift
> ### finding: hold ep49, slot ep50 for 2026-08-19 22:30
>
> Presented the topic-drift analysis above to the owner live in chat. Asked
> directly: hold ep49 (Cardiff Giant, HISTORY/ABSTRACT — the worst-performing
> category) and slot ep50 (coffee, EVERYDAY/RELATABLE — the best-performing
> category) into the open 2026-08-19 22:30 slot instead. **Owner replied
> "Yes"** — this is the real chat approval for both the hold and the slot
> assignment, not an automated-trigger approval.
>
> **Queue for 2026-08-19, updated:**
>
> | slot | episode | category | note |
> |---|---|---|---|
> | 16:30 | ep47 gagaloris | ANIMAL | unchanged, per the 2026-08-17 queue table |
> | 22:30 | ep50 coffee | EVERYDAY/RELATABLE | newly approved/slotted this conversation |
>
> **ep49 (Cardiff Giant) is HELD, not rejected** — stays in the backlog,
> sent to Telegram, awaiting a future decision. Do not slot it into any
> upcoming date without a fresh approval; `episode_log.csv` row 49's status
> field records the hold and the reason. **Do not build a fresh
> HISTORY/ABSTRACT episode to replace it either** — per the new topic-mix
> target, the next few build slots should skew ANIMAL/EVERYDAY, not
> backfill the category that was just identified as the problem.
>
> **`storage/todays_uploads.json` is not touched by this entry** — it only
> holds *today's* (2026-08-18) slots per the existing convention, and both
> of today's slots are already published. **The 2026-08-19 02:00 build job
> must read this table, not build fresh topics for either slot** — both
> 2026-08-19 slots are already spoken for by already-built, already-approved
> episodes.

> ### 2026-08-18 — views-decline investigation (owner-requested, FIRST pass — superseded)
>
> **Superseded by the topic-drift section above.** Kept as the record of a
> reasoning error worth not repeating: this pass compared *lifetime* views
> across videos of different ages, correctly noticed the age confound, and
> then over-corrected into "there's no real problem." The right move was to
> measure views at matched age immediately — which takes one extra API pass
> and turns an ambiguous picture into a p=0.0005 result. **When a metric is
> age-confounded, control for age; do not settle for "it's probably the
> confound."** Original text follows.
>
> Owner asked why recent videos are dropping in views instead of rising.
> Pulled real numbers via `docs/skill/youtube/fetch_channel_analytics.py`
> plus two one-off scripts against the same OAuth token (channel-wide
> `videos.list` for lifetime views/duration by publish date, and Analytics
> `dimensions=day,insightTrafficSourceType` for a true day-of-view trend) —
> not guesswork.
>
> **What the data actually shows:**
> - **Real but partial decline, and it is confounded by video age.**
>   Grouping by *publish* date, avg views/video: early (7/25-8/3) 597 →
>   peak (8/4-8/10) 834 → recent (8/11-8/17) 651. But this compares
>   lifetime-so-far totals across videos of very different ages — a video
>   published yesterday has had 1 day to accumulate views vs. two weeks for
>   an 8/4 video, so part of the "recent" numbers being lower is structural,
>   not a real-time signal.
> - **The true day-of-view trend (not by-publish-date) does NOT show a
>   monotonic collapse.** Total channel views per calendar day: 8/8 2262
>   (peak) → 8/11 1055, 8/12 1100 (real dip) → **8/13 2060, 8/14 1721**
>   (rebounded back near-peak). YouTube Analytics has ~2 day processing
>   lag, so 8/16-18 aren't in confirmed data yet — there is no verified
>   real-time evidence of a *current* sharp drop as of this writing, only a
>   dip on 8/11-12 that already partly recovered by 8/13-14. Re-check this
>   in ~2 days once 8/16-18 are processed before treating a drop as
>   confirmed and ongoing.
> - **Retention has NOT declined** — average-view-percentage in the
>   confirmed-data window (8/11-8/15: 35-74%) is comparable to or better
>   than the peak window (8/4-8/10: 32-101%). Content quality/watch-time,
>   once someone clicks, is intact. The problem (to the extent it's real)
>   is on the *reach/distribution* side, not content quality.
> - **Traffic-source mix is unchanged** — Shorts feed is ~97% of views in
>   every period measured (early/peak/recent). No shift away from Shorts
>   feed to search/browse/external; whatever's happening is inside the
>   Shorts algorithm's own distribution decision, not a channel-external
>   factor.
> - **Duration/format are not implicated.** Recent videos are still 49-64s
>   (same as peak period) except two brief outliers (Octopus 28s on 8/14,
>   which actually got 1111 views/61% retention — no evidence short length
>   hurt it).
> - **Two individual videos flopped hard, well below the channel's normal
>   500+ floor:** Facts 29 (volcanoes/lava-lake topic) 117 views, Facts 36
>   (bees, ep45) 331 views. Worth reviewing their hook lines specifically —
>   the Shorts algorithm tests every upload on a small audience first and
>   expands distribution based on early swipe-through/completion signals,
>   so a weak first 1-2 seconds can suppress total reach independent of
>   overall retention.
> - **Channel is only ~3.5 weeks old (launched 2026-07-25).** New-channel
>   exploratory-distribution boosts commonly taper after the first few
>   weeks as YouTube settles into steady-state distribution — a plausible
>   partial explanation that isn't a content problem and isn't fixable by
>   changing the format.
>
> **Recommendations given to the owner:** don't reactively change format
> (duration/A-B arm) — the data doesn't implicate either. Do tighten hook
> lines specifically, since that's the best-supported lever given retention
> is fine but reach dipped. Prioritize topics resembling the channel's
> proven biggest hits (Facts 4/12/18/21-26, the moa story) over narrower
> ones. Review Facts 29 and Facts 36 individually for a weak hook. Finish
> the countdown-vs-listicle A/B test (§10, currently tied 3-3, needs one
> more build per arm) before layering in a new experiment; a hook-style
> test is the logical next one once it wraps, since hooks are what the data
> actually points at.

> ### 2026-08-18 02:00 build — ep49 Cardiff Giant story + ep50 coffee facts
>
> **Both 2026-08-17 slots published** (ep42 Emu War 16:30, ep45 bees 22:30),
> so this job re-staged `storage/todays_uploads.json` for 2026-08-18 with the
> two already-approved episodes next in the queue table set 2026-08-17
> 10:32: ep46 Swiss hijack → 16:30, ep48 ancient Greece facts → 22:30. Both
> carry the owner's 2026-08-17 batch approval ("כולם מאושרים"); slotting them
> recorded an existing approval and implied no new one. **ep47 (gagaloris)
> remains queued for 2026-08-19 16:30 per that table — untouched by this
> job.** The 2026-08-19 22:30 slot has no queued content; see below for what
> fills it.
>
> **Disk-space methodology bug found and fixed before cleanup.** The first
> attempt to find safe-to-delete `storage/tasks/<uuid>` dirs under-matched,
> because marking an episode PUBLISHED overwrites `episode_log.csv`'s
> `status` field — which sometimes held the only recorded UUID-path
> reference, making published episodes' directories falsely look orphaned.
> Fixed by checking the full raw CSV text for each UUID, cross-referenced
> against a "must keep" list built only from currently
> unpublished/queued/awaiting-approval rows (the ones whose `status` field
> is guaranteed not yet overwritten). Cleaned ~14 truly-orphaned dirs,
> 95%→81% disk usage, 7.2GB free — comfortable for tonight's two renders.
>
> **Built ep49 (Cardiff Giant, 1869 hoax — FIRST time hoax/con-artist
> topic).** Locked via `--from-dry-run`
> (`docs/skill/plans/locked_scripts/cardiffgiant_locked.json`) since the
> Barnum fake-of-a-fake / lawsuit-dismissal payoff is a precise sequence
> that a rewrite could easily flatten. One AI clip (mandatory hook only —
> shovel revealing pale stone); the other 7 segments are real Pexels footage
> pinned by exact file path. **Mtime-pairing caught again:** the courtroom
> segment's candidate was first assumed, from its thumbnail, to be a
> costume/cosplay judge — re-extracting a higher-resolution frame showed it
> was actually stylized studio courtroom stock, accepted since it makes no
> false claim about a specific real case. 64.28s, just over the ~63s soft
> ceiling (kept — the six-beat structure needed the room). Sent to Telegram,
> **awaiting owner approval**, not slotted anywhere. Full sourcing:
> `docs/skill/story_cardiffgiant_lead.txt`, `episode_log.csv` row 49.
>
> **Built ep50 (coffee myths/facts — FIRST time this topic).** A/B tally
> was tied 3-3 (A={33,41,45}, B={40,43,48}) going in; tie broken by
> alternating off the most recently-built facts episode (ep48, Arm B), so
> this is **Arm A run #4** (countdown). Written `--pre-written`
> (`docs/skill/facts_coffee.txt`) since 3 of 6 facts carry hedges
> (Beethoven's 60-beans story is biographer-sourced and unproven; the
> Ethiopian goat-herder discovery is legend, not settled; the "coffee is the
> 2nd most traded commodity" claim is explicitly busted as false — real rank
> ~98th per MIT's Observatory of Economic Complexity). All three hedges
> survived into the auto-generated caption without flattening this time —
> checked and left as-is, no hand-rewrite needed. **Confirmed Pexels gap:
> "civet cat"** returns only wrong-species/non-representative matches (a
> fence cat, an obscured dark animal, a domestic ginger tabby) — worked
> around with coffee-beans-roasting footage instead of forcing a wrong
> animal, since the facts format's AI budget is hook-only, not per-fact.
> Zero AI clips needed. All 8 segments pinned via `--segment-clips` using
> file paths from **isolated single-term probes** (one term per probe
> directory) specifically to dodge Pexels's known cross-call result-order
> instability — every candidate's duration checked against its segment
> length before pinning, all comfortably safe. 63.22s (at the soft
> ceiling), 27.0MB. Sent to Telegram, **awaiting owner approval**, not
> slotted anywhere. Full outcome: `episode_log.csv` row 50.
>
> **Neither new build was auto-slotted into the open 2026-08-19 22:30
> slot.** Per standing practice, a self-sourced build does not become
> approved just because a slot happens to be open — both ep49 and ep50 go
> into the normal "sent to Telegram, awaiting approval" backlog exactly
> like ep42/45/46/47/48 originally did. **2026-08-19 22:30 remains
> unfilled** until the owner approves something for it; the backlog is now
> ep49 + ep50, both flagged here explicitly rather than left to pile up
> silently.

> ### 2026-08-16 02:00 build — ep45 bees (facts only; no story built)
>
> **Both 2026-08-15 slots published** (ep40 Vikings 16:30 `YFn3yQXVYIQ`,
> ep44 Wojtek 22:30 `vnUoTVMnlY8`), so `storage/todays_uploads.json` was
> consumed. **This job re-staged it for 2026-08-16** with the two
> already-approved episodes: ep41 mushrooms (Facts 34) → 16:30, ep43
> Antarctica (Facts 35) → 22:30. Both carry the owner's 2026-08-15 chat
> approval; slotting them recorded an existing approval and implied no new
> one. **Note for future build jobs: nothing else stages this file.** The
> 13:00 Routine that used to do it is gone (only 02:00 / 16:30 / 22:30
> remain), so if the 02:00 job does not write tomorrow's file, both publish
> jobs find a stale date and silently skip.
>
> **Built: ep45 bees, A/B Arm A (countdown), 54.56s.** Arms were tied 2/2;
> broke the tie by alternating off the most recent facts *build* (ep43,
> Arm B), per §10's corrected count-builds-not-approvals rule.
>
> **NOT built: the story episode.** §10 item 2 asks for one story + one facts
> per day and two story leads are sourced and fact-checked
> (`story_swisshijack_lead.txt`, `story_gagaloris_lead.txt` — the Swiss
> hijack was selected: nobody harmed, no living-celebrity likeness, and the
> "Switzerland's air force only works business hours" twist fits the brand).
> The session ran out of budget after the bees episode's two render passes.
> Flagged rather than half-built: an unverified episode is worse than a
> missing one. **2026-08-17 is still coverable** — ep45 plus ep42 (Emu War,
> STORY, built and awaiting approval since 2026-08-14) fill both slots if
> ep42 is approved. If ep42 is dropped, 2026-08-17 needs a story built.

> ### 2026-08-16, later same session — ep46 Swiss hijack story, built on direct request
>
> Owner asked directly to build the story that got flagged as not-built above.
> **Real fact-check catch before scripting: the lead's payoff was wrong.**
> `story_swisshijack_lead.txt` originally claimed "Switzerland granted him
> asylum rather than prosecuting him." Independent re-verification found this
> does not hold up — Swiss prosecutors declined to prosecute at all (not the
> same as asylum) after a panel unanimously found the hijacker had been in a
> state of complete paranoia during the hijacking; he was ordered into
> mandatory psychiatric treatment instead of prison. "Granted asylum" is
> unconfirmed and at least one source directly contradicts it. The corrected
> payoff is arguably a better twist than the original — more specific, more
> surprising, and it's actually sourced. **Lesson: a lead's payoff line
> deserves the same independent verification as its setup facts — leads
> supplied secondhand (Facebook screenshots, in this case) can get the ending
> wrong even when the middle of the story checks out.** Full correction and
> sourcing in `docs/skill/story_swisshijack_lead.txt` and `episode_log.csv`
> row 46.
>
> **Two AI clips used** (hook + fighter-jet-scramble), within the STORY
> budget. The fighter-jet segment is a newly confirmed Pexels gap — three
> different search terms all returned the same handful of civilian
> airshow-crowd footage, wrong tone and containing identifiable bystanders.
> **Also caught before rendering: a Pexels candidate for the
> psychiatric-treatment segment showed a woman in a wheelchair** — rejected,
> since the real hijacker is male and the wheelchair implies an unrelated
> physical disability; same failure class as ep28 Kenoyer's gender-mismatched
> prison photo. Used an empty, peopleless hospital corridor instead.
>
> **Noted a pipeline quirk, not a defect:** `story-result.json`'s
> `ai_generated_segments` field just lists every index passed via
> `--segment-clips`, not which ones are actually AI-sourced. This build passed
> real pinned Pexels files for 5 of 7 segments (to dodge Pexels's known
> result-reordering instability) plus 2 genuine AI clips, and the field lists
> all 7. Do not trust that field name at face value in a future session.

> ### 2026-08-17 10:32 — all 5 backlog episodes approved at once, queue set
>
> Owner reviewed all 5 unapproved videos sent individually to Telegram
> (no upload kit, just the raw files for review) and replied **"כולם
> מאושרים"** — all approved, in a single message covering ep42, 45, 46,
> 47, 48 together. **Backlog is now 0.**
>
> **Queue order, oldest-first, alternating story/facts so none land
> back-to-back** (last published before this batch was ep43, a facts
> episode, so opening the queue on a story is safe):
>
> | order | slot | episode | format |
> |---|---|---|---|
> | 1 | 2026-08-17 16:30 | ep42 Emu War | STORY |
> | 2 | 2026-08-17 22:30 | ep45 bees | facts (Arm A) |
> | 3 | 2026-08-18 16:30 | ep46 Swiss hijack | STORY |
> | 4 | 2026-08-18 22:30 | ep48 ancient Greece | facts (Arm B) |
> | 5 | 2026-08-19 16:30 | ep47 gagaloris | STORY |
>
> **`storage/todays_uploads.json` only holds today's two slots** (per the
> existing convention), so it currently has ep42/ep45 staged for
> 2026-08-17. **The 2026-08-18 and 2026-08-19 02:00 build jobs need to
> stage the remaining queue from this table** — ep46+ep48 for 08-18, then
> ep47 for one of 08-19's two slots (the other 08-19 slot needs a fresh
> build, or check whether the queue itself is not to be treated as fixed
> since new approvals may land before then). **Do not build fresh
> episodes to fill 08-18 or the first 08-19 slot — these three are
> already built, verified, and approved,** just not yet slotted. Building
> new ones instead would leave already-approved content sitting unused.

> ### 2026-08-17 02:00 build — ep47 gagaloris story + ep48 Greece facts
>
> **Both 2026-08-16 slots published** (ep41 mushrooms 16:30, ep43 Antarctica
> 22:30), so `todays_uploads.json` needed a fresh file. **Nothing is approved
> yet, so it was staged with both slots `approved: false`** rather than left
> pointing at the stale 08-16 date — the 16:30/22:30 jobs will read this and
> send a clear "nothing approved" notice instead of silently finding a stale
> file.
>
> **Backlog is now 5 unapproved, all flagged explicitly to the owner**: ep42
> (Emu War STORY, since 2026-08-14 — 3 days old), ep45 (bees), ep46 (Swiss
> hijack STORY), ep47 (gagaloris STORY), ep48 (Greece facts). This matches
> the 2026-08-15 precedent (build to 5, flag clearly, do not build a 6th/7th
> without an answer) rather than halting early — ep42's age is the one thing
> that most needs the owner's attention.
>
> **Built ep47 (gagaloris — Lady Gaga bitten by a slow loris on a 2014 video
> shoot).** Unlike the Swiss hijack lead, every claim in this lead held up on
> independent re-verification — no corrections needed. Two AI clips (hook +
> venom-description beat) after confirming Pexels only returns lemurs and
> marmosets for "slow loris primate" searches — wrong species, would have
> directly contradicted "looks like a stuffed toy" narration. **Real defect
> caught and fixed:** a Pexels clip selected for the "she laughed it off"
> segment was mischaracterized during selection as generic film-crew
> footage — it actually showed a person in a lion-style mask playing a tuba
> on a photo backdrop, tonally incoherent against the narration. Swapped,
> re-verified all 7 segments, zero regressions.
>
> **Built ep48 (ancient Greece facts, Arm B flat listicle).** First-time
> topic, six independently-verified facts, three carrying hedges (democracy's
> ~80% exclusion is an approximation across sources; the Parthenon's
> curve-to-correct-an-illusion explanation is contested by at least one
> recent paper, not settled fact; the Hippocratic oath in modern use means
> *modernized* versions, not the literal ancient text) — built `--pre-written`
> for exactly this reason. **The auto-generated caption reintroduced the
> Parthenon overreach anyway** ("designed to trick the eye" as flat fact),
> confirming again that hedges need checking at every text-generation step,
> not just the script. Hand-rewritten before sending. **Confirmed Pexels gap:
> "Spartan warrior helmet"** returns a street scene, a costumed horseback
> reenactor, and empty rocks — nothing usable, joining WWII/Vikings/lava-lake
> on the known-gap list. Used a generic marble bust as a visual echo rather
> than force it or spend a facts-episode AI clip on a non-hook segment (the
> AI budget for facts is hook-only per §10 item 3). **One QA-only note, not a
> defect:** the single most literal fact (Parthenon columns) got a hazier,
> less specific shot than was available — logged rather than re-rendered,
> same tier as ep35's chess-boxing note.
>
> **`--pre-written` is now the default for any fact carrying a hedge.** The
> dry run caught the LLM rewrite introducing three errors at once, including
> one flatly wrong claim ("its angle points toward the sun" — the waggle
> angle encodes bearing *relative to* the sun) and a mangled payoff that
> merged "not endangered" and "they are livestock" into a phrase meaning the
> opposite, while dropping "researchers argue" so a contested claim became a
> flat assertion. See `episode_log.csv` row 45.
>
> **Disk hit 95% (2.2G free) and was cleaned to 4.5G** by deleting task dirs
> for 12 already-published episodes. Builds cost ~365MB each and re-renders
> are routine, so this needs watching. **Only delete dirs whose episode is
> PUBLISHED** — ep41/ep42/ep43 dirs are queued for upload and must survive.

> ### 2026-08-15 02:00 build — ep43 Antarctica + ep44 Wojtek
>
> **Both 2026-08-14 slots published** (ep33 Rome 16:30, ep37 Inky 22:30), so
> `storage/todays_uploads.json` was fully consumed and **still dated
> 2026-08-14** — a fresh file is needed for 2026-08-15, which has **nothing
> approved in it**.
>
> **Backlog decision.** Three finished episodes were already awaiting approval
> (ep40 Vikings 47.6s, ep41 mushrooms 47.4s, ep42 Emu War 49.5s). Built 2 more
> anyway rather than skipping, and flagged the pile to the owner explicitly
> instead of silently stacking. **Backlog is 5 unapproved — do not build a 6th
> and 7th without an answer on ep40/41/42.** Note those three were built under
> neither regime cleanly (they are ~48s, between the old ~55s and the
> short-lived ~30s); with the rewind they are much closer to spec than they
> were, so the "off-spec, drop them?" framing sent to the owner on 2026-08-15
> is now mostly moot.
>
> **Built:** ep43 Antarctica (facts, **Arm B flat listicle**) and ep44 Wojtek
> the soldier bear (STORY). Veo token probed alive before both. Both were
> first built at ~33s under the short-lived rule and then **rebuilt at full
> length** after the rewind — see their `episode_log.csv` rows for both
> durations.
>
> **Pexels gap confirmed again, two new categories.** No usable *lava lake*
> footage (returns CGI graphics, an industrial furnace, turquoise crater
> lakes, and a tropical village) and no usable *WWII-era* footage — "soldiers
> marching vintage war" returns **Napoleonic reenactors**, the same trap the
> D-Day episode hit. Add both to the sloths/glass-frogs/Vikings list of
> categories where the fix is an AI clip or a verified visual echo, not a
> better search term.
>
> **Defect caught on ep44 and fixed by re-render:** the enlistment beat's
> Pexels clip showed a **Turkish-layout typewriter and the legible name
> "FERİDE"** under narration about a *Polish* army paybook — third instance of
> the read-the-on-screen-text failure (after ep32's Süper Lig banner and
> ep33's ELEKTRIK/SU labels). Replaced with a generated paybook clip prompted
> for *deliberately illegible* writing, which is the reusable trick here: an
> AI document shot with shallow depth of field cannot contradict the
> narration the way real foreign text does.

Measurements are dated. Anything not marked as measured is reasoning, and is
labelled as such — several conclusions below rest on very few data points, and
saying so is more useful than sounding confident.

---

## 0. State as of 2026-08-08 09:40 Israel — read this first

A pinned summary for picking up a fresh session fast. Full rationale for every
line here is in the dated sections below and in `SKILL.md`; this is only the
"what's true right now" digest.

**CORRECTION 2026-08-13 21:xx — the pending-approval backlog was reported as
4 deep but was actually only 2. Ep36 (Egypt, "Facts 30 🏺") and ep38 (sharks,
"Facts 31 🦈") were BOTH ALREADY PUBLISHED, uploaded manually by the owner
outside this session/pipeline (same pattern as ep35's manual chess upload)
— neither upload was ever recorded back into `episode_log.csv` or here,
so a fresh session reading only the docs had no way to know and kept
listing them as awaiting approval.** Caught by pulling the real YouTube
uploads playlist directly (`channels.list` → `playlistItems.list` →
`videos.list` via the Data API, `docs/skill/youtube/token.json`) and
diffing video titles against `episode_log.csv`'s "awaiting approval" rows,
after the owner said "some I uploaded myself." `episode_log.csv` rows
36/38 are now corrected with the real video ids/dates/view counts.
**Lesson: when the owner may have uploaded manually (they have done this
before — ep35 chess), don't trust `episode_log.csv`/this file's "awaiting
approval" status at face value if it's been more than a few hours — pull
the actual channel upload list and cross-check titles before reporting a
backlog number or risking a double-upload.** The real backlog after this
fix is 2: **ep33 (ancient Rome)** and **ep37 (Inky the octopus story)** —
confirmed absent from the live channel by title.

**UPDATE same evening — both approved live in chat by the owner** ("הם
מאושרים יעלו מחר" — they're approved, will go up tomorrow). Written into
`storage/todays_uploads.json` for **2026-08-14**: ep33 (Rome) → 16:30 slot,
ep37 (Inky) → 22:30 slot, both `approved: true`/`published: false`. Also
recorded in `episode_log.csv` rows 33/37. **Pending-approval backlog is now
0.** The owner separately asked, independent of the backlog state, to build
**2 new episodes at tonight's 02:00 build regardless** — so the 02:00
2026-08-14 build job should build 2 new episodes as normal (the backlog
being clear makes this the default choice anyway, but note it was also an
explicit standing instruction for tonight specifically, not just inferred
from an empty backlog).

**UPDATE 2026-08-14 04:00 build.** Cron was temporarily moved 02:00→04:00 IDT
for this one firing only (owner request, unrelated to content). Veo token
re-checked via `--probe`, still dead — per §10 item 4, the STORY build was
paused (not built) rather than shipped without its AI clip; a Telegram
message asked the owner for a fresh `docs/skill/veo/token.json`. Built 2
facts episodes instead (§10's flex-to-2-facts rule) to fill both 8/15 slots:
**ep40 Vikings (Arm B, flat listicle)**, sent to Telegram, awaiting approval
— see `episode_log.csv` row 40 for the footage-substitution detail (Pexels
has essentially no real Viking-era footage, same class of gap as
sloths/glass-frogs; built entirely on verified visual echoes instead).
**ep41 mushrooms/fungi (Arm A, countdown)** — arguable #1 payoff is the
real 2022 Guinness "largest organism" title dispute between the Oregon
honey fungus and a Shark Bay seagrass meadow, genuinely contested by
area/weight/definition, which fits the countdown format's disagreement-CTA
requirement unusually well. **Also caught and fixed while in the area**:
ep33 (Rome)'s title was still "Facts 27" in its `result_json`, but the live
channel's highest number had moved to "Facts 32" since that build — left
uncorrected it would have published tomorrow as a numerically-regressive
title. Fixed to "Facts 33" (metadata only, no re-render needed, same
precedent as the 2026-08-06 title-sync). **Flagging, not fixing: ep33's
`result_json` caption is still the original auto-generated recall-style
text** ("name the exact year MIT and Harvard...") even though
`episode_log.csv` row 33 says a hand-written disagreement-style caption was
sent to Telegram instead — that correction apparently never got written
back into the JSON file. Since `upload_video.py` reads caption straight
from this file, the automated 16:30 upload would ship the wrong
(recall-style) caption unless this is corrected before then. Did not
guess/overwrite it without the exact approved text on hand — owner should
confirm/paste the correct caption, or re-approve the recall-style one if
that's actually fine.

**PUBLISHED 2026-08-14 16:47 Israel** by the automated 16:30 job — video id
`1I1TXQS4pLw`, https://youtube.com/shorts/1I1TXQS4pLw, live title "Random
But True Facts 33 🏛️". Sequence was re-verified against the live channel
immediately before upload (highest existing was "Facts 32"), so the
2026-08-14 04:00 retitle from "Facts 27" held up. **The 22:30 slot (ep37,
Inky the octopus, STORY) followed at 22:33** — video id `rjjDcnuzcOk`,
https://youtube.com/shorts/rjjDcnuzcOk, 27.0s. **Both 2026-08-14 slots are
now published and `storage/todays_uploads.json` is fully consumed** — the
next build job needs to stage a fresh file for 2026-08-15. The three
episodes built for those slots (ep40 Vikings, ep41 mushrooms, ep42 Great
Emu War) are all still **awaiting owner approval** — none has a slot
assigned, so 2026-08-15 has nothing approved in it yet.

**RESOLVED 2026-08-14 — owner decision: ship ep33 with the recall-style
caption as-is, do not chase down the lost hand-written text.** Explicitly
**not** a reversal of the disagreement-CTA rule (§5d) — it stays the
required convention for every countdown-format caption going forward, on
ep34 onward. This is a one-off exception for ep33 specifically, made
because the originally-approved replacement text was never saved anywhere
retrievable, not because recall-style CTAs are fine again.

**UPDATE 2026-08-14, same session — Veo/YouTube token fixed, story resumed.**
Owner sent a fresh combined-scope token (same client_id and scopes already
shared by both `docs/skill/youtube/token.json` and `docs/skill/veo/token.json`
— this project has apparently always used one shared credential for both
despite `veo/authorize_local.py`'s docstring describing them as meant to stay
separate). Installed to both files, verified with `--probe` (Veo) and a live
Data API call (YouTube) before trusting it. Per §10 item 4's stop-and-ask
policy, immediately resumed the paused STORY build: **ep42, the Great Emu
War (Western Australia, 1932)** — self-sourced, fact-checked, 2 AI clips
(hook + soldiers-arrive beat), sent to Telegram awaiting approval. Full
detail in `episode_log.csv` row 42. This is the first-ever confirmation that
the halt-and-ask policy actually resumes work quickly once unblocked, not
just that it prevents shipping a compromised video — worth keeping as the
default going forward.

~~**STANDING RULE 2026-08-08 — every episode opens on an AI-generated hook
clip.**~~ **SUPERSEDED 2026-08-13/14 — see §10.** The owner's original
instruction (generate the first frame of every video with AI, because that
is the frame you have full control over) still applies **as the default
for STORY format only**. For **facts/countdown format, the AI hook is now
optional/opportunistic** — generate one only when Pexels genuinely cannot
supply a strong hook shot, same test as the skill's original design, not
on every video regardless. Reasoning and the data behind this reversal are
in §10. The rest of the original rule is unchanged where AI clips ARE
used: budget is the mandatory-when-used hook plus up to two more AI clips
without asking (a fourth needs approval), and **Pexels footage must stay
in the mix** so an episode never reads as all-AI. Full guidance on what
makes a hook image strong vs. weak is in `ai-footage-fill/SKILL.md`.

**Live/pending right now:**
- Ep20 (Facts 20, human body) is **published, public**, video id `MsvTGDudZ-U`.
  Its live YouTube title reads "Random But True Facts 19 👀" — a mislabel from
  a manual upload the owner did outside a session; owner declined the fix.
- Ep21 (D-Day crossword) is **published, public**, video id `S_zjnvbzZXw`.
  Flagged 2026-08-07 as underperforming (27 views); investigated, no fixable
  cause found — see the dated §5c entry.
- Ep22 (pizza, "Facts 20 👀") **published, public**, video id `yfuSDGdpTw4`,
  16:30 slot 2026-08-06.
- Ep23 (space facts, "Facts 21 👀") **published, public**, video id
  `EtNhXZdSKZc`, 22:30 slot 2026-08-06.
- Ep24 (big cats, "Facts 22 👀") **published, public**, video id
  `DsoMMdBDb7Q`, 16:30 slot 2026-08-07.
- Ep25 (weather phenomena, "Facts 23 👀") **published, public**, video id
  `vo1w94hVmjY`, 22:30 slot 2026-08-07.
- **Ep26 (moa story) and ep27 (insects, "Facts 24 👀")** — today's 2026-08-08
  09:00 build. Both **approved and published, public**: ep27 at the 16:30
  slot, video id `ygEgNnja-2I`; ep26 at the 22:30 slot, video id
  `m8MyE4SPKZ0`, published live by the automated 22:30 job.
  This is the first STORY built since ep21, applying the 2026-08-07 20:00
  report's concrete action (both prior stories now beat the facts baseline on
  retention — see §5c). Ep26 is the moa story, script locked since
  2026-08-03, first time actually rendered — cleanest frame-verification pass
  of the session (avg footage specificity ~4.75/5), just ran long at 68.68s
  (allowed for stories, 30-90s). Ep27 is the channel's first live
  ranked-countdown episode, topic insects (fresh outlier research — calendar
  and §5a list still exhausted), two footage bugs (empty-leaf hook cuts, a
  mismatched crate-of-bugs shot) caught by frame verification and fixed via
  clip-override splice before delivery. Full detail in `episode_log.csv` rows
  26/27. Slot assignment: ep27 (insects) → 16:30, ep26 (moa) → 22:30. Neither
  slot has been recorded into `storage/todays_uploads.json` yet — that's the
  13:00 job's job, once the owner approves.
  **Same-morning follow-up on ep26:** owner flagged that both "New Zealand"
  mentions (the mid-episode fact and the outro) showed generic fern-leaf
  close-ups and felt repetitive/disconnected from the words. Generated a
  third AI clip (Veo 3.1-fast) — a sweeping aerial shot over misty NZ
  rainforest with mountains — and spliced it into both spots, replacing the
  fern footage. `story-result.json`'s `video_file` was updated **in place**
  to point at the corrected, recompressed render (46MB) since that field is
  what `upload_video.py` actually reads — the corrected version was resent to
  Telegram and is what should be approved, not the original send. Full
  detail (prompt, verification, AI-segment count) in `episode_log.csv` row
  26's updated outcome_note.
  **Second same-morning follow-up, this time on ep27:** owner caught that the
  insects episode's transition sound was still identical at every cut — a
  correct catch, ep27 was built *before* the SFX variety/bridging fix (§5e)
  landed later that same morning. Fixed by re-running only the SFX pass
  against the already-footage-fixed `with-captions-fixed.mp4` (no need to
  re-render footage, captions, or TTS) with the new 4-variant pool. Verified
  on the real delivered audio by diffing the post-SFX track against the
  pre-SFX track (isolates the added sound from narration): 3 distinct
  variants across 6 transitions, no immediate repeats, every onset lands
  0.10–0.18s before its nominal cut point. `viral-result.json`'s `video_file`
  updated in place again. **Lesson for future same-day pipeline fixes: a code
  fix does not retroactively apply to a video already rendered before the fix
  landed — check whether anything built earlier that same session needs the
  same re-application, don't assume "the code is fixed" means "every
  already-sent file reflects it."**

**STORY RATIO RAISED 2026-08-09 — stories now run ~1 in 3 uploads, not
1 in 4-5.** Owner-approved off the retention evidence (stories 51.2% vs facts
45.2%, counting only >=100-view videos). Full reasoning and the caveats are in
§5's upload-flow rule. Paired decision: **source story leads independently**
instead of waiting for the owner to supply them, since lead supply — not the
ratio — is what actually caps story output. Anything the owner sends still
jumps the queue.

**2026-08-09/10 sequencing, corrected once by the owner mid-conversation —
this is the final version, not the first plan floated:** the first idea (an
extra 19:30 slot today for Kenoyer) was superseded before it ever fired; the
one-shot wakeup for it was cancelled. Actual plan:
- **2026-08-09 16:30:** Facts 25 (sleep) — normal slot Routine.
- **2026-08-09 22:30:** Kenoyer true-crime story — normal slot Routine, swapped
  in for what was originally Facts 26 (trees) at this slot.
- **2026-08-10 16:30:** Facts 26 (trees) — moved here from 2026-08-09 22:30.
- **2026-08-10 22:30:** Great Auk story — unchanged from the original plan.
All four are already owner-approved for these exact slots. **Consequence for
tomorrow's 09:00 job: build ZERO new episodes** — both 2026-08-10 slots are
already filled and approved. Tomorrow's 13:00 job should find
`storage/todays_uploads_2026-08-10.json` pre-staged with both slots
`approved: true` (promote it to `storage/todays_uploads.json`, or re-derive
from `episode_log.csv` rows 29/31 if that staged file is missing) rather than
asking the owner to re-confirm anything.

- **Ep30 (Facts 25, sleep) and ep31 (Facts 26, trees)** — today's 2026-08-09
  09:00 build, **sent to Telegram, awaiting approval**: ep30 → 16:30, ep31 →
  22:30. Both facts/ranked-countdown, both first-time categories. **Two facts
  episodes rather than a story because the previous upload (moa, 22:30
  2026-08-08) was itself a story** and the flow rule forbids back-to-back
  stories — the two finished stories below stay in inventory instead. §5c
  actions applied: hook shape logged (both contest-form), footage specificity
  rated pre-delivery (ep30 ~4.25/5, ep31 ~4.6/5), and both held inside the
  50-58s core range (53.5s / 54.1s). Live channel was checked before titling:
  highest existing "Facts N" was 24, so these are 25 and 26. Full detail in
  `episode_log.csv` rows 30/31.

  **UPDATE 2026-08-10 16:30:** ep31 (trees) hit a real upload failure at its
  16:30 publish attempt — `docs/skill/youtube/token.json`'s refresh token was
  expired/revoked (`invalid_grant`, exactly 7 days after the token was
  created, consistent with Google's 7-day refresh-token expiry for OAuth
  apps still in "Testing" publishing status — see `SKILL.md` §8j). Owner
  notified via Telegram, sent a fresh `token.json` shortly after, and also
  asked live in-conversation for a one-time schedule change: publish ep31
  immediately once the token was fixed, but move ep29 (Great Auk)'s normal
  22:30 publish to **2:00am Israel time (2026-08-11), today only**. Both
  handled: ep31 published live immediately (`h2RlkUXI7YA`); ep29 uploaded as
  private with YouTube's own `--publish-at 2026-08-10T23:00:00Z` (=02:00
  IDT) so YouTube itself flips it public at that exact time — a one-off use
  of the `--publish-at` escape hatch (`SKILL.md` §8e), not a reversal of the
  2026-08-04 direct-publish-at-slot-time decision (§8i). `storage/
  todays_uploads.json`'s 22:30 entry was marked `published: true` right away
  (the upload itself succeeded) specifically so tonight's normal 22:30
  Routine sees it and skips instead of double-uploading. Tomorrow's routine
  goes back to normal live 16:30/22:30 publishing — this was a today-only
  exception, not a new standing schedule.

- **Ep32 (internet culture, the "6-7" meme)** — built 2026-08-09 from an
  owner-supplied lead (a fully-written Hebrew 6-fact draft citing Wikipedia).
  **Sent to Telegram, awaiting approval — no slot assigned.** Independently
  fact-checked before use anyway, per standing discipline, and caught two
  real errors in the draft: the basketball coincidence is LaMelo Ball's OWN
  height (6'7"), not "his brother's"; and the "meaningless slang used by
  kids" description is Dictionary.com's own framing of their own Word of the
  Year pick, not Merriam-Webster's — Merriam-Webster's actual 2025 word was
  unrelated ("slop"). See `docs/skill/plans/facts/sixseven_lead.txt`.
  Unusually real-people-dense topic (a real minor at the center of one fact,
  named athletes, a member of Congress) — the mandatory AI hook is a purely
  abstract "6/7 numerals bursting from a phone" concept with zero people, and
  every Pexels segment is generic/unbranded B-roll, never claiming to show
  any specific named individual. First render ran long (70.16s) because the
  length-estimate formula only covered the 6 facts and missed the hook/outro's
  own spoken time — trimmed twice to land at 57.76s. **Two real footage
  defects caught on frame verification**, both fixed by pinning single
  pre-verified clips via `--segment-clips` rather than trusting a re-probed
  term: a phone-screen cut showed a real, legible, unrelated ad for another
  creator's course; a stadium-crowd cut showed Turkish Süper Lig fans and
  banner text landing exactly on the words "a Premier League" — direct
  footage-contradicts-narration. (Two follow-up searches for literal Premier
  League footage returned Hungarian and AFC Asian Cup branding instead —
  Pexels appears to have no real EPL footage, so this settled for
  brand-clean generic crowd energy rather than chasing exact-league
  accuracy.) Final: 57.76s, 27.4MB. Full detail in `episode_log.csv` row 32.

- **Ep33 (ancient Rome, ranked countdown)** — self-sourced 2026-08-10 (no
  owner lead pending; own judgment call to fill the still-empty 2026-08-11
  pipeline slot while both of 2026-08-10's slots were already filled from
  the prior day's approved plan). **Sent to Telegram, awaiting approval — no
  slot assigned.** Fresh category, all 6 facts independently sourced and
  verified (`docs/skill/plans/facts/rome_lead.txt`). Applied the ep32
  length-estimate lesson proactively this time — budgeted hook+outro word
  counts into the estimate up front — and landed at 174 words / 57.72s on
  the **first** render, no post-render trimming needed. **Two real footage
  defects caught on frame verification**, both whole-segment mismatches
  rather than single-cut: segment 4 (the vomitorium/"exit passage" fact,
  term `ancient ruins stone corridor`) returned Angkor Wat / Khmer temple
  ruins for the *entire* segment — the wrong civilization, not just a bad
  cut. Segment 6's first cut — the **#1 payoff segment**, self-healing Roman
  concrete — returned a rustic wooden door with legible modern Turkish
  utility labels ("ELEKTRIK", "SU") instead of any ancient wall at all, on
  the single most important shot in the episode. Both fixed by pinning
  verified clips via `--segment-clips` (`storage/pexels_pinned/`): the
  corridor segment got a genuine stone exit-passage/stairway shot; the
  payoff segment got the actual **Pantheon interior** — the world's most
  famous surviving Roman-concrete structure, a direct thematic match — plus
  a clean aqueduct close-up. Re-rendered with those two segments pinned
  while the five already-good segments kept their verified
  `--segment-terms`, then **re-verified all 8 segments again**, not just the
  2 fixed ones, since a fresh Pexels probe on the untouched segments could
  in principle have introduced a new regression — none did. Also: the
  auto-generated caption asked a recall question ("name the exact year..."),
  which contradicts the ranked-countdown format's own rule that the CTA
  should invite disagreement, not recall — discarded and hand-written to
  match the outro. Final: 57.72s, 42.5MB, no compression needed. Full detail
  in `episode_log.csv` row 33.

- **Ep34 (volcanoes) and ep35 (chess), both ranked countdown** — self-sourced
  2026-08-11 09:00 build (ep32 and ep33 both still unapproved, so this is a
  new day's build on top of an already-growing backlog — flagged to the
  owner explicitly in the delivery message rather than silently piling up a
  4th and 5th unapproved candidate). **Both sent to Telegram, awaiting
  approval — no slots assigned.** Both fresh categories, all facts
  independently sourced (`docs/skill/plans/facts/volcanoes_lead.txt`,
  `chess_lead.txt`). Both landed inside target length on the first render
  (volcanoes 62.98s, right at the 63s ceiling; chess 53.24s, core range) —
  the length-estimate lesson from ep32/ep33 continues to hold once applied
  proactively. Ep34 used 2 AI clips (hook + Olympus Mons, since no real
  Mars-volcano footage exists — same accepted unphotographable-subject class
  as prior astronomy episodes); ep35 used 1 (hook only). Both clean on full
  frame verification, zero defects on either — first time in a while neither
  build needed a mid-process fix. Minor QA-only note on ep35: the
  "chess boxing" segment never actually cut to its pinned boxing-gloves
  term, staying pure-chess-visual the whole time — not a defect (nothing
  contradicts the narration), just lower specificity, logged per the
  2026-08-10 resolution that footage-specificity is tracked for QA, not
  retention prediction anymore. Both auto-generated captions asked
  recall-style CTAs contradicting the countdown format's disagreement rule —
  both discarded and hand-written to match their outros, with no em dashes
  per the 2026-08-10 standing rule. Full detail in `episode_log.csv` rows
  34/35.

- **Ep28 (true crime, Ina Kenoyer $30M fake-inheritance poisoning)** — built
  2026-08-08 from an owner-supplied lead (a Facebook repost linking to NBC
  News), explicitly flagged as a high-priority viral build with specific
  requirements: more than 3 AI clips combined with real Pexels footage,
  30-45s, full hook/story-arc structure. **Sent to Telegram, awaiting owner
  approval — has no assigned slot.** Independently fact-checked across 6
  outlets before writing a fresh script (never copied the source post's own
  wording) — see `docs/skill/story_kenoyer_lead.txt`. Locked via
  `--from-dry-run` (`docs/skill/plans/locked_scripts/kenoyer_locked.json`).
  4 AI-generated segments (hook, poison, hospital, reveal/twist) — above the
  ai-footage-fill skill's normal 1-2 clip default, justified since the owner
  explicitly asked for it — all deliberately symbolic/non-likeness (silhouette,
  hands-only, empty corridor, empty envelope), since unlike the channel's
  other true-crime-adjacent leads (decades/centuries old), this is a real,
  recently-resolved case with a real convicted defendant and real named
  victim. First render caught two real defects on frame verification, fixed
  before delivery without touching the AI clips or the locked script: (1) the
  Pexels term for the email/relationship beat ("person reading laptop
  shocked") pulled a happy couple high-fiving at a laptop for its first cut —
  wrong tone for a somber narration — swapped to "person reading email
  serious concerned"; (2) the term for the outro/prison beat ("prison bars
  hallway") pulled a **male** prisoner right on the "serving twenty five
  years" line — Kenoyer, the convicted person, is a woman — swapped to
  "woman prisoner orange jumpsuit cell", verified correct gender on
  re-render. Final: 35.96s, 18.1MB (no compression needed). Full detail in
  `episode_log.csv` row 28.

- **Ep29 (animal facts, Great Auk — the extinct original "penguin")** —
  built 2026-08-08 from an owner-supplied lead (a screenshot of a Facebook
  post saying Greenland has no penguins, asking for it to be expanded from
  the internet into a ~30s short). **Sent to Telegram, awaiting owner
  approval — has no assigned slot.** The source screenshot also carried an
  unrelated political meme (a White House repost about Greenland) —
  deliberately left out; the build covers only the natural-history/etymology
  fact. Researched and fact-checked across 6 outlets, see
  `docs/skill/story_greatauk_lead.txt`. Locked via `--from-dry-run`
  (`docs/skill/plans/locked_scripts/greatauk_locked.json`). Hook-twist: real
  penguins are Southern-Hemisphere-only, but the word "penguin" was coined
  first for a different bird — the Great Auk, extinct since 1844, which
  actually lived in the North Atlantic near Greenland. Clean
  frame-verification pass on the first render — no defects found by
  eye-checking single frames — but this turned out to be a real gap in the
  verification method, not a clean pass: 1 AI-generated clip (the auk, zero
  surviving photography — same treatment as the moa episode) had been reused
  across two **adjacent** segments (reveal at 15.2s, payoff at 21.8s), so
  the same 8s clip visibly restarted from frame 0 right next to itself —
  invisible when checking one still frame per segment, obvious in actual
  playback. **Owner caught it** (repeat at 0:16/0:20). Fixed by generating a
  second, visually distinct Great Auk clip (`greatauk_walk.mp4` — wider
  tracking shot, different wave/rock composition) for the payoff segment
  instead of reusing the reveal segment's clip. **Lesson: reusing one AI
  clip across two segments only works when they're far apart in the
  timeline (moa's hook-and-payoff-callback pattern) — adjacent or
  near-adjacent segments need their own distinct clip, or the reuse reads as
  a stutter/loop, not a callback.** Re-rendered, re-verified all 6 segments
  including multiple timestamps across the 3/4 boundary. **Then rebuilt again
  under the new AI-hook standing rule** (see the top of this section): the
  Pexels glacier opening was replaced with a generated shot of a lone penguin
  under the aurora borealis — an image that cannot exist, which is exactly the
  episode's subject, so frame 0 poses the question the narration answers. Now
  3 AI segments (hook, reveal, payoff) against 3 Pexels segments. Final:
  33.68s, 25.0MB. Full detail in `episode_log.csv` row 29.
  **Gotcha worth remembering: the animate step repaints the first frame**, so
  the image reviewed under `--image-only` is *not* the one that ships. Always
  re-check the actual rendered frame 0 after animating — here the repaint
  happened to be stronger, but that was luck, not design.

**FORMAT CHANGE 2026-08-07 — read §5d before building anything.** The flat
6-fact listicle is no longer the default. New facts episodes are
**ranked countdowns**: #6 first, #1 last, with a deliberately arguable #1 and
an outro that asks for the disagreement. Pass **`--counter-mode countdown`**
(mandatory for this format — otherwise the screen shows `6/6` while the
narration says "number one"). The driver was a channel-level diagnosis, not a
retention tweak: 15.5k views had produced **18 subscribers** (0.12%) and **10
comments across 25 videos**. Full reasoning and the exact spec are in §5d.
**Transition SFX is opt-in, OFF by default** since 2026-08-08 (§5e) — pass
`--sfx` to add it. **Background music is also opt-in** — `--bgm` (same
measured -18dB level). Neither is a build's default behavior; both need to
be asked for.

**SFX: tried, fixed twice, then dropped — read §5e's dated entries before
touching the audio pipeline again.** It was on by default for one day
(2026-08-07). Owner feedback that day: the transition sound was always
identical and often felt disconnected from the cut. Fixed both problems in
`viral.add_transition_sfx()` — a 4-variant pool instead of one fixed file
(`resource/sfx/transitions/`, randomized with no back-to-back repeats), and
placement shifted to start ~40% of the sound's own duration *before* the
cut so it bridges the outgoing/incoming shot instead of stinging the new
one. Verified by measuring actual output audio, not by ear. Applied to
today's two live episodes retroactively (the code fix landed after they'd
already been built, so they'd shipped with the old single-sound behavior —
caught by the owner, re-fixed from the cached pre-SFX intermediate file, no
full re-render needed). **Then, same day, the owner said it still didn't
sound good and asked to drop it entirely.** `--sfx` is now opt-in (default
off, argument renamed from `--no-sfx`) — the pool/bridging code stays in the
repo, unused unless explicitly asked for again. Do not re-enable this by
default without being asked; two real fix attempts already didn't clear the
bar.

**New capabilities added this session, both need conscious use, neither is
automatic yet:**
- **`docs/skill/ai-footage-fill/`** — generates a single AI B-roll clip
  (nano-banana first frame + Veo animation) for the one segment per episode
  where Pexels genuinely has nothing usable. Splices in via `--segment-clips`
  on either episode script. Credentials are live and working: Google Cloud
  project `ringed-rune-503816-b8`, OAuth token at `docs/skill/veo/token.json`
  (not a service-account key — the owner's choice, see the skill's own
  SKILL.md for the setup path). **Image model fixed 2026-08-08:**
  `gemini-3.1-flash-image` ("Nano Banana 2") now actually works — the
  earlier "404s on this project despite being listed" note (2026-08-05) was
  a wrong diagnosis, not a real entitlement gap. The model 404s at the
  regional Vertex location (`us-central1`) but works at `location="global"`;
  the owner asked to retry it with that location and it succeeded.
  `generate_ai_clip.py` now calls the primary image model through its own
  client at `image_location` (default `"global"`), separate from the client
  used for the fallback model and Veo (`location`, default `us-central1`) —
  those two live at different Vertex locations on this project and always
  did, `models.list()` just didn't surface that distinction clearly. Still
  falls back to `gemini-2.5-flash-image` on an actual 404, in case
  entitlements ever do change; sidecar JSON records which model really ran.
  Verified end to end: a real call through the CLI produced a genuine
  on-topic image with `gemini-3.1-flash-image`, no fallback needed. Video
  model is `veo-3.1-fast-generate-001`, unaffected throughout — Veo was
  never the broken piece. **Not wired into the
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


**THE DAILY ROUTINE, adopted 2026-08-03, architecture updated 2026-08-04,
trimmed to three Routines 2026-08-11.** The owner set a fixed operating
rhythm and asked for it to run on scheduled wake-ups. Their prompts still
begin by re-reading these docs, because context gets compacted:

| Israel time | UTC cron | Job |
|---|---|---|
| 09:00 | `0 6 * * *` | Build the day's TWO episodes, send both + full upload kits to Telegram, ask for approval. **Uploads nothing.** |
| 16:30 | `30 13 * * *` | Read `storage/todays_uploads.json` — if the 16:30 slot is approved and not yet published, upload it live as public **right now**. Otherwise skip and notify. |
| 22:30 | `30 19 * * *` | Same as 16:30, for the 22:30 slot. |

**2026-08-11: the 13:00 approval-recording job and the 20:00 dashboard job
were deleted at the owner's explicit request** ("תמחק את כל הטריגרים חוץ מ 9
לייצירת סרטונים 16:30 ו 22:30, את השאר נעשה לפי בקשה" — delete every Routine
except 09:00/16:30/22:30, the rest happens on request). Both jobs still
work exactly as documented below; they just no longer fire automatically:
- **Approval recording** now happens live in conversation instead of at a
  fixed 13:00 slot — this was already the de facto pattern before the
  deletion (e.g. the 2026-08-11 chess/volcano approvals both happened this
  way), so nothing about the actual mechanism changes: still write
  `storage/todays_uploads.json` with `"approved": true` only once the owner
  has explicitly confirmed that exact rendered version, same hard rule as
  always.
- **The dashboard** now generates and publishes only when the owner asks for
  it, using the same `generate_dashboard.py` command, the same stable
  Artifact URL, and the same §5c retention-check discipline described
  below — none of that logic changed, only the trigger.
- Only three Routines remain: 09:00 build, 16:30 publish, 22:30 publish —
  all still session-bound (see the failure below for why that is not
  optional) and all still `--confirm --privacy public` only when
  `storage/todays_uploads.json` already has `"approved": true` for that
  slot and date. If the owner ever wants the 13:00/20:00 cadence back,
  recreate them from the prompts still on file in this session's Routine
  history rather than reinventing them.

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

1. **Stories run roughly 1 in every 3 uploads, never back-to-back.**
   **RATIO RAISED 2026-08-09 from 1-in-4-5 to 1-in-3, owner-approved**, using
   exactly the revisit condition the original rule set ("revisit once the first
   stories have real retention data"). That condition is now met — three
   stories have finalized numbers. The evidence, counting only videos with
   >=100 views so the tiny-n outliers don't drive it: **stories average 51.2%
   retention (n=2: ep17 47.2%, ep19 55.2%) against 45.2% for facts (n=15)**,
   and the four most recent finalized facts episodes landed at 31-40%. Ep21's
   82.83% is real but sits on 28 views, so it is excluded from the average
   rather than used to inflate it. Treat this as a direction, not a proof:
   n=2 on the story side is thin, and the ratio should move back if stories
   regress toward the facts baseline as more land.
   The 6-fact countdown is still the channel's identity and still the majority
   of uploads; stories are now a bigger minority, not the new default.
   **The binding constraint is lead supply, not the ratio** — 1-in-3 needs a
   fresh, fact-checked story lead roughly every 1.5 days. Owner decision the
   same day: **source leads independently rather than waiting for the owner to
   supply them** (moa, dollar, D-Day and Great Auk were all self-sourced and
   verified this way), with any lead the owner does send jumping to the front
   of the queue.
2. **~~Never two consecutive uploads from the same topic category.~~
   REVOKED 2026-08-18 — this rule was measurably costing reach.** See the
   "topic drift" analysis section near the top of this file. In short:
   ANIMAL and EVERYDAY/RELATABLE topics carry a median 814 day-1 views and
   a 37% breakout rate; NATURE/SCIENCE and HISTORY/ABSTRACT carry median
   596 and a 6% breakout rate (permutation test on the median gap,
   p=0.0005, n=36). The forced-rotation rule kept pushing the channel out
   of its two winning categories because they "had just been used," and
   the topic mix flipped from 54% animal / 17% history to 17% animal / 50%
   history — exactly tracking the disappearance of every breakout.
   **Replacement rule: target ~50% ANIMAL and ~15% EVERYDAY/RELATABLE
   across any rolling 10 uploads.** Repeating a category on consecutive
   days is fine and often correct; what must not repeat is the specific
   *subject* (rule 4 below still stands, and is the real anti-staleness
   mechanism). Variety was never the thing driving this channel — it was
   an assumption, and it did not survive contact with the numbers.
3. **The two same-day slots must differ on at least one axis** — format or
   category. Two animal-facts episodes on the same day is exactly the
   "random" feel the owner is asking to avoid. **Softened 2026-08-18:**
   format (story vs facts) alone satisfies this. Do not burn an animal
   slot on a weak category just to make the two slots differ on category —
   an animal story plus an animal facts episode on the same day is
   acceptable and is better than pairing one animal with one chess.
4. **Check `episode_log.csv`'s `key_subjects` column before finalising a
   topic.** Never reuse a specific subject (a species, a brand, a person)
   that appeared in the last 5 episodes. This is the whole reason that
   column exists. **This rule is the one that stays** — "more animal
   episodes" means octopus, then crows, then wolves, not octopus three
   times.

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

## 5d. Ranked-countdown format (adopted 2026-08-07) — CURRENT DEFAULT

**This replaces the flat 6-fact listicle as the default for new facts
episodes.** Owner decision 2026-08-07, in response to the channel being stuck
at a ~1000-view ceiling.

**The diagnosis that drove it** (real numbers, pulled from the API that day):
25 videos, ~15.5k total views, **18 subscribers** — a 0.12% view→sub
conversion, against 0.5–2% for a healthy Shorts channel. And **10 comments
across all 25 videos** (0.064%), despite every single episode ending in a
"comment which fact surprised you" CTA. Likes were fine (2.0%), so the
problem was never "the videos are bad" — it was that nothing gave anyone a
reason to want *more*, and nothing gave anyone anything to *say*. The best
video the channel has ever had is 1508 views; a Shorts breakout is 10k+.
**Nothing has ever escaped the algorithm's initial test pool.** That is a
channel-identity problem, not a per-video retention problem — which is why
the fix is a format change and not another 5% retention tweak.

Note what this diagnosis did *not* blame, because both were checked and
cleared: length (already tested — the long format beat the short one on both
retention and views, see "What this means for our format" in
`shorts_growth_guide.md`; do not reopen it), and production quality (frame
verification catches real defects, but polish was never the ceiling).

**The format:**

1. **Hook must promise the #1 and invite disagreement.** Not "what if X?" —
   something closer to "these are the 6 <things>, ranked, and you're going to
   argue about number one." The hook's job is now to set up a *contest*, not
   just curiosity.
2. **Six items, counted DOWN: #6 first, #1 last.** The strongest item goes
   last, in the payoff position. This is the completion-compulsion structure
   the channel already adopted, but with the viewer told *explicitly* how far
   the payoff is.
3. **#1 must be genuinely arguable** — a defensible pick that a reasonable
   person could rank differently. A #1 nobody can dispute produces the same
   zero comments we already have. This is the single most important line in
   this section: the ranking is the engagement engine, and a ranking with an
   obvious answer is not a ranking.
4. **The outro asks for the disagreement, not a recall question.** "Tell me
   what should have been number one" beats "comment which surprised you" —
   the old CTA is measurably dead (10 comments / 25 videos).
5. **Pass `--counter-mode countdown`.** The on-screen counter then reads
   `#6 … #1` instead of `1/6 … 6/6`. This is mandatory for this format —
   with the default `progress` mode the screen would show `6/6` while the
   narration says "number one", and the two numbers visibly contradict.
6. **The narration speaks the rank too** ("Number six: …", "And number
   one: …"), not just the on-screen counter. It is deliberate redundancy,
   not a mistake: a large share of Shorts viewing is sound-off (the counter
   carries it) and a large share is screen-glanced-away (the voice carries
   it). Write it with `--pre-written` so the rank wording survives verbatim
   — an unconstrained LLM rewrite reliably drops or reorders the numbering,
   which breaks the countdown against the counter.

**Still true, unchanged:** all facts fact-checked independently before
render, every segment frame-verified after render, payoff segment scrutinised
hardest. The format changed; the verification bar did not.

**What this is a test of.** The hypothesis is that a recognisable, repeatable
format with built-in disagreement raises sub conversion and comments, and
that those channel-level signals are what unlock distribution past ~1000.
Track subs and comments per episode, not just views and retention — those
two were the actual diagnosis and they are the actual scoreboard. Give it a
real run of episodes before judging; a single ranked episode that lands at
900 views proves nothing either way.

## 5e. Background music and transition SFX (adopted 2026-08-07)

Until 2026-08-07 every episode shipped with **a single audio stream:
narration, no music, no effects** — verified by inspecting the actual
rendered files, not assumed. `shorts_growth_guide.md` (Rank 4) had already
flagged this as "a genuine, cheap gap" and it had gone unimplemented.

**Background music — `--bgm`, OFF by default.** First shipped on-by-default,
then the owner said explicitly not to put music on every video — so it is
now opt-in per episode via `viral.mix_background_music()`. Mechanics worth
knowing regardless of the default:

- **It runs as its own ffmpeg pass with `-c:v copy`.** Only the audio is
  re-encoded, so it costs seconds and the video is untouched.
- **The volume default is measured, not guessed.** The bundled tracks in
  `resource/songs/` are ~-20.0 LUFS and our narration is ~-20.5 LUFS — nearly
  identical loudness. So "pick a small-looking number" fails badly: the first
  attempt at `0.08` put the music around -42 LUFS, inaudible on a phone.
  `0.12` (≈ -18dB) sits the music ~18dB under the narration, which measures
  correctly: in a silent gap between sentences the level rises from -62dB to
  -46dB (clearly present), and during speech the mixed level is *identical*
  to narration-only (music never competes). **Re-measure with
  `ffmpeg -i <file> -af ebur128 -f null -` if the track library ever
  changes** — this number is only valid for ~-20 LUFS source music.
- **Reversed 2026-08-08: was one fixed track, now randomized per render.**
  The original reasoning (a fixed track builds "this channel sounds like
  this" identity, random would undo it) held for one day. Owner then said
  explicitly not to stay fixed on the default track and to vary it per
  video. `--bgm-file` with no value now picks uniformly at random from all
  29 tracks in `resource/songs/` at render time (`SONGS_DIR` in
  `viral_episode.py`); pass `--bgm-file <path>` to force one specific track
  (e.g. for a deliberate mood match — see the same-day example below).
  Verified the LUFS of a couple of newly-picked tracks lands close enough to
  the original -19.8 LUFS default (-20.9, -21.1) that the existing `0.12`
  calibration still holds without per-track re-tuning; re-measure if a
  track's loudness ever looks like an outlier.
- `bgm_file`/`bgm_volume` are recorded in each render's result JSON *only
  when actually applied* (`None` if `--bgm` was never passed, or if the mix
  failed and fell back) — so "did music help" stays honestly answerable
  later, same reasoning as `narration_speed`.

**Transition SFX — `--sfx` to enable, OFF by default (flipped 2026-08-08,
see below).** A short "whoosh" plays at the start of the hook→fact-1
transition and at every fact boundary after that (`viral.add_transition_sfx()`,
timestamps taken from `fact_timings`). Briefly defaulted on (2026-08-07 only)
because the owner asked for it outright then; after it didn't hold up even
with fixes, it went back to opt-in like everything else in this section.

- **No usable asset existed anywhere in the repo or `Pexels`** (that catalog
  is video only) for this, so `docs/skill/make_transition_sfx.py` synthesises
  it — a numpy-generated swept-noise "whoosh" (`resource/sfx/whoosh.wav`) and
  a lower "impact" alternative (`resource/sfx/impact.wav`), both committed as
  ordinary tracked assets, not regenerated per render.
- **The synthesis had two real bugs, both caught by measuring the actual
  output, not by ear** (this environment cannot listen): the first envelope
  peaked at 46ms while the frequency sweep was still down at ~470Hz, so the
  loudest moment landed before the "whoosh" ever got interesting — fixed by
  centering the envelope mid-sweep instead of at the start. Separately, the
  overlap-add synthesis produced a full-scale spike in the very first
  samples (edge frames have incomplete window coverage, so the normalization
  divide blows them up) — fixed by padding the synthesis and cropping the
  edges away. Re-measured after each fix (spectral centroid over time,
  amplitude envelope) before trusting either one.
- **Placement is via ffmpeg's `amix`/`adelay`/`asplit`**, one delayed copy of
  the sfx per timestamp, `normalize=0` for the same reason as the music mix
  (default normalization would quietly shrink the narration by 1/N of the
  input count). Verified against a silent test video before ever touching a
  real render: bursts of audio appear only in tight windows exactly at the
  requested timestamps, silence everywhere else.
- `sfx_files` (the resolved pool, not the one file a given transition
  happened to land on — that part is random) is recorded in the result JSON
  when applied, `None` otherwise — same "record what happened, not what was
  asked" rule as music.

**Neither pass can fail a render.** Both are wrapped: if the file is missing
or ffmpeg errors, it logs a warning and the pipeline falls through to the
next stage (or to `final-viral.mp4` directly) rather than losing the whole
render. This matters concretely — adding the music pass first shipped with
this guard *missing*, and a missing track killed a six-minute render that
had already produced a perfectly good captioned video. Verified for both
passes by running each against a nonexistent file and confirming
`final-viral.mp4` still gets produced.

**Render order: captions → SFX → music**, each writing its own intermediate
(`with-captions.mp4` → `with-sfx.mp4` → `final-viral.mp4`), so any single
stage can be re-run or re-mixed from the previous file's output without
re-rendering the base video.

**2026-08-08 fix — the single fixed whoosh sounded artificial and didn't
connect the two shots it sat between.** Owner, verbatim (Hebrew): "כל פעם יש
אותו סאונד במעברים זה נשמע מלאכותי וגם הרבה פעמים הוא לא קשור. צריך שהסאונד
במעבר יהיה מקשר בין הסרטון שלפני לסרטון שאחרי ולא כל פעם אותו הסאונד" — every
transition used the exact same sound (felt artificial), and it often didn't
read as connected to the footage; the transition sound should bridge the clip
before and the clip after, not repeat identically every time. Two separate
problems, two separate fixes, both in `viral.add_transition_sfx()`:

1. **Same file every time → a 4-variant pool, randomized per transition.**
   `docs/skill/make_transition_sfx.py` now also generates
   `resource/sfx/transitions/{transition_1..4}.wav` — distinct duration
   (0.35–0.55s), frequency range, and one with a **reversed (falling) sweep**
   instead of just parameter jitter on the same gesture, so the variants are
   audibly different in kind, not just in pitch. `add_transition_sfx()` takes
   `sfx_files: str | list[str]`; with more than one file it picks a random
   one per transition point that is never the same as the immediately
   previous pick (plain `random.choice` alone would let two identical sounds
   land back to back and undo the fix). A single-string call still behaves
   exactly as before — this is additive, not a breaking change.
2. **Sound started exactly at the cut, so it only ever belonged to the new
   shot → placement now straddles the cut.** The old code `adelay`'d the sfx
   to the timestamp itself, meaning the *entire* sound played after the cut —
   sonically it was "a stinger glued onto the new segment," never touching
   the outgoing footage, which is exactly what "not connected" describes.
   Fixed by starting the sound `DEFAULT_SFX_BRIDGE_FRAC` (0.4, i.e. 40% of
   that sound's own duration) **before** the timestamp, clamped to not go
   negative. Roughly 40% of the sound now plays over the tail of the
   outgoing clip and 60% over the head of the incoming one — it bridges both
   sides of the cut instead of announcing only one of them. This placement
   change applies unconditionally, including to single-file/backward-compat
   calls.

**Verified without playback, same method as the original synthesis bugs**:
built a 24s silent test video, ran the new function against it with a 4-file
pool and four timestamps, then measured the *actual output audio* (not just
trusted the log) — energy onset in each transition window landed
0.18–0.22s **before** its nominal cut point (confirms bridging), and the
per-window spectral centroid trend confirmed genuinely different sounds
landed at different points, including the reversed-sweep variant measuring
as falling (centroid dropped from ~3.3kHz to ~0.8kHz) where the others rose.
Also confirmed byte-for-byte: `resource/sfx/whoosh.wav` is unchanged by this
change (same synthesis params/seed as before, still there for anyone forcing
a single file), and a plain-string call to `add_transition_sfx()` still
reuses one file every time — old behavior, not removed, just no longer the
default.

`viral_episode.py --sfx-file` now defaults to the pool **directory**
(`resource/sfx/transitions/`) instead of one file; passing it a single
`.wav` path still works and forces that one sound everywhere, same as
before 2026-08-08.

**Same day, a few hours later — the fix worked, and the owner still didn't
want it.** Both real bugs above (identical sound, unconnected placement)
were confirmed fixed, and the fix was applied retroactively to both of that
day's live episodes (§0's "SFX FIX" paragraph has the retroactive-apply
story). The owner's next message: "תוריד את האפקטים של המעברים זה לא נשמע
טוב" — remove the transition effects, it doesn't sound good. Read as a
general call on the feature, not a one-off for those two videos (unlike the
same message's second half, which *was* scoped to "the 2 videos" — see the
BGM entry below). `viral_episode.py`'s CLI flag was renamed `--no-sfx` →
`--sfx` and its default flipped to off, matching how `--bgm` already works —
opt-in, not assumed. The pool/bridging code in `app/services/viral.py` is
untouched and fully working; it's just not called unless `--sfx` is passed.
**Do not re-enable this as a default without being asked again** — it went
through a real fix cycle (not a guess-and-hope) and the owner still said no.
If asked to revisit, the pool and bridging logic are ready to use as-is.

**Same message, BGM half — scoped to "the 2 videos," not a default flip.**
"עדיין אין מוזיקת רקע ל-2 הסרטונים" — there's still no background music for
the 2 videos — reads as pointing at that day's two specific renders, not a
request to make `--bgm` the default again (which would contradict the
2026-08-07 "don't put music on every video" instruction, never reversed).
Added music to both of that day's episodes on request; **`--bgm` (whether
music plays at all) stays opt-in, the pipeline default is unchanged.** If
this reading turns out wrong, the fix is a one-line default flip, not a
design change — flag it if the owner asks for music again on a day when
they didn't explicitly say so.

**Immediate follow-up, same day: the fixed *track choice* was the actual
complaint, not whether music plays at all.** "אל תישאר קבוע על המוזיקה
הדיפולטיבית תגוון לפי הסרטון... תשנה את המוזיקה ב-2 הסרטונים" — don't stay
fixed on the default music, vary it per video, change the music in the 2
videos. Unlike the "on/off" question above, this one reads as general (no
"just these 2" qualifier on the first half), so it changed the *default*:
`--bgm-file` now randomizes across the library instead of always picking
`output000.mp3` (§5e's dated entry above has the mechanics). For that day's
two specific videos, went further than plain randomization — analyzed all
29 tracks' tempo/RMS/spectral centroid with `librosa` (`uv run --with
librosa`, not a project dependency) and hand-picked one energetic/bright
track for the fast-paced insects countdown (`output012.mp3`, fastest tempo
in the library) and one slow/dark track for the somber moa extinction story
(`output007.mp3`, slowest tempo, lowest spectral centroid) — a deliberate
mood match, not the random default. The random default is what an ordinary
future build gets; hand-picking by analyzed mood is a nice-to-have worth
doing again for a story or a tonally distinct episode, not required every
time.

**Gap closed same day: `story_episode.py` had no music support at all
before this.** Adding music to the moa episode required a one-off Python
script calling `viral.mix_background_music()` directly, because the story
pipeline's CLI never had `--bgm`. Since the owner's instruction was "every
video" needs varied music, not just facts-format ones, wired `--bgm` /
`--bgm-file` / `--bgm-volume` into `story_episode.py` properly — same
opt-in default, same random-track-per-render behavior, writes through a
`with-captions.mp4` intermediate exactly like `viral_episode.py` so a
failed mix can't kill an otherwise-good render. Stories still get no
transition SFX and never did (no per-fact boundaries to hang a whoosh on,
irrelevant to today's SFX removal either way).

## 5f. How to reverse the 2026-08-07 changes

All three changes above are controlled by runtime flags, so **reversing any
of them needs no code edit and no re-render**:

| To undo | Do this |
|---|---|
| Ranked countdown | Just stop passing `--counter-mode countdown`. `progress` is still the built-in default, so the old `1/6…6/6` listicle needs no flag at all. |
| Background music (on/off) | Nothing to do — `--bgm` is opt-in, so a normal build already has no music. If one specific build passed `--bgm`, just don't pass it next time. |
| Background music (track choice, 2026-08-08) | Pass `--bgm-file resource/songs/output000.mp3` explicitly to force the old fixed track instead of the random-per-render default. |
| Transition SFX (as of 2026-08-08, `--sfx` is opt-in and OFF by default) | Nothing to do — a normal build already has no SFX. To add it back for a specific build, pass `--sfx` (the old `--no-sfx` flag no longer exists, it was renamed and its default flipped the same day it was added). |
| SFX variety (2026-08-08, only matters if `--sfx` is passed) | Pass `--sfx-file resource/sfx/whoosh.wav` (a single file, not the `transitions/` directory) to force one sound everywhere again. |
| SFX cut-bridging placement (2026-08-08, only matters if `--sfx` is passed) | Not exposed as a flag — pass `bridge_frac=0.0` to `viral.add_transition_sfx()` directly (code edit) to restore "starts exactly at the cut." No owner request for this yet; only the "always the same sound" half was asked to stay reversible via a flag. |
| Just a volume | `--bgm-volume` / `--sfx-volume`, or re-mix from the relevant intermediate file in the task dir — no re-render needed. |

If the code itself has to go, the behaviour-changing commits revert cleanly
and were **tested doing so** (in a throwaway worktree, confirming the result
is byte-identical to the pre-change state, with no conflicts) — check
`git log` for the current commit hashes on this branch, the ones referenced
in earlier drafts of this section were superseded by the opt-in flip and the
SFX addition.

Everything else from 2026-08-07 is documentation or log rows and carries no
runtime behaviour.

**What is *not* reversible this way**, and is worth knowing before assuming a
clean undo exists:
- **Published videos.** `yfuSDGdpTw4` and `EtNhXZdSKZc` are live and public.
  Undoing those means deleting or unlisting them in YouTube Studio; nothing
  in this repo can do it.
- **Approved-but-unpublished slots.** While the 16:30/22:30 Routines have not
  yet fired, an approval can still be withdrawn by setting that slot's
  `approved` to `false` in `storage/todays_uploads.json` (gitignored) — the
  Routines re-read it at fire time. After they fire, it becomes the case
  above.
- **Overwritten render artifacts.** The splice-fix reruns overwrote each
  episode's `final-viral.mp4` in place, so the pre-fix (defective) cuts are
  gone. No loss in practice, but it means "compare against the original
  render" is not available after a splice fix — copy it aside first if a
  before/after is ever wanted.

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

**2026-08-07 20:00 report — two episodes finalize: ep19 (story) strengthens
the story-format lead, ep18 (facts, 63.5s) becomes the first real data
point for a length-hurts-retention hypothesis.**

- **Ep19 (Dollar story, 55.2%) is the second story-format data point**,
  alongside ep17 (Ferrari/Lamborghini, 48.45% at the time, now settled at
  47.4% live — small downward drift as more data lands, not a new event).
  Both story episodes now sit at or above the long-format facts baseline
  (45.8%, §5), averaging ~51.3%. This reinforces rather than resolves the
  "story format ≥ facts on retention" lead flagged after ep17 alone (n=1,
  "keep testing") — n=2 with both points on the same side of the baseline
  is a real trend, not proof, but it's now strong enough to act on.
  **Concrete action: actively prioritize story format going forward rather
  than treating it as an experiment still proving itself** — and since
  story leads were the bottleneck, not format performance, source and
  fact-check more of them (see the leads note below).
- **Ep18 (everyday objects, 31.2%) is the second-worst finalized facts
  retention on the channel** (only ep3's 35.9% and the true low-n outliers
  are comparably weak) **and it is also the longest facts episode finalized
  so far, at 63.5s** — the exact length ep19's own build log flagged as
  "nothing on this channel has been tested past 63s" before trimming the
  dollar story back to 48.2s specifically to avoid confounding the
  story-format test with an untested length. Ep18 unintentionally *is* that
  untested-length data point, and its retention is weak. This is n=1 and
  everyday-objects-as-a-topic is a live confound (nothing here rules out
  "this specific topic underperforms" instead of "63.5s underperforms"),
  so this is a hypothesis, not a finding. **Concrete action: default facts
  episodes back toward the established 50-58s core range rather than
  letting them drift toward 63s+, and specifically watch ep23 (space
  facts, 66.06s — the longest facts episode built, still pending) as the
  next real test of this hypothesis** — if ep23 also lands low, that's two
  independent long episodes both underperforming and worth treating as a
  real length ceiling; if it lands normal, ep18's low number was more
  likely the topic than the length.
- **Story-lead correction: Inky (ep14, the octopus escape story) was never
  actually blocked any more — it just wasn't re-checked.** It was
  deliberately held 2026-08-03 "until the first story (ep17) has real
  retention data in" — that condition was satisfied when ep17 finalized
  (before tonight, see the 2026-08-06 log). So as of tonight there are
  **two ready story leads, not one**: `story_moa_lead.txt` (fact-checked,
  script-locked) and `docs/skill/story14_lead.txt` (Inky, fact-checked,
  written, its hold condition already cleared). Both should be treated as
  available for the next story slot, not just moa.

**2026-08-08 20:00 report — two episodes finalize: ep20 undercuts the
hook-shape hypothesis, ep21 turns the "unexplained flop" thread into a
real finding.**

- **Ep20 (human body, 35.28%) was a deliberate strange-image-statement
  hook, built specifically to grow item 1's ep4-comparison.** Ep4 (also
  statement-form) sits at 81.59% — the channel's outlier high. Ep20, same
  hook shape, lands at 35.28%: third-worst finalized facts episode on the
  channel, despite having the **highest footage-specificity rating logged
  so far (~4.6/5)**. A 46-point spread between two statement-hook episodes
  is bigger than most of the *cross-shape* comparisons this log has been
  tracking. **Concrete action: stop attributing ep4's outlier status to its
  hook shape** — ep20 is direct counter-evidence that "open on the strange
  image" reliably lifts retention on its own. Whatever made ep4 exceptional
  (topic, specific facts, luck) is still unexplained; pick hook shape for
  variety and fit, not as a retention lever. Also worth flagging as a
  second counter-data-point against "higher footage-specificity rating
  predicts better retention" (item 2) — ep20's 4.6/5 did not protect it
  from a below-average result. Both open actions stay open (n is still
  small), but neither should be treated as validated just because the
  channel keeps collecting the data.
- **Ep21 (D-Day story, 82.83% retention on only 28 views) reframes last
  night's "unexplained severe flop" entry with real evidence, not just
  ruled-out technical causes.** The handful of people who actually saw it
  watched **82.83% of it** — above ep4's 81.59% record, and far above the
  ~46% facts baseline. Facts 8 (the channel's other severe outlier, also
  28 views) finalized earlier at 51.88% — also at-or-above average. **Both
  of the channel's severe-outlier flops now have above-average retention
  among the tiny audience that saw them.** That is real, if thin (n=2,
  each on a handful of views), evidence for "this is a distribution miss,
  not a content miss" — content that bad would not hold attention this
  well even for 28 people. **Concrete action: when a future episode flops
  this hard, check retention as soon as it's available before spending more
  effort second-guessing the episode's structure or facts** — on this
  channel's evidence so far, a severe view-count flop with strong retention
  among actual viewers means the algorithm didn't show it to people, not
  that the video itself was bad.
- **Ep13's retention drifted from 59.64% to 66.71%** as more Analytics data
  landed — now the second-best finalized episode on the channel behind ep4.
  Not a new data point (already logged), just noting the drift is larger
  than the small day-to-day movement seen on other episodes; no action
  needed.
- **Length hypothesis still open:** ep23 (space, 66.06s — the longest facts
  episode built) is still "pending" as of tonight, still the next real test
  of whether ep18's weak 31.51%/63.5s result generalizes to length or was
  specific to the everyday-objects topic. Watch tomorrow.

**2026-08-09 09:00 build — open actions applied, plus a new hard-stop check
that has nothing to do with retention.** Ep30 (sleep) and ep31 (trees) both
used contest-form hooks (§5d requires the hook to set up an argument, so the
countdown format effectively fixes hook shape — worth noting that item 1's
question-vs-statement comparison can no longer grow from facts episodes while
the countdown format is the default; only stories can still vary it). Footage
specificity rated pre-delivery: ep30 ~4.25/5, ep31 ~4.6/5. **Ep31 is a useful
data point for the category-ceiling hypothesis in the other direction**: trees
are richly photographable and it scored the session's highest average with
ordinary search effort, where ep23 (space) and ep25 (weather) were capped low
by genuinely unphotographable subjects. That is consistent with the ceiling
being set by the topic, not by how hard anyone searched.

**Both episodes were held to 53-54s** per the 2026-08-07 action against the
63s+ drift. Ep23 (space, 66.06s) is *still* pending and is still the outstanding
test of whether ep18's weak 31.5%/63.5s was length or topic — nothing new to
report on it tonight.

**New production rule, not a retention lesson — see §6.** The first render of
ep30's #1 segment shipped a real patient's name, DOB and hospital, legible on a
monitor inside a licensed Pexels medical clip, under narration about a fatal
inherited disease. It was caught by the standing payoff-segment frame check and
replaced before delivery. Logged in §6 as a permanent pre-ship check on any
clip containing a screen, document or signage. Worth stating plainly because it
is a different *class* of defect from everything else in this log: not "does
this footage match the words" but "does this footage expose a real person."

**2026-08-09 20:00 report — ep23 finally crosses from pending, resolving the
length hypothesis that has been open since 2026-08-07; ep21 drifts hard enough
to be worth flagging on its own.**

- **Ep23 (space facts, 66.06s — the longest facts episode on the channel)
  finalizes at 102.75% retention.** That number is almost certainly inflated
  by Shorts' autoplay-loop behavior (viewers rewatching within one view
  session can push `averageViewPercentage` past 100% — the same mechanism
  documented for AI2's 128.83% outlier in §5b, there excluded from the hero
  stat by the `views>=100` floor; ep23 has 596 views, well past that floor,
  so this isn't a low-n fluke, but the raw percentage still shouldn't be read
  literally). Even discounted heavily, there is no way to read this number as
  a retention penalty. **RESOLVED: length (60-66s) does not reliably predict
  weak retention on this channel** — ep18's weak 31.51%/63.5s result was more
  likely driven by its everyday-objects topic specifically than by its
  runtime, since the *next* long episode (ep23, similar length) shows the
  opposite result. Concrete action: stop holding facts episodes back from the
  established 50-58s core range purely on length-anxiety grounds; a topic
  that earns 60s+ can have it. Re-open only if a future 60s+ episode lands
  weak *and* isn't better explained by its topic, the same standard just
  applied to close this one out.
- **Ep22 (pizza) also finalizes tonight at 44.10%** — unremarkable, sits right
  in the mid-40s cluster most non-outlier facts episodes land in (§5c item 4's
  "most episodes cluster in the low-to-mid 40s" pattern). No new action; just
  logged so it isn't sitting as a false "pending" indefinitely.
- **Ep21 (D-Day story) drifted from 82.83% to 66.95%** as more views came in
  (28 → 37) — a much bigger swing than the small day-to-day drift seen on
  other episodes (e.g. ep13's 59.64%→66.71%). At this view count Analytics is
  still extremely sensitive to single viewers, so **the "severe outlier flops
  still show above-average retention" finding from 2026-08-08 needs a caveat,
  not a retraction**: 66.95% is still comfortably above the ~46% facts
  baseline, so the core conclusion (this was a distribution miss, not a
  content miss) still holds — but the specific 82.83% figure quoted that
  night should not be treated as ep21's settled number. Expect further
  drift at this view count; re-check before citing an exact figure for ep21
  again.

**2026-08-10 20:00 report — ep24 and ep25 both finalize, and item 2's
footage-specificity hypothesis is now RESOLVED against itself.**

- **Ep24 (big cats, 66.9%) and ep25 (weather, 85.61%) both finalize
  tonight — both well above the ~46% facts baseline**, and ep25 is now the
  **second-best retention on the whole channel**, behind only ep23's
  102.75%. Both used question-form hooks (no new data for item 1's
  question-vs-statement comparison this round).
- **Item 2 (footage-specificity rating predicting retention) is now
  RESOLVED, and resolved against the hypothesis.** Ep25 logged the
  **lowest** footage-specificity rating of any facts episode this session
  (~3.8/5 — hail and several other phenomena were near-unphotographable)
  and still landed the **second-highest retention on the channel**. Ep24's
  ~4.3/5 rating produced a strong-but-unremarkable 66.9%. Combined with
  ep20's counter-example from 2026-08-08 (the **highest** rating logged,
  ~4.6/5, paired with one of the **lowest** retentions, 35.28%), the
  evidence now runs in both directions: high rating with low retention
  (ep20) and low rating with high retention (ep25). **Concrete action:
  stop rating footage specificity as a retention-prediction exercise —
  keep logging it per-episode (it is still useful as a defect/QA record
  and for the separate category-ceiling observation), but do not spend
  extra search effort chasing a higher number in the belief it will move
  retention.** This closes out item 2 the same way item 2's sibling
  (completion-compulsion, 2026-08-06) and the length hypothesis
  (2026-08-09) were closed: a same-session pair with the rating running
  the *opposite* direction from the predicted outcome.
- Both episodes had real footage defects caught and fixed pre-delivery on
  frame verification (ep24: a tiger obscured by foreground leaves; ep25: a
  slowed-motion lightning clip and a payoff-segment fix) — worth noting
  since both still landed well above baseline despite shipping with
  caught-and-fixed defects, which is itself a small point of reassurance
  that the verification step is doing its job rather than papering over a
  structurally weak build.

**2026-08-11 20:00 report — ep26 (moa) and ep27 (insects) both cross from
pending to real retention, one reinforcing the story-format decision, the
other flagging the ranked-countdown format's first real data point.**

- **Ep26 (moa story, "The Bird With No Wings At All") finalizes at 68.11%
  retention on 1,324 views** — the best story-format number on the channel
  by a real margin, and unlike ep21 (D-Day, 66.95% but only 37 views) this
  sits on a large enough sample to trust. Added to the >=100-views story
  average from the 2026-08-09 ratio decision: Ferrari 46.95%, Dollar
  55.28%, moa 68.11% — **n=3, avg 56.8%**, still comfortably clear of the
  ~45% facts baseline. This is the "verdict in" the dashboard's own
  takeaway now states for the story-vs-facts check. **Concrete action:
  keep the 1-in-3 story cadence from 2026-08-09 — this is a third
  confirming data point, not a reason to raise it further yet (n=3 is
  still thin for that), but there is no signal here to walk it back
  either. Lead supply stays the binding constraint, so keep sourcing story
  leads independently rather than waiting on it.**
- **Ep27 (insects, facts) finalizes at 37.31% retention on 892 views** —
  the first-ever rendered ranked-countdown episode (`--counter-mode
  countdown`, adopted 2026-08-07), and its retention lands *below* the
  ~45% facts baseline, notably weaker than the two non-countdown facts
  episodes published the same week (ep24 big cats 66.9%, ep25 weather
  85.61%). **Important caveat: §5d's stated hypothesis for this format is
  about subscriber conversion and comments, not retention** — so this
  number does not by itself resolve or contradict that hypothesis, and
  should not be read as "the countdown format failed." It is a real,
  slightly concerning retention data point on n=1, nothing more.
  **Concrete action: do not change the countdown format on this single
  number. Two more countdown episodes (ep30 sleep, ep31 trees) are still
  pending and are the real next data points — if both also land below the
  ~45% facts baseline, add a dedicated retention-side note to §5d's
  hypothesis (currently silent on retention entirely) rather than treating
  subs/comments as the only thing worth watching on this format.**

## 6. Production rules learned the hard way

**The Veo/Vertex AI OAuth token expires on the same ~7-day cycle as the
YouTube token — it is not a one-time setup.** Building ep39 (currency
facts) on 2026-08-13, `docs/skill/ai-footage-fill/scripts/generate_ai_clip.py`
failed with `google.auth.exceptions.RefreshError: invalid_grant: Token has
been expired or revoked`, the exact same error class already documented
for `docs/skill/youtube/token.json` in SKILL.md 8j. Root cause is
identical: the Google Cloud project's OAuth consent screen is still in
"Testing" status, so Google expires refresh tokens for test users after
roughly 7 days regardless of use — `docs/skill/veo/token.json` was 8 days
old (created 2026-08-05) when it failed. **Diagnosed, not guessed**: the
traceback itself named the exact failure. **Fix requires the owner**:
re-run `docs/skill/veo/authorize_local.py` locally and send back a fresh
`token.json`, same as the YouTube-token fix. **Do not block the day's
build on this** — ep39 was completed with real Pexels footage standing in
for both planned AI clips (a cliff of round millstones for the Yap giant-
stone-disc concept, an underwater boulder for the sunk-stone payoff),
flagged to the owner via Telegram, and logged in episode_log.csv as a
one-off deviation from the 2026-08-08 AI-hook standing rule, not a policy
change. **Generalised rule: any OAuth token under this project's Testing-
status consent screen will expire on the same ~7-day clock — check token
age before assuming a credential failure is something else**, and budget
for the owner needing to re-authorize roughly weekly until the consent
screen is published/verified (the long-term fix already named in 8j).

**A fact can be individually true and still misattributed to the wrong
civilization or era — check the SOURCE's actual date, not just the claim
itself.** Ep36 (ancient Egypt) originally scripted fact #6 as "ancient
Egyptians invented toothpaste," sourced from a real papyrus recipe (rock
salt, mint, dried iris, pepper). The recipe is genuine and the sourcing
notes even flagged it during the original fact-check as "Greco-Roman
period, not necessarily pharaonic" — but that caveat stayed in the lead
file and never made it into the actual narration. The owner caught it
after publish-review, correctly pointing out that "ancient Egyptians"
reads as the pyramid-building civilization to a viewer, not Egypt three-
plus centuries later under Greek and Roman rule. **Every fact re-verified
clean against fresh outside sources when checked** — this was never a
wrong-fact problem, it was a wrong-*attribution* problem, the kind that
survives a normal fact-check because the individual claim really is true.
**Concrete rule: when a source's date sits in a different named era or
ruling civilization than the one the script attributes it to, put that
distinction in the narration itself** ("in Egypt under Roman rule," "over
a thousand years after the pyramids") **rather than only in the internal
sourcing notes where a viewer will never see it.** Fixed by rewording the
line and re-rendering from the same footage pins; all 8 segments
re-verified post-re-render per the standing discipline, landed at 62.8s
(actually shorter than the flawed version's 63.62s despite more words).

Full detail in `SKILL.md`; the short version:

- **Never use an em dash (—) in any text that goes out publicly under the
  channel's voice** — comment replies, captions, titles, pinned comments.
  Owner instruction, 2026-08-10: the em dash is a well-known AI-writing
  tell and immediately gives away that a reply was AI-written, which is
  exactly the "AI slop" accusation the channel is trying to defuse in
  comment replies, not invite. Use a regular hyphen with spaces (`word -
  word`), a comma, a period, or just restructure the sentence instead.
  Applies to anything drafted for the owner to paste, not just things this
  pipeline posts directly.
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
- **Read the text that appears ON SCREEN inside a stock clip before shipping
  it.** 2026-08-09, Facts 25: a Pexels brain-angiogram clip pulled for the #1
  fact had a real patient's **name, date of birth and hospital** clearly legible
  on the monitor — running under narration about a fatal inherited brain
  disease, i.e. an identifiable private individual visually implied to have that
  illness. The clip is properly licensed; that licence covers *use*, it does not
  make it OK to imply a named stranger is dying of a prion disease. Caught only
  because payoff-segment frames get looked at. **Applies to any clip containing
  a screen, monitor, document, badge, form or signage** — medical, office and
  "person at a laptop" footage most of all. Zoom in and actually read it; a
  frame that looks like generic B-roll at thumbnail size can carry someone's
  personal data at full resolution.
- **A generic ruins/architecture term can return the wrong civilization
  entirely, for the WHOLE segment, not just one bad cut.** 2026-08-10, ep33
  (ancient Rome): `ancient ruins stone corridor` returned Angkor Wat / Khmer
  temple architecture for every cut in the segment, and a separate term
  returned a modern rustic door with legible Turkish utility labels for the
  #1 payoff segment — neither was a partial miss, both were the wrong
  subject top to bottom. Checking only one frame, or assuming a segment that
  "sounds architectural" is safe because the term contains the right era
  word, both fail here. Verify every segment's actual subject matches the
  fact being narrated, not just its on-screen text.
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
- **A loud-but-garbled TTS glitch reads as a frozen caption, and looks
  identical to silence unless you check volume.** Owner-reported bug on Facts
  28 (volcanoes, 2026-08-11): the caption froze on-screen for 6.44s right
  after "the entire planet." `align_facts_to_words()`
  (`app/services/viral.py` ~line 195) deliberately sets each fact segment's
  end boundary to the *next* fact's speech-start time (per whisper), so
  adjacent captions stay touching instead of flashing blank - that design is
  correct, but it means any abnormally long gap in the underlying audio
  between two facts gets faithfully rendered as a long dead caption.
  `ffmpeg silencedetect` at -35dB and -30dB/0.3s found *nothing* unusual in
  the suspect window - because the audio wasn't silent. `ffmpeg volumedetect`
  on the exact window showed it was loud (mean -19dB, max -1.7dB), and a
  direct re-run of `transcribe_word_timings()` on that audio confirmed
  whisper genuinely found zero words there despite the volume: a real Gemini
  TTS glitch (garbled/unintelligible audio), not a silence/pause and not a
  captioning-code bug. **Diagnosis rule: when a caption looks stuck, don't
  stop at `silencedetect` - also run `volumedetect` on the exact suspect
  window and, if it's loud, re-transcribe that audio directly. Loud-but-
  glitched and true-silence look identical to a human watching the frozen
  caption but need the same fix either way (a fresh TTS re-render).**
- **Re-verify ALL segments after ANY re-render, not just the one(s) you
  fixed.** Fixing the Facts 28 TTS glitch above required a full re-render
  (same script/footage pins, fresh TTS pass). The re-render fixed the
  caption freeze, but a full re-verification pass (not just re-checking the
  fixed segment) caught a second, completely unrelated defect that had not
  been in the original buggy render at all: a recreational
  parasailing/yacht/jet-ski clip landed on the underwater-volcanism fact,
  courtesy of Pexels result instability striking on that specific render.
  This is now the second confirmed case (after the ep33 Rome re-render) of a
  fix-only re-check shipping a brand-new defect - re-rendering re-rolls
  every unpinned segment's Pexels pool, not just the segment you touched, so
  a full frame-by-frame pass across every segment is mandatory after any
  re-render, with no exceptions for segments that were "already verified
  clean" on a prior render.

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

**Model note, checked directly rather than assumed — and the original
diagnosis was WRONG, corrected 2026-08-08.** The entire Gemini 3.x image
tier — `gemini-3.1-flash-image` ("Nano Banana 2"),
`gemini-3.1-flash-image-preview`, `gemini-3.1-flash-lite-image` ("Nano Banana
2 Lite"), `gemini-3-pro-image` ("Nano Banana Pro") — showed up in
`models.list()` for this project at the regional location (`us-central1`)
but every one 404'd on an actual call there, first observed 2026-08-05 and
re-confirmed 2026-08-08. That was read as a project-level entitlement gap
("listed but not enabled"). **It wasn't.** The owner asked to try the exact
call with `location="global"` instead of `us-central1`, and it worked —
`gemini-3.1-flash-image` returned a real image, `model_version` in the
response confirming it actually ran. Checked properly afterward:
`models.list()` under `location="global"` shows *only*
`gemini-3.1-flash-image` from this project's available models; under
`location="us-central1"` the model is listed too but 404s on every call.
The fallback model and Veo are the exact mirror image — listed and working
at `us-central1`, **not listed at all** under `"global"`. So this was never
one location being right and one being wrong across the board; the primary
image model and everything else simply live in different Vertex locations
on this project, and a single shared client (one location) could only ever
reach one side.

**Fixed 2026-08-08 in `generate_ai_clip.py`:** `gemini-3.1-flash-image` is
the default image model, called through its own client scoped to
`image_location` (default `"global"`, `DEFAULT_IMAGE_LOCATION`), separate
from the client used for `image_model_fallback` and Veo (`location`,
default `us-central1`, `DEFAULT_LOCATION`). Falls back to
`gemini-2.5-flash-image` at the regular location only on an actual
404/NOT_FOUND (any other error — safety refusal, quota, auth — still
propagates rather than being silently papered over by a model swap). The
sidecar JSON's `image_model` field records whichever model actually
produced the image; `image_model_requested` keeps the one that was asked
for, so a real access change later would show up as the two fields
matching. `--probe` now lists the primary image model against its own
location instead of the shared one, so it stops incorrectly reporting a
working model as unreachable. Verified end to end with a throwaway prompt:
ran through the real CLI, no fallback message printed, `gemini-3.1-flash-image`
succeeded on the first attempt, produced a genuine on-topic image.
**Lesson for next time a "listed but 404s" model shows up: check location
before concluding it's an entitlement gap** — `models.list()` does not
reliably distinguish "visible at this location" from "visible project-wide,
callable somewhere else."

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

## 10. Performance analysis and A/B test (owner-approved 2026-08-13/14)

**Full channel pull, 2026-08-13 evening — 39 videos, 36 subscribers, ~24.5K
views.** Pulled live Data API stats (views/likes/comments, all 39 videos)
plus Analytics API retention (frozen for the newest ~3) and cross-joined
against `episode_log.csv`'s format/AI-clip/countdown fields. Full numbers
live in this session's chat log; the finding that matters:

**The countdown format (adopted 2026-08-07 specifically to fix low
subscriber/comment conversion) is measuring WORSE than the era before it on
every live metric, not better:**

| metric | pre-countdown facts (17 videos) | countdown facts (9 videos) | change |
|---|---|---|---|
| avg views | 766 | 634 | -17% |
| avg likes | 16.1 | 9.0 | -44% |
| like-rate | 2.10% | 1.42% | -32% |
| avg retention | 53.7% | 51.6% | -2pt |
| subs/video | 1.35 | 1.00 | -26% |

n is small (9, and 3 of those lack final retention since Analytics is frozen
~48h) so this is not proof the format is bad — but every live metric moving
the same direction is a real signal, not noise, and it is the opposite
direction the format was adopted to move. **STORY format continues to
outperform everything**: 63.4% avg retention, 3.10% like-rate, 1.50
subs/video across 6 stories — ep26 (moa) alone brought +7 subscribers, the
single best subscriber-conversion video on the channel. The channel's
highest-ever retention facts episodes (space 101.3%, weather 84.3%, big
cats 75.8%, the original animal-ensemble Facts 4 at 81.6%) all predate the
countdown switch, which weakens the case that the countdown mechanic itself
is what retention responds to — topic/footage specificity looks like the
bigger lever. AI-clip count also correlates with retention, but every
episode with 3-4 AI clips is a STORY, so this cannot be separated from the
format effect with current data — see the AI-hook policy change below.

**Owner approved all 5 proposed actions, 2026-08-13/14:**

**1. Controlled A/B test, countdown vs. the old flat listicle, for facts
episodes only.** Protocol: alternate arms on every new facts build —
**Arm A = countdown** (`--counter-mode countdown`, current default),
**Arm B = flat listicle** (`--counter-mode progress`, the pre-2026-08-07
behavior, recall-style outro instead of the disagreement-invite CTA).
Self-balancing: before each facts build, count **built-and-frame-verified**
episodes in each arm since 2026-08-14 and build whichever arm has fewer
(ties go to whichever arm hasn't run today). Ep33 (Rome, already
built/approved, countdown) counts as **Arm A run #1**.

> **Counting rule corrected 2026-08-15 — count BUILT, not APPROVED.** This
> originally read "completed+approved", which stalls the moment approvals
> lag behind builds. On 2026-08-15 the backlog was 5 unapproved with only
> ep33 approved since 2026-08-14, so the counts read Arm A 1 / Arm B 0 even
> though ep43 (Arm B) was already built and verified — the rule would have
> assigned Arm B to the next facts build, and the one after that, until
> approvals landed. That is a run of consecutive same-arm builds caused
> purely by bookkeeping, which is exactly the imbalance the self-balancing
> rule exists to prevent. An episode's arm is fixed the moment it renders;
> approval decides whether it *ships*, not which arm it belongs to. Count a
> build once it has passed frame verification. If an episode is later
> dropped rather than approved, subtract it from its arm's count then — do
> not pre-emptively withhold the count while it sits awaiting approval.

**Live arm counts as of 2026-08-15, under the corrected rule:**

| arm | episodes since 2026-08-14 | count |
|---|---|---|
| **A — countdown** | ep33 Rome (57.72s, published), ep41 mushrooms (47.4s, approved) | **2** |
| **B — flat listicle** | ep40 Vikings (47.6s, approved), ep43 Antarctica (56.0s, approved) | **2** |

**Resolved 2026-08-15: the owner approved ep40 and ep41 as a pair**, so both
arms keep their ~47.5s data point and the arms stay level at 2/2. ep43
(Antarctica) and ep44 (Wojtek) were approved in the same exchange. Backlog is
down to 1 — ep42 Emu War, a STORY, outside the A/B test.

**The arms are balanced at 2/2, so the next facts build is a tie — break it
on whichever arm hasn't run today.** They also stay balanced under either
outcome of the pending ep40/ep41 decision, because that pair is one episode
from each arm: approve both and it is 2/2, drop both and it is 1/1. This is
why ep40 and ep41 must be decided **as a pair** — approving or dropping only
one leaves the arms at 2/1 *and* puts a lone ~47.5s episode in one arm
against ~56s in the other, reintroducing the length confound the 2026-08-15
rebuild was done to remove, this time inside a single arm. Target **minimum 4 completed
episodes per arm** before drawing a conclusion — expected around
2026-08-21 uploads at the current ~1 facts episode/day pace, with real
retention readable a couple of days after that (~2026-08-23). Judge on the
same metrics as the table above (views, likes, like-rate, retention,
subs), not on any single one in isolation. This is a floor, not a fixed
end date — extend it if results are still ambiguous at n=4/arm, or stop
early if one arm is clearly and consistently ahead well before then.
**Log which arm every facts episode used in its `episode_log.csv`
outcome_note** (the word "countdown" or "flat listicle", explicitly) so
the arm assignment is auditable without re-deriving it from the CLI flags.

**2. Story ratio raised from ~1-in-3 to 1-in-2 uploads.** Directly
supported by the table above — story is the best-performing format on
every metric measured. Practical shape: **every day's two build slots
should be one STORY + one facts** (whichever arm is due next per #1),
never two stories back-to-back (existing rule, unchanged) and never two
facts on the same day unless a story lead genuinely isn't ready in time
(flex to 2 facts that day, catch the ratio up the next day). Leads:
self-source per `SKILL.md` step 0 and this file §9 when the inbound queue
is empty, exactly as already established — an owner-supplied lead still
jumps the queue.

**3. AI hook clip: mandatory-by-default only for STORY, optional/
opportunistic for facts.** See the superseded-rule note in §0. Reasoning:
the data shows no measurable facts-format benefit from the single
mandatory hook clip (retention scattered across the arm-B-era episodes
with no trend), it adds ~$3.24/clip with no shown return there, and it
made the pipeline depend on a Veo token that dies roughly weekly — for no
demonstrated gain in that format. STORY keeps the mandatory hook (plus up
to 2 more without asking, a 4th needs approval) because multi-AI-clip
stories are the strongest content on the channel and routinely need shots
Pexels simply cannot supply (extinct animals, symbolic true-crime
dramatization). For facts, generate an AI clip only when Pexels genuinely
has nothing usable for the hook — same test the skill was originally
designed around.

**4. Veo/YouTube token expiry: STOP and ask, don't silently substitute.**
Owner's explicit instruction 2026-08-13/14: "every time the token expires,
stop the generation and ask me to generate a new token, I will do it."
This changes the prior behavior (documented in §6 for ep39: build with
Pexels-only and log a deviation, don't block the day). New policy:
- **STORY build, Veo token dead:** do **not** silently fall back and
  finish the story without its AI clip(s). Stop that build, send a
  Telegram message to the owner stating exactly which episode is blocked
  and that a fresh `docs/skill/veo/token.json` is needed (re-run
  `docs/skill/veo/authorize_local.py` locally), and wait. Resume once a
  fresh token arrives — do not re-attempt on a stale token.
- **Facts build, Veo token dead:** no stop needed — the AI hook is
  optional there now (see #3), so proceed Pexels-only as normal. Still
  send a short Telegram FYI that the token is dead, so the owner can
  renew it before the next STORY build needs it, without treating it as
  urgent/blocking.
- Same halt-and-ask posture already applies to the YouTube upload token
  (`docs/skill/youtube/token.json`) per `SKILL.md` 8j — unchanged, this
  is now the explicit standing policy for both tokens, not YouTube's
  alone.
- **Confirmed dead again 2026-08-13 ~22:xx UTC** (`invalid_grant`, via
  `--probe`) — a fresh token was requested from the owner the same
  evening this policy was adopted. Check `--probe` before assuming
  status; do not assume it is still dead indefinitely.

**5. Audit pinned-comment + early-reply discipline.** Per `SKILL.md` item
10, a pinned comment + replying to early comments is the strongest
documented subscriber-conversion lever, ahead of any format mechanic —
worth confirming this is actually happening consistently on recent
uploads (pinned comment posted immediately after each publish, replies
sent to early comments) rather than assumed. Not yet audited as of
2026-08-14 — do this the next time upload activity allows checking the
channel's comment section directly.

**Schedule communicated to the owner via Telegram 2026-08-14** — see that
message for the day-by-day build/slot plan through ~2026-08-21. If this
file and that message ever disagree (a lead falls through, a token outage
shifts a day), this file is the one to trust and update; the Telegram
message was a snapshot at send time, not a live document.
