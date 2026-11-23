# Prospect profile template

The people version of the prospect profile:
`./proposals/<client-slug>/prospect-profile.md`. It holds the same content as
`prospect-profile.yaml` (schema in `prospect-profile-schema.md`), written to be read by a
person: a partner should be able to open it and understand the prospect in a few minutes.
Raw material lives in `./proposals/<client-slug>/research/`.

proposal-prospect-profile writes both files and keeps them in step. The other skills read the
YAML first and this file for detail, may append to it (never rewrite sections they did not
create), and record what they added in the change log.

## Conventions

- Keep the section headings and their order exactly as below, so other skills can find them.
- Every table has a **Source** column. Sources are a URL, `tool, YYYY-MM-DD`, a transcript
  file and timestamp, or `user, YYYY-MM-DD`.
- Status words, as in the YAML: `confirmed`, `from_source` (read from a source, not yet
  confirmed), `unverified` (with reason), `proposed` (our suggestion, not yet agreed), `gap`.
- Counts carry "about" and the filters used.
- No em or en dashes. No API keys, account IDs or tool setup details.
- Unknown fields stay in the file with `gap` so nothing is silently dropped.

## Research folder layout

```
proposals/<client-slug>/
  prospect-profile.md
  prospect-profile.yaml
  research/
    sources/index.md, S<n>-<type>-<short-slug>.md (from proposal-source-sweep)
    people/<person-slug>-profile.json, <person-slug>-posts.json
    company/linkedin-company.json, company-posts.json, firmographics.json
    website/<page>.md
    brand/brand.json (plus the script's downloaded files)
    competitors.md
    ads/<company-slug>.json
    transcripts/<date>-<meeting-slug>.md
    market/accounts.md, personas.md, signals.md
    inputs/ (files the user supplied: decks, docs, notes)
```

## Template (copy from the line below)

---

```markdown
---
client: <Client>
slug: <client-slug>
website: https://<domain>
profile_version: 1
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft | gaps open | ready
catalogue_version: v2
---

# <Client>: prospect profile

## 1. Snapshot
Five to eight lines: who they are, what they sell, to whom, stage, the proposal intent, the
services in scope, the deadline, and the one-line angle we propose.

## 2. Engagement

| Field | Value | Source |
|---|---|---|
| Intent | new pitch / upsell / renewal | user |
| Relationship | external / portfolio company | user |
| Services in scope | e.g. founder branding (Standard), outbound (LinkedIn + email) | user |
| Lead service | | user |
| Call or deadline | YYYY-MM-DD, presenter role | user |
| Prices shown | yes / no (GBP, ex VAT) | user |
| Format wanted | deck / plan page / both | user |

### Pricing overrides
Any price that differs from the catalogue, with who agreed it and why. Empty if none.

## 3. What was discussed and promised
Word for word where possible. Verbal prices, trial or pilot terms, timelines, guarantees,
names or assets promised, by either side.

| What | Exact words or summary | Who said it | Source |
|---|---|---|---|

## 4. People

| Name | Role | Decision role (decision maker / champion / user / influencer) | LinkedIn | Followers | Posts in last 3 months | Status | Source |
|---|---|---|---|---|---|---|---|

Per key person, a short block:
- Career proof points (with source)
- Content baseline: posts in period, median reactions, format mix, top posts (link and
  multiple of median), main themes, what is missing
- Founder brand in scope: yes / no

## 5. Company

| Field | Value | Source |
|---|---|---|
| Legal or trading name | | |
| HQ and regions | | |
| Founded | | |
| Employees | | |
| Funding and investors | | |
| Stage | | |
| Category | | |
| Pricing model | | |
| LinkedIn page followers | | |
| Recent news (last 6 months) | | |

## 6. What they sell
- Product or service, in their words and in plain words
- Modules or packages
- Use cases (bullet per use case, with page URL)
- Main CTA and tone of voice

## 7. Proof

| Proof (customer, number, quote, award) | Detail | Public? | Source |
|---|---|---|---|

Mark anything the client has not approved for public use.

## 8. Their ICP and market

### ICP definition
Segments, company sizes, regions, buyer personas, deal size. Status per line: confirmed /
proposed.

### Accounts by segment and region
Table from Amplemarket counts, with filters and date.

### Personas by title
Table from Apollo counts: persona, explicit titles used, count per segment, deduped total,
spot-check result.

### Signals
| Signal | Filter used | Count | Share of persona | Tool and date | Outreach reason (one line) |
|---|---|---|---|---|---|

### Recommended target shapes
For example: top 100 accounts (definition and count), top 500, next ring.

### Caveats
Database counts, tag overlap, size band mismatch, exact-title misses, regions left out.

## 9. Competitors

| Competitor | Direct or adjacent | Positioning | Public pricing | LinkedIn ads (count, formats) | Source |
|---|---|---|---|---|---|

## 10. LinkedIn ads
Client's own ads (count, formats, offers, posting profile), what competitors run, where
nobody competes. "No ads found" is a valid entry.

## 11. Brand

| Item | Value | Status | Source |
|---|---|---|---|
| Primary accent | #xxxxxx | confirm visually | brand_colors.py, YYYY-MM-DD |
| Text colour | | | |
| Surface colour | | | |
| Secondary colours | | | |
| Fonts | | | |
| Logo URL | | | |
| Light or dark ground suggested | | proposed | |

## 12. Calls and transcripts

| Date | Meeting | Account searched (role) | File | Kept or duplicate |
|---|---|---|---|---|

Key points with timestamps: pains, goals and targets, what they tried, objections, budget
hints, quotes worth reusing. Internal only.

## 13. Sensitivities
Names not to use, customers not to mention, topics to avoid, confidentiality rules.

## 14. Proposed angle
Our one-paragraph thesis for the proposal and the order of services, marked `proposed`.

## 15. Gaps

| Gap | Why it matters | Who can fill it (user / client / paid lookup) | Status |
|---|---|---|---|

## 16. Research log

| Step | Route used | Calls | Paid spend | Date |
|---|---|---|---|---|

## 17. Change log

| Date | Skill | Change |
|---|---|---|
```
