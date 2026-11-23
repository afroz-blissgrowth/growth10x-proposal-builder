# Research recipes

How proposal-research researches a prospect. For each item: the routes in order (first available
wins, the last is always "ask the user to paste"), what to save, and what it costs.

Prices below were checked in November 2026. Recheck the actor page if an estimate looks off.

## Tool detection

At the start, check which tools exist by name: MCP tools containing `apify`, `Apollo`,
`Ample` (Amplemarket), `Fireflies`, plus web search and web fetch. An Apify token in the
environment also allows REST calls. Never hardcode a server name; match on these words.

## Cost rules

| Tool | Free | Paid (ask first, show estimate) |
|---|---|---|
| Apify | Nothing | Every actor run (pay per item, plus a tiny start fee) |
| Apollo | People search (`apollo_mixed_people_api_search`), organization lookup (`apollo_organizations_lookup`) | Company search (1 credit per request with results), organization enrich, people match or bulk match, reveals |
| Amplemarket | `search_companies`, `search_people` | `enrich_person`, `enrich_company` |
| Fireflies | All search and transcript reads | None |
| Web search and fetch | All | None |

Apollo company search asks "This will consume 1 credit. Do you want to proceed?". Avoid it;
use organization lookup plus Amplemarket company search instead.

Typical paid spend for one prospect (3 people with 20 posts each, company page and 20 posts,
30 ads, one small crawl): about $0.20 to $0.30.

## Apify actors (no LinkedIn login or cookies needed)

Call through the Apify MCP (`fetch-actor-details` for the input schema, then `call-actor`),
or REST: `POST https://api.apify.com/v2/acts/<user~name>/run-sync-get-dataset-items` with a
Bearer token and the input as JSON body.

| Need | Actor | Minimal input | Price |
|---|---|---|---|
| Profile | `harvestapi/linkedin-profile-scraper` | `{"urls":["https://www.linkedin.com/in/x"]}` | about $0.004 a profile |
| Person posts | `harvestapi/linkedin-profile-posts` | `{"targetUrls":[url],"maxPosts":20,"postedLimit":"3months"}` | about $0.002 a post |
| Company page | `harvestapi/linkedin-company` | `{"companies":["https://www.linkedin.com/company/x"]}` | about $0.004 a company |
| Company posts | `harvestapi/linkedin-company-posts` | same shape as person posts | about $0.002 a post |
| Ad Library | `alexmorain/linkedin-ad-library-scraper` | `{"advertisers":["Company"],"maxAdsPerQuery":30,"includeDetails":false}` | about $0.001 an ad ($0.002 with details) |
| Ad Library (alternative) | `unseenuser/LinkedIn-ads` | `{"companies":["Company"],"maxResults":30}` | about $0.005 a result |
| Website | `apify/website-content-crawler` | `{"startUrls":[{"url":"https://x.com"}],"maxCrawlPages":15,"crawlerType":"cheerio"}` | platform compute, cents per small crawl |

Actor IDs and inputs can change. Always read the input schema before the first run.

## R1. LinkedIn profile (each key person)

1. Apify profile scraper.
2. Apollo people search with `person_linkedin_urls` (free; title and employer only).
3. Amplemarket `search_people` by name plus company domain (free).
4. Web search for the public profile and press bios.
5. Ask the user to paste the profile text or a PDF export.

Save: `research/people/<person-slug>-profile.json` (or `.md` if pasted).
Extract: headline, current role and start date, past roles, education, follower count,
career proof points (with source).

## R2. Person recent posts

1. Apify profile posts, 20 posts, last 3 months.
2. Web search `site:linkedin.com/posts "<name>"`.
3. Ask the user to paste 3 to 5 recent posts.

Save: `research/people/<person-slug>-posts.json`.
Extract: posts in period, median reactions and comments, format mix (text, image, carousel,
video, document), top 3 posts by reactions with the multiple of median, main themes, CTA use.
Do not compute anything the data does not support; say "n too small" under 5 posts.

## R3. Company LinkedIn

