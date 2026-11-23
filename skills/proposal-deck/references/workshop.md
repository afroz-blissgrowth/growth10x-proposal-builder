# The deck workshop: formats for each stage

The deck is built with the user in stages. Each stage writes one file, shows it, asks numbered
questions with suggested answers, and waits. The files are internal (sources and notes stay in
them); only the built deck is client-facing.

## How every gate asks

```
Here's the storyline for ReelFlow (10 beats). Reply "all good" or correct by number.

1. Open on their goal, not on us: "£1m ARR from organisers by December 2027". Agree? [yes]
2. Put the market slide before the plan, so the plan reads as the answer to the numbers? [yes]
3. Drop the separate thesis slide and carry "show, don't pitch" in the plan slide? [no: the
   thesis is the reason the plan differs from what they tried; keep it]
```

- Each question carries a suggested answer and its reason. The user should be able to reply in
  one line.
- About 8 questions at most per round. Ask what changes the deck; never what a source settled.
- If the user's answer conflicts with the evidence or the logic, say so once with the evidence and
  an alternative, then follow their decision and note it in `offer.md`'s decision log.
- The skill never answers its own questions, including in test runs.

## Stage 1: storyline.md

```markdown
# <Client> deck: storyline
From offer.md agreed <date>. <N> beats. Decision we want: <one line>.

| # | Act | Action title (full sentence, client-specific) | Job of the beat | Key message (offer.md s1) | Evidence (source) |
|---|---|---|---|---|---|
| 1 | Hook | Your next £1m comes from the organisers outside your top 50 | Frame the opportunity in their terms | 1 | goal, call 05:20; market map 19 Nov |
| 2 | Situation | Easyfairs proved the product; reach is now the limit | Agree where they are | 2 | 10 shows on contract (call 08:10) |
| ... |
```

Rules: 8 to 12 beats. Action titles are claims with a verb, not topics ("The plan" is a topic;
"Four tests, one lab, every result in your name" is a claim). Each beat traces to a key message.
The arc usually runs hook, situation, goal, problem, why this approach, the plan, each play with
its mechanism and proof, measurement, first weeks, the ask. Apply the name-swap test to every
title: if another client's name fits, rewrite it.

## Stage 2: slide-plan.md (machine read by deck_check.py)

One `## <n>. <id>` heading per slide, then `- key: value` lines. Values that are lists use ` | `.

```markdown
## 3. goals
- act: Goal
- kind: content            # content | cover | thanks | agenda | hero | closing (only content is gated for fill and words)
- job: Agree the goal and the gap, in their numbers
- audience_move: "we need more leads" -> "we need 38 more organisers outside the top 50"
- action_title: Break even in 2027 with organisers paying for it
- key_message: 1
- evidence: £1m ARR by Dec 2027 (call 05:20) | Easyfairs 10 shows (call 08:10) | avg deal about £25k (pricing page)
- facts: £1m | Easyfairs | December 2027 | 38 more organisers
- layout: stat-row
- layout_reason: two goal numbers plus the path to them; stat cards with a timeline below
- blocks: b-stats (2) | b-tl (4 points) | b-card (gap) | b-card (their words)
- motion: count-up on both numbers | timeline draws | cards rise staggered
- interaction: hover links numbers to timeline points (data-nm)
- mockups: none
- time_based: yes
- ground: dark
- words: 130 to 180
- icons: none
- speaker_note: internal only, never on the slide
```

`deck_check.py` reads `kind`, `words`, `facts`, `layout`, `time_based` and `mockups`; the critic
reads the rest. Show the plan to the user as a compact table (id, action title, layout, motion,
interaction, words) with the full entries below it.

Density targets come from `content-standard.md`. A content slide below 130 words needs a reason
in `layout_reason` (a hero visual, a mockup that carries the content) and a lower `words` range.

## Stage 3: pilot

Cover, goals and the lead play's mechanism slide. One review file, one link
(`build.py --review`), every gate passing, the critic run once. Ask about ground, accent strength,
density and motion.

## Stage 4: batch loop (about 5 slides per batch)

1. Content in chat (plain text, no quote bars): per slide the action title, body copy, numbers
   with sources. Ask for OK or changes per slide.
2. Design the part files from the plan.
3. Gates: `build.py <deck_dir> --theme <t>` then
   `deck_check.py <deck_dir>/build/<slug>-<t>.html --deck <deck_dir> --render --slides <ids>`.
   Fix until it passes. `gate-<t>.json` is the record; the batch is not shown while it fails.
4. Critic: a fresh subagent with only the PNGs, the plan entries and `critic-rubric.md`.
5. Show one contact sheet and the link. Ask per slide. Apply feedback only to the slides named.

## The fact checklist (per deck)

Before the final pass, write `deck/checklist.md`: yes or no lines generated from `offer.md` and
the profile, each checked against the built deck. For example:
- Slide goals uses ReelFlow's own goal with currency and date. yes or no
- Every price equals the catalogue version in the profile, ex VAT. yes or no
- No slide names Growth Console or "the console". yes or no
- The cover shows the ReelFlow logo, not the name in text. yes or no
- Every key message in offer.md lands on at least one slide (which). yes or no
- Every competitor named is in research/competitors.md. yes or no
- Each plan's start date is the same on every slide that shows it. yes or no
- Every claim in a mockup message is in the proof list in offer.md. yes or no
Any "no" is fixed before publishing.
