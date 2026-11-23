#!/usr/bin/env python3
"""Lint, render and probe a Growth10x plan page with headless Chromium. Python 3 stdlib only (macOS sips
for slicing; without sips you get the full-length PNGs only).

Usage:
  python3 render_page.py PAGE.html --out QA_DIR [--mode internal|client] [--themes dark,light]
                         [--mobile dark] [--widths 1440] [--forbid "Name One,Name Two"]
                         [--slice 1500] [--profile-dir DIR] [--label founder-brand]

What one pass does:
  1. Copy lint on the HTML source (dashes, banned words, placeholders, Illustrative labels, prices and
     ex VAT, internal blocks in a client file, forbidden names, emoji).
  2. For each theme and width: a QA copy of the page in "still" mode (final states, no motion) with
     scripts/probe.js injected; Chrome --dump-dom returns the probe's JSON (page height, overflow,
     clipped text, contrast in that theme, broken images, fonts).
  3. A full-length screenshot at that width (chunked when taller than 16,000px), then review slices
     with sips, so every part of the page can be looked at with the Read tool.
Writes QA_DIR/report.json and QA_DIR/report.md, prints a summary, exits 1 if any error was found.

Chrome safety (standing rule): every launch uses its own --user-data-dir (a fresh temp folder unless
--profile-dir is given), plus --no-first-run --no-default-browser-check --disable-extensions. This script
never kills, quits or signals any Chrome process. A launch that times out is reported and left alone.
"""
import argparse, html as htmlmod, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, 'probe.js')
MAX_SHOT = 16000


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


def chrome(args, profile, timeout=150):
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
           '--no-default-browser-check', '--disable-extensions', '--mute-audio',
           '--user-data-dir=' + profile, '--force-device-scale-factor=1'] + args
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        # never kill Chrome: report and move on
        return None
    return out.decode('utf-8', 'replace')


# ------------------------------------------------------------------ copy lint
BANNED_ERR = [r'\bagency\b', r'\bagencies\b', r'\bkick-?off\b', r'\brecommended\b', r'quick chat', r'just checking in']
BANNED_WARN = [r'\brevolutionary\b', r'game-changing', r'\bsupercharge', r'\bunlock', r'\bleverage\b', r'\bseamless',
               r'\bcutting-edge\b', r'\bsynerg']
EMOJI = re.compile('[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]')


