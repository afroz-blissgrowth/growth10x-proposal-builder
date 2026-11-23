# Design system

The house look is the ContextPath deck (dark) and its light variant. Lineage: ground,
constellation, glass, highlight block, dotted wave, timelines and step circles come from the
Growth10x discovery deck; type and footer come from the Tipped deck. This is the house design for
**every** deck. The only things taken from the client are their brand colour and their real logo.
Other approved decks (Tipped and others) inspire content and page structure, never the look.
Never copy the client's own deck style.

## Stage

- Fixed 1920x1080 stage, scaled to the window with a 16px side gutter. All sizes are stage px.
- Slide padding 96 top, 128 sides, 150 bottom. **Content must end above y 930** (the footer
  sits below). The probe errors past 970.
- Slide is a flex column, default gap 56px. Dense slides lower it in their part CSS (22 to 44px).

## Themes

Both themes ship in every build; `data-theme` on `<html>` picks one.

| Token | Dark | Light |
|---|---|---|
| `--bg` ground | #17161D | #FAF9F5 |
| `--fg` text | #F7F5F2 | #17161D |
| `--fg-2` body | 74% | 80% |
| `--fg-3` labels, secondary | 50% | 64% |
| `--fg-4` faint (dividers, ticks) | 38% | 52% |
| `--glass` panels | ink at 62% | white at 74% |
| `--line`, `--line-2` | 12%, 24% | 12%, 22% |

Pick the ground from the profile (section 11) and the client's colour: a pale or neon accent
(lime, yellow, light cyan) reads best on dark; a deep accent (navy, forest, maroon) on light.
Pilot both in one review file (`build.py --review`: slides 1 to 3 light, 4 to 6 dark, one link) unless the user has already chosen. Use `--fg-4` only for non-text marks; small
text needs `--fg-3` or stronger to pass contrast.

## Accent (the client colour)

Choose it from research, not from the logo: `brand.json` `accent_pick` is the colour the client's
site uses most for fills, buttons, links and highlights (weighted by CSS use). A logo often
carries a secondary colour (ReelFlow: orange mark, teal site; the accent is the teal #10B5A8).
Show the pick, the runner-up and the logo colours to the user and record their yes as
`"brand_confirmed": true`.

Set `accent` in deck.json. `build.py` derives, per theme:

| Token | Use |
|---|---|
| `--acc`, `--acc-rgb` | Fills, borders, bars, dots, the highlight block. Tints as `rgba(var(--acc-rgb),a)` |
| `--on-acc` | Text on an accent fill (white or ink, chosen for contrast) |
| `--acc-tx` | Accent-coloured text. Pushed to 5.2:1 on the ground so it stays above 4.5 on glass |
| `--acc-ink`, `--acc-mid`, `--acc-pale` | Accent on white paper mockups (text, bars, soft fill) |

Pale accents get a deeper fill on light ground; very dark accents get lifted on dark ground.
Standard alphas: .04 to .07 card tint, .1 to .16 chips and soft fills, .35 to .45 tinted
borders, .5 to .6 emphasised border. Keep accents subtle: one highlight per headline, accent on
numbers and the picked item, never whole panels. **Never hard-code a colour in a part file**
(lint error): use tokens only.

## Type (Manrope everywhere)

| Role | Size and weight |
|---|---|
| Slide title h2 | 64px 700, -0.03em, sentence case, one line, no full stop |
| Cover title | 72px (112px white-label) |
| Lead or sub | 24 to 28px |
| Card title | 26 to 32px 700 |
| Body | 21 to 26px |
| Secondary | 19 to 20px |
| Caps label (`.tag`, `.eyebrow`) | 18px 700, 0.16 to 0.2em tracking (15px inside dense components) |
| Graphic labels | 18px minimum |
| Big stats | 64 to 124px 700, -0.04em, `--acc-tx`, with a count-up |

**Hierarchy rule**: inside any card, the heading is at least 1.2 times the detail text and at
least 200 heavier (blocks use `b-h` 30px 800 over `b-d` 21px 400); row titles under 26px (lists,
tables, lanes) at least 1.08x and 200 heavier. Labels are caps with tracking; chips and run-in bold
are not headings. A heading that reads as part of the body fails the gate (`[hierarchy]`). The
ContextPath layouts (card titles 1.2x to 1.5x, 700 over 400) pass as they are.

Wordmark: Bricolage Grotesque 800 "Growth" plus Fraunces italic "10x"
(`<span class="wm gx">Growth<span class="ten">10x</span></span>`). Manrope and Bricolage are
embedded; Fraunces loads from Google Fonts (Georgia italic offline).

## Signature elements

- **Highlight block** `.hl` on the key phrase of each headline: accent block at 86% height,
  sweeps in at about .55s, text turns `--on-acc`. Exactly one per headline.
- **Eyebrow** above the title: accent bar, caps, `<i>·</i>` separator ("Engine 1 · How it runs").
- **Glass panels** `.glass`, radius 18 to 22px. Icon squares `.ri` (`.ri.on-acc` for accent).
- **Line icons**: from `assets/icons.svg` (24px grid, stroke 1.8, no fill, round caps), used as
  `<svg class="ic"><use href="#i-..."/></svg>`. Chosen by meaning for this client (`components.md`).
- **Logo**: the client's real logo on the cover and thanks lockups (SVG first, else PNG 400px or
  wider), a light variant on dark ground. Never the name in text when a logo exists.
