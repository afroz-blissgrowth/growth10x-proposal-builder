#!/usr/bin/env python3
"""Gate checks for a built Growth10x deck. Python 3 stdlib only. Writes a pass or fail JSON; exit 1 on any error.

Usage:
  python3 deck_check.py <built.html> [--deck <deck_dir>] [--plan slide-plan.md] [--terms terms.txt]
                        [--render] [--out gate.json] [--slides id,id]

Static checks (from the HTML, the slide plan and deck.json):
  words        visible words per slide within the plan's "words" range (no plan: content slides 130 to 220, warning only)
  banned       banned terms from proposal-shared/references/house-rules.md (the banned-terms block), e.g. Growth Console
  units        every k, m, M, bn or % figure carries a currency or a defining noun; money words (ARR, revenue,
               pipeline, budget ...) need a currency; a bare "1M" fails
  specific     client-specificity: each content slide names at least 2 distinct client terms or sourced facts
               (deck.json "client_terms", --terms, and the plan's "facts"); 0 means the slide would fit any client
  facts        every fact listed in the plan for a slide appears on that slide
  timeline     a time-based slide (plan "time_based: yes", or 3+ dates, months, quarters or weeks in its text) has a
               timeline element that draws
  interaction  every run of 3 consecutive content slides has at least one click (data-go, data-open, flip, popover,
               tabs, hover links) or build (data-b)
  mockups      every mockup the plan names for a slide is opened from that slide
  layout       data-layout ids are registered in references/layout-library.md and never repeat on adjacent slides
  logo         the cover (and thanks) lockup shows the client's logo as an image, not the name in text
  brand        deck.json says the accent and logo were confirmed by the user ("brand_confirmed": true)
--render adds the rendered checks from qa_render.py --probe-only (per slide: fill 58% or more, empty band 70px or
less, warnings under 66% or over 40px; heading at least 1.2x its detail and 200 heavier, row titles under 26px 1.08x;
count-up on hero numbers, entrance motion, overflow, contrast) and the deck averages over content slides:
fill 70% or more, empty band 30px or less (negative bands count as 0), words 140 or more.
Thresholds calibrated on the approved ContextPath deck (fill mean 73%, band mean 28px, 155 words a content slide).
"""
import argparse, html as H, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
HOUSE = os.path.join(SKILL, '..', 'proposal-shared', 'references', 'house-rules.md')
LAYOUTS = os.path.join(SKILL, 'references', 'layout-library.md')

EXEMPT_KINDS = {'cover', 'thanks', 'agenda', 'hero', 'closing'}
DECK_FILL_MIN, DECK_BAND_MAX, DECK_WORDS_MIN = 70.0, 30.0, 140.0
INTERACTIVE = re.compile(r'data-(go|open|note|nm|tab|b)="|class="[^"]*\b(wi-c|b-flip|b-tab)\b')
TIMELINE = re.compile(r'class="(?:[^"]*\s)?(tl|tl-bar|nt|nt-tr|rm|rm-c|b-tl|b-tl-bar|dn-tl|x2-mo|gantt|nx|nstep|b-steps|wf-line|fb-tr|fb-bar)(?=[\s"])|data-draw')   # whole class tokens only ("se-nx" is not "nx")
MONTHS = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*'
TIME_MARK = re.compile(r'\b(%s\b|Q[1-4]\b|[Ww]eek[s]? \d|[Mm]onth[s]? \d|20[2-3]\d\b|[Dd]ay \d)' % MONTHS)
COUNT_NOUNS = ('account|accounts|people|person|users|user|views|view|followers|follower|attendees|events|event|companies|company|'
               'contacts|contact|impressions|members|tickets|leads|lead|organisers|organizers|funds|fund|firms|shows|show|sites|'
               'downloads|subscribers|visits|visitors|employees|staff|seats|posts|messages|emails|calls|meetings|deals|customers|'
               'buyers|decision|leaders|installs|signups|sign-ups|registrations|records|rows|units|items|times|x')
MONEY_WORDS = re.compile(r'\b(ARR|MRR|cARR|revenue|pipeline|GMV|sales|budget|spend|turnover|raised|raise|funding|valuation|'
                         r'ACV|LTV|TAM|SAM|SOM|deal size|contract|fees?|profit|income|billings?|bookings?)\b', re.I)
