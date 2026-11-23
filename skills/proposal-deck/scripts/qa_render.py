#!/usr/bin/env python3
"""Render and probe a built Growth10x deck with headless Chromium. Python 3 stdlib only.

Usage:
  python3 qa_render.py <deck.html> <out_dir> [--theme dark|light] [--slides id,id] [--no-mid] [--no-probe]
                       [--mid 400,1200] [--jobs 6] [--label NAME]

What it does (one pass):
  1. Final-state screenshots: every slide at every build step, with an injected style that sets all
     animation and transition durations and delays to 0 (so what you see is the resting design).
  2. Mockups: every .mz overlay opened through the #sNm-<id> review hash, final state.
  3. Mid-animation frames: each slide at --mid milliseconds (default 400 and 1200) with animations ON,
     to confirm the entrances exist and play.
  4. DOM probe (scripts/dom_probe.js): interactions (every data-open opens and closes, every data-go lands
     and the back pill returns), then layout checks per slide and mockup (overflow, clipping, off-stage,
     footer clearance, text collisions, timeline pins on the bar, highlight height, contrast, fonts).
  5. Animation probe: walks the deck build by build and counts running animations about 300ms in.
  6. Contact sheets (scripts/contact_sheet.py): final, mockups, mid frames.
Writes <out_dir>/qa-results-<label>.json and prints a short report. Exit code 1 if the probe found errors.

Review builds (build.py --review: slides with data-theme, light first then the same slides dark) are detected
automatically: --theme is ignored, the label is "review", every slide is shot in its own theme (the deck
switches theme as it lands on each slide) and contact sheet captions say which theme each frame is.
"""
import argparse, concurrent.futures as cf, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1952, 1080            # 1920 stage + 16px gutters, so the stage renders at scale 1
STILL = ('<style id="qa-still">*,*::before,*::after{animation-duration:0s!important;animation-delay:0s!important;'
         'transition-duration:0s!important;transition-delay:0s!important}</style>')

def find_chrome():
    # Uses Playwright's own Chromium, a separate browser. Never the user's installed Google Chrome,
    # which must not be launched at all (it closed a user's open tabs on 18 Nov 2026).
    env = os.environ.get('G10X_CHROMIUM')
    if env and os.path.exists(env):
        return env
    import glob
    # headless_shell first: it exits cleanly after --screenshot / --dump-dom (full Chromium can hang).
    for pat in ('~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-mac*/headless_shell',
                '~/.cache/ms-playwright/chromium_headless_shell-*/chrome-linux/headless_shell',
                '~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium',
                '~/.cache/ms-playwright/chromium-*/chrome-linux/chrome'):
        hits = sorted(glob.glob(os.path.expanduser(pat)))
        if hits:
            return hits[-1]
    sys.exit('Playwright Chromium not found. Run: npx playwright install chromium '
             '(a separate browser; your own Google Chrome is never used).')

CHROME = None

PROFILE_ROOT = None   # isolated headless profiles live here; never the user's own Chrome profile

def chrome(args, timeout=90):
    # Each call gets its own throwaway profile dir (parallel calls cannot share one). This script never
    # kills, quits or restarts any Chrome process, so the user's own browser is untouched.
    ud = tempfile.mkdtemp(prefix='p-', dir=PROFILE_ROOT)
    try:
        cmd = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
               '--disable-extensions', '--mute-audio', '--force-device-scale-factor=1', '--user-data-dir=' + ud,
               '--window-size=%d,%d' % (W, H)] + args
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except subprocess.TimeoutExpired:
        return ''
    finally:
        shutil.rmtree(ud, ignore_errors=True)

def shot(url, out, budget):
    for attempt in range(3):          # parallel headless Chromium occasionally exits without writing; retry
        if os.path.exists(out): os.remove(out)
        chrome(['--virtual-time-budget=%d' % budget, '--screenshot=' + out, url])
        if os.path.exists(out) and os.path.getsize(out) > 0: return out
    return None

