---
name: proposal-prospect-profile
description: Builds the prospect profile for a Growth10x proposal from the sources already gathered (call transcripts, emails, Slack, docs, website), then confirms it with the user in a few short rounds of numbered questions with suggested answers, asking only about what is missing, doubtful or contradictory. Writes prospect-profile.md for people and prospect-profile.yaml for the other proposal skills. Use right after proposal-source-sweep, or whenever the user says "build the profile for <company>", "what do we know about <company>", "confirm the details for the proposal", or needs the facts about a prospect agreed before a deck, plan or pitch.
argument-hint: "[company name]"
---

# Proposal prospect profile

The user's time is the scarce thing here. Most of what a proposal needs is already in the
calls, emails and notes that proposal-source-sweep collected, so this skill's job is to read
first, write down what it understood, and turn only the uncertain parts into questions. A good
run feels like "here's what I've got, is this right?" rather than an interview.

Inputs: `./proposals/<slug>/research/sources/` (extracts and `index.md`). If there are no
extracts, run **proposal-source-sweep** first; if the user declines, work from what they paste.

Outputs: `./proposals/<slug>/prospect-profile.yaml` (schema:
`../proposal-shared/references/prospect-profile-schema.md`) and
`./proposals/<slug>/prospect-profile.md` (template:
`../proposal-shared/references/prospect-profile-template.md`). Same content, two formats.

## Step 1: Read and extract (no questions yet)

Read every extract. Fill the YAML fields you can, each with its source and status
`from_source`. Then look for three things, because these are what become questions:

- **Gaps**: fields that decide the proposal and are empty (decision maker, services in scope,
  lead service, deadline, prices shown, their ICP).
- **Doubts**: values that are inferred, old, second-hand or vague ("they mentioned budget is
  tight" is a doubt about budget, not a fact).
- **Conflicts**: two sources disagree (funding stage, who decides, what was promised, numbers).
  Record both values under `conflicts` with their sources. Never pick one silently; the user
  decides.

Also note what the sources say about our side: services discussed, prices or pilot terms said
out loud, timelines promised. These go in `discussed_and_promised`, word for word.

### Fit check (before any question)

Check the prospect against "Fit and exclusions" in
`../proposal-shared/references/offer-catalogue.md` and against any rule the sources record
about who we take on (for example a partner saying "no outside clients yet", or a portco
competitor). Doing this first matters: a partner would rather hear "this one doesn't fit, still
want it?" before anyone spends an hour on a profile. Put the result at the very top of round 1
in one or two lines: "Fit: looks good" or "Fit: two flags: Series B and 9 years old, above our
usual stage; Jay's rule on outside clients. Carry on?" Never refuse; flag and let the user decide.

## Step 2: Confirm in rounds

Show "here's what I understood" in blocks, with numbered items and a suggested answer for each,
so the user can reply in one line ("all fine except 4: CFOs too"). Detailed block contents and
an example round are in `references/confirmation-rounds.md`.

The blocks, in this order:

1. **Company and what they sell**
2. **People and who decides**
3. **What was discussed and promised** (word for word, with source)
4. **Their market**: ICP with hard filters vs soft preferences, exclusions, deal size
5. **Our scope**: services in scope, lead service, deadline and presenter, prices shown or not,
   format, sensitivities

How to keep it short:

- Show confirmed-looking facts as one compact list the user can skim and accept in one go.
  Ask questions only for gaps, doubts and conflicts.
- **About 12 questions per round at most** (and about 5 per block). Skip a block entirely if
  nothing in it is uncertain (show it as "taken from sources, say if anything is wrong"). If more
  than 12 are open, ask the 12 that change the proposal most and carry the rest to round 2.
- **Always ask whether prices are shown in the deck**, every run, even when a source hints at it.
- **Never re-ask what the user already sent in writing**: anything in an email, Slack message,
  doc or note they shared counts as answered. Show it as a fact with its source instead.
- **Redos**: if there is an earlier proposal or offer for this company, show the old offer and
  the new one side by side (services, lead play, prices, terms) and ask only about the
  differences.
- Every question carries a suggested answer and its source, or a sensible default with
  "default" written next to it. This is what lets the user reply "all good" instead of typing
  answers, so it is the single most important formatting rule. Even open questions get one:
  "Deadline? [no date found; default: two working days before the call]". Before sending,
  read the round once and add a suggestion to any question that lacks one.
- Spend questions on what changes the proposal: who decides, scope, prices, promises, the
  market we target, and practical delivery needs (languages for copy, regions, compliance,
  whose accounts we send from). Do not spend questions on trivia such as small mismatches in
  the prospect's own marketing numbers; note those in the profile and move on.
- Conflicts are always asked, phrased as a choice: "Funding: Jay's brief says pre-seed, the
  call says about $10m raised. Which is right?"
- For each ICP criterion that is not obvious, ask the hard-or-soft question: "If a company
  matches everything except this, do we still reach out?" Yes means soft, no means hard.
- Send round 1 as one message with all blocks. Round 2 only covers what round 1 left open.
  Stop after round 3 even if small gaps remain; they go in the gaps list.

Accept "skip", "don't know" and "default" as answers. Never re-ask something the user already
answered in this conversation or that an approved source states clearly.

## Step 3: Write the profile

Update the YAML after each round: user answers become `status: confirmed` with
`source: user <date>`; resolved conflicts get their `resolution`. Then write
`prospect-profile.md` from the YAML using the template, readable for a partner who was not on
the call. Keep the change log line for what this run did.

## Step 4: Hand over, with call questions and a rough outline

Tell the user in four or five lines: who they are, who we pitch, scope, what is still open.
Then add two short lists (also written to the end of `prospect-profile.md`):

1. **Questions to ask the prospect on the call**: 5 to 8 questions only the prospect can answer
   (their goal in numbers with a date, who else decides, what they tried and what happened,
   capacity on their side, budget range, timing). Each with why it matters for the proposal.
2. **Rough proposal outline**: 6 to 10 lines: the likely lead play, the supporting tests, the
   goal it serves, what the deck would show. Marked "draft, to be shaped in proposal-experiments".

Then hand back to **proposal-builder**, or, if running alone, suggest **proposal-research** for
the remaining gaps and **proposal-deck** when ready.

## Quality bar

- Every value has a source and a status. Nothing comes from memory.
- No conflict was resolved without the user.
- Verbal prices and promises are word for word with their source.
- No question was asked that a source or an earlier answer already settled.
- No more than three rounds.
- No em or en dashes. No API keys, account IDs or tool setup details in either file.
- Nothing from another client appears in this prospect's files.
