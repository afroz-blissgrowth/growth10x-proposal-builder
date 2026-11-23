#!/usr/bin/env python3
"""Contact sheet: a labelled grid of screenshots in one PNG, so a whole pass can be reviewed at a glance.

Usage: python3 contact_sheet.py <out.png> <img1.png> [<img2.png> ...] [--cols 4] [--title TEXT]
Uses Pillow when it is installed; otherwise writes an HTML grid and screenshots it with headless Chromium.
"""
import argparse, html, os, shutil, subprocess, sys, tempfile

THUMB_W, THUMB_H, PAD, HEAD = 480, 270, 16, 30

def make(items, out_png, title='', cols=4, chrome=None):
    """items: list of (png_path, label). Returns out_png."""
    items = [(p, l) for p, l in items if p and os.path.exists(p)]
    if not items: return None
    try:
        from PIL import Image, ImageDraw  # noqa: F401
        return _pil(items, out_png, title, cols)
    except ImportError:
        return _chrome(items, out_png, title, cols, chrome)

def _pil(items, out_png, title, cols):
    from PIL import Image, ImageDraw
    rows = (len(items) + cols - 1) // cols
    W = cols * (THUMB_W + PAD) + PAD
    H = 50 + rows * (THUMB_H + HEAD + PAD) + PAD
    sheet = Image.new('RGB', (W, H), (40, 40, 46))
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 16), title, fill=(240, 240, 240))
    for i, (p, label) in enumerate(items):
        im = Image.open(p).convert('RGB'); im.thumbnail((THUMB_W, THUMB_H))
        x = PAD + (i % cols) * (THUMB_W + PAD); y = 50 + (i // cols) * (THUMB_H + HEAD + PAD)
        d.text((x, y + 6), label, fill=(220, 220, 220))
        sheet.paste(im, (x, y + HEAD))
    sheet.save(out_png)
    return out_png

def _find_chrome():
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

def _chrome(items, out_png, title, cols, chrome):
    chrome = chrome or _find_chrome()
    rows = (len(items) + cols - 1) // cols
    W = cols * (THUMB_W + PAD) + PAD
    H = 60 + rows * (THUMB_H + HEAD + PAD) + PAD
    cells = ''.join('<figure><figcaption>%s</figcaption><img src="file://%s"></figure>' % (html.escape(l), html.escape(os.path.abspath(p)))
                    for p, l in items)
    page = ('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#28282E;color:#eee;font:14px/1.2 -apple-system,Helvetica,Arial,sans-serif}'
            'h1{font-size:16px;margin:0;padding:20px %dpx 14px}main{display:grid;grid-template-columns:repeat(%d,%dpx);gap:%dpx;padding:0 %dpx}'
            'figure{margin:0}figcaption{height:%dpx;line-height:%dpx;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
            'img{display:block;width:%dpx;height:%dpx;object-fit:contain;background:#000;outline:1px solid #444}</style>'
            '<h1>%s</h1><main>%s</main>') % (PAD, cols, THUMB_W, PAD, PAD, HEAD, HEAD, THUMB_W, THUMB_H, html.escape(title), cells)
    tmp = tempfile.mkdtemp(prefix='g10x-sheet-')
    try:
        hp = os.path.join(tmp, 'sheet.html'); open(hp, 'w', encoding='utf-8').write(page)
        # isolated throwaway profile; never touches or closes the user's own Chrome
        subprocess.run([chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check',
                        '--disable-extensions', '--allow-file-access-from-files',
                        '--user-data-dir=' + os.path.join(tmp, 'ud'), '--force-device-scale-factor=1', '--window-size=%d,%d' % (W, H),
                        '--virtual-time-budget=3000', '--screenshot=' + os.path.abspath(out_png), 'file://' + hp],
                       capture_output=True, timeout=120)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out_png if os.path.exists(out_png) else None

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('out'); ap.add_argument('imgs', nargs='+')
    ap.add_argument('--cols', type=int, default=4); ap.add_argument('--title', default='')
    a = ap.parse_args()
    p = make([(i, os.path.splitext(os.path.basename(i))[0]) for i in a.imgs], a.out, a.title, a.cols)
    print(p or 'no images')
