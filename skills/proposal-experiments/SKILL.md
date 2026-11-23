---
name: proposal-experiments
description: Works out the strategy and the offer for a Growth10x proposal WITH the user. From the confirmed prospect profile and research it proposes a strategy with sourced reasons, generates 10 to 20 offer and test options across Growth10x services and test tracks (markets and regions, buyer types, adjacent industries, channels, partnerships, founder branding, LinkedIn ads), questions the user in numbered rounds until the shortlist and the reasoning are agreed, states every goal precisely, and writes offer.md, which proposal-deck needs before it starts. Use after proposal-research, or when the user says "what should we propose to <company>", "experiments for <company>", "shape the offer", "what tests would we run", "agree the strategy", or before any deck or plan is built.
argument-hint: "[company name or slug]"
---

# Proposal experiments and offer

A deck is only as good as the strategy under it. The decks the owner approved (ContextPath is the
reference) worked because every slide came from research into that client's market, buyers,
numbers and situation, and from a strategy the team had argued through. A skill that jumps from
a profile to slides produces a thin copy of the last deck. This skill is the step in between: it
thinks, proposes, and then **checks the thinking with the user** before anything is built.

It is a conversation, not a list. Each round shows the reasoning with its sources, asks numbered
questions with a suggested answer and the reason for it, pushes back when an answer conflicts
with the evidence, and records what was agreed and why. That recorded "why" is what lets the
deck explain why each part of the plan fits this client.

Inputs: `./proposals/<slug>/prospect-profile.yaml` and `.md`, `research/`, and the source
extracts. If the profile is missing or still has blocking gaps (decision maker, their goal, the
services in scope), say so and offer to run proposal-prospect-profile or proposal-research first.

Read before starting:
- `../proposal-shared/references/offer-catalogue.md` (services, scope, prices, fit rules)
- `../proposal-shared/references/house-rules.md` (especially sections 3, 4, 10 and 11)
- `references/test-tracks.md` (the tracks, what a good test looks like, metrics per channel)
- `references/offer-template.md` (the offer.md format)

