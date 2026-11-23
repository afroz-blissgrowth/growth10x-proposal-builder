#!/usr/bin/env python3
"""Extract likely brand colours and fonts from a website. Python 3 stdlib only.

Usage:
    python3 -I brand_colors.py <url> [outdir]

Fetches the homepage, its inline styles, every linked stylesheet (plus one level
of @import), and writes them to outdir (a fresh temp dir by default) so the raw
files can be checked. Prints a JSON summary to stdout:
  theme_color_meta, css_brand_tokens (resolved var() values), top_brand_colours,
  top_neutrals, fonts (font-family counts), font_face_families, google_fonts.

Also prints accent_pick (the site's most-used brand colour, weighted by how the
CSS uses it, with runners-up) and logo (candidates found on the page, downloaded to
<outdir>/logo/, SVG first, with pixel sizes and a guess of which is the light or
inverted variant for dark ground).

How to read it: the accent is the colour the SITE uses most for buttons, links,
highlights and fills (accent_pick), not the first colour in the logo file: a logo
can carry a secondary colour (an orange mark on a teal site). A named brand token
that agrees with accent_pick settles it. Show the pick, the runner-up and the
logo colours to the user and let them confirm. JS-rendered sites with no CSS in
the HTML return little; fall back to a crawler or brand guidelines.
"""
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from collections import Counter

UA = {"User-Agent": "Mozilla/5.0 (Macintosh) brand-colors/1.1"}
MAX_STYLESHEETS = 25
GENERIC_FONTS = {"inherit", "initial", "unset", "sans-serif", "serif", "monospace",
                 "system-ui", "-apple-system", "blinkmacsystemfont", "cursive"}


def get(url, limit=3_000_000):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read(limit).decode("utf-8", "replace")
    except Exception as e:  # network, SSL, 403: report and carry on
        print(f"skip {url}: {e}", file=sys.stderr)
        return ""


