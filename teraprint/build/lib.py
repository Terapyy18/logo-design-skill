"""Helpers for building TeraPrint Studio logo SVGs: path transforms and font outlines."""
import re
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONTS = Path(__file__).resolve().parent / "fonts"
ASSISTANT = FONTS / "assistant-latin-600-normal.woff"
ASSISTANT_700 = FONTS / "assistant-latin-700-normal.woff"
PLAYFAIR = FONTS / "playfair-display-latin-600-normal.woff"

TOKEN = re.compile(r"[MLCQZAHVmlcqzahv]|-?\d*\.?\d+(?:e-?\d+)?")


def fmt(v):
    v = round(v, 2)
    return str(int(v)) if v == int(v) else f"{v:g}"


def transform(d, sx=1.0, sy=None, tx=0.0, ty=0.0, mirror_w=None):
    """Scale + translate an absolute-command path (M L C Q Z only). mirror_w flips horizontally."""
    sy = sx if sy is None else sy
    out, cmd, nums = [], None, []
    toks = TOKEN.findall(d)

    def flush():
        if cmd is None:
            return
        if cmd in "Zz":
            out.append("Z")
            return
        pts = []
        for i in range(0, len(nums), 2):
            x, y = nums[i], nums[i + 1]
            if mirror_w is not None:
                x = mirror_w - x
            pts.append(f"{fmt(x * sx + tx)} {fmt(y * sy + ty)}")
        out.append(cmd + " " + " ".join(pts))

    for t in toks:
        if t.isalpha():
            flush()
            cmd, nums = t, []
            if t in "Zz":
                flush()
                cmd = None
        else:
            nums.append(float(t))
    flush()
    return " ".join(out)


def text_path(text, font=ASSISTANT, size=40, x=0.0, baseline=0.0, tracking=0.0, align="left"):
    """Return (d, width) for text outlined at `size` px with letter-spacing `tracking` (em)."""
    f = TTFont(str(font))
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    upm = f["head"].unitsPerEm
    s = size / upm
    adv = []
    for ch in text:
        g = cmap[ord(ch)]
        adv.append((g, gs[g].width * s))
    total = sum(a for _, a in adv) + tracking * size * (len(text) - 1)
    cx = x - (total / 2 if align == "center" else total if align == "right" else 0)
    parts = []
    for g, a in adv:
        pen = SVGPathPen(gs, ntos=fmt)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, cx, baseline)))
        parts.append(pen.getCommands())
        cx += a + tracking * size
    return " ".join(p for p in parts if p), total


def cap_height(font=ASSISTANT, size=40):
    f = TTFont(str(font))
    gs = f.getGlyphSet()
    bp = BoundsPen(gs)
    gs[f.getBestCmap()[ord("H")]].draw(bp)
    return bp.bounds[3] * size / f["head"].unitsPerEm


def svg(d_list, w=256, h=256, title="TeraPrint Studio", fill="#0A0A0A"):
    paths = "\n".join(
        f'  <path fill="{fill}" fill-rule="evenodd" d="{d}"/>' if isinstance(d, str)
        else f'  <path fill="{fill}" fill-rule="evenodd" {d[1]} d="{d[0]}"/>'
        for d in d_list)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(w)} {fmt(h)}" width="{fmt(w)}" '
            f'height="{fmt(h)}" role="img" aria-labelledby="title">\n  <title id="title">{title}</title>\n'
            f'{paths}\n</svg>\n')
