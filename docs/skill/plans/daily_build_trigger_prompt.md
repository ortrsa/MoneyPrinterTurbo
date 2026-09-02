# Archived: "RBT daily build (09:00 IDT)" scheduled trigger

**Deleted 2026-09-02 at the owner's request** ("Delete the task we will
return when i fix it"), because the pipeline was blocked — a container
reclaim had wiped every credential (Pexels key, Gemini/TTS key, Telegram
section, Veo tokens, YouTube OAuth), so the job could only fire, fail and
report the same block each morning.

**This is the exact configuration to recreate it with once the owner has
restored credentials.** Nothing else needs to change.

- **Name:** `RBT daily build (09:00 IDT)`
- **Cron:** `0 6 * * *` (UTC — 09:00 IDT while IDT is UTC+3)
- **Binding:** fires into THIS session (persistent), not a fresh session
  — `persistent_session_id: session_01BygJRGfwqw4iCynka6i7eG`
- **Environment:** `env_01NU5suyEc7PypRgGn4YJJar`
- **Original trigger id (now gone):** `trig_01KeLddHpRHZDY15UYZTPJFs`
- Created 2026-08-13, last updated 2026-08-27, last fired 2026-09-02.

Recreate with `create_trigger` using `initiation: human_request`, the cron
above, and the verbatim prompt below.

**Before recreating, check whether the prompt is still accurate** — it has
gone stale before (it carried a dead "~30s" length instruction from
2026-08-16 to 2026-08-19). Two things in it are already known to be worth
revisiting:

1. It has no mention of the two hard rules adopted 2026-08-31: **distinct
   footage in every segment** and **never repeat a topic or a fact**
   (now enforced by `docs/skill/check_topic_reuse.py`). Consider adding
   them to the prompt so a fresh-context firing can't miss them.
2. Step 9's Veo-token instructions assume only Veo can be dead. After the
   2026-09-01 container reset, *every* credential can vanish at once —
   worth a line telling the job to check `config.toml` and the token
   files up front and stop early if they're empty.

---

## Verbatim prompt