def probe_json(dom):
    hits = re.findall(r'<script type="application/json" id="qa-probe-out">(.*?)</script>', dom or '', re.S)
    for h in reversed(hits):
        try: return json.loads(h)
        except ValueError: continue
    return None

def dump(url, budget):
    for attempt in range(3):          # retry: a headless run occasionally returns before the probe writes
        dom = chrome(['--virtual-time-budget=%d' % budget, '--dump-dom', url], timeout=180)
        if 'id="qa-probe-out">{' in (dom or ''): return dom
    return dom

def parse_deck(html):
    body = html[html.index('<body'):]
    secs = []
    for m in re.finditer(r'<section\b([^>]*)>', body):
        a = m.group(1)
        if not re.search(r'class="[^"]*\bslide\b', a): continue
        sid = re.search(r'\bid="([^"]+)"', a).group(1)
        st = re.search(r'data-steps="(\d+)"', a)
        end = body.index('</section>', m.end())
        th = re.search(r'\bdata-theme="([^"]+)"', a)
        secs.append({'id': sid, 'steps': int(st.group(1)) if st else 0, 'theme': th.group(1) if th else None,
                     'opens': re.findall(r'data-open="([^"]+)"', body[m.end():end])})
    mzs = re.findall(r'<div\b[^>]*class="mz[" ][^>]*>', body)
    mz_ids = [re.search(r'id="([^"]+)"', t).group(1) for t in mzs]
    return secs, mz_ids

def with_theme(html, theme):
    if not theme: return html
    return re.sub(r'(<html\b[^>]*data-theme=")[^"]*(")', r'\g<1>%s\2' % theme, html, count=1)