1. Apify company page plus company posts (20).
2. Apollo `apollo_organizations_lookup` (free) plus Amplemarket `search_companies` with
   `company_domains:[domain]` (size, industry, location, funding, news, job openings).
3. Web fetch of the about and careers pages.
4. Ask.

Save: `research/company/linkedin-company.json`, `research/company/company-posts.json`,
`research/company/firmographics.json`.

## R4. Website

1. Web fetch: home, product or platform, pricing, customers or case studies, about, careers,
   blog index (free).
2. Apify website content crawler (15 pages) when the site is JS-heavy or fetch fails.
3. Ask for a deck or one-pager.

Save: `research/website/<page>.md`.
Extract: what they sell, who it is for, use cases, proof (customer names, numbers, quotes,
awards) with page URL, pricing model, main CTA, tone of voice.

## R5. Brand colours and fonts

Run: `python3 -I "${CLAUDE_SKILL_DIR}/scripts/brand_colors.py" <url> <empty-dir>`.
Use a fresh empty folder under `research/brand/`. The script is stdlib only.

Reading the output:
- `accent_pick.pick` is the accent: the most-used saturated colour on the site, weighted by
  property (backgrounds and text colour count more than borders), with a bonus when the company's
  own logo also uses it. Very dark and very pale colours are skipped (text and surfaces).
  A named token that agrees (`named_tokens_agree`) settles it. Never take the logo's first hex.
- Show the user the pick, `runners_up` and `logo_colours`; they confirm before any deck build.
- `logo`: candidates downloaded to `<dir>/logo/`, own mark first (`own: true`), SVG first.
  `light_variant_guess` flags files named white, light or inverted. Make a light variant of an
  SVG with `scripts/logo_variant.py` when there is no official one.
- Take the darkest neutral as text colour and the lightest as surface.
- Fonts: most-used family, plus `@font-face` and Google Fonts names.
- Confirm against the logo before use. Mark "confirm visually" in the profile.
- If the site renders with JavaScript and the script finds nothing, use the crawler output,
  the logo file, or ask for brand guidelines.

Save: the script now writes `<outdir>/brand.json` itself (also printed), with `logo_pick` = the
company's own mark. Check `logo_pick` is their logo, not a customer's (sites show many logos).

## R6. Competitors

1. Start with competitors the user named.
2. Web search: "<category> software", "<Company> alternatives", "<Company> vs", review sites
   (G2, Capterra) and analyst lists.
3. Amplemarket `list_competitors` or company search by industry and size for lookalikes.

Save: `research/competitors.md` (name, URL, one-line positioning, public pricing, source).
Keep to 5 to 8. Flag direct versus adjacent.

## R7. LinkedIn Ad Library

1. Apify ad library actor for the client and up to 5 competitors, 30 ads each.
2. Web fetch `https://www.linkedin.com/ad-library/search?companyIds=<id>` (often blocked).
3. Ask the user for screenshots.

Save: `research/ads/<company-slug>.json`.
Extract per advertiser: number of ads, formats, posting profile (founder or company page),
offers and CTAs, oldest live ad. "No ads found" is a finding.

## R8. Call transcripts (Fireflies)

Normally done by proposal-source-sweep (see `../proposal-source-sweep/references/source-routes.md`, path from the skill folder).
Run it here only for meetings the sweep did not cover.

Fireflies results are account specific: only meetings the connected account can see. Always
write which account or workspace was searched (by role, not by email).

1. `fireflies_search` with the company name as keyword, scope all, limit 20; again with the
   domain and each person's email as participant; add a from-date if known.
2. Several bots can record one meeting. Keep the longest transcript, note the others.
3. For each relevant meeting: `fireflies_get_summary`, then `fireflies_get_transcript`.
4. Fallback: Apollo conversations search if the team records there; else ask for pasted
   notes or a transcript file.

Save: `research/transcripts/<date>-<meeting-slug>.md` (summary plus full text).
Extract with timestamps: pains, goals and targets, what they tried, objections, budget hints,
quotes worth reusing, and anything promised by either side. These files stay local.

## R9. Market and prospect map for the client's ICP