def visible_text(src):
    s = re.sub(r'<(script|style)\b.*?</\1>', ' ', src, flags=re.S | re.I)
    s = re.sub(r'<!--.*?-->', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', htmlmod.unescape(s))


def lint(src, mode, forbid):
    errs, warns = [], []
    def e(rule, detail): errs.append({'rule': rule, 'where': 'source', 'detail': detail})
    def w(rule, detail): warns.append({'rule': rule, 'where': 'source', 'detail': detail})
    for ch, name in (('\u2014', 'em dash'), ('\u2013', 'en dash')):
        for m in re.finditer(ch, src):
            line = src.count('\n', 0, m.start()) + 1
            e('dash', '%s on line %d: ...%s...' % (name, line, src[max(0, m.start() - 30):m.start() + 30].replace('\n', ' ')))
    for ent in ('&mdash;', '&ndash;', '&#8212;', '&#8211;', '&#x2014;', '&#x2013;'):
        if ent in src:
            e('dash', 'dash entity %s in the source' % ent)
    text = visible_text(src)
    low = text.lower()
    for pat in BANNED_ERR:
        for m in re.finditer(pat, low):
            e('banned-word', '"%s" in: ...%s...' % (m.group(0), text[max(0, m.start() - 40):m.end() + 40]))
    for pat in BANNED_WARN:
        for m in re.finditer(pat, low):
            w('hype-word', '"%s" in: ...%s...' % (m.group(0), text[max(0, m.start() - 40):m.end() + 40]))
    for pat, what in ((r'\{\{[^}]*\}\}', 'template token'), (r'\[\[[^\]]*\]\]', 'placeholder'), (r'\bTODO\b', 'TODO'),
                      (r'\bTBC\b', 'TBC'), (r'lorem ipsum', 'lorem ipsum'), (r'YYYY-MM-DD', 'date placeholder')):
        for m in re.finditer(pat, src if what == 'template token' else text, flags=re.I):
            (e if mode == 'client' or what == 'template token' else w)('placeholder', '%s left in: %s' % (what, m.group(0)))
    if EMOJI.search(text):
        e('emoji', 'emoji in visible text')
    for m in re.finditer(r'<[a-z]+[^>]*class="[^"]*\bmock\b[^"]*"[^>]*>', src):
        if 'Illustrative' not in src[m.end():m.end() + 600]:
            e('illustrative', 'a .mock block has no "Illustrative" label near its start (line %d)' % (src.count('\n', 0, m.start()) + 1))
    if re.search(r'[£$€]\s?\d', text):
        if 'ex VAT' not in text:
            e('prices', 'prices shown but "ex VAT" appears nowhere')
        w('prices', 'prices are on the page: only if the user said prices are shown, and only from the offer catalogue')
    if re.search(r'href="#"', src):
        (e if mode == 'client' else w)('dead-link', 'placeholder link href="#"')
    for name in forbid:
        if name and re.search(r'\b' + re.escape(name) + r'\b', text, flags=re.I):
            e('forbidden-name', '"%s" appears on the page' % name)
    if mode == 'client':
        if '<!-- INT' in src or re.search(r'class="[^"]*\bint\b', src):
            e('internal-block', 'internal blocks still in the client file: run new_page.py --strip-internal')
        for pat, what in ((r'\bCheck:', '"Check:" marker'), (r'\bunverified\b', '"unverified"'), (r'\binternal\b', '"internal"'),
                          (r'research/', 'a research file path')):
            if re.search(pat, text, flags=re.I):
                e('internal-text', what + ' in client copy')
        if 'id="method"' not in src:
            w('method', 'no method section: the client version keeps a short method note')
    else:
        if 'id="sources"' not in src:
            w('sources', 'internal draft has no sources table (id="sources")')
    title = re.search(r'<title>(.*?)</title>', src, flags=re.S)
    if not title or not title.group(1).strip():
        e('title', 'page has no <title>')
    elif not 2 <= len(title.group(1).split()) <= 5:
        w('title', 'title should be a short name of 2 to 4 words: "%s"' % title.group(1).strip())
    return errs, warns


# ------------------------------------------------------------------ render
def qa_copy(src, theme, qy, path):
    head = ('<script>document.documentElement.classList.add("still");document.documentElement.setAttribute("data-qa","1");'
            'document.documentElement.setAttribute("data-theme",%s);%s</script>' % (
                json.dumps(theme), 'document.documentElement.setAttribute("data-qy","%d");' % qy if qy else ''))
    src = re.sub(r'(<head[^>]*>)', lambda m: m.group(1) + head, src, count=1)
    probe = '<script>' + open(PROBE, encoding='utf-8').read() + '</script>'
    src = src.replace('</body>', probe + '</body>', 1) if '</body>' in src else src + probe
    open(path, 'w', encoding='utf-8').write(src)
    return 'file://' + path


def probe(src, theme, width, tmp, profile):
    url = qa_copy(src, theme, 0, os.path.join(tmp, 'qa-%s-%d.html' % (theme, width)))
    dom = chrome(['--window-size=%d,900' % width, '--virtual-time-budget=7000', '--dump-dom', url], profile)
    if dom is None:
        return {'errors': [{'rule': 'chrome-timeout', 'where': 'page', 'detail': 'probe timed out'}], 'warnings': [], 'height': 0}
    found = re.findall(r'<pre id="qa-out"[^>]*>([^<]*)</pre>', dom)
    m = found[-1] if found else None
    if not m:
        return {'errors': [{'rule': 'probe-missing', 'where': 'page', 'detail': 'probe did not report (script error?)'}], 'warnings': [], 'height': 0}
    return json.loads(htmlmod.unescape(m))


def sips_slices(png, width, height, slice_h, prefix):
    out = []
    if not shutil.which('sips'):
        return [png]
    y, k = 0, 1
    while y < height:
        h = min(slice_h, height - y)
        dst = '%s-%02d.png' % (prefix, k)
        r = subprocess.run(['sips', '-c', str(h), str(width), '--cropOffset', str(y), '0', png, '--out', dst],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.returncode == 0:
            out.append(dst)
        y += slice_h; k += 1
    return out


def shoot(src, theme, width, height, out_dir, tmp, profile, slice_h, label):
    base = os.path.join(out_dir, '%s-%s-%d' % (label, theme, width))
    shots, y, part = [], 0, 1
    height = max(height, 900)
    while y < height:
        h = min(MAX_SHOT, height - y)
        url = qa_copy(src, theme, y, os.path.join(tmp, 'shot-%s-%d-%d.html' % (theme, width, part)))
        png = '%s-full%s.png' % (base, '' if height <= MAX_SHOT else '-part%d' % part)
        r = chrome(['--window-size=%d,%d' % (width, h), '--virtual-time-budget=7000', '--screenshot=' + png, url], profile)
        if r is not None and os.path.exists(png):
            shots.append((png, h))
        y += MAX_SHOT; part += 1
    slices, n = [], 0
    for png, h in shots:
        n += 1
        slices += sips_slices(png, width, h, slice_h, '%s-p%d' % (base, n) if len(shots) > 1 else base)
    return [s for s, _ in shots], slices


def main():
    global CHROME
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('page'); ap.add_argument('--out', required=True)
    ap.add_argument('--mode', choices=['internal', 'client'], default='internal')
    ap.add_argument('--themes', default='dark,light', help='themes to render at desktop width')
    ap.add_argument('--widths', default='1440'); ap.add_argument('--mobile', default='',
                    help='theme to render at 390px as well (for example dark); empty to skip')
    ap.add_argument('--forbid', default='', help='comma-separated names that must not appear')
    ap.add_argument('--slice', type=int, default=1500); ap.add_argument('--profile-dir', default='')
    ap.add_argument('--label', default=''); ap.add_argument('--lint-only', action='store_true')
    a = ap.parse_args()

    page = os.path.abspath(a.page)
    src = open(page, encoding='utf-8').read()
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    label = a.label or os.path.splitext(os.path.basename(page))[0]
    forbid = [x.strip() for x in a.forbid.split(',') if x.strip()]
    errs, warns = lint(src, a.mode, forbid)
    report = {'page': page, 'mode': a.mode, 'lint': {'errors': errs, 'warnings': warns}, 'renders': []}

    if not a.lint_only:
        CHROME = find_chrome()
        tmp = tempfile.mkdtemp(prefix='g10x-plan-qa-')
        profile = a.profile_dir or tempfile.mkdtemp(prefix='g10x-chrome-profile-')
        os.makedirs(profile, exist_ok=True)
        jobs = [(t.strip(), int(w)) for t in a.themes.split(',') if t.strip() for w in a.widths.split(',')]
        if a.mobile:
            jobs.append((a.mobile, 390))
        for theme, width in jobs:
            res = probe(src, theme, width, tmp, profile)
            full, slices = shoot(src, theme, width, int(res.get('height') or 0), out, tmp, profile,
                                 a.slice if width > 600 else 1800, label)
            report['renders'].append({'theme': theme, 'width': width, 'height': res.get('height'),
                                      'errors': res.get('errors', []), 'warnings': res.get('warnings', []),
                                      'info': res.get('info', {}), 'full': full, 'slices': slices})
        shutil.rmtree(tmp, ignore_errors=True)

    n_err = len(errs) + sum(len(r['errors']) for r in report['renders'])
    n_warn = len(warns) + sum(len(r['warnings']) for r in report['renders'])
    report['summary'] = {'errors': n_err, 'warnings': n_warn}
    json.dump(report, open(os.path.join(out, 'report.json'), 'w'), indent=1)

    lines = ['# Render report: %s' % os.path.basename(page), '', 'Mode: %s. Errors: %d. Warnings: %d.' % (a.mode, n_err, n_warn), '']
    def block(title, items):
        if items:
            lines.append('## ' + title)
            for i in items:
                lines.append('- [%s] %s: %s%s' % (i.get('rule'), i.get('where'), i.get('detail'), (' | "' + i['text'] + '"') if i.get('text') else ''))
            lines.append('')
    block('Lint errors', errs); block('Lint warnings', warns)
    for r in report['renders']:
        lines.append('## Render %s %dpx (page height %spx)' % (r['theme'], r['width'], r['height']))
        lines.append('Slices: ' + ', '.join(os.path.basename(s) for s in r['slices']))
        lines.append('')
        block('Errors, %s %d' % (r['theme'], r['width']), r['errors']); block('Warnings, %s %d' % (r['theme'], r['width']), r['warnings'])
    open(os.path.join(out, 'report.md'), 'w').write('\n'.join(lines))
    print('\n'.join(lines))
    sys.exit(1 if n_err else 0)


CHROME = None
if __name__ == '__main__':
    main()
