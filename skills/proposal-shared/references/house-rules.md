# Growth10x house rules

Apply to every file the proposal-builder chain produces: prospect profiles, content docs, decks, plan
pages, sample messages. Run the final check at the bottom before anything goes to a client.

## 1. Language and punctuation

- **No em dashes or en dashes, anywhere.** Use a comma, a full stop or brackets. Write ranges
  in words: "2 to 3 Feb", "8 to 12 posts", "Series A to B". Hyphens inside words are fine.
- Plain, direct English. Short sentences. No hype words ("revolutionary", "game-changing",
  "unlock", "supercharge", "leverage" as a verb).
- Avoid "kick-off". Say "first call", "start" or "week 1".
- Client-facing copy is in the **second person** ("you", "your team"). Internal drafts can talk
  about the client in the third person.
- Headlines: sentence case, one line, no full stop.
- Numbers as digits with commas (1,200). Ranges as "2 to 3". Approximate counts say "about".
- Never imply the client has not tried something. Say what we would add or run differently.

## 2. Positioning

- Growth10x is a **growth partner**, never an "agency", "vendor" or "supplier". Do not call
  the client a "customer of the agency" either.
- On owner or team slides, show **roles, not freelancer or contractor names** ("Content lead",
  "Outbound operator", "Ads specialist"). Named leadership only if the user asks.
- **Confidentiality: never reveal other clients.** No other client names, logos, numbers,
  quotes, campaigns or screenshots, unless the user confirms that proof is approved for
  sharing. Past work is described in neutral terms ("a B2B SaaS client").
- Do not share internal idea or pricing logic (margins, costs, discounts given to others).

## 3. Numbers and facts

- **Never invent numbers.** Every figure in the prospect profile or a client file has a source (URL, tool
  and date, transcript, or the user). Anything else is labelled Illustrative or left out.
- Unverified facts are marked "unverified" in the profile and are not used on client files
  until confirmed.
- Database counts (Apollo, Amplemarket) are shown as approximate, with tool and date in the
  method note. They are database counts, not verified people.
- Use the client's own real results only with a source, and only the agreed metric
  definitions (for example: positive reply = any interest; reply rate is over people
  messaged).

## 4. Prices

- From `offer-catalogue.md` only. State the catalogue version in the profile.
- Round numbers, ex VAT, and say "ex VAT" wherever a price appears.
- Show prices on a client file only when the user says prices are shown.
- No performance or pay-per-meeting offers unless the user asks.
- Verbal numbers already said to the client are recorded in the profile and never contradicted
  without the user's say-so.

## 5. Mockups and examples

- Every mockup (posts, messages, ads, dashboards) carries an **Illustrative** label.
- Sample outreach, posts and ads use **fictional names** and fictional companies. Never use a
  real prospect's name in a mockup.
- **No invented engagement counts** on example posts or ads (no fake likes, comments,
  impressions). Leave counts off.
- First LinkedIn messages in samples: no links, no "quick chat", no "just checking in".
  Question-style, no pitch.

## 6. Deck and page design

- One idea per slide. Add depth through clicks and pop-ups, not extra slides.
- **No divider slides.** No "Recommended" pills or badges. Say "our pick" in copy if a
  recommendation is needed.
- **One main timeline per deck.** Do not repeat roadmaps or week plans across slides; a short
  dated path on the goals slide is fine if it differs in form.
- **Subtle accents.** The client's brand colour is the single accent. Do not copy the client's
  own deck style.
- Minimal line illustrations that match across slides.
- **No names or emails on the closing slide.** End on one clear question for the client.
- The progress bar moves once per slide, not per click.

## 7. Client files are clean

- **No internal notes, speaker notes, "Check:" markers, source mapping or open questions** in
  anything the client sees. Strip speaker notes before sending.
- Keep two versions where useful: an internal draft (third person, research mapping, quotes,
  open questions) and a client version (second person, clean).
- No tool setup details, account names, internal links or file paths in client files.
- Call transcripts and internal call notes stay in the local research folder. Quote a client's
  own words back to them only when it helps and is clearly theirs.

## 8. Working with the user

- Never remove anything or change any fact without asking. When the user gives copy, use it
  word for word.
- Content first, design second: agree the words before building slides.
- Show cost estimates and get a yes before any paid tool run.
- Draft any message to a client in chat first. Send nothing without an explicit go.

## 9. Final check (run before handing over any file)

- [ ] Search the file for em dashes (U+2014) and en dashes (U+2013): zero hits. For example
      `grep -nP '\x{2013}|\x{2014}' <file>` or a two-line Python check.
- [ ] Search for "agency", "kick-off", "Recommended": zero hits in client copy.
- [ ] Every number traces to a source in the profile, or is labelled Illustrative.
- [ ] Prices match the catalogue version, are round, and say ex VAT (or are absent by choice).
- [ ] No other client's name, number or logo.
- [ ] No freelancer names, no names or emails on the closing slide.
- [ ] No speaker notes, "Check:" markers or internal comments in the client version.
- [ ] Mockups labelled Illustrative, fictional names, no engagement counts.
- [ ] One main timeline only.
- [ ] No "Growth Console" or "the console" anywhere in client copy.
- [ ] Every content slide names this client's facts (name-swap test passes); every number has
      its noun, currency and date.
- [ ] Decks: `proposal-deck/scripts/deck_check.py <built> --deck <deck_dir> --render` passes.

## 10. Banned terms (read by proposal-deck/scripts/deck_check.py)

The block below is machine read: `severity | term | why`. An error fails the deck gate. Add new standing
rules here so every deck picks them up.

```banned-terms
error | Growth Console | never name it in a client deck: it is included in everything we do, so describe what it does (tracking, reporting) without the name
error | the console | same rule: describe the reporting, do not name a product
error | Recommended | no "Recommended" pills or badges; say "our pick" in copy
warn | agency | Growth10x is a growth partner
warn | kick-off | say "first call", "start" or "week 1"
warn | kickoff | say "first call", "start" or "week 1"
warn | revolutionary | hype word
warn | game-changing | hype word
warn | unlock | hype word
warn | supercharge | hype word
warn | seamless | hype word
warn | cutting-edge | hype word
warn | synergy | hype word
warn | best-in-class | hype word
```

## 11. Substance and specificity (the owner's main bar)

- Every content slide is about **this client**: their market, buyers, numbers, competitors and
  situation, each from a source. At least 2 to 3 sourced client facts per content slide. If a
  slide would still work with another client's name swapped in, it is generic: rewrite it.
- Reusing a layout, structure or wording pattern from an earlier deck is fine. What is not fine is
  a slide whose substance was not worked out for this client.
- Every number says what it counts, the currency, by when and whose it is: "£1m ARR from event
  organisers by December 2027", never "1M ARR". Goals are stated precisely in `offer.md` first.
- Icons are chosen by meaning for this client (a ticket for an events business, not a bank).
- Headings and their detail text look clearly different: heading at least 1.2 times the size of the
  detail text in the same card and at least 200 heavier (700 or 800 over 400).
- The real client logo goes on the cover and closing slide; the accent is the client's main brand
  colour as used across their site (not just the first colour in the logo), confirmed by the user.