Goal: how big is the client's market, who exactly buys, and how many show a signal right now.
Free endpoints only. Use `per_page` 1 or `page_size` 1 and read the total, so nothing is
pulled into context. Never enrich or reveal.

### Step 1: define the ICP

From the website, transcripts and the user's answer: segments (industries), company size
bands, regions, and 3 to 6 buying personas. If unknown, propose one and mark it "proposed".

### Step 2: accounts by segment and region (Amplemarket `search_companies`)

- Filters: `company_industries` (values from `get_industries`, max 10 per call),
  `company_locations` (countries, max 10 per call; "Europe" returns 0, so split Europe into
  two country groups), `company_sizes`.
- Requires an `intent` string of 25 to 35 words. Use `full_output:false`.
- Industries match on secondary tags, so segments overlap and pull in some non-fits. Say so.

Output table: segment rows, region by size columns, totals.

### Step 3: personas by title (Apollo `apollo_mixed_people_api_search`)

- Filters: `person_titles` (explicit list), `include_similar_titles: false`,
  `organization_num_employees_ranges`, `organization_locations`, plus industry or keyword
  filters for the segment. `per_page` 1, read `total_entries`.
- **Explicit titles only.** Ambiguous short forms and what they also match:

| Ambiguous | Also matches | Write instead |
|---|---|---|
| CPO | Chief Product Officer, Chief People Officer, prosthetist or orthotist | Chief Procurement Officer (or the one you mean, spelled out) |
| CRO | Chief Risk Officer, clinical research organisation roles | Chief Revenue Officer |
| CDO | Chief Data Officer, Chief Digital Officer, Chief Design Officer | the full title |
| CCO | Chief Commercial, Customer, Compliance or Communications Officer | the full title |
| Head of Growth | growth hacking, plant growth, investment growth roles | Head of Growth Marketing, VP Growth |
| Partner | law, accounting, VC partners | the exact role and industry filter |

- Spot-check: for each ambiguous or broad title, pull 5 names (`per_page` 5) and confirm they
  are the right job. Log the check.
- Output: persona by segment table, plus a deduped total across segments (run all segments
  in one call) and a note that segment sums double count.

### Step 4: signal counts

Pick 3 to 6 signals from `../proposal-shared/references/research-signals.md` (path from the
skill folder) that fit the client. Typical free counts with Apollo people search on the key persona:
- New in role: `person_days_in_current_title_range` max 90 or 180.
- Hiring: `q_organization_job_titles` plus `organization_job_posted_at_range` from a date.
  Broad titles match almost everyone; use specific ones.
- Tech stack: technology filters if the schema has them (check for credit notes).
- Funding: from news search for a named list; Apollo company search funding filters cost
  credits, ask first.

Output table: signal, filter, count, share of persona total, tool and date.

### Step 5: caveats (always written)

Database counts, not verified people. Industry tags overlap. Size bands differ between
Apollo and Amplemarket, so account and people numbers are not from the same company set.
Exact titles miss variants, so true reach is likely higher. List any regions left out.

Save: `research/market/accounts.md`, `research/market/personas.md`,
`research/market/signals.md`, each with a "Calls made" line (tool, number of calls, credits
used: 0).

### Warm paths (optional, free)

Amplemarket `search_people` with `linkedin_networks:["all_networks"]` on the target accounts
shows connections through the team's own reps. Record counts only.

## Directories and member lists: check the composition before you build a segment on them

A directory the client names as "the long tail" may not be. SISO (Society of Independent Show
Organizers) has 195+ members producing 3,500+ events, about 18 events each (siso.org/about-siso,
2026): mid-size organisers, not the 1 to 5 show long tail Chris described. Before a directory carries
a segment, read its own about page for member and event counts, divide, and say on the slide how the
list is filtered ("SISO members cut to those with 1 to 5 shows"). Free sources for event markets:
UFI statistics (global exhibitions), EIA SASIE (UK), AUMA (Germany), AEO (UK members' events),
Stax top 20 organisers (concentration). Search results alone are not a source; open the page.