def save(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def norm_hex(h):
    h = h.lower()
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    return "#" + h[:6]  # drop alpha


def rgb_to_hex(parts):
    try:
        vals = [max(0, min(255, int(float(x)))) for x in parts[:3]]
        return "#%02x%02x%02x" % tuple(vals)
    except ValueError:
        return None


def is_neutral(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return max(r, g, b) - min(r, g, b) < 18  # greys, black, white


HEX_RE = re.compile(r"#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b")
RGB_RE = re.compile(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)")
DECL_RE = re.compile(r"([\w-]+)\s*:\s*([^;{}]+)")


def colours_in(value):
    out = [norm_hex(h) for h in HEX_RE.findall(value)]
    for m in RGB_RE.findall(value):
        h = rgb_to_hex(m)
        if h:
            out.append(h)
    return out


# properties that carry the brand on a page weigh more than borders or shadows
WEIGHT = {"background": 3, "background-color": 3, "color": 2, "fill": 2, "stroke": 1, "border-color": 1,
          "border": 1, "outline-color": 1, "box-shadow": 0.3, "text-decoration-color": 1}


def get_bytes(url, limit=5_000_000):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read(limit), r.headers.get("Content-Type", "")
    except Exception as e:
        print(f"skip {url}: {e}", file=sys.stderr)
        return b"", ""


def png_size(b):
    if b[:8] == b"\x89PNG\r\n\x1a\n" and len(b) > 24:
        return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")
    return None


def find_logos(html, url, out):
    """Logo candidates: <img> or inline <svg> marked logo, then icons. Downloads to out/logo/."""
    cands = []
    for tag in re.findall(r"<img\b[^>]*>", html, re.I):
        src = re.search(r'\ssrc=["\']([^"\']+)', tag) or re.search(r'data-src=["\']([^"\']+)', tag)
        if src and re.search(r"logo|brand|wordmark", tag, re.I):
            cands.append(("img", urllib.parse.urljoin(url, src.group(1)), tag))
    for m in re.finditer(r"<(a|div|span|header)[^>]*(?:class|id|aria-label)=[\"'][^\"']*logo[^\"']*[\"'][^>]*>\s*(<svg\b.*?</svg>)", html, re.I | re.S):
        cands.append(("inline-svg", None, m.group(2)))
    for m in re.finditer(r"<svg\b[^>]*(?:class|id|aria-label)=[\"'][^\"']*logo[^\"']*[\"'][^>]*>.*?</svg>", html, re.I | re.S):
        cands.append(("inline-svg", None, m.group(0)))
    for m in re.finditer(r'<link[^>]+rel=["\'](?:apple-touch-icon|icon|mask-icon)["\'][^>]*href=["\']([^"\']+)', html, re.I):
        cands.append(("icon", urllib.parse.urljoin(url, m.group(1)), m.group(0)))
    d = os.path.join(out, "logo"); os.makedirs(d, exist_ok=True)
    res, seen = [], set()
    for i, (kind, src, tag) in enumerate(cands[:12]):
        key = src or tag[:200]
        if key in seen: continue
        seen.add(key)
        if kind == "inline-svg":
            data, ctype, ext = tag.encode(), "image/svg+xml", ".svg"
        else:
            data, ctype = get_bytes(src)
            if not data: continue
            ext = ".svg" if (b"<svg" in data[:2000] or src.lower().split("?")[0].endswith(".svg")) else os.path.splitext(src.split("?")[0])[1][:5] or ".bin"
        fn = os.path.join(d, "logo-%02d-%s%s" % (i + 1, kind, ext))
        with open(fn, "wb") as f: f.write(data)
        size = png_size(data)
        light = bool(re.search(r"white|light|invert|negative|reverse|dark-bg|on-dark", (src or "") + tag, re.I))
        cols = sorted(set(colours_in(data.decode("utf-8", "replace")))) if ext == ".svg" else []
        res.append({"file": fn, "kind": kind, "src": src, "format": ext.strip("."), "px": size,
                    "light_variant_guess": light, "colours_in_file": cols[:6]})
    name = urllib.parse.urlparse(url).netloc.lower().replace("www.", "").split(".")[0]
    for r in res:
        r["own"] = name in ((r["src"] or "") + r["file"]).lower() or r["kind"] == "inline-svg"
    def rank(r):   # the company's own mark first (customer logos on the page also say "logo"), SVG first, then size
        return (not r["own"], r["kind"] == "icon", r["format"] != "svg", -((r["px"] or (0, 0))[0]))
    return sorted(res, key=rank)


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    url = sys.argv[1]
    if not re.match(r"https?://", url):
        url = "https://" + url
    out = sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp(prefix="brand_")
    os.makedirs(out, exist_ok=True)

    html = get(url)
    save(os.path.join(out, "index.html"), html)
    if not html:
        print(json.dumps({"url": url, "error": "homepage could not be fetched"}, indent=2))
        sys.exit(1)

    links = re.findall(r'<link[^>]+href=["\']([^"\']+\.css[^"\']*)', html, re.I)
    links += re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)', html, re.I)
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I))
    css += "\n" + "\n".join(re.findall(r'style=["\']([^"\']+)', html))

    seen = 0
    for href in dict.fromkeys(links):
        if "fonts.googleapis" in href or seen >= MAX_STYLESHEETS:
            continue
        sheet_url = urllib.parse.urljoin(url, href)
        body = get(sheet_url)
        save(os.path.join(out, f"style{seen}.css"), body)
        seen += 1
        css += "\n" + body
        for imp in re.findall(r'@import\s+(?:url\()?["\']?([^"\')\s;]+)', body)[:5]:
            if "fonts.googleapis" in imp:
                continue
            sub = get(urllib.parse.urljoin(sheet_url, imp))
            save(os.path.join(out, f"style{seen}_import.css"), sub)
            css += "\n" + sub

    meta = re.findall(r'<meta[^>]+name=["\']theme-color["\'][^>]*content=["\']([^"\']+)', html, re.I)
    meta += re.findall(r'<meta[^>]+name=["\']msapplication-TileColor["\'][^>]*content=["\']([^"\']+)', html, re.I)

    # All custom properties, so var() references in brand tokens can be resolved.
    props = {}
    for name, val in re.findall(r"(--[\w-]+)\s*:\s*([^;}{]+)", css):
        props.setdefault(name, val.strip())

    def resolve(val, depth=0):
        m = re.match(r"var\(\s*(--[\w-]+)", val)
        if m and depth < 5 and m.group(1) in props:
            return resolve(props[m.group(1)], depth + 1)
        return val

    brand_words = re.compile(r"primary|brand|accent|secondary|main", re.I)
    tokens = {n: resolve(v) for n, v in props.items() if brand_words.search(n)}

    # Count colours only inside declaration values, so ID selectors like #add are ignored.
    cols = Counter()
    weighted = Counter()
    for prop, value in DECL_RE.findall(css):
        for c in colours_in(value):
            cols[c] += 1
            weighted[c] += WEIGHT.get(prop.lower(), 0.5)
    for c in colours_in(" ".join(re.findall(r'(?:fill|stroke|stop-color)=["\']([^"\']+)', html))):
        weighted[c] += 0.5   # inline SVG on the page, logo included, counts a little

    brand = [(c, n) for c, n in cols.most_common() if not is_neutral(c)][:8]
    neutrals = [(c, n) for c, n in cols.most_common() if is_neutral(c)][:4]

    fonts = Counter()
    for f in re.findall(r"font-family\s*:\s*([^;}{]+)", css, re.I):
        first = resolve(f.strip()).split(",")[0].strip().strip("'\"")
        if first and not first.startswith("var(") and first.lower() not in GENERIC_FONTS:
            fonts[first] += 1
    face = re.findall(r"@font-face\s*{[^}]*?font-family\s*:\s*['\"]?([^;'\"}]+)", css, re.I)
    gfonts = re.findall(r"fonts\.googleapis\.com/css2?\?family=([^\"'&]+)", html + css)

    def sat(h):
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
        mx, mn = max(r, g, b), min(r, g, b)
        return 0 if mx == 0 else (mx - mn) / mx
    def val(h):
        return max(int(h[i:i + 2], 16) for i in (1, 3, 5)) / 255
    token_vals = [colours_in(v)[0] for v in tokens.values() if colours_in(v)]
    logos = find_logos(html, url, out)
    own = [lg for lg in logos if lg["kind"] != "icon" and lg.get("own")] or [lg for lg in logos if lg["kind"] != "icon"][:1]
    logo_cols = [c for lg in own[:1] for c in lg["colours_in_file"] if not is_neutral(c)]
    # very dark or very pale colours are text and surfaces, not the accent; a site colour that is also in
    # the company's own logo gets a bonus (brand confirmed twice), but logo colours alone never win
    ranked = sorted(((c, round(w * (1.5 if c in logo_cols else 1), 1)) for c, w in weighted.items()
                     if not is_neutral(c) and sat(c) > 0.3 and 0.3 < val(c) and not (val(c) > 0.97 and sat(c) < 0.15)),
                    key=lambda x: -x[1])
    pick = ranked[0][0] if ranked else (token_vals[0] if token_vals else None)
    accent = {"pick": pick, "runners_up": ranked[1:4], "named_tokens_agree": pick in token_vals,
              "logo_colours": logo_cols[:4],
              "note": "Most-used brand colour on the site, weighted by property. If the logo's main colour differs, show both and ask."}

    result = {
        "url": url,
        "accent_pick": accent,
        "logo": logos,
        "files_dir": out,
        "stylesheets_fetched": seen,
        "theme_color_meta": meta,
        "css_brand_tokens": dict(list(tokens.items())[:15]),
        "top_brand_colours": brand,
        "top_neutrals": neutrals,
        "fonts": fonts.most_common(5),
        "font_face_families": sorted(set(x.strip() for x in face))[:10],
        "google_fonts": sorted(set(urllib.parse.unquote_plus(g) for g in gfonts)),
    }
    if logos:
        result["logo_pick"] = logos[0]["file"]   # own mark first; check it is the company's logo, not a customer's
    with open(os.path.join(out, "brand.json"), "w", encoding="utf-8") as f:   # the file proposal-deck reads
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
