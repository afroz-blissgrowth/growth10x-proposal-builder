# Build and QA

Python 3 stdlib only. Pillow is optional (contact sheets fall back to headless Chromium).
Rendering uses Playwright's headless Chromium (`chromium_headless_shell-*` in the Playwright
cache, or `G10X_CHROMIUM`). **Never the user's Google Chrome.** If the scripts say Chromium is
not found, stop and tell the user (`npx playwright install chromium-headless-shell` installs
it); do not point them at Chrome.

## Deck folder

```
proposals/<slug>/offer.md   agreed strategy and offer (proposal-experiments); required
proposals/<slug>/deck/
  storyline.md          approved storyline (internal)
  slide-plan.md         approved slide plan, read by deck_check.py (internal)
  checklist.md          per-deck yes or no fact checklist (internal)
  deck.json
  slides/01-cover.html  one part file per slide, numbered in deck order
  mockups/mz-*.html     optional overlays
  assets/               logos and images (embedded as base64 at build)
  build/                <slug>-<theme>.html, <slug>-review.html (pilot), lint-*.json, gate-*.json (generated)
  qa/round<N>/          QA output per pass (generated)
```

## deck.json

```json
{"client": "Northwind Polymers", "slug": "northwind-polymers", "prepared_for": "Elin",
 "month_year": "December 2026", "accent": "#2F80ED", "theme": "dark", "white_label": false,
 "prices_shown": false, "title": "Northwind Polymers growth plan",
 "brand_confirmed": true, "accent_source": "most-used brand colour on northwind.com, user 2026-12-01",
 "logo": {"dark": "assets/logo-light.svg", "light": "assets/logo-dark.svg"},
 "client_terms": ["Northwind", "Elin", "OEM", "Volvo Trucks", "DACH", "Covestro", "polymer compounders"],
 "slides": ["slides/01-cover.html", "slides/02-goals.html", "slides/03-engine.html"],
 "mockups": ["mockups/mz-brief.html"]}
```

- `brand_confirmed` must be true before any build: the user has seen and confirmed the accent and
  the logo on both grounds (`build.py --brand-check` builds a preview without it).
- `logo` needs a file per ground (light logo for dark ground). Only when no logo exists and the
  user agreed, set `"logo_text_ok": true` and the name is set in text.
- `client_terms`: names, customers, partners, competitors, places, segments and key figures for
  the specificity gate. The client name is added automatically.
- `mockups` omitted = every file in `mockups/`. `title` is the browser tab title.

## Part files

```html
<!-- prefix: eg -->
<style>
/* optional, scoped to this slide by build.py */
.slide{gap:40px!important}
.eg-note{font-size:20px}
</style>
<section class="slide ly-engine" id="engine" data-steps="2" aria-label="Engine 1: How it runs">
  ...
</section>
```

- Exactly one `<section class="slide ...">` with a unique `id` (`cover` and `thanks` reserved
  for first and last) and an `aria-label`.
- Set `data-layout="<id>"` on the section (ids in `layout-library.md`) and `data-kind` when the
  slide is not a content slide (`agenda`, `hero`, `closing`).
- Compose from blocks in `assets/components.html` (`b-*`), or start from a whole layout
  (`@component <name>`, keep its `ly-<name>` class). Either way rewrite every text node with this
  client's substance. Library text is placeholder words.
- Icons: `<svg class="ic" aria-hidden="true"><use href="#i-<name>"/></svg>`, picked by meaning
  (`components.md`).
- New classes must start with the prefix (`eg-`). Component classes can be used as they are.
- CSS in the part is scoped to the slide id. `.slide` in a part means that slide.
- Colours only through tokens (`var(--acc)`, `rgba(var(--acc-rgb),.1)`, `var(--fg-3)`).
- Tokens filled at build: `{{LOCKUP}}` (cover and thanks lockup), `{{CLIENT}}`,
  `{{PREPARED_FOR}}`, `{{MONTH_YEAR}}`, `{{TEAM}}` (Growth10x or "Growth team" in white label),
  `{{PREPARED_LINE}}`.
- Mockup part: a `<!-- prefix: xyz -->` comment (else the prefix is the first 3 letters of the id
  after `mz-`), optional `<style>`, then one `<div class="mz" id="mz-...">` with the
  `.mz-hd` header whose tag ends "Illustrative". Opened by `data-open="mz-..."` on a slide.

## Components

