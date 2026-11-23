# Components: blocks, layouts and icons

**Prefixes**: a slide prefix must not be one the library already uses (`td`, `th`, `en`, `ow`,
`pl`, `nt`, `wi`, `cm`, `fd`, `pz`, `tg`, `et`, `fb`, `st`, `ob`, `dn`, `ad`, `cn`, `rm`, `om`, `nx`
and others): the library's CSS for `.td-c` leaks into a slide that defines its own `.td-c`. build.py
fails on a collision. Use 3 or 4 letters (`tdy`, `ths`, `eng`). Mockup parts take a
`<!-- prefix: xyz -->` comment too; without it the prefix is the first 3 letters of the mockup id.

**Stretched panels**: grids and tab panes stretch cards to the row height. A card with 3 lines in a
400px row is hollow and fails `[hollow]`. Give every stretched card a bottom-anchored line with
substance (`margin-top:auto`: an output, a verdict, "Starts / We need", what it tells us), or let the
row size to its content. Ordinal numerals (1, 2, 3) stay under 56px, or the gate reads them as hero
numbers that need a count-up.

Everything lives in `assets/components.html` (search `@component <name>`) with its CSS in the
`g10x-components` style block; build.py keeps only the CSS a deck uses. Open the file in a
browser to see them (viewing is fine; scripts never launch the user's browser).

Two kinds:
- **Blocks** (`b-*`): small generic pieces in the house style. Compose a slide from 2 to 4 of
  them to fit the slide plan. This is the default way to build.
- **Layouts from approved decks** (`ly-*`): whole slides from the ContextPath deck with
  placeholder words. Reusing one is allowed when its structure fits what the slide must do; keep
  the `ly-<name>` class and rewrite every text node with this client's substance.

## Blocks

| Block | Classes | Use when | Motion and interaction |
|---|---|---|---|
| Card | `b-card` (`.on-acc`), `b-h` heading, `b-d` detail, `b-k` label | Any panel with a heading and detail. Heading 30px 800, detail 21px 400 (1.43x, 400 heavier) | Rise with `in` and `--d` |
| Stat cards | `b-stats`, `b-stat`, `b-num` with `data-count`, `data-pre`, `data-suf` | The hero is a number: goals, market size, results | Count-up (required for hero numbers), accent bar grows |
| Timeline that draws | `b-tl` (`--n`), `b-tl-bar`, `b-tl-i` (`--k`, `.now`), `data-draw` | Anything dated: goals by month, first 90 days, events | Bar draws, nodes pop in order |
| Step flow | `b-steps`, `b-step` (`.on-acc`), `b-step-n`, `b-card` | A mechanism in 3 to 5 steps | Connector grows, steps stagger; add `data-b` builds to walk it |
| Lanes | `b-lanes`, `b-lane`, `b-lane-h`, `b-chips`, `b-chip` | Tiers, audiences or channels side by side | Lanes stagger |
| Rings and dots | `b-rings` (svg `b-ring`, `b-rl`), `b-dots` (`i.on`) | Nested audiences, share of a whole, 1 in N | Rings and dots pop in order |
| Market map | `b-map` (`--cols`), `b-tile`, `b-bar` (`--w`) | Segments or regions with counts and a verdict | Count-ups, bars grow |
| Comparison table | `b-cmp`, `td.on-acc` | Today against with us, options, packages | Rows stagger |
| Quote bar | `b-quote` with `q` and `cite` | Their words or a buyer's words; one per slide | Bar draws |
| Mockup opener | `b-open` with `data-open="mz-..."` | Wherever showing beats telling | Opens the mockup overlay |
| Tabs | `b-tabs`, `b-tab-row`, `b-tab[data-tab]`, `b-pane` (`.sel`) | One question, 2 to 4 answers (region, segment, service) | Click switches panes |
| Flip cards | `wi-r`, `wi-c` (from the flip layout) | Several routes, each with a "how it works" back | Click turns |
| Popovers | `.wf` with `.wf-n[data-note]` and `.wf-pop` (engine layout) | Steps that need a sentence of detail on demand | Click opens |
| Hover links | `data-nm="key"` on two elements | Numbers linked to timeline points | Hover lights both |
| Builds | `data-steps="N"` on the section, `data-b="k"` on elements | A sequence told click by click | Each click reveals the next |
| Source line | `b-src` (or `.src`) | Every count or market number | None |

A worked example that passes every gate: `assets/examples/goals-acme.html` (fictional client).

## Layouts from approved decks

| Name | Structure | Typical layout id |
|---|---|---|
| cover, thanks | Lockup, highlighted line, wave | cover, thanks |
| numbers | Stat cards hover-linked to a month timeline, proof build | stat-row |
| cards | Card grid, 3 or 4 columns | situation |
| thesis | Numbered points beside a hub diagram | thesis |
| prize | Count-up stats, bars, ranked strip, source | market-map |
| plan | Priority rows that jump (`data-go`) | plan |
| target | Rings and tier cards | share, lanes |
| engine | Signals panel, flow, tier lanes, always-on band, popovers | process |
| outbound | Flow cards, pulsing end, KPI row | process |
| campaigns | Table whose rows open brief mockups | channel-play |
| founder, examples, pillars, packages | Founder brand set | channel-play, compare |
| stories, shoot | Story to campaign, one day to many outputs | proof, process |
| events, tiers, flip, photo | Calendar with pins, staircase tiers, flip cards, photo with tracker | timeline, flip-grid |
| dinners | Two-panel playbook with a 3-point timeline | channel-play |
| ads | Columns plus a loop diagram | channel-play |
| ai-gap, ai-who, ai-answer, months | AI search set | channel-play, timeline |
| funnel | Channel roles by funnel stage | lanes |
| console | Reporting layers and a mini dashboard. Never title it "Growth Console" or "the console"; describe what is tracked | process |
| roadmap, owners, next | Quarter roadmap, owners grid, next steps | timeline, owners, ask |
| mockups | mz-ai, mz-brief, mz-cm-1 to 6, mz-dash | (overlays) |

## Icons

`assets/icons.svg` holds the line icons (24px grid, stroke 1.8, no fill). Use them as
`<svg class="ic" aria-hidden="true"><use href="#i-ticket"/></svg>` (inside `.ri` for an icon
square). build.py inlines only the ones used and fails on an unknown id.

**Pick by meaning for this client.** The icon must say something true about the item next to it
in this client's world. A bank icon on an events company is wrong because it means nothing there.
Write the meaning in the slide plan (`icons: ticket = registrations | stage = speaking slot`).

| Icon | Meaning | Icon | Meaning |
|---|---|---|---|
| `i-venue` | Venue, expo hall, office | `i-stage` | Stage, keynote, speaking slot |
| `i-ticket` | Tickets, registrations, attendees | `i-badge` | Attendee or exhibitor badge |
| `i-calendar` | A date, schedule, deadline | `i-video` | Video, filming, shoot day |
| `i-play` | Player, demo, clip | `i-page` | Web page, landing page, event site |
| `i-doc` | White paper, case study, brief | `i-megaphone` | Campaign, ads, announcement |
| `i-message` | LinkedIn message, DM | `i-mail` | Email |
| `i-phone` | Calls | `i-factory` | Manufacturing, plants, OEMs |
| `i-fund` | Investor, fund, PE owner | `i-coins` | Money, revenue, budget |
| `i-chart` | Growth, results, ROI | `i-bars` | Comparison of sizes, counts |
| `i-globe` | Regions, international | `i-pin` | A city or location |
| `i-people` | Group, audience, team | `i-person` | One person, founder, persona |
| `i-handshake` | Partnership, co-host, referral | `i-target` | ICP, target accounts, goal |
| `i-signal` | Buying signal, trigger | `i-search` | Research, AI search, lists |
| `i-spark` | AI, automation | `i-layers` | Platform, system, setup |
| `i-flow` | Workflow, pipeline | `i-check` | Done, proven, approved |
| `i-clock` | Time, speed | `i-quote` | Testimonial, their words |
| `i-dinner` | Dinner, breakfast, roundtable | `i-mic` | Podcast, interview, panel |
| `i-post` | Social post, founder content | `i-shield` | Trust, security, compliance |
| `i-store` | Retail, hospitality | `i-home` | Property, housing |
| `i-sun` | Energy, solar | `i-health` | Healthcare, pharma |
| `i-truck` | Logistics, distribution | `i-briefcase` | Professional services |
| `i-code` | Software, developers | `i-school` | Education, training |
| `i-link` | Integration, referral link | `i-flag` | Milestone, launch |
| `i-test` | Experiment, pilot, A/B test | | |

Missing a meaning? Add a symbol to `icons.svg` in the same style, with a one-line meaning
comment, and a row here.