def main():
    global CHROME, PROFILE_ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument('deck'); ap.add_argument('out')
    ap.add_argument('--theme', choices=['dark', 'light'])
    ap.add_argument('--slides'); ap.add_argument('--label')
    ap.add_argument('--no-mid', action='store_true'); ap.add_argument('--no-probe', action='store_true')
    ap.add_argument('--probe-only', action='store_true', help='no screenshots: run only the layout probe (fill, band, hierarchy, count-up, overflow, contrast) and the animation probe')
    ap.add_argument('--mid', default='400,1200'); ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--profile-dir', help='folder for the isolated headless Chromium profiles (default: <out>/.chrome-profiles)')
    a = ap.parse_args()
    CHROME = find_chrome()
    deck = os.path.abspath(a.deck); out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    PROFILE_ROOT = os.path.abspath(a.profile_dir or os.path.join(out, '.chrome-profiles'))
    os.makedirs(PROFILE_ROOT, exist_ok=True)
    html = open(deck, encoding='utf-8').read()
    secs, mz_ids = parse_deck(html)
    review = any(s['theme'] for s in secs)
    if review and a.theme:
        print('review build: each slide renders in its own theme, --theme %s ignored' % a.theme)
    if not review: html = with_theme(html, a.theme)
    label = a.label or ('review' if review else (a.theme or re.search(r'data-theme="([^"]+)"', html).group(1)))
    only = set(a.slides.split(',')) if a.slides else None

    # QA copies next to the outputs (file URLs, so hashes work)
    still = os.path.join(out, '_qa-still.html'); anim = os.path.join(out, '_qa-anim.html')
    probe_js = open(os.path.join(HERE, 'dom_probe.js'), encoding='utf-8').read()
    # the frozen style goes in <head> so the deck script sees it at boot (count-ups then show their final figure)
    still_html = html.replace('</head>', STILL + '\n</head>', 1) if '</head>' in html else html.replace('</body>', STILL + '\n</body>')
    open(still, 'w', encoding='utf-8').write(still_html)
    open(anim, 'w', encoding='utf-8').write(html)
    probe_l = os.path.join(out, '_qa-probe.html'); probe_a = os.path.join(out, '_qa-probe-anim.html')
    open(probe_l, 'w', encoding='utf-8').write(still_html.replace('</body>', '<script>window.QA_MODE="layout";\n' + probe_js + '</script>\n</body>'))
    open(probe_a, 'w', encoding='utf-8').write(html.replace('</body>', '<script>window.QA_MODE="anim";\n' + probe_js + '</script>\n</body>'))

    tasks = []   # (kind, label, url, png, budget)
    theme_of = {}   # shot label -> theme, for review captions
    mz_owner = {}
    for i, s in enumerate(secs, 1):
        for z in s['opens']: mz_owner.setdefault(z, i)
        if only and s['id'] not in only: continue
        for k in range(0, s['steps'] + 1):
            tag = 's%02d-%s%s' % (i, s['id'], '.%d' % k if s['steps'] else '')
            theme_of[tag] = s['theme']
            tasks.append(('final', tag, 'file://%s#s%d%s' % (still, i, '.%d' % k if k else ''), os.path.join(out, 'final-' + label, tag + '.png'), 5000))
        if not a.no_mid:
            for ms in [int(x) for x in a.mid.split(',') if x]:
                tag = 's%02d-%s@%dms' % (i, s['id'], ms)
                theme_of[tag] = s['theme']
                tasks.append(('mid', tag, 'file://%s#s%d' % (anim, i), os.path.join(out, 'mid-' + label, tag + '.png'), ms))
    for z in mz_ids:
        i = mz_owner.get(z)
        if not i: continue
        if only and secs[i - 1]['id'] not in only: continue
        tag = 'mz-%s' % z.replace('mz-', '')
        theme_of[tag] = secs[i - 1]['theme']
        tasks.append(('mockup', tag, 'file://%s#s%dm-%s' % (still, i, z.replace('mz-', '')), os.path.join(out, 'mockups-' + label, tag + '.png'), 3000))
    for d in ('final', 'mid', 'mockups'): os.makedirs(os.path.join(out, d + '-' + label), exist_ok=True)   # per theme, so dark and light passes can share one out_dir

    if a.probe_only: tasks = []
    shots = {'final': [], 'mid': [], 'mockup': []}
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(shot, t[2], t[3], t[4]): t for t in tasks}
        probe_f = None if a.no_probe else ex.submit(dump, 'file://%s#s1' % probe_l, 8000)
        nsteps = sum(s['steps'] + 1 for s in secs)
        anim_f = None if a.no_probe else ex.submit(dump, 'file://%s#s1' % probe_a, 2000 + nsteps * 450)
        for f in cf.as_completed(futs):
            t = futs[f]; p = f.result()
            shots[t[0]].append({'label': t[1], 'png': p})
        probe = anim_res = None
        if probe_f:
            probe = probe_json(probe_f.result()) or {'error': 'probe produced no output (script error or timeout)'}
        if anim_f:
            anim_res = probe_json(anim_f.result()) or {'error': 'animation probe produced no output'}
    for k in shots: shots[k].sort(key=lambda x: x['label'])

    # contact sheets
    sheets = {}
    sys.path.insert(0, HERE)
    import contact_sheet
    def cols_for(k, items):
        # review: one row per theme when it fits (light row, then the same frames dark below it)
        if review:
            n = sum(1 for _, lab in items if lab.endswith('(light)'))
            if n and n * 2 == len(items) and n <= 8: return max(n, 3)
        return 4 if k != 'mid' else 6
    for k, name in (('final', 'contact-final'), ('mockup', 'contact-mockups'), ('mid', 'contact-mid')):
        items = [(s['png'], s['label'] + (' (%s)' % theme_of[s['label']] if review and theme_of.get(s['label']) else ''))
                 for s in shots[k] if s['png']]
        if items:
            sheets[k] = contact_sheet.make(items, os.path.join(out, '%s-%s.png' % (name, label)), title='%s: %s (%s)' % (os.path.basename(deck), name.replace('contact-', ''), label),
                                           cols=cols_for(k, items), chrome=CHROME)

    # summarise
    errors, warns = [], []
    if probe and 'views' in probe:
        f = probe.get('fonts', {})
        if f and not f.get('manrope'): errors.append('fonts: Manrope not loaded')
        for it in probe.get('interactions', []):
            if it['kind'] == 'data-open' and not (it['opens'] and it['closesOnEsc']): errors.append('interaction: data-open %s from %s opens=%s closes=%s' % (it['target'], it['from'], it['opens'], it['closesOnEsc']))
            if it['kind'] == 'data-go' and not (it['lands'] and it['backPill'] and it['backReturns']): errors.append('interaction: data-go %s from %s lands=%s back=%s returns=%s' % (it['target'], it['from'], it['lands'], it['backPill'], it['backReturns']))
            if it['kind'] == 'flip' and not it['ok']: errors.append('interaction: flip card did not open')
        for v in probe['views']:
            for x in v['issues']:
                line = '%s: [%s] %s: %s' % (v['id'], x['kind'], x['where'], x['msg'])
                (errors if x['sev'] == 'error' else warns).append(line)
    elif probe:
        errors.append('probe: ' + probe.get('error', 'unknown'))
    if anim_res and 'steps' in anim_res:
        for st in anim_res['steps']:
            if st['step'] == 0 and st['running'] == 0:
                warns.append('%s: no animation sampled 300ms after the slide appears (the layout probe [motion] check is the gate)' % st['slide'])
    elif anim_res:
        warns.append('animation probe: ' + anim_res.get('error', 'unknown'))
    res = {'deck': deck, 'label': label, 'review': review, 'shots': shots, 'sheets': sheets, 'probe': probe, 'anim': anim_res, 'errors': errors, 'warnings': warns}
    json.dump(res, open(os.path.join(out, 'qa-results-%s.json' % label), 'w'), indent=1)
    for p in (still, anim, probe_l, probe_a):
        try: os.remove(p)
        except OSError: pass
    n_ok = sum(1 for k in shots for s in shots[k] if s['png'])
    print('QA %s: %d screenshots (%d final, %d mockups, %d mid)' % (label, n_ok, len(shots['final']), len(shots['mockup']), len(shots['mid'])))
    for k, p in sheets.items(): print('  contact sheet %-7s %s' % (k, p))
    if probe and 'views' in probe:
        for v in probe['views']:
            m = v.get('metrics')
            if m: print('  %-14s %-8s fill %5s%%  empty band %4spx  hierarchy %s  hero numbers %s, count-ups %s' % (
                v['id'][:14], m.get('kind'), m.get('fill'), m.get('emptyBand'), min(m['hier']) if m.get('hier') else '-', m.get('heroNumbers'), m.get('countUps')))
    if anim_res and 'steps' in anim_res:
        print('  animations at 300ms per build: ' + ', '.join('%s.%d=%d' % (s['slide'], s['step'], s['running']) for s in anim_res['steps']))
    def collapse(lines):
        seen, out = {}, []
        for l in lines:
            k = re.sub(r'\[(\w[\w-]*)\] [^:]*?: ', r'[\1] ', l, count=1)
            if k in seen: seen[k][1] += 1
            else: seen[k] = [l, 1]; out.append(k)
        return [seen[k][0] + (' (x%d)' % seen[k][1] if seen[k][1] > 1 else '') for k in out]
    errors, warns = collapse(errors), collapse(warns)
    for e in errors: print('  ERROR  ' + e)
    for w in warns[:80]: print('  warn   ' + w)
    if len(warns) > 80: print('  ... %d more warnings in the JSON' % (len(warns) - 80))
    print('  probe: %d errors, %d warnings' % (len(errors), len(warns)))
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