CURRENCY = re.compile(r'[£$€]|\b(GBP|USD|EUR)\b')
MAG = re.compile(r'(?<![\w.])([£$€]?\s?\d[\d,]*(?:\.\d+)?)\s?(k|K|m|M|mn|bn|B)(?![A-Za-z])')
PCT = re.compile(r'(\d[\d,.]*)\s?%')

def read(p): return open(p, encoding='utf-8').read()

def text_of(fragment, keep_svg=True):
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', fragment, flags=re.S)
    if not keep_svg: t = re.sub(r'<svg\b.*?</svg>', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', H.unescape(t)).strip()

def chunks_of(fragment):
    """Text per element, in order, so a stat value can be read with the label that follows it."""
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', fragment, flags=re.S)
    return [re.sub(r'\s+', ' ', H.unescape(c)).strip() for c in re.split(r'<[^>]+>', t) if c.strip()]

def words(t): return len(re.findall(r"[A-Za-z0-9£$€][A-Za-z0-9'’.,%&+/-]*", t))

def parse_sections(doc):
    body = doc[doc.find('<body'):] if '<body' in doc else doc
    out = []
    for m in re.finditer(r'<section\b([^>]*)>', body):
        a = m.group(1)
        if not re.search(r'class="[^"]*\bslide\b', a): continue
        depth, j = 1, m.end()
        pat = re.compile(r'<(/?)section\b[^>]*>')
        while depth:
            n = pat.search(body, j)
            if not n: break
            depth += -1 if n.group(1) else 1
            j = n.end()
        inner = body[m.end():j]
        sid = re.search(r'\bid="([^"]+)"', a).group(1)
        kind = re.search(r'data-kind="([^"]+)"', a)
        base = re.sub(r'-d$', '', sid)
        k = kind.group(1) if kind else (base if base in ('cover', 'thanks') else 'content')
        lay = re.search(r'data-layout="([^"]+)"', a)
        out.append({'id': sid, 'kind': k, 'attrs': a, 'html': inner, 'layout': lay.group(1) if lay else None})
    return out

def parse_plan(path):
    """slide-plan.md: one '## <n>. <id>' (or '## <id>') heading per slide, then '- key: value' lines."""
    plan, cur = {}, None
    for line in read(path).splitlines():
        h = re.match(r'^##\s+(?:\d+[.)]?\s+)?([\w-]+)', line)
        if h:
            cur = plan.setdefault(h.group(1), {}); continue
        kv = re.match(r'^\s*[-*]\s+([\w ]+?):\s*(.*)$', line)
        if cur is not None and kv:
            cur[kv.group(1).strip().lower().replace(' ', '_')] = kv.group(2).strip()
    return plan

def rng(v, default):
    m = re.findall(r'\d+', v or '')
    return (int(m[0]), int(m[1])) if len(m) >= 2 else default

def split_list(v):
    out = [x.strip().strip('"\'') for x in re.split(r'\s*[|;]\s*', v or '') if x.strip().strip('"\'')]
    return [x for x in out if x.lower() not in ('none', 'no', 'n/a', '-', 'nothing')]   # "mockups: none" means no mockups

def banned_terms():
    out = []
    if not os.path.exists(HOUSE): return out
    m = re.search(r'```banned-terms\n(.*?)```', read(HOUSE), re.S)
    for line in (m.group(1) if m else '').splitlines():
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 2 and parts[0] in ('error', 'warn'):
            out.append((parts[0], parts[1], parts[2] if len(parts) > 2 else ''))
    return out

def registered_layouts():
    if not os.path.exists(LAYOUTS): return set()
    return set(re.findall(r'^###\s+`([\w-]+)`', read(LAYOUTS), re.M))

def unit_issues(sec):
    issues = []
    ch = chunks_of(sec['html'])
    for i, c in enumerate(ch):
        after = ' '.join(ch[i:i + 3]); before = ' '.join(ch[max(0, i - 1):i + 1])
        for m in MAG.finditer(c):
            tok = (m.group(1) + m.group(2)).strip()
            if re.match(r'^\d{1,2}\s?[mM]$', tok) and re.search(r'\b(min|minutes?|months?|metres?|miles?)\b', after[m.end() - m.start():][:20]):
                continue
            tail = c[m.end():] + ' ' + ' '.join(ch[i + 1:i + 3])
            head = c[:m.start()]
            has_cur = bool(CURRENCY.search(m.group(1)) or CURRENCY.search(head[-6:]) or re.match(r'\s*(GBP|USD|EUR)\b', tail))
            money = MONEY_WORDS.search(tail[:60]) or MONEY_WORDS.search(head[-40:])
            noun = re.match(r'\s*(\+\s*)?(%s)\b' % COUNT_NOUNS, tail, re.I) or re.match(r'\s*[a-z]', tail)
            if money and not has_cur:
                issues.append('units: "%s" sits next to "%s" but has no currency: write it as "£1m ARR" or "$1m ARR"' % (tok, money.group(0)))
            elif not has_cur and not noun:
                issues.append('units: bare "%s": say what it counts and whose it is ("1,000 sign-ups", "£1m revenue by Dec 2027")' % tok)
        for m in PCT.finditer(c):
            rest = (c[m.end():] + ' ' + ' '.join(ch[i + 1:i + 3])).strip()
            pre = c[:m.start()].strip()
            if not re.search(r'[A-Za-z]{3,}', rest[:80]) and not re.search(r'[A-Za-z]{3,}', pre[-60:]):
                issues.append('units: "%s%%" has no defining noun (what is it a share of?)' % m.group(1))
    return sorted(set(issues))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck_html'); ap.add_argument('--deck'); ap.add_argument('--plan'); ap.add_argument('--terms')
    ap.add_argument('--render', action='store_true'); ap.add_argument('--out'); ap.add_argument('--slides')
    a = ap.parse_args()
    doc = read(a.deck_html)
    cfg = {}
    if a.deck and os.path.exists(os.path.join(a.deck, 'deck.json')):
        cfg = json.load(open(os.path.join(a.deck, 'deck.json'), encoding='utf-8'))
    plan_path = a.plan or (os.path.join(a.deck, 'slide-plan.md') if a.deck and os.path.exists(os.path.join(a.deck, 'slide-plan.md')) else None)
    plan = parse_plan(plan_path) if plan_path else {}
    terms = list(cfg.get('client_terms', []))
    if cfg.get('client'): terms.append(cfg['client'])
    if a.terms: terms += [t.strip() for t in read(a.terms).splitlines() if t.strip() and not t.startswith('#')]
    terms = sorted(set(terms), key=len, reverse=True)
    banned = banned_terms()
    layouts = registered_layouts()
    secs = parse_sections(doc)
    only = set(a.slides.split(',')) if a.slides else None

    deck_err, deck_warn, results = [], [], []
    # deck level: brand confirmation and logo
    if cfg and not cfg.get('brand_confirmed'):
        deck_err.append('brand: deck.json has no "brand_confirmed": true. Show the user the accent (with where it came from) and the logo on both grounds, and record their yes before any build')
    for sec in secs:
        if sec['id'] in ('cover', 'thanks') or (sec['kind'] in ('cover', 'thanks')):
            lk = re.search(r'<h1 class="lockup".*?</h1>', sec['html'], re.S)
            if sec['kind'] == 'cover' and (not lk or '<img' not in lk.group(0)):
                deck_err.append('logo: the cover lockup has no client logo image (name set in text). Download the real logo (SVG, or PNG 400px or wider, light variant for dark ground) and set deck.json "logo"')
            if sec['kind'] == 'thanks' and lk and '<img' not in lk.group(0):
                deck_warn.append('logo: the thanks lockup shows the client name in text, not the logo')
    # per slide
    for s in secs:   # the plan's kind wins over the HTML (a closing slide without data-kind)
        pk = plan.get(re.sub(r'-d$', '', s['id']), {}).get('kind')
        if pk: s['kind'] = pk
    content_idx = [i for i, s in enumerate(secs) if s['kind'] not in EXEMPT_KINDS]
    prev_layout = None
    for i, sec in enumerate(secs):
        sid, base = sec['id'], re.sub(r'-d$', '', sec['id'])
        if only and sid not in only and base not in only: continue
        p = plan.get(base, {})
        kind = p.get('kind', sec['kind'])
        E, W = [], []
        t = text_of(sec['html'])
        n = words(t)
        lo, hi = rng(p.get('words'), (130, 220))
        if kind not in EXEMPT_KINDS:
            if p.get('words'):
                if not lo <= n <= hi: E.append('words: %d visible words, plan target %d to %d' % (n, lo, hi))
            elif not lo <= n <= hi:
                W.append('words: %d visible words (content standard %d to %d; add the target to the slide plan)' % (n, lo, hi))
        for sev, term, why in banned:
            if re.search(r'(?<![\w-])%s(?![\w-])' % re.escape(term), t, re.I):
                (E if sev == 'error' else W).append('banned: "%s"%s' % (term, (' (' + why + ')') if why else ''))
        E += unit_issues(sec)
        if kind not in EXEMPT_KINDS:
            hits = sorted({x for x in terms if re.search(r'(?<![\w])%s(?![\w])' % re.escape(x), t, re.I)}, key=str.lower)
            facts = split_list(p.get('facts'))
            found = [f for f in facts if f.lower() in t.lower()]
            for f in facts:
                if f not in found: E.append('facts: the plan puts "%s" on this slide, it is not there' % f)
            spec = len(set(h.lower() for h in hits) | set(f.lower() for f in found))
            sec['specific'] = {'terms': hits, 'facts': found, 'score': spec}
            if not terms and not facts:
                W.append('specific: no client terms or plan facts to check against (set deck.json "client_terms")')
            elif spec == 0:
                E.append('specific: no client names, numbers or facts on this slide; it would work for any client (name-swap test fails)')
            elif spec < 2:
                E.append('specific: only 1 client-specific item (%s); a content slide needs at least 2 to 3 sourced facts about this client' % ', '.join(hits + found))
            elif spec < 3:
                W.append('specific: 2 client-specific items (%s); aim for 3' % ', '.join(hits + found))
            tb = p.get('time_based', '').lower()
            t_nosrc = text_of(re.sub(r'<(\w+)\b[^>]*class="[^"]*\bsrc\b[^"]*"[^>]*>.*?</\1>', ' ', sec['html'], flags=re.S))
            marks = set(m[0] for m in TIME_MARK.findall(t_nosrc))
            if not TIMELINE.search(sec['html']):
                if tb.startswith('y'):
                    E.append('timeline: the plan marks this slide time-based; it has no timeline that draws (b-tl, tl, nt, rm, nx or data-draw)')
                elif not tb and len(marks) >= 3 and p:
                    # heuristic only: an error when the slide is mostly about time (the plan should say time_based: yes or no)
                    msg = 'timeline: %d dates or periods in the text and no timeline that draws; if the slide is about time, use b-tl or b-steps (set time_based in the plan)' % len(marks)
                    (E if len(marks) >= 4 or kind == 'goals' else W).append(msg)
                elif not p and len(marks) >= 4:
                    W.append('timeline: %d dates or periods in the text and no timeline that draws (no slide plan to say whether the slide is about time)' % len(marks))
            for z in split_list(p.get('mockups')):
                if 'data-open="%s"' % z not in sec['html']: E.append('mockups: plan says this slide opens %s; no data-open="%s" on it' % (z, z))
            lay = sec['layout'] or p.get('layout')
            if lay:
                if layouts and lay not in layouts: E.append('layout: "%s" is not in references/layout-library.md' % lay)
                if prev_layout and lay == prev_layout: E.append('layout: same layout "%s" as the slide before; vary it' % lay)
            prev_layout = lay
        sec['interactive'] = bool(INTERACTIVE.search(sec['html']))
        results.append({'id': sid, 'kind': kind, 'words': n, 'interactive': sec['interactive'],
                        'specific': sec.get('specific'), 'errors': E, 'warnings': W})
    # interaction windows over content slides
    if not only:
        cs = [secs[i] for i in content_idx]
        for k in range(0, max(0, len(cs) - 2)):
            win = cs[k:k + 3]
            if not any(s['interactive'] for s in win):
                deck_err.append('interaction: no click or build on %s; give one of them a jump, mockup, flip, popover, tabs or build' % ', '.join(s['id'] for s in win))
    # rendered checks
    render = None
    deck_avg = None
    if a.render:
        outdir = os.path.join(os.path.dirname(os.path.abspath(a.out)) if a.out else os.path.dirname(os.path.abspath(a.deck_html)), 'gate-probe')
        cmd = [sys.executable, os.path.join(HERE, 'qa_render.py'), a.deck_html, outdir, '--probe-only']
        if not re.search(r'<html\b[^>]*data-theme=', doc): cmd += ['--theme', 'dark']
        import time
        t0 = time.time() - 1
        subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        # only results written by this run: an older review or other-theme file in the same folder must never be read
        js = [f for f in os.listdir(outdir) if f.startswith('qa-results-') and os.path.getmtime(os.path.join(outdir, f)) >= t0] if os.path.isdir(outdir) else []
        if js:
            render = json.load(open(os.path.join(outdir, max(js, key=lambda f: os.path.getmtime(os.path.join(outdir, f)))), encoding='utf-8'))
            byid = {r['id']: r for r in results}
            for v in (render.get('probe') or {}).get('views', []):
                r = byid.get(v['id'])
                if not r: continue
                r['metrics'] = v.get('metrics')
                seen = set()
                for x in v['issues']:
                    if r['kind'] in EXEMPT_KINDS and x['kind'] in ('fill', 'empty-band', 'balance', 'hierarchy', 'countup'): continue
                    msg = '[%s] %s' % (x['kind'], x['msg'])
                    if msg in seen: continue
                    seen.add(msg)
                    (r['errors'] if x['sev'] == 'error' else r['warnings']).append(msg)
            # deck averages over content slides (calibrated on the approved ContextPath deck)
            cm = [r for r in results if r['kind'] not in EXEMPT_KINDS and r.get('metrics')]
            if cm and not only:
                af = sum(r['metrics'].get('fill', 0) for r in cm) / len(cm)
                ab = sum(max(0, r['metrics'].get('emptyBand', 0)) for r in cm) / len(cm)
                aw = sum(r['words'] for r in cm) / len(cm)
                deck_avg = {'fill': round(af, 1), 'band': round(ab, 1), 'words': round(aw, 1), 'content_slides': len(cm),
                            'countups': sum(r['metrics'].get('countUps', 0) for r in cm),
                            'interactive': sum(1 for r in cm if r['interactive'])}
                if af < DECK_FILL_MIN: deck_err.append('fill: content slides average %.1f%% fill (deck minimum %.0f%%; the approved reference averages 73%%)' % (af, DECK_FILL_MIN))
                if ab > DECK_BAND_MAX: deck_err.append('empty-band: content slides average %.1fpx empty above the footer (deck maximum %.0fpx; reference 28px)' % (ab, DECK_BAND_MAX))
                if aw < DECK_WORDS_MIN: deck_err.append('words: content slides average %.0f words (deck minimum %.0f; reference 155)' % (aw, DECK_WORDS_MIN))
        else:
            deck_err.append('render: the probe produced no results (see qa_render.py output)')
    n_err = len(deck_err) + sum(len(r['errors']) for r in results)
    gate = {'deck': os.path.abspath(a.deck_html), 'plan': plan_path, 'passed': n_err == 0, 'errors': n_err,
            'deck_errors': deck_err, 'deck_warnings': deck_warn, 'averages': deck_avg, 'slides': results}
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.deck_html)), 'gate.json')
    json.dump(gate, open(out, 'w', encoding='utf-8'), indent=1)
    print('GATE %s: %s, %d errors  (%s)' % (os.path.basename(a.deck_html), 'PASS' if gate['passed'] else 'FAIL', n_err, out))
    if deck_avg: print('  averages over %(content_slides)d content slides: fill %(fill)s%%, band %(band)spx, words %(words)s, count-ups %(countups)s, interactive %(interactive)s' % deck_avg)
    for e in deck_err: print('  ERROR  deck: ' + e)
    for w in deck_warn: print('  warn   deck: ' + w)
    for r in results:
        if r['errors'] or r['warnings']:
            m = r.get('metrics') or {}
            print('  %s (%s, %d words%s)' % (r['id'], r['kind'], r['words'], (', fill %s%%, band %spx' % (m.get('fill'), m.get('emptyBand'))) if m else ''))
            for e in r['errors']: print('    ERROR  ' + e)
            for w in r['warnings']: print('    warn   ' + w)
    sys.exit(0 if gate['passed'] else 1)

if __name__ == '__main__':
    main()
