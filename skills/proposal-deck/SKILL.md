---
name: proposal-deck
description: Builds a Growth10x client proposal or pitch deck as a single HTML slide file, as a workshop with the user, from the agreed offer.md (made by proposal-experiments) and the prospect profile. Brand check (logo and accent), storyline of 8 to 12 beats for approval, a per-slide plan for approval, a 3-slide pilot published as one review file (slides 1 to 3 light, 4 to 6 dark, one link), then batches of about 5 slides with automatic gates and user feedback, then a final pass and one link. House design is the ContextPath look; only the client's colour and logo change. Use for "proposal deck for <client>", "pitch deck for <client>", "build the deck", "Growth10x deck", "turn the offer into slides", or to change or re-skin an existing Growth10x deck.
argument-hint: "[client name or slug]"
---

# Growth10x proposal deck

A deck the owner approves is dense, specific and alive: every content slide carries this
client's market, buyers, numbers, competitors and situation, each with a source, laid out in the
house style (dark or light ground, glass panels, highlight sweeps, constellation, count-ups,
timelines that draw, click-throughs). The deck that failed (an events company pitched with
another client's slides, words swapped, 82px empty bands, no count-ups, "1M ARR" with no
currency, an orange accent from the logo instead of the site's teal, no client logo) failed
because it skipped the thinking and the user. So this skill is a **workshop**: it stops at each
stage, asks numbered questions with suggested answers, and moves on only on the user's yes.

Reusing layouts, structures and even phrasing from approved decks is allowed. What is not
allowed is a slide whose substance was not worked out for this client.

Read before starting:
- `../proposal-shared/references/house-rules.md` (every rule; sections 10 and 11 are gated)
- `references/lessons.md` (every owner correction so far; read it every time)
- `references/workshop.md` (the stage formats: storyline, slide plan, batch loop, question rounds)

Read when you reach them: `references/layout-library.md` (layouts by what a slide does),
`references/content-standard.md` (what a full slide holds), `references/components.md`
(building blocks and icons), `references/design-system.md`, `references/build-and-qa.md`
(commands, gates), `references/critic-rubric.md` (the fresh-eyes review).

## Hard rules

- **Never launch the user's Google Chrome**, and never kill, quit or signal any browser
  process. Rendering only through `scripts/qa_render.py` and `scripts/deck_check.py`, which use
  Playwright's headless_shell. If it is missing, stop and tell the user.
- **No `offer.md`, no deck.** If `./proposals/<slug>/offer.md` is missing, say so and offer to run
  proposal-experiments. Do not build from the profile alone or from memory.
- Never name "Growth Console" (or "the console") in a client deck: it is included in everything.
  Describe what is tracked and reported.
- Every number says what it counts, the currency, by when and whose ("£1m ARR from event
  organisers by December 2027"). The gate fails a bare "1M".
- No em or en dashes anywhere. Never invent numbers. Never reveal other clients. No names or
  emails on the closing slide. Mockups say Illustrative, use fictional names, no counts.
- Headings and their detail text look clearly different: a card heading at least 1.2x the detail
  size and at least 200 heavier (blocks: `b-h` 30px 800 over `b-d` 21px 400); row titles under 26px
  at least 1.08x and 200 heavier.
- Icons are picked by meaning for this client from `assets/icons.svg` (a ticket or a stage for an
  events company, never a bank).
- Every stage ends with a question to the user and waits. In test runs the simulated answers come
  from the run instructions; the skill still stops and asks and never answers itself.

## Stage 0: Load and brand check (gate 0)

1. Read `offer.md` in full, then `prospect-profile.md` and `.yaml`, `experiments.md`, any
   `plans/`. Note the strategy brief (audience, decision wanted, key messages, proof), goals,
   commercials, format, deadline. If `catalogue_version` is older than the catalogue, say what
   changed for the services in scope.
2. **Brand.** From research (`research/brand/brand.json`): the accent is `accent_pick`, the
   site's most-used brand colour, not the logo's first colour. The logo is the company's own file
   (SVG first, else PNG 400px or wider) plus a light variant for dark ground (official if one
   exists, else `../proposal-research/scripts/logo_variant.py`). If either is missing, run that
   part of proposal-research now.
3. Show the user, in one message: the accent swatch hex with where it came from and the runner-up,
   the logo on dark and on light (render a 2-slide check with `build.py --review --brand-check` if
   useful), and the ground suggestion. Ask: "Accent #10B5A8 (teal, most used on reelflow.io;
   runner-up yellow #FCD456). Logo as shown. Correct?" Record the answer in `deck.json` as
   `"brand_confirmed": true` with `accent` and `logo`. build.py refuses to build without it.
4. Build the deck's term list for the specificity gate: `deck.json` `"client_terms"` = company
   and product names, people, named customers and partners, competitors, places, segment names,
   and the key figures from `offer.md`. These are what make a slide unmistakably theirs.

## Stage 1: Storyline (gate 1)

Write `./proposals/<slug>/deck/storyline.md` (format in `references/workshop.md`): 8 to 12 beats,
each one full-sentence **action title** (a claim with a verb, specific to the client), the job of
the beat, the key message from `offer.md` it carries, and its evidence with sources. Acts usually
run: their situation, their goal, the core problem, why this approach wins in their market, the
plan, each play with its mechanism and proof, how we measure, the first weeks, the ask.

Show it, then ask numbered questions with suggested answers: order, what to cut, which beat
leads, anything missing for the decision wanted. Push back if a change breaks the logic ("moving
pricing before the problem means they see cost before value; keep it after the plan?").
Do not plan slides until the storyline is approved.

## Stage 2: Slide plan (gate 2)

Write `./proposals/<slug>/deck/slide-plan.md`: one entry per slide in the schema in
`references/workshop.md` (id, act, kind, job, audience move, action title, key message, evidence
and source, facts that must appear, layout from `references/layout-library.md` with the reason,
blocks, motion recipe, interaction, mockups, time_based, ground, density and words target,
icons with their meaning). Rules:
- Choose layouts by what the slide does (problem, proof, process, market, timeline, offer), not
  by what the last deck had. No layout twice in a row.
- Every content slide: words 130 to 220 unless the plan says why, at least 3 client-specific
  facts, at least one build or interaction in every run of 3 slides, a count-up on any slide whose
  hero is a number, a timeline that draws on any slide about time, mockups where showing beats
  telling. Targets from `references/content-standard.md`.
- One idea per slide; depth goes into builds, jumps and mockups, not extra slides.

Show the plan as a compact table plus the full entries, then ask about anything uncertain (which
proof to show, what the mockup shows, density). Do not build until it is approved.

## Stage 3: Pilot review (gate 3)

Build the cover, the goals slide and the lead play's mechanism slide as one review file:
`python3 scripts/build.py <deck_dir> --review` (slides 1 to 3 light, 4 to 6 dark, one link). Fix
every lint and gate error, run `qa_render.py` on the review file, read the contact sheet yourself,
run the critic (`references/critic-rubric.md`), fix, then publish ONE private link. Ask: ground
(light or dark), accent strength, density, motion, anything off. Record the answers in the
profile change log and in `references/lessons.md` if they are standing rules.

## Stage 4: Build in batches of about 5 (gate per batch)

For each batch, in plan order:
1. **Content first**: show the copy for the batch's slides (action titles, body, numbers with
   sources) as plain text in chat. Ask for an OK or changes per slide.
2. **Design**: write the part files from blocks in `assets/components.html`, following the
   plan's layout, motion and interaction. Rewrite every text node; keep `data-layout`.
3. **Automatic gates**: `build.py` (lint plus the static gate) and
   `deck_check.py <built> --deck <deck_dir> --render` must pass: per content slide fill 58% or more
   and empty band 70px or less (aim for 66% and 40px), deck averages fill 70% or more, band 30px or
   less and 140 words or more (the approved ContextPath deck: 73%, 28px, 155 words), words in range, units, banned terms, specificity, timelines,
   interaction every 3 slides, count-ups on hero numbers, entrance motion, hierarchy, hollow panels.
4. **Critic**: a fresh subagent reviews the batch's PNGs against the rubric and the name-swap
   test, plus the batch's lines of the fact checklist. Fix hard findings.
5. **User feedback**: one contact sheet and the link. Apply feedback only to the slides named.
   Then the next batch.

## Stage 5: Final pass and publish

1. Full build in the chosen theme, full QA render once, `deck_check.py --render` passing, the
   critic on the whole deck (coherence, storyline, repetition), the fact checklist all yes, and
   the house rules final check (section 9).
2. Publish the built HTML as one private artifact; republish to the same path to keep the link.
   Once a link has been shared with the client, new work goes to a separate link and the shared
   version is snapshotted.
3. Append to the profile change log, and add any new owner correction to `references/lessons.md`.

## Files

| Path | What it is |
|---|---|
| `assets/template-shell.html` | Page shell: fonts, tokens, stage, nav, JS (builds, jumps, mockups, count-ups, tabs, flips, constellation). Never edit per client |
| `assets/components.html` | Building blocks (`b-*`) and full layouts from approved decks, flattened CSS, plus mockups |
| `assets/icons.svg` | Line icon set with meanings; build.py inlines the ones a deck uses |
| `assets/examples/` | Worked example slides that pass every gate |
| `scripts/build.py` | Assembles the deck, sets accent tokens, inlines icons, lints, runs the static gate |
| `scripts/deck_check.py` | The gate: static checks plus `--render` probe; writes gate JSON, exit 1 on failure |
| `scripts/qa_render.py` | Screenshots, mid-animation frames, DOM probe, contact sheets (`--probe-only` for a fast check) |
| `scripts/dom_probe.js`, `contact_sheet.py`, `csskit.py` | Used by the scripts above |
| `references/workshop.md` | Storyline, slide plan schema, batch loop, question rounds, fact checklist |
| `references/layout-library.md` | Registered layouts by function with element schema and density |
| `references/content-standard.md` | What a full slide holds, per slide type |
| `references/components.md` | Blocks, components and icons, and when to use each |
| `references/critic-rubric.md` | Fresh-eyes review of rendered slides |
| `references/lessons.md` | Owner corrections, read before every deck |
| `references/design-system.md`, `references/build-and-qa.md` | Tokens, type, motion; commands, deck.json, gates |
| `references/slide-structure.md` | Storyline beats and service moves (what each play's slides usually need to show) |
