---
name: proposal-source-sweep
description: Finds everything we already have on a prospect before anyone asks a question: meeting recordings and transcripts (Fireflies), email threads (Gmail), Slack messages, Google Drive docs, Notion pages, calendar meetings, HubSpot if connected, the company website with a light web search, founders' YouTube or podcast appearances, and LinkedIn profiles. Shows the user what it found, ingests the sources they approve, and saves clean extracts for the prospect profile. Use as the first step of any proposal or pitch prep, or whenever the user says "what do we have on <company>", "pull everything on <company>", "check calls and emails for <company>", or before writing a proposal, deck or plan for a company.
argument-hint: "[company name, website or person]"
---

# Proposal source sweep

The point of this skill is that the user never re-types what already exists. A call
transcript, an email thread and a Slack note usually answer most intake questions; reading
them first turns a 13-question interview into a few confirmations.

Output goes to `./proposals/<slug>/research/sources/`, one extract per source, plus
`./proposals/<slug>/research/sources/index.md` listing what was found, what was ingested and
what was skipped.

## Step 1: Ask what to search, before searching anything

The user's calls, inbox and Slack are theirs; looking through them is something they agree to
each time, not something the skill decides. So first detect which sources are connected (by
tool name, without calling them) and ask in a single message that opens with one plain line
saying what will happen:

```
I'll search existing sources for anything we have on ReelFlow, then build the profile from that.

Here's where I can look:
 1. Call recordings (Fireflies)
 2. Email (Gmail)
 3. Slack
 4. Google Drive docs
 5. Notion
 6. Calendar
 7. HubSpot
 8. Their website, plus a light web search on what they do
 9. YouTube or podcast appearances by their founders
10. LinkedIn profiles of the founders and key people (paid, I'll show the cost first)

Search 1 to 9? Reply with numbers to leave out.
Use something else? Tell me or paste it.
Feel free to include any other documents or resources, or anything you particularly want me to look at.
```

Rules for this message:
- List only sources that are actually connected (HubSpot only if a HubSpot tool is connected).
  The website, the light web search and YouTube or podcasts are always available.
- LinkedIn is one item, marked paid. Do not list Apify or any other tool by name as a source:
  the user thinks in sources, not tools.
- If the user already named the company, don't ask for it again; still ask which sources.
- Search only what they approve.

## Step 2: Search the approved sources (read only)

Search each source the user approved, and nothing else. Routes,
search terms and what to extract per source are in `references/source-routes.md`. Search terms
are the company name, the website domain, each person's name and email, and obvious variants
(spacing, abbreviations, the product name).

Search in parallel where tools allow. Keep each search cheap: titles, dates, senders and
snippets only. Do not open full transcripts or threads yet.

If a source the user approved turns out not to work, note it in one line ("Gmail not reachable; skipped") and move on.
If a search fails, retry once, then list it as unavailable. Never stop the sweep for one
source.

## Step 3: Show what was found, and let the user choose

Present one numbered list, newest first, grouped by type. One line each: type, title, date,
who, and one short reason it looks relevant. Mark likely duplicates (several notetakers record
the same meeting: keep the longest). Example:

```
Found 7 sources on Atmospheric AI:

Calls
 1. Fireflies: "Growth10x x Atmospheric AI", 18 Nov, Dan, Afroz, Roee (38 min)
Docs
 2. Google Doc: "Call brief: Roee Goldberg", 11 Nov, by Jay
Slack
 3. DM with Dan, 18 Nov: 6 messages about Roee's call and experiments
 4. #growth10x, 17 Nov: 2 messages
Email
 5. Gmail: "Intro: Roee <> Dan", 10 Nov, 4 messages
Web
 6. atmosphericai.com (home, use cases, about)
 7. LinkedIn: Roee Goldberg (paid scrape, about $0.01)

Ingest all 7? Reply with numbers to skip (e.g. "skip 4"), or add anything I missed.
```

Paid items (LinkedIn profiles and similar) show their estimated cost and only run on a
yes. Everything else is free and runs on "go". Items without a date (a website, a profile)
show "checked <today>" so every line has one.

## Step 4: Ingest what was approved

For each approved source, open the full item and write
`research/sources/S<n>-<type>-<short-slug>.md` with:

- A header: type, title, date, people, link or id, and how it was found.
- The facts relevant to a proposal, as short bullets with timestamps or quotes: who they are,
  what they sell and to whom, pains, goals and numbers, what was discussed or promised (word for
  word), budget hints, timing, objections, names mentioned, anything to avoid.
- For our own internal sources (Slack, internal docs), keep the facts and strategy, and drop
  personal chatter.

Extracts, not dumps: a 40-minute transcript becomes a page of facts with timestamps. Keep the
full transcript only if the user asks. Size the work to the source: a call, a long thread or a
brief gets its own extract file; a one-line Slack mention, a calendar invite or a short email
goes as a two-line entry in `index.md` instead. This keeps the sweep fast without losing
anything.

Keep a short `research/sources/actions.md` as you go: each search or read (tool, query, result
count). It shows the user exactly what was looked at, and proves nothing was sent or changed.

Work through sources in parallel where possible and give a one-line update as each finishes.

## Step 5: Hand over

Update `index.md` (found, ingested, skipped and why, unavailable sources), then hand over to
**proposal-prospect-profile**, which reads the extracts and builds the confirmation rounds. If
running on its own, end by telling the user where the extracts are.

## Ground rules

- Read only. Never send, reply, react, move, label or edit anything in the user's tools.
- Internal call notes and transcripts stay in the local `research/` folder; never post them
  anywhere.
- Only search for the named company and its people. Do not browse unrelated inboxes, channels
  or meetings.
- Record which account or workspace each source came from by type only (for example
  "Fireflies, user's account"); never write account IDs, keys or setup details.
- No em or en dashes in anything written.