- **Background**: blurred drifting constellation (`canvas#net`) under a veil; dotted wave on
  cover and thanks, coloured from `--acc-rgb`.
- **Footer**: wordmark plus "Prepared for <client>" left (hidden on cover and thanks), back
  pill, arrows and `NN / NN` counter right; progress bar along the bottom, once per slide.

## Motion (keep it: it is the ContextPath feel)

- `.in` elements rise in when the slide opens, staggered with inline `style="--d:.3s"`.
  Lists stagger with `--k`. Typical order: eyebrow 0s, title .1s, sub .2s, panels .3s to .6s.
- Builds: `data-steps="N"` on the section, `data-b="k"` on elements; each click reveals the
  next. Use 1 to 2 builds on a slide that tells a sequence; most slides have none.
- Component animations: count-ups (`data-count`), growing bars and lines, timeline fill with
  pulsing nodes, marching dashes, workflow dot. Resting state is the final design, so print
  and reduced motion show the finished slide.
- Do not add new keyframes per slide unless needed; reuse `rise`, `fade`, `grow`, `pulse`, `hl`.

## Interactions

- `data-go="<slide id>"` jumps to a slide and shows a "Back to ..." pill (label from the
  source section's `data-back`). Used on the plan slide and engine overviews.
- `data-open="mz-<id>"` opens a mockup overlay (Esc closes, arrows page). Mockups live after
  the slides; every header tag ends "Illustrative".
- Engine workflow steps (`.wf-n[data-note]`) open a popover on click. Flip cards turn on click.
- Review links: `#s7` slide 7, `#s7.1` build 1, `#s15m-cm-1` slide 15 with mockup mz-cm-1 open.

## White label

`--white-label` (or `"white_label": true`) removes the Growth10x lockup and wordmark, the nav
reads "Prepared for <client>, <month>", and the cover title carries the slide. Also replace
"Growth10x" in copy with "our team" and remove partner mockups that name us.

## Pitfalls already solved (do not reintroduce)

1. Generic class names collide across slides. Every new class takes the slide prefix.
2. Timeline geometry comes from one `--tl-h` variable; never set `.tl` top or height in px.
3. Highlight at 86% height so two-line titles do not clip; mockup highlights need a static rule.
4. Flattened component CSS uses `!important` in places; an override in a part file needs
   `!important` too (for example `.slide{gap:22px!important}`).
5. Clicking the stage advances. Custom widgets must be buttons or links, or stop propagation.
6. Hidden builds are inert: a link inside an unrevealed `data-b` cannot be clicked.
7. Logos: a light logo on transparent ground for dark theme, a dark one for light theme.
8. The constellation is random, so compare layouts between renders, not pixels.
