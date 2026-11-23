---
name: proposal-builder
description: Start here for any Growth10x proposal, pitch or prospect prep. Runs the proposal skills in order (find what we already know about the company, confirm it with the user in a few short rounds, research the gaps, work out the strategy and offer with the user, then build the deck as a workshop, or plans) and keeps one prospect profile so nothing is asked twice. Use whenever the user says "proposal for <company>", "new prospect", "prep for a pitch call with <company>", "we have a call with <company> next week", "build a deck for <company>", "start proposal builder", or names a company they want to pitch, even if they don't say "proposal".
argument-hint: "[company or prospect name]"
---

# Proposal builder

The entry point. It does not do the work itself; it runs the other proposal skills in the
right order, keeps the user oriented, and makes sure each step builds on the last instead of
starting over. The user should never have to repeat something they already said or something
that already exists in their calls, emails, Slack or docs.

Everything for one prospect lives in `./proposals/<slug>/` (relative to where the user is
working). The shared record is the prospect profile: `prospect-profile.md` for people and
`prospect-profile.yaml` for the skills. Schema: `../proposal-shared/references/prospect-profile-schema.md`.

## The order, and why

1. **proposal-source-sweep**: find every source we already have on the company and ingest the
   ones the user approves. Reading before asking is what makes the later questions short.
2. **proposal-prospect-profile**: turn the sources into the profile, then confirm it with the
   user in batched rounds. Only missing, doubtful or contradictory items become questions.
3. **proposal-research**: website, case studies, LinkedIn, competitors, ads, market sizing,
   and the brand (the site's main colour and the real logo files) for whatever the profile lacks.
4. **proposal-experiments**: the strategy and offer, worked out WITH the user: 10 to 20 sourced
   options, numbered question rounds with pushback, a shortlist, goals stated precisely, and
   `offer.md`. This is the step that makes the deck specific to the client; never skip it.
5. Write `proposal-plan.md` (below) from `offer.md` and stop for the user's go-ahead.
6. Outputs: **proposal-deck** (a workshop: brand check, storyline, slide plan, pilot, batches of
   about 5, final pass), and plan skills where in scope (proposal-outbound-plan,
   proposal-founder-brand, proposal-linkedin-ads, proposal-dinners-events, proposal-aeo-audit,
   proposal-testimonials), plus proposal-plan-page or proposal-one-pager.

proposal-deck will not start without `offer.md`. If another skill in the list is not installed,
say so in one line and carry on with the next one; never block the whole run on a missing piece.

## Step 0: Pick up where things are

Make a slug from the company name (lowercase, hyphens). If `./proposals/<slug>/` exists, read
`prospect-profile.yaml` and any `proposal-plan.md`, then tell the user in three or four lines
what is done and what is next, and ask whether to continue from there or start fresh. Starting
fresh keeps the old folder as `<slug>-<date>-old`; never delete it.

If it does not exist, ask for the company name if it was not given, and go to step 1.

Talk to the user in plain words, never about folders, files, slugs or YAML: say "No earlier
work on Atmospheric AI, starting fresh" rather than "no proposals/ folder found". The user
should only hear about what matters to them (the company, sources, questions, the deck).

## Step 1 to 4: Run the skills

Hand over to each skill in turn and let it run its own steps. Between skills, give the user a
two-line status ("Profile confirmed: 3 people, 4 services in scope, 2 gaps left. Next:
research.") so they always know where they are.

Keep the conversation moving: the user wanted fewer, smarter questions. Do not add your own
questions between skills unless something blocks the next one. The strategy step is the
exception that proves the rule: there the questions ARE the work, so let proposal-experiments
run its rounds fully.

## Step 5: The proposal plan (one page, for Dan or Jay)

Before building anything heavy, write `./proposals/<slug>/proposal-plan.md` so a partner can
approve the direction in two minutes. Keep it to one screen:

```markdown
# Proposal plan: <Company>
Updated: YYYY-MM-DD

## Who they are
<two lines: what they sell, to whom, stage>

## Who we're pitching
<name, role, decision maker or not; meeting date and who presents>

## Their market
<ICP in one line: titles, industries, size, regions; headline counts if researched>

## What we'd propose (from offer.md)
Lead play: <one line>, because <client-specific reason, source>
1. <test>: <hypothesis, the one metric, success bar>
2. ...

## Goals (what, currency, by when, whose)
<from offer.md section 4>

## Scope and commercials
<services in scope, lead service, prices shown or not>

## Open questions
<only the ones that block the proposal>
```

Then show the user the plan and a short menu, tailored to what is in scope. For example:

```
What next?
[A] Build the deck now
[B] Detailed outbound plan first (then the deck)
[C] Founder branding plan first
[D] Save and come back later
```

Run what they pick. Offer companion pages (detailed plans, a one-pager) only after the deck is
signed off, as a question, never automatically.

## Rules that apply across the whole run

- Read `../proposal-shared/references/house-rules.md` once at the start; every skill follows it.
- Nothing is sent to anyone. Skills read sources and write local files. Publishing a deck is a
  private link the user shares themselves.
- Call notes and transcripts stay in the local `research/` folder.
- Paid lookups (Apify, Apollo credits, enrichment) are shown with a cost estimate and wait for
  a yes. One yes can cover a batch the user has seen.
- Rendering uses the separate Playwright browser through the repo scripts, never the user's
  own Chrome (it has closed people's tabs before).
- Work with whatever tools this user has connected. Detect them by name; never assume a
  specific account, workspace or person.