Blocks, layouts and icons, with when to use each: `components.md`. To see them rendered, open
`assets/components.html` in a browser (viewing only; scripts never launch the user's browser).

## build.py

```
python3 scripts/build.py <deck_dir> [--theme dark|light|both] [--review] [--white-label] [--only id,id] [--lint-only] [--out FILE] [--no-gate] [--brand-check]
```

Pilot review (`--review`, or `"review": true` in deck.json when no `--theme` is given): one
file, `build/<slug>-review.html` and `build/lint-review.json`. Slides 1 to 3 in light theme,
then slides 4 to 6 = the same three slides in dark theme. How it works:
- each slide section gets `data-theme="light"`; the copies get `data-theme="dark"` and every id
  gets the suffix `-d` (`cover-d`, `goals-d`, inner ids too), with `data-go`, `href="#..."`,
  `url(#...)` and aria references updated so the dark copies link to dark slides;
- every CSS rule that names a slide id (`#cover`, `#goals .nm-c`, shell or part CSS) is
  duplicated for the `-d` id in place, so both copies get the same per-slide styling;
- the cover and thanks lockups use the logo for each theme;
- the shell's `go()` switches `<html data-theme>` to the slide's `data-theme` and re-reads
  `--fg-rgb`, `--net-a` and `--acc-rgb` for the canvas; cover styling matches ids by prefix
  (`cover`, `cover-d`, `thanks`, `thanks-d`); the counter shows the total (06 for a 3-slide pilot).
This is the only pilot format: publish it as one link. `--theme both` is for local comparison
only and is never published as two links.

Writes `build/<slug>-<theme>.html` (single self-contained file, about 180KB plus images) and
`build/lint-<theme>.json`, then runs the static gate (`deck_check.py`, below) and writes
`build/gate-<theme>.json`. Component CSS is tree-shaken to what the deck uses; icons are inlined.
Exit 1 on lint or gate errors. `--no-gate` skips the gate (local experiments only);
`--brand-check` builds a preview for the brand question without `brand_confirmed`.

Lint errors (must fix): no `brand_confirmed`; no logo file per ground; unknown icon id; em or en dash anywhere; notes, `Check:`, TODO, TBC, placeholders in
visible text; "Recommended"; missing `data-go` or `data-open` targets; duplicate ids; no
`cover`; mockup header without "Illustrative"; unprefixed new classes or generic class names;
hard-coded colours; highlight not at 86%; `data-b` beyond `data-steps`; email on the closing
slide; external scripts or stylesheets (Google Fonts allowed).
Warnings (fix or justify): "agency", "kick-off", headline without exactly one `.hl` or ending
in a full stop, prices without "ex VAT" when prices are shown, non-round prices, no `thanks`
slide (expected in a pilot), unused mockups, classes with no CSS.

## qa_render.py

```
python3 scripts/qa_render.py <built.html> <deck_dir>/qa/round<N> --theme dark|light [--slides id,id] [--no-mid] [--jobs 3] [--probe-only]
```

One pass: final-state screenshot of every slide at every build step (animations frozen),
each mockup opened through its review hash, mid-animation frames at 400 and 1200ms, a DOM
probe and an animation probe, then contact sheets. Output, per theme label:
`final-<theme>/`, `mid-<theme>/`, `mockups-<theme>/`, `contact-final-<theme>.png`,
`contact-mid-<theme>.png`, `contact-mockups-<theme>.png`, `qa-results-<theme>.json`.
Dark and light passes can share one round folder. Exit 1 if the probe found errors.

Review file: run it without `--theme` (it is ignored if given). The label is `review`
(`contact-final-review.png`, `qa-results-review.json`), each slide is shot in its own theme,
captions read `s04-cover-d (dark)`, and the final sheet puts the light frames in the first row
and the same frames dark in the row below when they fit.

Probe messages and the usual fix:

| Message | Fix |
|---|---|
| `[footer] ... bottom at y 976` | Tighten that slide: shorter copy so lines do not wrap, lower `.slide` gap, smaller paddings (with `!important` if the component sets it) |
| `[contrast] ... 4.2 below 4.5` | Use `--fg-3` or stronger for small text, `--acc-tx` (not `--acc`) for accent text, or `--fg` for numbers inside tinted circles |
| `[clipped]`, `[outside-panel]`, `[off-stage]` | Text too long for its box or pushed out: cut copy first, then widen |
| `[pin-align]` | Timeline pins off the bar: set `--tl-h` only, never px tops |
| `[highlight]` | `.hl` wraps badly or is missing: shorten the phrase |
| `[collision]` | Two text boxes overlap: reduce copy or move one |
| `interaction: data-go ... back=False` | Source section needs `data-back`, target id must exist |
| `[motion] no entrance animation` | Add `in` and `--d` to the header and panels |
| `[fill]`, `[empty-band]`, `[hierarchy]`, `[countup]` | See the gate table below |
| `fonts: Manrope not loaded` | Shell fonts block was edited; restore it |

Reading the pass: open the contact sheets first, then full-size frames for anything doubtful.
Look for wrapping in pills and labels, empty bands (a panel much taller than its content),
the highlight on the right phrase, accent overuse, and the mid sheet showing slides mid-entrance
(entrances exist). Mid frames are early states under virtual time and look faint; that is expected.

Keep render counts low: a 3-slide pilot review is about 24 screenshots in one pass; for a full deck
re-render only changed slides with `--slides`, and do the full pass once at the end.

## deck_check.py (the gate)

```
python3 scripts/deck_check.py <built.html> [--deck <deck_dir>] [--plan slide-plan.md] [--terms terms.txt] [--render] [--slides id,id] [--out gate.json]
```

Writes a pass or fail JSON and exits 1 on any error. With `--render` it reads only probe results
written by this run (an older review or other-theme file in `gate-probe/` once gave a false pass). A batch is not shown to the user, and the
deck is not published, while it fails. Static checks read the HTML, `deck/slide-plan.md` and
`deck.json`; `--render` adds the rendered probe (`qa_render.py --probe-only`, about a second).

| Check | Fails when | Usual fix |
|---|---|---|
| `words` | Visible words outside the plan's range (no plan: warning outside 130 to 220) | Add the missing mechanism or proof; or cut |
| `banned` | A banned term from house-rules section 10 (Growth Console, the console, Recommended) | Describe what it does instead |
| `units` | k, m, bn or % with no noun; a money word (ARR, revenue, pipeline) with no currency | "£1m ARR from organisers by Dec 2027" |
| `specific` | Fewer than 2 client terms or plan facts on a content slide (0 = name-swap fails) | Put their names, numbers, segments, competitors on it |
| `facts` | A fact the plan lists for the slide is not on it | Add it, or change the plan with the user |
| `timeline` | Plan says time_based (or 4+ dates in the text) and no timeline that draws | b-tl or b-steps |
| `interaction` | Three content slides in a row with no click or build | Add a jump, mockup, flip, popover, tabs or build |
| `mockups` | A mockup the plan names is not opened from the slide | `data-open` on a b-open |
| `layout` | Unregistered `data-layout`, or the same layout as the slide before | Pick by function, vary |
| `logo` | The cover lockup has no logo image | Real logo in deck.json |
| `[fill]` | Content covers under 58% of the content box (warning under 66%) | Add substance (content-standard.md) |
| `[empty-band]` | More than 70px empty above the footer (warning over 40px) | Same; or enlarge the visual |
| deck `fill`, `empty-band`, `words` | Content-slide averages under 70% fill, over 30px band or under 140 words | Fix the thinnest slides first (the gate prints the averages) |
| `[hierarchy]` | A card heading under 1.2x its detail text or less than 200 heavier (row titles under 26px: 1.08x) | Use `b-h` and `b-d`, or raise the heading |
| `[countup]` | A hero number (56px or more) with no `data-count` | Add data-count, data-pre, data-suf |
| `[hollow]` | A panel 200px or taller with half of it empty below its content, or 38% of it empty between its content and a pinned button or line (warnings from 40% and 30%) | Add the output, verdict or proof line the panel is missing, or let it shrink |
| `[motion]` | No entrance animation on the slide | `in` with a staggered `--d` on header and panels |

Exempt from fill, band and words: `cover`, `thanks`, and sections with
`data-kind="agenda|hero|closing"`. Thresholds can be tuned per run with `window.G10X_FILL_MIN`,
`G10X_BAND_MAX` and `G10X_HIER_MIN` in the probe, but the house values are the bar. They were
calibrated on the approved ContextPath deck (19 Nov 2026): its content slides pass every gate
except the banned console wording and a few rules added after it (count-ups on its numbers and
outbound slides, a click every 3 slides in its founder stretch, the Recommended pill, the 136px band
on its founder package slide). The plan's `kind` wins over the HTML for exemptions (a closing slide
without `data-kind` is still exempt).
