import math
from lib import svg, transform, text_path, cap_height, fmt, ASSISTANT, ASSISTANT_700, PLAYFAIR

KNIGHT = ("M 140 20 C 132 32 128 42 127 52 C 122 56 118 60 114 64 C 96 82 70 104 52 124 "
          "C 40 136 36 150 46 160 C 54 168 66 166 76 158 C 88 154 100 152 110 152 "
          "C 122 154 124 166 116 176 C 98 196 84 208 82 226 L 206 226 "
          "C 214 186 212 128 190 86 C 180 66 166 52 152 46 C 148 38 144 28 140 20 Z")
EYE = "M 124 90 C 124 95 120 98 116 98 C 112 98 108 95 108 90 C 108 86 112 83 116 83 C 120 83 124 86 124 90 Z"

def circle(cx, cy, r, ccw=False):
    s = 0 if ccw else 1
    return (f"M {fmt(cx)} {fmt(cy-r)} A {fmt(r)} {fmt(r)} 0 1 {s} {fmt(cx)} {fmt(cy+r)} "
            f"A {fmt(r)} {fmt(r)} 0 1 {s} {fmt(cx)} {fmt(cy-r)} Z")

def sliver(p0, p1, bulge):
    """Tapered brush-stroke shape from p0 to p1, max half-thickness `bulge` (pointed ends)."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    a = (x0 + dx * .3, y0 + dy * .3); b = (x0 + dx * .7, y0 + dy * .7)
    k = bulge * 1.33
    return (f"M {fmt(x0)} {fmt(y0)} C {fmt(a[0]+nx*k)} {fmt(a[1]+ny*k)} {fmt(b[0]+nx*k)} {fmt(b[1]+ny*k)} {fmt(x1)} {fmt(y1)} "
            f"C {fmt(b[0]-nx*k*.5)} {fmt(b[1]-ny*k*.5)} {fmt(a[0]-nx*k*.5)} {fmt(a[1]-ny*k*.5)} {fmt(x0)} {fmt(y0)} Z")

# ---------- A : Pinceau — mane carved by three brush strokes ----------
A = KNIGHT + " " + EYE + " " + " ".join([
    sliver((150, 62), (196, 130), 6),
    sliver((156, 100), (198, 176), 6),
    sliver((160, 142), (196, 214), 5.5),
])

# ---------- B : Deux camps — counterchanged circle ----------
s, tx, ty = 0.74, 128 - 128 * 0.74, 128 - 124 * 0.74
kB = transform(KNIGHT, s, tx=tx, ty=ty) + " " + transform(EYE, s, tx=tx, ty=ty)
half = "M 128 12 A 116 116 0 0 0 128 244 Z"
B_main = half + " " + kB
B_ring = "M 128 12 A 116 116 0 0 1 128 244 L 128 234 A 106 106 0 0 0 128 22 Z"

# ---------- C : La case — knight on a square with double rule, ear breaking out ----------
s, tx, ty = 0.74, 128 - 124 * 0.74, 22
kC = transform(KNIGHT, s, tx=tx, ty=ty)
eC = transform(EYE, s, tx=tx, ty=ty)
def rrect(x0, y0, x1, y1, r, ccw=False):
    if not ccw:
        return (f"M {x0+r} {y0} L {x1-r} {y0} A {r} {r} 0 0 1 {x1} {y0+r} L {x1} {y1-r} A {r} {r} 0 0 1 {x1-r} {y1} "
                f"L {x0+r} {y1} A {r} {r} 0 0 1 {x0} {y1-r} L {x0} {y0+r} A {r} {r} 0 0 1 {x0+r} {y0} Z")
    return (f"M {x0+r} {y0} A {r} {r} 0 0 0 {x0} {y0+r} L {x0} {y1-r} A {r} {r} 0 0 0 {x0+r} {y1} L {x1-r} {y1} "
            f"A {r} {r} 0 0 0 {x1} {y1-r} L {x1} {y0+r} A {r} {r} 0 0 0 {x1-r} {y0} Z")
frame = rrect(20, 40, 236, 236, 6) + " " + rrect(28, 48, 228, 228, 2, ccw=True)
inner = rrect(36, 56, 220, 220, 2) + " " + rrect(42, 62, 214, 214, 1, ccw=True)
# knight sits on inner rule's floor; it is drawn as ivory (hole) inside a solid tile
tile = rrect(48, 68, 208, 208, 1)

def write(name, paths, w=256, h=256):
    open(f"../concepts/{name}.svg", "w").write(svg(paths, w, h, title=f"TeraPrint Studio — {name}"))

write("a-symbol", [transform(A, 1, tx=-3, ty=5)])
write("b-symbol", [B_main, B_ring])


# C: La case — double rule like the box lid; the knight's head breaks through the top of the frame.
from shapely.geometry import Polygon, box
from shapely import affinity
from lib import TOKEN

def flatten(d, n=24):
    toks = TOKEN.findall(d); pts=[]; polys=[]; i=0; cur=None
    while i < len(toks):
        c = toks[i]; i += 1
        if c == "M":
            cur = (float(toks[i]), float(toks[i+1])); i += 2; pts=[cur]
        elif c == "L":
            cur = (float(toks[i]), float(toks[i+1])); i += 2; pts.append(cur)
        elif c == "C":
            p = [cur] + [(float(toks[i+k]), float(toks[i+k+1])) for k in (0,2,4)]; i += 6
            for t in [j/n for j in range(1,n+1)]:
                u=1-t
                pts.append(tuple(u**3*p[0][a]+3*u*u*t*p[1][a]+3*u*t*t*p[2][a]+t**3*p[3][a] for a in (0,1)))
            cur = pts[-1]
        elif c == "Z":
            polys.append(Polygon(pts))
    return polys

def to_d(geom):
    out=[]
    gs = getattr(geom, "geoms", [geom])
    for g in gs:
        for ring in [g.exterior, *g.interiors]:
            c = list(ring.coords)[:-1]
            out.append("M " + " L ".join(f"{fmt(x)} {fmt(y)}" for x,y in c) + " Z")
    return " ".join(out)

kpoly = flatten(KNIGHT)[0]
sc = 0.80
sc = 0.90
M = [sc,0,0,sc,128-125*sc, 236-226*sc]
kp = affinity.affine_transform(kpoly, M)
def rr(x0,y0,x1,y1,r):
    return box(x0+r,y0+r,x1-r,y1-r).buffer(r, quad_segs=8)
outer = rr(20,84,236,242,8).difference(rr(27,91,229,235,2))
inner = rr(37,101,219,225,2).difference(rr(41,105,215,221,0.01))
cut = kp.buffer(7, join_style=1).intersection(box(0,0,256,228))
frame = outer.union(inner).difference(cut)
eye = affinity.affine_transform(flatten(EYE)[0], M)
C_geom = frame.union(kp.intersection(box(0,0,256,236))).difference(eye)
C_geom = affinity.translate(C_geom, 0, -18)
write("c-symbol", [to_d(C_geom)])

# ---------- lockups (horizontal, height 256) ----------
import re as _re
def sym_paths(name):
    t = open(f"../concepts/{name}.svg").read()
    return _re.findall(r' d="([^"]+)"', t)

def bbox_x(d):
    xs = [float(v) for v in TOKEN.findall(d)[1::1] if not v.isalpha()]
    return xs

def lockup_single(sym, out, font, size, tracking, cap_shift=0):
    ch = cap_height(font, size)
    x0 = 256 + 40
    base = 128 + ch / 2 + cap_shift
    d, w = text_path("TERAPRINT STUDIO", font, size, x0, base, tracking)
    write(out, sym_paths(sym) + [d], w=x0 + w + 8, h=256)

def lockup_double(sym, out):
    s1 = 92
    ch1 = cap_height(PLAYFAIR, s1)
    x0 = 256 + 40
    d1, w1 = text_path("TERAPRINT", PLAYFAIR, s1, x0, 128 + 8, 0.04)
    s2 = 44
    # STUDIO tracked to the same width as TERAPRINT
    _, wraw = text_path("STUDIO", ASSISTANT_700, s2, 0, 0, 0)
    tr = (w1 - wraw) / (5 * s2)
    d2, w2 = text_path("STUDIO", ASSISTANT_700, s2, x0, 128 + 8 + 30 + cap_height(ASSISTANT_700, s2), tr)
    write(out, sym_paths(sym) + [d1, d2], w=x0 + w1 + 8, h=256)

lockup_single("a-symbol", "a-lockup", ASSISTANT_700, 70, 0.36)
lockup_double("b-symbol", "b-lockup")
lockup_single("c-symbol", "c-lockup", ASSISTANT_700, 70, 0.36)
