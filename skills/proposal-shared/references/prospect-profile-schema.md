# prospect-profile.yaml schema

The machine-readable twin of `prospect-profile.md`. Both live in `./proposals/<client-slug>/`.
`proposal-prospect-profile` writes them; every later skill reads the YAML first (it is quicker
to parse and harder to misread than prose) and `prospect-profile.md` when it needs the detail.

Every value is an object with `value`, `source` and `status` so a later skill can tell a fact
from a guess. Status is one of: `confirmed` (the user said so, or a primary source states it),
`from_source` (read from a source, not yet confirmed by the user), `proposed` (our
suggestion), `unverified` (found but doubtful, say why in `note`), `gap` (unknown).

Sources are short and traceable: `fireflies:<meeting title> <YYYY-MM-DD> <mm:ss>`,
`gmail:<subject> <YYYY-MM-DD>`, `slack:<channel or DM> <YYYY-MM-DD>`, `gdoc:<title>`,
`notion:<page title>`, `calendar:<event> <YYYY-MM-DD>`, a URL, or `user <YYYY-MM-DD>`.
Never write API keys, account IDs or tool setup details.

```yaml
meta:
  client: Atmospheric AI
  slug: atmospheric-ai
  created: 2026-11-19
  updated: 2026-11-19
  profile_version: 1
  catalogue_version: v2
  status: draft            # draft | confirming | ready

engagement:
  intent:          {value: new pitch, source: user 2026-11-19, status: confirmed}
  relationship:    {value: external, source: ..., status: ...}   # external | portfolio company
  services_in_scope:
    - {value: outbound, lead: true, source: ..., status: proposed}
  deadline:        {value: 2026-11-25, presenter: Dan, source: ..., status: ...}
  prices_shown:    {value: false, source: ..., status: ...}
  format_wanted:   {value: deck, source: ..., status: ...}     # deck | plan page | both

discussed_and_promised:      # word for word where the source allows
  - {what: pilot terms, words: "...", who: Dan, source: ..., status: from_source}

people:
  - name: ...
    role: ...
    decision_role: decision maker   # decision maker | champion | user | influencer
    linkedin: https://...
    founder_brand_in_scope: true
    source: ...
    status: ...

company:
  website:     {value: https://..., source: ..., status: ...}
  what_they_sell: {value: ..., source: ..., status: ...}
  stage:       {value: ..., source: ..., status: ...}
  funding:     {value: ..., source: ..., status: ...}
  employees:   {value: ..., source: ..., status: ...}
  hq:          {value: ..., source: ..., status: ...}

icp:                         # THEIR customers, not ours
  hard_filters:              # if a prospect misses this, we do not contact them
    titles:      [{value: Chief Procurement Officer, source: ..., status: ...}]
    industries:  [...]
    company_size: {min: ..., max: ..., source: ..., status: ...}
    regions:     [...]
  soft_preferences:          # nice to have; used for scoring and personalisation, not filtering
    - {value: recently hired procurement leaders, source: ..., status: proposed}
  exclusions:  [...]          # competitors, existing customers, partners
  deal_size:   {value: ..., source: ..., status: ...}

competitors:
  - {name: ..., note: ..., source: ..., status: ...}

sensitivities:
  - {value: do not mention <customer>, source: ..., status: confirmed}

conflicts:                   # two sources disagree; never resolve silently
  - field: company.funding
    a: {value: ..., source: ...}
    b: {value: ..., source: ...}
    resolution: {value: ..., source: user 2026-11-19}   # empty until the user answers

gaps:
  - {field: ..., why_it_matters: ..., who_can_fill: user | client | paid lookup}

sources_ingested:
  - {id: S1, type: fireflies, title: ..., date: ..., file: research/sources/S1-....md}
```

Keep field names stable. A skill that needs a field that does not exist adds it under the
closest section and records the addition in the profile's change log.
