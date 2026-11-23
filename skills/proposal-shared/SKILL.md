---
name: proposal-shared
description: Reference library for the Growth10x proposal-builder skills (proposal-builder, proposal-source-sweep, proposal-prospect-profile, proposal-research, proposal-experiments, proposal-deck, proposal-plan-page and the plan skills). Holds the offer catalogue and prices, the house writing rules, the buying-signal library and the prospect profile schema and template. Not a workflow on its own. Load it when another proposal skill points here, or when the user asks for Growth10x prices, packages, house rules or signal ideas.
---

# Growth10x shared library

This skill does nothing by itself. It is the single source of truth that the other
proposal-builder skills read, so prices, rules and signals live in one place.

## Files

| File | What it holds | Read it when |
|---|---|---|
| `references/offer-catalogue.md` | Every Growth10x service with scope and price (GBP ex VAT), structure (Console, Core, Premium), terms and fit rules, versioned | Any time a price, package, post count, sender count or scope line is written |
| `references/house-rules.md` | Writing, design and content rules for every client-facing file, including the machine-read banned terms (section 10) and the substance rules (section 11) | Before writing any copy, and again in the final check |
| `references/research-signals.md` | Buying signals by type, how to detect each with the available tools, and how to phrase the outreach reason | Building a prospect map, an outbound plan, an ads plan, or a "why now" slide |
| `references/prospect-profile-schema.md` | Fields and statuses of `prospect-profile.yaml`, the record every skill reads first | Reading or writing a prospect profile |
| `references/prospect-profile-template.md` | The people version, `prospect-profile.md`, and the research folder layout | Writing or appending to `prospect-profile.md` |

## How the other skills use it

- They read these files by relative path from their own skill folder:
  `../proposal-shared/references/<file>.md`.
- Nobody copies prices or rules into their own files. If a value is needed, read it here.
- If a client gets a price that differs from the catalogue, record it in that client's
  `prospect-profile.md` under "Pricing overrides" with the reason. Do not edit the catalogue
  for one client.

## Updating

- Prices change only in `references/offer-catalogue.md`. Bump the version and date at the
  top of that file and add a line to its change log.
- Rules change only in `references/house-rules.md`.
- When the user states a new standing rule ("never do X in a deck"), offer to add it to
  `house-rules.md` so every skill picks it up.

## When the user asks directly

- "What do we charge for X?": answer from the catalogue, state the version, say prices are
  ex VAT, and flag anything marked "on request" or "confirm before quoting".
- "What are our rules for decks?": summarise `house-rules.md`.
- "What signals could we use for <market>?": shortlist from `research-signals.md`, then
  suggest running proposal-research for real counts.
