import io, re, cairosvg
from PIL import Image, ImageDraw
from lib import text_path, cap_height, PLAYFAIR, FONTS, ASSISTANT_700, svg
GOLD, BLACK, IVORY = "#C9A961", "#0A0A0A", "#F5F5F0"
ITALIC = FONTS / "playfair-display-latin-400-italic.woff"

def paths(f): return re.findall(r' d="([^"]+)"', open(f).read())
def vb(f): return [float(v) for v in re.search(r'viewBox="([^"]+)"', open(f).read()).group(1).split()]
def raster(svgtxt, h=None, w=None):
    png = cairosvg.svg2png(bytestring=svgtxt.encode(), output_height=h, output_width=w)
    return Image.open(io.BytesIO(png)).convert("RGBA")
def colour(f, c, h=None, w=None):
    v = vb(f); return raster(svg(paths(f), v[2], v[3], fill=c), h=h, w=w)

def stacked(sym, c):
    """symbol over TERAPRINT STUDIO, for the box lid"""
    s = colour(sym, c, h=230)
    d, wt = text_path("TERAPRINT STUDIO", ASSISTANT_700, 34, 0, 34, 0.42)
    t = raster(svg([d], wt, 36, fill=c), w=360)
    im = Image.new("RGBA", (max(s.width, t.width), s.height + 30 + t.height), (0, 0, 0, 0))
    im.alpha_composite(s, ((im.width - s.width) // 2, 0)); im.alpha_composite(t, ((im.width - t.width) // 2, s.height + 30))
    return im

def lid(sym):
    S = 520; im = Image.new("RGBA", (S, S), BLACK); dr = ImageDraw.Draw(im)
    for m, t in ((22, 3), (32, 1)):
        dr.rectangle([m, m, S - m, S - m], outline=GOLD, width=t)
    lg = stacked(sym, GOLD); im.alpha_composite(lg, ((S - lg.width) // 2, 64))
    d, w = text_path("Rome Antique", PLAYFAIR, 40, 0, 40, 0.02)
    t = raster(svg([d], w, 52, fill=IVORY), h=52); im.alpha_composite(t, ((S - t.width) // 2, 388))
    d, w = text_path("Chaque camp a son histoire", ITALIC, 22, 0, 24, 0.01)
    t = raster(svg([d], w, 30, fill=GOLD), h=30); im.alpha_composite(t, ((S - t.width) // 2, 450))
    return im

def avatar(sym):
    S = 240; im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    disk = Image.new("L", (S, S), 0); ImageDraw.Draw(disk).ellipse([0, 0, S - 1, S - 1], fill=255)
    bg = Image.new("RGBA", (S, S), BLACK); m = colour(sym, GOLD, h=170)
    bg.alpha_composite(m, ((S - m.width) // 2, (S - m.height) // 2)); im.paste(bg, (0, 0), disk)
    small = colour(sym, BLACK, h=32)
    return im, small

def header(lock):
    W, H = 760, 90; im = Image.new("RGBA", (W, H), IVORY)
    lg = colour(lock, BLACK, h=48); im.alpha_composite(lg, (28, (H - 48) // 2))
    dr = ImageDraw.Draw(im); dr.line([0, H - 1, W, H - 1], fill="#DDDAD0")
    return im

rows = []
for n in "abc":
    sym, lock = f"../concepts/{n}-symbol.svg", f"../concepts/{n}-lockup.svg"
    L = lid(sym); A, fav = avatar(sym); Hd = header(lock)
    row = Image.new("RGBA", (1340, 560), "#E9E6DE")
    row.alpha_composite(L, (20, 20))
    row.alpha_composite(A, (570, 40))
    fb = Image.new("RGBA", (72, 72), "white"); fb.alpha_composite(fav, (20, 20)); row.alpha_composite(fb, (850, 124))
    row.alpha_composite(Hd, (570, 330))
    gold_lock = colour(lock, GOLD, h=56); dark = Image.new("RGBA", (760, 110), BLACK)
    dark.alpha_composite(gold_lock, (28, 27)); row.alpha_composite(dark, (570, 430))
    rows.append(row)
out = Image.new("RGB", (1340, 560 * 3 + 40), "#E9E6DE")
for i, r in enumerate(rows): out.paste(r, (0, i * 570 + 10), r)
out.save("../concepts-situation.png")