Output: `./proposals/<slug>/experiments.md` (all options, scored, with the user's picks) and
`./proposals/<slug>/offer.md` (the agreed strategy and offer). proposal-deck will not start
without `offer.md`.

## Step 1: Read and form a view (no questions yet)

Read the profile, research and extracts. Write down for yourself, with a source for each:
- **Their goal in their words**, and what is missing to state it precisely (what, currency, by
  when, whose: "£1m ARR from event organisers by December 2027", never "1M ARR").
- **Where they are today**: customers, proof, channels that work, channels that do not,
  capacity (who on their side can take calls, approve copy, appear on camera).
- **Their market**: the ICP, segments with counts, the buyers by explicit title, competitors and
  what they do (ads, content, events), buying signals that exist for this market.
- **Constraints and sensitivities**: who must not be contacted, rules from partners, budget hints,
  deadlines, things they said they will not do.
- **The core problem** in one sentence: why they are not at the goal yet.

Then form a strategy: a lead play and supporting plays, each tied to that problem. Be opinionated:
a proposal that offers everything has no strategy. The default is one lead service plus two or
three tests, unless the evidence says otherwise.

## Step 2: Generate 10 to 20 options

Use the tracks in `references/test-tracks.md` (markets and regions, buyer types, adjacent
industries, channels, offers and hooks, partnerships, founder branding, LinkedIn ads, events and
dinners, proof and testimonials, AI search). For each option fill every field:

| Field | What it holds |
|---|---|
| What | The play or test in one line, concrete ("LinkedIn plus a personalised event page to UK organisers running 1 to 5 shows a year") |
| Why it fits | The client-specific reason, with its source (profile section, call timestamp, research file) |
| Hypothesis | "If we do X for Y, then Z, because W" |
| The one metric | The single number that decides it (positive replies per 100 messaged, booked calls, sign-ups) |
| Success bar | The number that means keep going, and the time box ("5 booked calls from 300 messaged in 6 weeks") |
| What we need from them | Inputs, approvals, people, assets, access |
| Service and price | Which catalogue service carries it, and its price if prices are shown |
| Effort and risk | Low, medium or high, with one line why |

Score each option on fit to the core problem, evidence strength, speed to a signal and cost, and
sort. Generic options that would fit any client get dropped here: apply the name-swap test ("if I
put another client's name in, does this still read the same?"). Write all of them to
`experiments.md` with their scores; nothing is deleted later, picks are marked.

## Step 3: Strategy round (stop and ask)

Show the strategy and the top options in one message, then ask. Format:

```
Here's the strategy I'd propose for ReelFlow, and why.

Core problem: Chris closes the big organisers one by one, but nothing reaches the long tail
(call, 12:40: "getting someone to open it feels like the big challenge").
Lead play: signal-led outbound to UK organisers running 1 to 5 shows a year, each message
carrying a page built on their own event site (their best-converting asset today, call 18:05).
Supporting tests: ...

Does this make sense? Specifically:
1. Lead with long-tail organisers rather than new verticals, because the product is proven
   with organisers (Easyfairs, 10 shows) and the verticals have no proof yet. Agree? [yes]
2. Include the US test now? Chris is the only seller and said capacity is tight (call, 31:10),
   so I'd hold it to month 3. [hold to month 3]
3. Cold calling to test property and accountancy: the cheapest way to learn which vertical is
   real. In, or not now? [in, as a 2-week test]
4. Founder branding for Chris: the industry runs on reputation (call, 22:30). Core package? [yes]
5. Show prices in the deck? [no: profile says prices not shown]
```

Rules for the round:
- Numbered questions, each with a suggested answer in brackets and the reason in the line, so the
  user can reply "all good except 2".
- About 8 questions per round at most; three rounds at most. Ask only what changes the plan.
- **Push back when an answer conflicts with the evidence.** Say what the evidence says and offer
  an alternative; then do what the user decides and record both: "You chose to lead with
  property; the only proof today is with organisers (profile s7). Option: run property as the
  second test with calls first. Keep property as lead?"
- Never re-ask something already answered in this conversation or stated in a source.
- In test runs the simulated user's answers come from the run instructions, but the skill still
  stops and asks: it never answers its own questions.

## Step 4: Shortlist and goals (stop and ask)

Show the shortlist the answers produced (usually one lead play and 2 to 4 tests) and then state
**every goal precisely**: what is counted, the currency, by when, and whose number it is, plus the
source and whether it is the client's goal or our estimate. Ask the user to confirm each:

```
Goals as I'd write them in the deck:
1. £1m ARR from event organisers by December 2027 (ReelFlow's goal, call 05:20) [confirm]
2. 40 paying organisers outside the top 50 by December 2027 (our estimate: £1m / about
   £25k a year each, from the pricing page) [confirm or correct the average deal]
3. 5 booked calls per 300 organisers messaged in the first 6 weeks (our success bar) [confirm]
```

Then commercials: structure (base, core, premium, or a bundle), prices shown or not, any pricing
override with its reason, the term, and what is promised verbally (word for word from the
profile). Then format and deadline: deck, plan pages, one-pager; who presents; the date.

## Step 5: Write offer.md and hand over

Write `offer.md` from `references/offer-template.md`. It holds the strategy brief that the deck
is built on: audience and the decision we want, the core problem, the strategy and **the agreed
reasoning for each choice** (with sources), 3 to 5 key messages, the proof available, the
services and tests with their hypotheses and metrics, the goals stated precisely, commercials,
format and deadline, and a decision log (what the user changed and why, including any pushback).

Show a short summary and ask for a final yes. Then append to the profile's change log
(`YYYY-MM-DD | proposal-experiments | offer agreed: <lead play>, <n> tests`) and hand back to
proposal-builder (or suggest proposal-deck if running alone).

## Quality bar

- Every option and every reason names something specific to this client, with a source.
- Every goal says what, currency, by when and whose. No bare "1M", no "10x growth".
- The user answered the strategy, shortlist and goals rounds; nothing was assumed silently.
- Pushback, when given, is recorded with the user's decision in the decision log.
- Never mention "Growth Console" in client-facing wording; it is included in everything and is
  described by what it does (tracking, reporting) when needed.
- No em or en dashes. No other client's names or numbers. Prices only from the catalogue.
