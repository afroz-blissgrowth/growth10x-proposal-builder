#!/usr/bin/env python3
"""Make a light (for dark ground) or dark (for light ground) variant of an SVG logo. Python 3 stdlib only.

Usage:
    python3 -I logo_variant.py <logo.svg> <out.svg> --for dark|light [--keep-brand]

--for dark   recolours dark fills and strokes (text, wordmark) to white so the logo reads on the dark deck ground.
--for light  recolours very light fills to ink (#17161D) so a white logo reads on the light ground.
--keep-brand leaves saturated brand colours alone when they still read on the ground (contrast 3 or more: an
             orange mark stays orange, a navy wordmark turns white); without it only near-neutral colours change. Always look at the result (render it on the ground) and show it to the user: an
             official light or inverted logo from the client's site or press kit beats a generated one.
PNG logos cannot be recoloured here; look for an official variant or ask the user.
"""
import re
import sys

HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")


def rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(c):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def sat(c):
    mx, mn = max(c), min(c)
    return 0 if mx == 0 else (mx - mn) / mx


def main():
    if len(sys.argv) < 5 or sys.argv[3] != "--for" or sys.argv[4] not in ("dark", "light"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    src, out, ground = sys.argv[1], sys.argv[2], sys.argv[4]
    keep = "--keep-brand" in sys.argv
    svg = open(src, encoding="utf-8").read()
    changed = []

    GROUND = {"dark": lum((0x17, 0x16, 0x1D)), "light": lum((0xFA, 0xF9, 0xF5))}

    def contrast(c):
        a, g = lum(c), GROUND[ground]
        return (max(a, g) + 0.05) / (min(a, g) + 0.05)

    def fix(m):
        c = rgb(m.group(0))
        brand = sat(c) > 0.35
        # a brand colour is kept only if it still reads on the deck ground (contrast 3 or more):
        # a navy wordmark (ReelFlow #08415A) is saturated but vanishes on the dark ground, so it turns white
        if keep and brand and contrast(c) >= 3:
            return m.group(0)
        if ground == "dark" and (lum(c) < 0.18 or contrast(c) < 3):
            changed.append(m.group(0)); return "#FFFFFF"
        if ground == "light" and (lum(c) > 0.8 or contrast(c) < 1.6):
            changed.append(m.group(0)); return "#17161D"
        return m.group(0)

    svg = HEX.sub(fix, svg)
    if ground == "dark" and not re.search(r'fill=|fill:', svg):
        svg = svg.replace("<svg", '<svg fill="#FFFFFF"', 1)   # unfilled paths default to black
        changed.append("default fill")
    open(out, "w", encoding="utf-8").write(svg)
    print("wrote %s, recoloured %d values (%s)" % (out, len(changed), ", ".join(sorted(set(changed)))[:200]))


if __name__ == "__main__":
    main()
