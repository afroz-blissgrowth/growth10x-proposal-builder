# Buying signals library

A signal is a public, dated event that makes a company more likely to buy now. Each entry
says what it is, how to detect it with the tools the chain assumes (Apify, Apollo,
Amplemarket, web search and fetch), what it costs, and how to turn it into an outreach
reason.

Tool parameter names change. Check each tool's schema before calling it, and keep the free
route first. Ask before any paid call and show the estimate.

## How to phrase any outreach reason

- Lead with the observed fact, then one relevant question. No pitch, no link, no "quick chat".
- Name the source the prospect would recognise ("saw the job post", "read your post on X"),
  never the tool ("our signal tracker flagged you").
- Never mention that you saw someone visit a website or view a profile.
- One signal per message. Stack signals for scoring, not for copy.
- Keep it under about 300 characters for a LinkedIn connection note.

Placeholders below: `<Company>`, `<Name>`, `<role>`, `<topic>`.

## Signal strength and freshness

| Strength | Signals | Act within |
|---|---|---|
| High | New in role (0 to 90 days), public tender or RFP, funding in the last 60 days, hiring for the exact problem the client solves, champion moved to a new company | 2 weeks |
| Medium | Leadership change elsewhere in the team, tech stack add or drop, regulatory deadline, price or supply shock in their category, event speaking or attending | 30 days |
| Low | General hiring growth, content themes, website visit (unless repeated), follower growth | Use for scoring only |

## 1. Hiring

- **What:** open roles that show a priority, a gap, or budget (for example the first sales
  hire, a RevOps role, a role that names a tool or problem the client solves).
- **Detect:**
  - Apollo people search (free): `q_organization_job_titles` plus
    `organization_job_posted_at_range` to count decision makers at companies hiring for given
    titles since a date.
  - Amplemarket company search (free): job openings fields and company job opening lookups.
  - Careers page via web fetch (free). LinkedIn jobs via an Apify jobs actor (paid, small).
  - Apollo organization job postings endpoint: check its credit note first.
- **Sharpen:** broad titles ("buyer", "manager") match almost every large company. Use exact,
  problem-specific titles.
- **Reason:** "Saw <Company> is hiring a <role>. Is that to build <topic> in house, or to run
  something you already have?"

## 2. Leadership change / new in role

- **What:** a new decision maker in the buying seat in the last 30 to 180 days. New leaders
  review vendors and set a plan in their first 90 days.
- **Detect:**
  - Apollo people search (free): `person_days_in_current_title_range` (for example max 90 or
    180) with explicit titles and company filters. Gives counts and names, no contact data.
  - Amplemarket people search (free): job change or tenure filters where available.
  - Trade press and company news pages via web search (free).
- **Reason:** "Congrats on the move to <role> at <Company>. What is top of the list for your
  first 90 days on <topic>?"

## 3. Champion moved

- **What:** someone who used or bought the client's product at a past company now works at a
  new ICP company.
- **Detect:** list of the client's past users (from the client) matched with Apollo people
  search by LinkedIn URL (free) to see current employer; Amplemarket people search by name.
- **Reason:** "You used <product category> at <Past company>. Now you are at <Company>, is
  <topic> something you are looking at again?"

## 4. Funding

- **What:** a new round, usually followed by hiring and new tooling within 3 to 6 months.
- **Detect:** web search for "<Company> raises" and news sites (free); Amplemarket company
  data (funding fields, news); Apollo organization lookup is free but returns basic fields
  only. Funding filters on Apollo company search cost 1 credit per request: ask first.
- **Reason:** "Congrats on the <round>. You mentioned using it for <stated use>. How are you
  thinking about <topic> as the team grows?"

## 5. Tech stack

- **What:** a company adds, drops or runs a tool that pairs with or competes with the client.
- **Detect:** Apollo people or company search with technology filters (check schema and
  credit note); Amplemarket technology filters where available; website source via web fetch
  (scripts and tags, free); job posts that name tools.
- **Reason:** "Noticed you run <tool>. How are you handling <gap the tool leaves>?"

## 6. Events

- **What:** the prospect is speaking at, sponsoring or attending an event in the client's
  space, or the client is attending one where prospects will be.
- **Detect:** event agenda, speaker and sponsor pages via web fetch (free); LinkedIn event
  posts via Apify post scrapers (paid, small). Do not try to scrape LinkedIn event attendee
  lists (needs a login).
- **Reason:** "Saw you are speaking at <Event> on <topic>. Will you be there both days? We
  are hosting a small dinner the night before." (Only offer what is real.)

## 7. Regulatory

- **What:** a new rule or deadline that forces change in the prospect's category (reporting,
  data, safety, AI, sustainability).
- **Detect:** regulator and government sites, trade press, law firm briefings via web search
  (free). Map which segments it hits, then count those segments with Amplemarket or Apollo.
- **Reason:** "With <rule> coming in on <date>, how is <Company> planning to handle
  <requirement>?"

## 8. Price and supply shocks

- **What:** a sudden cost or supply change in the prospect's inputs (commodity spikes,
  tariffs, shipping disruption, supplier exits).
- **Detect:** commodity and trade news via web search (free); the prospect's own earnings
  calls or posts mentioning it.
- **Reason:** "<Input> prices moved <direction> since <month>. Is that hitting <Company>'s
  margins or contract terms yet?" (Only use a figure with a source.)

## 9. Tenders and RFPs

- **Public:** UK Find a Tender and Contracts Finder, EU TED, US SAM.gov, plus local and
  sector portals. Search by keyword and buyer via web fetch (free).
- **Private:** posts asking for recommendations ("looking for a partner for X"), job posts for
  implementation roles, trade press on vendor reviews. Detect with Apify post search on
  keywords (paid, small) and web search.
- **Reason (public):** "Saw the <Buyer> tender for <scope>. Are you bidding or delivering
  in house?" (when the client sells to bidders). Do not cold pitch a buyer during a live
  procurement; check the tender rules on contact first.
- **Reason (private):** "Saw your post asking about <topic>. What did the shortlist look
  like?"

## 10. Content and posts

- **What:** prospects posting or engaging on the client's topic, or on competitors' posts.
- **Detect:**
  - Apify profile and company post scrapers for known accounts (about $0.002 a post).
  - Apify post search on keywords for new accounts.
  - Engagers on competitor or category posts (Apify engagement scrapers; paid per item).
- **Reason:** "Read your post on <topic>. You said <point>. Have you found <related problem>
  harder to solve than that?"
- Founder branding uses the same signals for DMs: message engagers and new connections with a
  question, never a pitch.

## 11. Website visitors

- **What:** companies or people visiting the client's site, especially pricing or case pages.
- **Detect:** only with the client's own tracking installed (for example Apollo website
  visitor tracking or a visitor identification tool). Needs the client's consent and setup.
- **Reason:** never cite the visit. Use the page topic: "Teams like <Company> often ask us
  about <topic on that page>. How are you handling it today?"
- Treat one visit as a scoring input. Repeated visits plus a fit company move to Tier 1.

## 12. Profile viewers and new connections

- **What:** people who view the founder's profile or accept a connection.
- **Detect:** LinkedIn native (founder's account), via the sending tool. No scraping.
- **Reason:** "Thanks for connecting, <Name>. What made you look at <topic>?"

## Using signals in a prospect map

For the prospect profile, count each relevant signal for the ICP with the free routes (Apollo people
search counts, Amplemarket company counts) and present a table:

| Signal | Filter used | Count | Tool and date | Note |
|---|---|---|---|---|

Pick the 3 to 6 signals with a real count and a clear outreach reason. Those become the
"live in 2 months" signals in the outbound plan.
