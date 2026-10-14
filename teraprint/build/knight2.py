"""Round 2 — the sculpted knight (detailed head + Staunton collar/base)."""
import math
from geo import *
from geo import _bez

HEAD = ("M 150 14 C 144 26 140 38 140 50 C 134 52 128 54 122 58 C 104 70 82 88 64 108 "
        "C 52 120 42 134 38 146 C 34 158 40 170 52 172 C 62 174 72 170 80 166 "
        "C 92 162 104 160 114 162 C 128 164 132 180 122 192 C 108 208 100 220 98 236 "
        "L 206 236 C 216 200 218 140 196 92 C 186 70 176 56 166 48 "
        "C 168 38 168 28 166 22 C 162 28 158 34 156 40 C 154 30 152 22 150 14 Z")

def back_edge(n=400):
    a = [(166, 48)] + _bez([(166, 48), (176, 56), (186, 70), (196, 92)], n // 4)
    b = _bez([(196, 92), (218, 140), (216, 200), (206, 236)], n)
    pts = a + b
    # arc-length param
    L = [0]
    for p, q in zip(pts, pts[1:]):
        L.append(L[-1] + math.dist(p, q))
    return pts, L

def at(pts, L, s):
    for k in range(1, len(L)):
        if L[k] >= s:
            p, q = pts[k-1], pts[k]; t = (s - L[k-1]) / ((L[k] - L[k-1]) or 1)
            x, y = p[0] + (q[0]-p[0])*t, p[1] + (q[1]-p[1])*t
            tx, ty = q[0]-p[0], q[1]-p[1]; ln = math.hypot(tx, ty) or 1
            tx, ty = tx/ln, ty/ln
            return (x, y), (tx, ty), (-ty, tx)   # tangent (downward), normal: (-ty,tx) points inward? checked below
    return pts[-1], (0, 1), (-1, 0)

def sculpted_head(n_locks=7, tuft=9, cut_w=6.5):
    h = poly(HEAD)
    pts, L = back_edge()
    total = L[-1] * 0.92
    adds, cuts = [], []
    marks = [total * (k / n_locks) ** 0.9 for k in range(n_locks + 1)]
    for k in range(n_locks):
        (p, t, nrm) = at(pts, L, marks[k]); (q, _, _) = at(pts, L, marks[k + 1])
        # outward normal = pointing right of the downward tangent (x increases)
        out = (t[1] * -1, t[0]) if (t[1] * -1) > 0 else (t[1], -t[0])
        out = (-out[0], -out[1]) if out[0] < 0 else out
        inn = (-out[0], -out[1])
        seg = math.dist(p, q)
        m1 = (p[0] + t[0]*seg*0.35 + out[0]*tuft, p[1] + t[1]*seg*0.35 + out[1]*tuft)
        m2 = (p[0] + t[0]*seg*0.85 + out[0]*tuft*0.9, p[1] + t[1]*seg*0.85 + out[1]*tuft*0.9)
        end = (q[0] + t[0]*seg*0.15 + out[0]*tuft*0.6, q[1] + t[1]*seg*0.15 + out[1]*tuft*0.6)
        # tuft: a lock of hair curling outward past the neck line, ending in a point below
        adds.append(stroke([(p[0]+inn[0]*6, p[1]+inn[1]*6), m1, m2, end], 12, 0.5, 14))
        # cut separating this lock from the previous one: starts at the valley, sweeps down-inward
        depth = 30 + 6 * math.sin(k / n_locks * math.pi)
        c_end = (p[0] + inn[0]*depth + t[0]*seg*1.0, p[1] + inn[1]*depth + t[1]*seg*1.0)
        c1 = (p[0] + out[0]*4 + t[0]*2, p[1] + out[1]*4 + t[1]*2)
        c2 = (p[0] + inn[0]*depth*0.5 + t[0]*seg*0.25, p[1] + inn[1]*depth*0.5 + t[1]*seg*0.25)
        c3 = (p[0] + inn[0]*depth*0.9 + t[0]*seg*0.6, p[1] + inn[1]*depth*0.9 + t[1]*seg*0.6)
        if k > 0:
            cuts.append(stroke([c1, c2, c3, c_end], cut_w, 0.4, cut_w * 0.9))
    g = unary_union([h] + adds)
    cuts += [
        poly("M 104 100 C 110 91 122 89 131 93 C 125 102 113 105 104 100 Z"),        # eye
        stroke([(98, 88), (108, 79), (124, 76), (140, 82)], 1, 1, 6),               # brow
        stroke([(49, 143), (55, 137), (63, 141), (60, 152)], 2, 1, 7),              # nostril
        stroke([(32, 160), (44, 159), (54, 160), (64, 158)], 6, 0.5, 5),            # mouth
        stroke([(92, 118), (110, 124), (124, 140), (124, 158)], 1, 1, 6),           # cheek
        stroke([(150, 22), (148, 30), (146, 38), (146, 48)], 1, 2, 5),              # inner ear
        stroke([(156, 46), (146, 58), (136, 64), (124, 68)], 7, 0.5, 6),            # forelock
    ]
    for c in cuts:
        g = g.difference(c)
    return g.buffer(0)

if __name__ == "__main__":
    save("../concepts/r2-head-v2.svg", sculpted_head())
