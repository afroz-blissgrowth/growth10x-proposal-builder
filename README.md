# Growth10x Proposal Builder

A set of Claude Code skills that take a Growth10x prospect from "we have a call next week" to an agreed offer and a finished HTML pitch deck. Each skill does one step and they share one prospect profile, so nothing is asked twice.

## The skills

| Skill | What it does |
| --- | --- |
| `proposal-builder` | Entry point. Runs the other skills in order and keeps track of where you are. |
| `proposal-source-sweep` | Finds what we already have on the company: calls, emails, Slack, docs, website, LinkedIn. |
| `proposal-prospect-profile` | Builds the prospect profile and confirms it with you in short rounds of numbered questions. |
| `proposal-research` | Fills the gaps: website, case studies, competitors, LinkedIn ads, brand colours, market map. |
| `proposal-experiments` | Works out the strategy and offer with you and writes `offer.md`. |
| `proposal-deck` | Builds the deck as a workshop: storyline, slide plan, pilot, batches, final pass. |
| `proposal-plan-page` | One-page plans (for example a founder brand or outbound plan) from the same profile. |
| `proposal-shared` | Reference library: offer catalogue and prices, house rules, signal library, profile schema. |

## Run order

1. Source sweep
2. Prospect profile (confirm with the user)
3. Research
4. Experiments (agree the offer, writes `offer.md`)
5. Deck, or plan pages

You normally just run `/proposal-builder <company>` and it walks through these steps for you.

## Install

1. Clone the repo:
   ```
   git clone https://github.com/afroz-blissgrowth/growth10x-proposal-builder.git
   ```
2. Copy every folder inside `skills/` into your Claude skills folder, `~/.claude/skills/` (or `<your Claude config dir>/skills/` if you use a custom `CLAUDE_CONFIG_DIR`):
   ```
   cp -R growth10x-proposal-builder/skills/* ~/.claude/skills/
   ```
3. Restart Claude Code.
4. Run `/proposal-builder <company>`.

## Requirements

- Python 3
- Playwright with Chromium, used for deck QA renders:
  ```
  pip install playwright && playwright install chromium
  ```

Connectors are optional and set up per user: Fireflies, Slack, Gmail, Notion, Apify and Amplemarket. The skills use whichever ones you have connected and skip the rest.