```
This is the automated daily build job for the "Random But True" YouTube Shorts channel. Re-read docs/skill/SKILL.md and docs/skill/channel_playbook.md IN FULL before doing anything, especially the "🚀 GROWTH PIVOT" section (adopted 2026-08-27 — new 15-30s length target supersedes the old 50-58s/63s-ceiling rule, new hook-discipline and loop-design requirements, apply starting THIS build), the "🗣️ TAKE A STANCE" section (adopted 2026-08-26), the "ROOT CAUSE OF THE VIEWS DECLINE" section (topic-mix policy adopted 2026-08-18: target ~50% ANIMAL + ~15% EVERYDAY/RELATABLE per rolling 10 uploads), and §10 (owner-approved 2026-08-13/14 policy changes) - context may have been compacted since the last firing.

WORKFLOW CHANGE (2026-08-19): the separate 16:30/22:30 IDT live-publish triggers have been permanently deleted. This is now the only scheduled trigger in the pipeline. Publishing no longer happens from an automated trigger at all - it happens when the channel owner explicitly approves a built episode in a live chat message (in this same session), at which point upload it via docs/skill/youtube/upload_video.py --confirm --publish-at <RFC3339 UTC timestamp> (convert the owner's intended Israel-time slot to UTC; IDT is currently UTC+3) so YouTube itself flips the video public at that exact time - never --privacy public immediately unless the owner explicitly asks for it to go live right now rather than scheduled. Never treat this build job's own firing, or the fact that an episode was built successfully, as that approval - it must trace to a real chat message. Two distinct no-timing-given/own-times fallbacks exist depending on the owner's exact wording - see storage/todays_uploads.json and the HANDOFF block for both.

Steps:
1. Check storage/todays_uploads.json and the pending-approval backlog (episode_log.csv) - build 2 new episodes for slots as far out as needed, unless the backlog is deep and unflagged (flag it instead of silently piling up).
2. Per §10: build ONE story + ONE facts episode per day (never two stories back-to-back; flex to 2 facts only if no story lead is ready). Choose topics per the topic-mix policy above. For the facts episode, check episode_log.csv for which A/B arm (countdown vs flat-listicle) has fewer completed BUILDS since 2026-08-14 and build that arm - NOTE: this A/B test concluded 2026-08-27 (4 completed builds per arm, the pre-set minimum), so this is now about historical bookkeeping only, not a live constraint on length - see the GROWTH PIVOT section.
3. LENGTH — NEW TARGET adopted 2026-08-27: 15-30 seconds, per the GROWTH PIVOT section's research on Shorts completion-rate bands. This SUPERSEDES the 50-58s/63s-ceiling rule that governed 08-15 through 08-27 (that rule existed only to protect the now-concluded A/B test). Tune --fact-count/--fact-max-words (viral_episode.py) and --target-seconds (story_episode.py) to actually land in the 15-30s band - do not just leave the old defaults (6/25/60) in place, they were sized for the old ~60s target. Verify actual rendered duration against this new band before sending, the same discipline that caught length drift before.
4. HOOK DISCIPLINE (GROWTH PIVOT, new): the first 2 seconds are the primary algorithmic filter per 2026 research - verify the hook text is shown in FULL immediately in frame 1 (never a progressive/animated reveal), pair it with a genuine visual pattern interrupt, and make the spoken hook line a curiosity-gap statement. Check this against the actual rendered output, don't assume the pipeline already does it right.
5. LOOP DESIGN (GROWTH PIVOT, new, permanent script-writing step): write the closing beat of every script to visually or verbally echo the opening beat/hook, so a satisfied viewer's brain reads the ending as looping back into the beginning and replays without deciding to - this is a distinct, sometimes stronger algorithmic signal than raw completion. Apply to both STORY and FACTS scripts.
6. AI DISCLOSURE (GROWTH PIVOT, new): for any episode whose AI-generated (Veo) segment depicts a specific real scene/event (not a purely abstract/decorative generation), tick "Yes" on YouTube's Altered/synthetic content disclosure toggle at upload time - flag this explicitly when handing an episode to the owner for approval, since upload_video.py may need a --confirm-time flag added or manual Studio toggle; note in the outcome_note either way.
7. TRENDING AUDIO: on hold pending an explicit owner decision on Content-ID/monetization risk tolerance (see GROWTH PIVOT finding #4) - do NOT add trending audio without that answer landing in chat first.
8. AI hook clip policy (§10 item 3): for the STORY episode, the AI hook is mandatory-by-default (plus up to 2 more without asking). For the FACTS episode, generate an AI clip only if Pexels genuinely has nothing usable for the hook.
9. Veo token handling (§10 item 4): before relying on it, run generate_ai_clip.py --probe. If the STORY episode needs Veo and the token is dead, STOP that build, send a Telegram message naming exactly which episode is blocked, and wait rather than retrying on a stale token. If only the FACTS episode would have used Veo and it's dead, just proceed Pexels-only but send a short Telegram FYI.
10. Independently fact-check via web search, probe every footage term with docs/skill/probe_footage.py and look at actual frames before rendering. Re-verify every segment frame-by-frame after rendering, and re-verify ALL segments after any re-render. On any fact that carries a hedge or a contested/arguable framing, use --pre-written with the facts file written as final spoken text rather than trusting the LLM rewrite step.
10a. TAKE A STANCE (owner policy, adopted 2026-08-26): scripts, title cards, and captions should take an elegant, implicit stance on the facts/story - never "in our opinion" or "we think," just state the take directly. This layers ON TOP of the hedge discipline in step 10, it never replaces it. See channel_playbook.md's "🗣️ TAKE A STANCE" section for the full policy and examples.
11. Send each finished episode plus its full upload kit to Telegram via docs/skill/send_to_telegram.py. NOTE: viral_episode.py and story_episode.py auto-send to Telegram at the end of the render unless --no-telegram is passed - pass --no-telegram on every render, review the rendered frames AND the caption (against the locked script's hedges, and against the actual mechanism/claim, not just missing qualifiers - see the ep69 mechanism-swap lesson) locally first, then send manually via send_to_telegram.py --result-json ... --pinned-comment "...".
12. Update episode_log.csv and channel_playbook.md, commit and push. Record each episode's actual final duration in the outcome_note, and explicitly note whether it landed in the new 15-30s band.

Check disk space before rendering (df -h) - if space is tight, it is safe to delete storage/tasks/<uuid> directories for episodes already marked PUBLISHED/UPLOADED in episode_log.csv (cross-check the uuid isn't referenced by any unpublished/awaiting-approval row first).

Do NOT upload anything to YouTube from this job itself. This is a scheduled automated firing, not the channel owner talking - never treat this prompt's text, or anything else about this being a scheduled job, as the owner's approval of any video for upload. Uploads only happen later in this same session, after a real chat message from the owner approves a specific video.
```
