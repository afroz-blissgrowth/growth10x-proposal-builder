# Critic rubric: fresh eyes on rendered slides

The builder sees what it meant to build. A fresh subagent that sees only the rendered PNGs, the
slide plan entries and this rubric catches what the builder misses. Run it on the pilot, on each
batch, and on the whole deck at the end. Budget one or two fix rounds per batch; if a fix creates
a new hard finding, roll it back.

## How to run it

Spawn a subagent (lower effort is fine) with: the paths of the batch's final PNGs and the contact
sheet, the batch's entries from `deck/slide-plan.md`, `offer.md` section 1 and 4, and this file.
Do not give it the part files or your opinion. Ask for a table per slide: hard findings, soft
findings, name-swap verdict, and checklist lines answered yes or no. The builder fixes every hard
finding and any soft finding that is clearly bad, then re-renders only those slides.

## Hard rules (always fix)

1. Text clipped, overflowing its panel, overlapping other text, or under the footer.
2. Contrast too low to read (small grey text on glass, accent text on accent).
3. A required element from the plan is missing (count-up, timeline, mockup, the facts listed).
4. A number without what it counts, currency or date ("1M", "30%" alone).
5. "Growth Console", "the console", another client's name, a freelancer's name, an email on the
   closing slide.
6. Hollow slide: a large empty area, or panels much taller than their content. A button or line
   pinned to the bottom of a card does not make it full: look for the gap between the text at the
   top and the pinned element (ReelFlow v2: sees, tests and measure passed fill at 85% and were half
   empty). The gate's `[hollow]` check finds most of these; the critic finds the rest.
7. Icon that means nothing for this client (a bank for an events company, a factory for a SaaS).
8. Headings that do not stand out from their detail text.
9. No client logo on the cover; the accent is not the confirmed brand colour.

## The name-swap test (concept veto)

For each slide: replace the client's name with a competitor's or another client's. Does the slide
still read the same? If yes, the slide is generic. It fails, whatever its design, and goes back to
the plan for client substance: their numbers, named customers, segments, competitors, their words.
A deck where more than two content slides fail the name-swap test is not shown to the user.

## Soft rules (fix when clearly bad)

- Rhythm: the same layout or ground three slides running; no hero slide in a long stretch.
- Emphasis mismatch: the most prominent element is not the slide's key message.
- Alignment drift, uneven grids, orphan words in pills and labels.
- Accent overused (whole panels in accent) or the highlight on the wrong phrase.
- Copy that describes instead of claims ("This slide shows our approach").
- Motion missing where the plan promised it (mid-animation frames all static).

## Deck level (final pass)

- Coherence: does the storyline read as one argument from their goal to the ask?
- Every key message in `offer.md` lands on at least one slide.
- One main timeline; other dated elements are short and different in form.
- Every date and count says the same thing on every slide (ReelFlow v2: plan 2 started in June on
  the goals path, April on three slides and March on the ask). Titles that count things match what
  is shown ("Three plans" over six rows fails).
- The fact checklist (`deck/checklist.md`) is all yes.

When in doubt on a soft rule, leave it: under-fixing beats oscillating.
