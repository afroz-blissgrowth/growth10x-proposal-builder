---
name: proposal-research
description: Researches a prospect for a Growth10x proposal and fills the gaps in its prospect profile. Crawls the company website, pulls case studies and named customers (the base for lookalike targeting), scrapes LinkedIn profiles and posts for the key people and the company page, finds competitors, checks the LinkedIn Ad Library for the prospect and its competitors, extracts brand colours and fonts, and builds a market map of their ICP with explicit job titles and free database counts. Use whenever a proposal, pitch, deck or plan needs facts the profile does not have yet, or the user says "research <company>", "look into <company>", "who are their competitors", "what ads do they run", "how big is their market", "get their brand colours", "scrape the founder's LinkedIn", even if they don't say "research".
argument-hint: "[company name or slug]"
---

# Proposal research

Fills what the prospect profile still lacks, and nothing else. It never asks intake
questions (that is proposal-prospect-profile's job) and never re-reads a source that
proposal-source-sweep already ingested.

Read before starting:
- `../proposal-shared/references/house-rules.md` (writing and fact rules)
- `../proposal-shared/references/prospect-profile-schema.md` (the YAML fields and statuses)
- `../proposal-shared/references/prospect-profile-template.md` (the people version and the
  research folder layout)

Read when you reach the steps: `references/research-recipes.md` (routes, actors, prices),
`../proposal-shared/references/research-signals.md` (signals for the market map), and
`../proposal-shared/references/offer-catalogue.md` (what the services in scope need).

## Ground rules

- **Free routes first.** Before any paid call (Apify runs, Apollo credits, any enrichment or
  reveal), show one cost estimate for all paid steps together and wait for a yes. One yes
  covers the batch the user has seen. Run the free steps while waiting.
- **Never invent.** Every fact gets a source. Doubtful things are `unverified` with a reason.
- Nothing is sent to anyone. This skill only reads and writes local files.
- Work with whatever tools this user has connected, detected by name (see the recipes).
  Never block on one source: use the next route, and if none works, log a gap.

## Step 1: Read the profile and decide what to research

1. Make the slug from the company name (lowercase, hyphens). Read
   `./proposals/<slug>/prospect-profile.yaml`. If it is missing, say so and offer to run
   proposal-source-sweep and proposal-prospect-profile first; if the user wants research
   anyway, create the folder and a minimal profile with only the company name and website.
2. Read `research/sources/index.md` and `sources_ingested` in the YAML. Anything already
   ingested there (for example website pages, LinkedIn profiles, transcripts) is not fetched
   again.
3. Build the to-do list from the items below. An item is in scope only if its fields are
   missing, `gap` or `unverified`, or its research is older than 30 days. Items that do not
   matter for the services in scope are skipped (no ads research if LinkedIn ads are not in
   scope and no competitor question is open).
4. Show the to-do list in a few lines with one cost line for the paid steps, for example:
   "Apify: 2 profiles, 40 posts, company page, 20 company posts, 60 ads, about $0.25. Reply
   yes to run the paid steps; free steps are starting now."

## Step 2: Research (parallel, after the list is shown)

Run independent items in parallel (background subagents are fine). Save every raw result to
`research/` with the file names in the recipes. Give a one-line update as each item finishes.

1. **People** (R1, R2). LinkedIn profile and last 3 months of posts for each key person:
   headline, career proof points, follower count, posting rhythm, top posts as a multiple of
   median, themes, what is missing. Say "n too small" under 5 posts.
2. **Company LinkedIn** (R3). Company page, recent posts and firmographics.
3. **Website** (R4). Crawl home, product, use cases, pricing, customers, about, careers, blog
   index. Write what they sell, to whom, use cases, pricing model, CTAs and tone.
4. **Case studies and customers.** From the customers page, case studies, logos and press:
   each named customer with industry, size, region and the result claimed, with the page URL.
   These are the seed list for lookalike targeting; note the pattern they share (industry,
   size band, region, buyer title).
5. **Brand: colour and logo** (R5). Run the colour, font and logo script:
   `python3 -I "${CLAUDE_SKILL_DIR}/scripts/brand_colors.py" <website> ./proposals/<slug>/research/brand/`
   (if `CLAUDE_SKILL_DIR` is not set, use this skill's base directory).
   - **Accent** = `accent_pick`: the colour the site uses most for fills, buttons, links and
     highlights, weighted by CSS use. Not the first colour in the logo file: logos often carry a
     secondary colour (ReelFlow's logo has an orange mark; the site and brand are teal #10B5A8).
     Record the pick, the runner-up and the logo's colours, and mark "confirm with the user".
   - **Logo**: the script downloads candidates to `research/brand/logo/`, the company's own mark
     first (customer logos on the page are skipped), SVG first, else the largest PNG (400px or
     wider). Copy the chosen file to `deck/assets/` later. Look for an official light or inverted
     variant (press kit, footer, dark sections); if none exists and the logo is SVG, make one:
     `python3 -I scripts/logo_variant.py <logo.svg> <logo-light.svg> --for dark --keep-brand`,
     then look at it on a dark ground. PNG only and no variant: note it as a gap for the user.
   - Fonts and text and surface colours as before.
6. **Competitors** (R6). Named ones first, then web search and lookalike search. Five to
   eight, each with one line on what they sell, positioning, public price and URL, direct or
   adjacent.
7. **LinkedIn Ad Library** (R7). The prospect and up to 5 competitors. Count, formats,
   posting profile, offers and CTAs. "No ads found" is a finding; write it down.
8. **Market map for THEIR ICP** (R9). Accounts by segment and region, personas by title,
   signal counts, caveats. Free endpoints only, totals read with page size 1, no enrichment
   or reveals. **Explicit titles only:** bare "CPO" also matches Chief Product Officer, Chief
   People Officer and prosthetists, so write "Chief Procurement Officer". Same for "CRO",
   "CDO", "CCO", "Head of Growth". Spot-check 5 names per ambiguous title. Record tool,
   filters and date for every count. (A fuller proposal-market-map skill is planned; until it
   exists, this step covers it.)
9. **Transcripts** (R8) only if proposal-source-sweep did not run or did not cover them.

## Step 3: Update the profile

- Write results into `prospect-profile.yaml` with `status: from_source` and a traceable
  `source` (URL, `tool <YYYY-MM-DD>`). Proposed items (for example an ICP we infer) are
  `proposed`. Never overwrite a `confirmed` value; if research disagrees with it, add an
  entry under `conflicts` and leave the value alone.
- Mirror the same facts into `prospect-profile.md` in the sections they belong to (people,
  company, what they sell, proof, ICP and market, competitors, ads, brand). Append; do not
  rewrite sections written by other skills.
- Update `gaps`: remove what was filled, add anything research could not find, each with why
  it matters and who can fill it (user, client, paid lookup).
- Add a row to the research log (step, route used, calls, paid spend, date) and one line to
  the change log: `YYYY-MM-DD | proposal-research | <what was added>`.

## Step 4: Hand back

Run the quality bars, fix anything that fails, then tell the user in a few lines:

- What was added (headline facts: ICP and market size, top competitors, ads found, brand
  colour) and where the raw files are.
- Paid spend, with the actual cost.
- Gaps still open, and any new conflicts for the user to settle.

Then hand back to proposal-builder (or, if running alone, suggest proposal-experiments as the
next step; proposal-deck needs the offer.md that proposal-experiments writes).

## Quality bars (check before hand back)

- [ ] Nothing already ingested by proposal-source-sweep was fetched again.
- [ ] Every fact has a source; nothing is from memory.
- [ ] Doubtful things are `unverified` with a reason; no `confirmed` value was overwritten.
- [ ] No number is invented, rounded up or extrapolated without saying so.
- [ ] Every count has its tool, filters and date; ambiguous titles were made explicit and
      spot-checked.
- [ ] Accent is the site's most-used brand colour (accent_pick), with runner-up and logo
      colours noted, marked "confirm with the user". Logo files saved (own mark, SVG or large
      PNG, plus a light variant or a gap).
- [ ] Paid spend stayed within what the user approved.
- [ ] No em or en dashes anywhere written.
- [ ] No other client's name, numbers or material appears.
- [ ] No API keys, account IDs or tool setup details are written to any file.
- [ ] Gaps list is current and each gap says who can fill it.
