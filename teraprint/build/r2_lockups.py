import re
from geo import *
from lib import ASSISTANT_700, PLAYFAIR, fmt
from r2 import centre, diamond

def word(font, text, size, tracking, x, baseline):
    gl = glyph_polys(font, text, size, tracking); out = []; cx = x
    for g, adv in gl:
        out.append(affinity.translate(g, cx, baseline)); cx += adv
    return unary_union(out), cx - x - tracking * size

def load(name):
    d = re.search(r' d="([^"]+)"', open(f"../concepts/{name}.svg").read()).group(1)
    return d

def wordmark_block(x0, cy, rules=True):
    """TERAPRINT (Playfair) over a ruled STUDIO line (Assistant), left aligned at x0, centred on cy."""
    t1, w1 = word(PLAYFAIR, "TERAPRINT", 84, 0.05, x0, cy + 6)
    # STUDIO centred under TERAPRINT between two rules ending in diamonds
    t2, w2 = word(ASSISTANT_700, "STUDIO", 30, 0.55, 0, 0)
    sx = x0 + (w1 - w2) / 2
    t2 = affinity.translate(t2, sx, cy + 52)
    parts = [t1, t2]
    if rules:
        y = cy + 41
        parts += [box(x0 + 4, y - 1.6, sx - 22, y + 1.6), box(sx + w2 + 22, y - 1.6, x0 + w1 - 4, y + 1.6),
                  diamond(x0 + 4, y, 5), diamond(x0 + w1 - 4, y, 5)]
    return unary_union(parts), w1

def horizontal(sym_name, out, gap=40):
    sym = poly_from_svg(sym_name)
    wm, w = wordmark_block(256 + gap, 128 - 10)
    save(f"../concepts/{out}.svg", unary_union([sym, wm]), w=256 + gap + w + 8, h=256)

def poly_from_svg(name):
    d = load(name)
    # polylines only (M/L/Z) as written by geo.save
    rings = [re.findall(r"(-?\d+\.?\d*) (-?\d+\.?\d*)", s) for s in d.split("Z") if s.strip()]
    g = Polygon()
    for r in rings:
        p = Polygon([(float(a), float(b)) for a, b in r]).buffer(0)
        g = g.symmetric_difference(p)
    return g

if __name__ == "__main__":
    horizontal("r2-a-piece", "r2-a-lockup")
    horizontal("r2-b-seal", "r2-b-lockup")
    horizontal("r2-c-board", "r2-c-lockup")
