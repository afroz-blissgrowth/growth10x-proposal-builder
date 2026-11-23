# Layout library

Layouts are chosen by what a slide does, not by what the last deck had. Each layout below is
registered (`deck_check.py` reads the `### \`id\`` headings) and set on the slide as
`<section ... data-layout="<id>">`. Rules: no layout twice in a row; a layout used more than
three times in a deck needs a reason in the plan. Reusing a layout from an approved deck is fine;
its content must be this client's.

Each entry: function, element schema (what must be on the slide, with counts), words, motion
recipe, interaction, and the blocks or components to build it from (`components.md`).

### `cover`
- Function: open with the promise in their terms.
- Elements: lockup with the client's real logo, title with one highlighted phrase (the payoff),
  one or two sentence sub with their numbers, prepared-for line.
- Words: 30 to 70. Motion: lockup and title rise, highlight sweeps, dotted wave. Component: cover.

### `stat-row`
- Function: goals, results, the size of something. The hero is 2 to 4 numbers.
- Elements: 2 to 4 b-stat cards (number with currency or noun, heading, one line of detail and
  source), plus one of: a b-tl to the date, a b-quote in their words, a proof strip.
- Words: 120 to 190. Motion: count-up on every number (required), cards stagger, timeline draws.
- Interaction: data-nm hover between numbers and timeline points, or a build revealing proof.
- Build from: b-stats, b-tl, b-quote; or the numbers component.

### `situation`
- Function: where they are today: what works, what does not, the gap.
- Elements: 3 to 4 cards (what is proven with names and numbers, what is idle or missing), a gap
  card on accent, one quote from them.
- Words: 140 to 200. Motion: cards stagger. Interaction: optional flip for detail.
- Build from: b-card grid, b-quote; or the cards component.

### `thesis`
- Function: why this approach wins in their market (the argument, not the plan).
- Elements: 3 numbered points, each a claim plus the evidence from their market; a diagram
  (hub, loop or rings) that shows the mechanism.
- Words: 110 to 170. Motion: points stagger, diagram draws. Component: thesis, or b-rings.

### `market-map`
- Function: the size and shape of their market, segment by segment.
- Elements: 3 to 9 segment tiles with counts (tool and date in the source line), bars to scale,
  a verdict per segment (first, test, later), and where we start.
- Words: 120 to 200. Motion: count-ups, bars grow. Interaction: tabs by region or a jump to the
  target list mockup. Build from: b-map, b-tabs; or the prize component.

### `share`
- Function: from the whole market to the first wave (nested audiences, 1 in N).
- Elements: rings or dot field, 3 cards that define each ring with counts and filters.
- Words: 110 to 170. Motion: rings pop in order. Build from: b-rings, b-dots, b-card.

### `plan`
- Function: the plays in priority order, each one jumping to its slide.
- Elements: 3 to 7 rows (play, one line why it fits them, the lead marked "our pick").
- Words: 110 to 180. Motion: rows stagger. Interaction: `data-go` on every row (required) and
  `data-back` on the section. Component: plan.

### `process`
- Function: a mechanism: how a play runs, step by step.
- Elements: 3 to 5 steps, each heading plus two lines; what goes in (signals, inputs) and what
  comes out (meetings, assets); one proof or number.
- Words: 140 to 220. Motion: connector grows, steps stagger. Interaction: popovers on steps
  (`.wf-n[data-note]`) or a build per stage. Build from: b-steps; or engine, outbound, stories.

### `lanes`
- Function: different treatment per tier, audience or channel.
- Elements: 2 to 4 lanes, each with who qualifies (explicit titles or filters) and chips for the
  channels or assets; exclusions lane.
- Words: 120 to 190. Motion: lanes stagger, chips fade in. Build from: b-lanes; or target.

### `channel-play`
- Function: one play in depth (ads, founder brand, dinners, AEO): who, what they see, what happens.
- Elements: 3 columns (who, what, next) with 3 to 4 items each, plus a loop or flow diagram, plus
  a proof line from their market or a mockup.
- Words: 150 to 220. Motion: columns stagger, loop animates. Interaction: mockup or tabs.
- Build from: b-card, b-steps, b-open; or ads, founder, dinners, ai-answer.

### `timeline`
- Function: anything about time: first 90 days, event calendar, the year.
- Elements: 4 to 10 dated points on a bar that draws, each with what happens and who; PLUS a second
  element that carries the detail: 3 phase cards (what happens, what the client gives) or quarter
  columns. A timeline alone fills about a third of the box (ReelFlow v2 roadmap: 34% fill).
- Words: 150 to 250. Motion: the bar draws, nodes pop in date order (required).
- Build from: b-tl; or events, roadmap, dinners.

### `compare`
- Function: today against with us, option against option, packages.
- Elements: a table of 3 to 6 rows, the picked column tinted; a line on why.
- Words: 110 to 190. Motion: rows stagger. Build from: b-cmp; or packages.

### `proof`
- Function: evidence: a customer story, a result, their own words.
- Elements: b-quote, 2 to 3 numbers with sources, and a b-open to the full story or example.
- Words: 110 to 180. Motion: quote bar draws, count-ups. Interaction: mockup.

### `tabs`
- Function: one question with 2 to 4 answers (by region, segment or service) on one slide.
- Elements: tab row, each pane with 2 to 3 cards. Words: 140 to 220 across panes.
- Interaction: tabs (required). Build from: b-tabs.

### `flip-grid`
- Function: several ways in (partners, channels), each with a front (what) and back (how).
- Elements: 4 to 8 flip cards. Words: 160 to 320 counting backs.
- Interaction: flip (required). Component: flip.

### `owners`
- Function: who owns what, roles only, client side included.
- Elements: grid of workstreams by owner with lead and support marks. Words: 60 to 120.
- Component: owners. (Kind content; keep it full: add the approvals each side gives.)

### `ask`
- Function: next steps and the one closing question. Kind `closing` (exempt from fill).
- Elements: 3 to 4 numbered steps with dates, the question. Words: 60 to 110.
- Motion: step line grows. Component: next.

### `thanks`
- Function: close. Lockup with the logo and one highlighted line. No names or emails.
