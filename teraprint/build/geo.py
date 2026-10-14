"""Shapely helpers: bezier path -> polygons, polygons -> SVG path, tapered strokes, glyph outlines."""
import math
from shapely.geometry import Polygon, MultiPolygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from lib import TOKEN, fmt

def _bez(p, n):
    out = []
    for j in range(1, n + 1):
        t = j / n; u = 1 - t
        out.append(tuple(u**3*p[0][a] + 3*u*u*t*p[1][a] + 3*u*t*t*p[2][a] + t**3*p[3][a] for a in (0, 1)))
    return out

def poly(d, n=32):
    """Absolute M/L/C/Z path -> shapely geometry (evenodd-ish: xor of subpaths)."""
    toks = TOKEN.findall(d); i = 0; cur = None; pts = []; polys = []
    while i < len(toks):
        c = toks[i]; i += 1
        if c == "M":
            cur = (float(toks[i]), float(toks[i+1])); i += 2; pts = [cur]
        elif c == "L":
            cur = (float(toks[i]), float(toks[i+1])); i += 2; pts.append(cur)
        elif c == "C":
            p = [cur] + [(float(toks[i+k]), float(toks[i+k+1])) for k in (0, 2, 4)]; i += 6
            pts += _bez(p, n); cur = pts[-1]
        elif c == "Z":
            polys.append(Polygon(pts).buffer(0))
    g = polys[0]
    for q in polys[1:]:
        g = g.symmetric_difference(q)
    return g

def stroke(pts, w0, w1=None, wmid=None, n=48):
    """Tapered brush stroke along a cubic (4 control points); widths at start, middle, end."""
    w1 = w0 if w1 is None else w1
    wmid = (w0 + w1) / 2 if wmid is None else wmid
    c = [pts[0]] + _bez(pts, n)
    L, R = [], []
    for k, (x, y) in enumerate(c):
        t = k / n
        a = c[max(k-1, 0)]; b = c[min(k+1, n)]
        dx, dy = b[0]-a[0], b[1]-a[1]; ln = math.hypot(dx, dy) or 1
        nx, ny = -dy/ln, dx/ln
        w = (1-t)**2*w0 + 2*(1-t)*t*(2*wmid - (w0+w1)/2) + t*t*w1
        w = max(w, 0) / 2
        L.append((x+nx*w, y+ny*w)); R.append((x-nx*w, y-ny*w))
    return Polygon(L + R[::-1]).buffer(0)

def circle(cx, cy, r):
    return Point(cx, cy).buffer(r, quad_segs=64)

def to_d(geom, tol=0.08):
    geom = geom.simplify(tol)
    out = []
    for g in getattr(geom, "geoms", [geom]):
        if g.is_empty or g.geom_type != "Polygon":
            continue
        for ring in [g.exterior, *g.interiors]:
            c = list(ring.coords)[:-1]
            out.append("M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in c) + "Z")
    return " ".join(out)

def glyph_polys(font_path, text, size, tracking=0.0):
    """Return list of (geom, advance) per char, glyph baseline at y=0, x from 0, y down."""
    f = TTFont(str(font_path)); gs = f.getGlyphSet(); cmap = f.getBestCmap(); s = size / f["head"].unitsPerEm
    out = []
    for ch in text:
        g = cmap[ord(ch)]; rp = RecordingPen()
        gs[g].draw(TransformPen(rp, (s, 0, 0, -s, 0, 0)))
        geoms = []; pts = []; cur = None
        for op, args in rp.value:
            if op == "moveTo":
                pts = [args[0]]; cur = args[0]
            elif op == "lineTo":
                pts.append(args[0]); cur = args[0]
            elif op == "curveTo":
                pts += _bez([cur, *args], 12); cur = args[-1]
            elif op == "qCurveTo":
                # convert implied-on-curve quadratic chain
                ctrl = list(args[:-1]); end = args[-1]
                ons = []
                for k in range(len(ctrl) - 1):
                    ons.append(((ctrl[k][0]+ctrl[k+1][0])/2, (ctrl[k][1]+ctrl[k+1][1])/2))
                ons.append(end)
                for k, q in enumerate(ctrl):
                    p0 = cur; p2 = ons[k]
                    c1 = (p0[0]+2/3*(q[0]-p0[0]), p0[1]+2/3*(q[1]-p0[1]))
                    c2 = (p2[0]+2/3*(q[0]-p2[0]), p2[1]+2/3*(q[1]-p2[1]))
                    pts += _bez([p0, c1, c2, p2], 10); cur = p2
            elif op in ("closePath", "endPath"):
                if len(pts) > 2: geoms.append(Polygon(pts).buffer(0))
                pts = []
        g2 = geoms[0] if geoms else Polygon()
        for q in geoms[1:]:
            g2 = g2.symmetric_difference(q)
        out.append((g2, gs[g].width * s + tracking * size))
    return out

def text_on_arc(font_path, text, size, cx, cy, r, center_deg=-90, tracking=0.0, bottom=False):
    """Set text along a circle of radius r (baseline). Top arc reads clockwise; bottom arc reads left-to-right."""
    gl = glyph_polys(font_path, text, size, tracking)
    total = sum(a for _, a in gl) - tracking * size
    ang_total = total / r
    geoms = []
    if not bottom:
        a = math.radians(center_deg) - ang_total / 2
        for g, adv in gl:
            mid = a + (adv - tracking*size) / 2 / r
            gg = affinity.translate(g, -(adv - tracking*size) / 2, 0)
            gg = affinity.rotate(gg, math.degrees(mid) + 90, origin=(0, 0))
            geoms.append(affinity.translate(gg, cx + r*math.cos(mid), cy + r*math.sin(mid)))
            a += adv / r
    else:
        a = math.radians(center_deg) + ang_total / 2
        for g, adv in gl:
            mid = a - (adv - tracking*size) / 2 / r
            gg = affinity.translate(g, -(adv - tracking*size) / 2, 0)
            gg = affinity.rotate(gg, math.degrees(mid) - 90, origin=(0, 0))
            geoms.append(affinity.translate(gg, cx + r*math.cos(mid), cy + r*math.sin(mid)))
            a -= adv / r
    return unary_union(geoms)

def save(path, geom_or_d, w=256, h=256, title="TeraPrint Studio", fill="#0A0A0A"):
    d = geom_or_d if isinstance(geom_or_d, str) else to_d(geom_or_d)
    open(path, "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(w)} {fmt(h)}" width="{fmt(w)}" height="{fmt(h)}" '
        f'role="img" aria-labelledby="title">\n  <title id="title">{title}</title>\n'
        f'  <path fill="{fill}" fill-rule="evenodd" d="{d}"/>\n</svg>\n')
