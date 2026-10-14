import math
from geo import *
from knight2 import sculpted_head
from lib import ASSISTANT_700, PLAYFAIR

def rr(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=12)

def piece(head_scale=0.80):
    """Full Staunton knight: sculpted head, collar ring, flared foot and beaded plinth."""
    hd = sculpted_head()
    hx, hy = 0, 0
    head = affinity.affine_transform(hd, [head_scale, 0, 0, head_scale, hx, hy])
    nb = 236 * head_scale - 2                     # neck bottom
    head = head.difference(box(0, nb, 256, 400))
    sl = head.intersection(box(0, nb - 3, 256, nb)).bounds
    cx = (sl[0] + sl[2]) / 2; nw = sl[2] - sl[0]
    g = 4
    collar = rr(cx - nw/2 - 10, nb + g, cx + nw/2 + 10, nb + g + 12, 6)
    t = nb + g + 12 + g
    fw, bw = nw / 2 - 2, nw / 2 + 34
    foot = poly(f"M {cx-fw} {t} L {cx+fw} {t} C {cx+fw+2} {t+12} {cx+bw-18} {t+20} {cx+bw} {t+22} "
                f"L {cx-bw} {t+22} C {cx-bw+18} {t+20} {cx-fw-2} {t+12} {cx-fw} {t} Z")
    p0 = t + 22 + g
    plinth = rr(cx - bw - 6, p0, cx + bw + 6, p0 + 14, 7)
    beads = [circle(cx + 14 * (i - 5), p0 + 7, 3.1) for i in range(11)]
    return unary_union([head, collar, foot, plinth.difference(unary_union(beads))])

def centre(g, w=256, h=256, pad=10):
    x0, y0, x1, y1 = g.bounds
    s = min((w - 2*pad) / (x1 - x0), (h - 2*pad) / (y1 - y0))
    g = affinity.scale(g, s, s, origin=(x0, y0))
    x0, y0, x1, y1 = g.bounds
    return affinity.translate(g, (w - (x1 - x0)) / 2 - x0, (h - (y1 - y0)) / 2 - y0)


def ring(cx, cy, r_out, r_in):
    return circle(cx, cy, r_out).difference(circle(cx, cy, r_in))

def diamond(cx, cy, r):
    return Polygon([(cx, cy - r), (cx + r * 0.7, cy), (cx, cy + r), (cx - r * 0.7, cy)])

def seal():
    C = 128
    g = [ring(C, C, 124, 119), ring(C, C, 88, 85)]
    g.append(text_on_arc(ASSISTANT_700, "TERAPRINT STUDIO", 19, C, C, 96, -90, 0.32))
    g.append(text_on_arc(ASSISTANT_700, "CHAQUE CAMP A SON HISTOIRE", 12.5, C, C, 106.5, 90, 0.22, bottom=True))
    g += [diamond(C - 102, C - 2, 5), diamond(C + 102, C - 2, 5)]
    # inner counterchanged disc with the sculpted head
    hd = sculpted_head()
    s = 0.62
    head = affinity.affine_transform(hd, [s, 0, 0, s, C - 128 * s - 4, C - 124 * s + 12])
    disc = circle(C, C, 80)
    left = disc.intersection(box(0, 0, C, 256))
    head = head.intersection(disc)
    inner = left.symmetric_difference(head)
    g.append(inner)
    return unary_union(g)


def octagon(cx, cy, r):
    return Polygon([(cx + r * math.cos(math.radians(22.5 + 45 * k)), cy + r * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)])

def board():
    """Octagon (8 = the board) with a double rule; the full piece stands on a checkerboard in perspective."""
    C = 128
    frame = octagon(C, C, 126).difference(octagon(C, C, 120))
    frame = frame.union(octagon(C, C, 115).difference(octagon(C, C, 111.5)))
    vp = (C, -120)
    rows = [(180, 192), (194.5, 208), (210.5, 226)]
    yb = rows[-1][1]
    def xat(xb, y):
        return vp[0] + (xb - vp[0]) * (y - vp[1]) / (yb - vp[1])
    cols = [C + 24 * (k - 0.5) for k in range(-5, 7)]
    tiles = []
    for r, (ya, yb2) in enumerate(rows):
        for k in range(len(cols) - 1):
            if (k + r) % 2 == 0:
                xa, xb = cols[k], cols[k + 1]
                tiles.append(Polygon([(xat(xa, ya), ya), (xat(xb, ya), ya), (xat(xb, yb2), yb2), (xat(xa, yb2), yb2)]))
    floor = unary_union(tiles).intersection(octagon(C, C, 106))
    p = centre(piece(), 256, 256, 0)
    p = affinity.scale(p, 0.60, 0.60, origin=(128, 256))
    p = affinity.translate(p, 0, 200 - 256)
    floor = floor.difference(p.buffer(4))
    return unary_union([frame, floor, p])

if __name__ == "__main__":
    save("../concepts/r2-a-piece.svg", centre(piece()))
    save("../concepts/r2-b-seal.svg", seal())
    save("../concepts/r2-c-board.svg", board())
