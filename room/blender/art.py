"""Draws the small artwork in the room with Pillow: book spines, covers, posters, notes.

Every function returns the path of a PNG in the cache directory. Sizes are in metres; PX is pixels per metre.
The typefaces in fonts/ are open (SIL Open Font License), taken from the Fontsource packages.
"""
import os, math, hashlib, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("ROOM_ART_CACHE", "/tmp/room-art")
PX = 3600

FONTS = {
    "gothic": "league-gothic-400", "bebas": "bebas-neue-400", "oswald": "oswald-400", "oswald-b": "oswald-600",
    "playfair": "playfair-display-400", "playfair-b": "playfair-display-700", "playfair-i": "playfair-display-400i",
    "garamond": "eb-garamond-400", "garamond-b": "eb-garamond-600", "garamond-i": "eb-garamond-400i",
    "baskerville": "libre-baskerville-400", "baskerville-b": "libre-baskerville-700",
    "cinzel": "cinzel-400", "cinzel-b": "cinzel-700", "script": "yellowtail-400",
}


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", FONTS[name] + ".woff"), max(4, int(size)))


def rgb(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(max(0, min(1, v)) * 255) for v in c)


def lin(c):
    """sRGB colour (hex or 0-1 tuple) to the linear values Blender materials take."""
    r = [v / 255 for v in rgb(c)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in r)


def _save(img, key):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, hashlib.md5(key.encode()).hexdigest()[:16] + ".png")
    img.convert("RGB").save(p)
    return p


def _fit(draw, text, fname, max_w, max_h, spacing=0):
    """Largest font size at which `text` fits in max_w x max_h."""
    size = int(max_h * 1.3)
    while size > 5:
        f = font(fname, size)
        l, t, r, b = draw.textbbox((0, 0), text, font=f)
        w = r - l + spacing * max(0, len(text) - 1)
        if w <= max_w and b - t <= max_h:
            return f
        size = int(size * 0.94)
    return font(fname, 5)


def _text(draw, xy, text, f, fill, anchor="lm", spacing=0):
    if not spacing:
        draw.text(xy, text, font=f, fill=fill, anchor=anchor)
        return
    x, y = xy
    total = sum(draw.textlength(ch, font=f) for ch in text) + spacing * (len(text) - 1)
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill, anchor="l" + anchor[1])
        x += draw.textlength(ch, font=f) + spacing


def _wear(img, seed, amount=1.0):
    """A little noise and edge darkening, so flat colour reads as a printed, handled object."""
    r = random.Random(seed)
    w, h = img.size
    noise = Image.effect_noise((w, h), 14 * amount).convert("L")
    img = Image.blend(img, Image.merge("RGB", [noise] * 3), 0.045 * amount)
    shade = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(shade)
    edge = max(2, int(min(w, h) * 0.07))
    d.rectangle([edge, 0, w - edge, h], fill=255)
    shade = shade.filter(ImageFilter.GaussianBlur(edge * 0.8))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(img, Image.blend(img, dark, 0.22 * amount), shade)


def spine(spec, thick, height):
    """Book spine. The text reads from the top of the spine to the bottom.

    spec keys: title, author, bg, fg, title_font, author_font, title_fg, author_fg,
    bands [(from, to, colour)] as fractions from the top, author_first, title_span (from, to), author_span,
    title_scale, author_scale (fraction of the spine width used by the text), upright (author set across the spine).
    """
    key = "spine" + repr(sorted(spec.items())) + f"{thick:.4f}{height:.4f}"
    L, T = int(height * PX), max(24, int(thick * PX))
    img = Image.new("RGB", (L, T), rgb(spec.get("bg", "#222222")))     # drawn lying down: x runs top to bottom
    d = ImageDraw.Draw(img)
    for a, b, c in spec.get("bands", []):
        d.rectangle([int(a * L), 0, int(b * L), T], fill=rgb(c))
    fg = spec.get("fg", "#f2efe6")
    title, author = spec.get("title", ""), spec.get("author", "")
    ts = spec.get("title_span", (0.07, 0.62) if author else (0.08, 0.92))
    as_ = spec.get("author_span", (0.68, 0.93))
    if spec.get("author_first"):
        ts, as_ = spec.get("title_span", (0.36, 0.93)), spec.get("author_span", (0.06, 0.30))
    if title:
        box_w, box_h = (ts[1] - ts[0]) * L, T * spec.get("title_scale", 0.62)
        sp = spec.get("title_spacing", 0) * T
        f = _fit(d, title, spec.get("title_font", "garamond-b"), box_w, box_h, sp)
        _text(d, (ts[0] * L if spec.get("title_align", "l") == "l" else (ts[0] + ts[1]) / 2 * L, T / 2), title, f,
              rgb(spec.get("title_fg", fg)), anchor=("l" if spec.get("title_align", "l") == "l" else "m") + "m", spacing=sp)
    if author and not spec.get("upright"):
        box_w, box_h = (as_[1] - as_[0]) * L, T * spec.get("author_scale", 0.42)
        sp = spec.get("author_spacing", 0) * T
        f = _fit(d, author, spec.get("author_font", "garamond"), box_w, box_h, sp)
        _text(d, (as_[1] * L if spec.get("author_align", "r") == "r" else as_[0] * L, T / 2), author, f,
              rgb(spec.get("author_fg", fg)), anchor=("r" if spec.get("author_align", "r") == "r" else "l") + "m", spacing=sp)
    img = img.rotate(-90, expand=True)                                    # stand it up: reads top to bottom
    if author and spec.get("upright"):
        d = ImageDraw.Draw(img)
        lines = author.split("|")
        f = min((_fit(d, ln, spec.get("author_font", "gothic"), T * 0.84, height * PX * 0.06) for ln in lines), key=lambda x: x.size)
        y = (as_[0] + as_[1]) / 2 * L - (len(lines) - 1) * f.size * 0.55
        for ln in lines:
            d.text((T / 2, y), ln, font=f, fill=rgb(spec.get("author_fg", fg)), anchor="mm")
            y += f.size * 1.1
    for a, b, c in spec.get("rules", []):                                  # thin lines across the spine
        ImageDraw.Draw(img).rectangle([int(T * 0.1), int(a * L), int(T * 0.9), int(b * L)], fill=rgb(c))
    return _save(_wear(img, key), key)


def big_short_cover(w, h):
    key = f"bigshort{w}{h}"
    W, H = int(w * PX), int(h * PX)
    img = Image.new("RGB", (W, H), (26, 26, 25))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * 0.15, H * 0.12, W * 0.85, H * 0.62], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(W * 0.16))
    img = Image.composite(Image.new("RGB", (W, H), (88, 86, 80)), img, glow)
    d = ImageDraw.Draw(img)
    # a rolled note on a hook, drawn simply
    cx, cy, r = W * 0.5, H * 0.4, W * 0.12
    d.line([cx, 0, cx, cy - r * 1.5], fill=(60, 110, 60), width=max(1, W // 300))
    d.rounded_rectangle([cx - r * 1.3, cy - r, cx + r * 1.1, cy + r], radius=r * 0.5, fill=(168, 172, 150))
    d.ellipse([cx + r * 0.2, cy - r, cx + r * 1.9, cy + r], fill=(196, 198, 176), outline=(110, 114, 96), width=3)
    for k in (0.75, 0.5, 0.25):
        d.ellipse([cx + r * 1.05 - r * 0.85 * k, cy - r * k, cx + r * 1.05 + r * 0.85 * k, cy + r * k], outline=(120, 124, 104), width=2)
    d.arc([cx - r * 0.5, cy - r * 1.7, cx + r * 0.5, cy + r * 1.25], 60, 270, fill=(200, 200, 196), width=max(2, W // 160))
    f = _fit(d, "MICHAEL", "oswald", W * 0.78, H * 0.085, W * 0.02)
    _text(d, (W / 2, H * 0.685), "MICHAEL", f, (240, 238, 232), "mm", W * 0.02)
    _text(d, (W / 2, H * 0.775), "LEWIS", f, (240, 238, 232), "mm", W * 0.02)
    f2 = _fit(d, "THE BIG SHORT", "oswald-b", W * 0.78, H * 0.06, W * 0.008)
    _text(d, (W / 2, H * 0.862), "THE BIG SHORT", f2, (110, 168, 82), "mm", W * 0.008)
    f3 = _fit(d, "INSIDE THE DOOMSDAY MACHINE", "oswald", W * 0.78, H * 0.022, W * 0.006)
    _text(d, (W / 2, H * 0.915), "INSIDE THE DOOMSDAY MACHINE", f3, (225, 223, 216), "mm", W * 0.006)
    return _save(_wear(img, key, 0.6), key)


def cap_front(w, h, text="Leland"):
    key = f"cap{text}{w}{h}"
    W, H = int(w * PX), int(h * PX)
    img = Image.new("RGB", (W, H), (14, 14, 16))
    d = ImageDraw.Draw(img)
    f = _fit(d, text, "playfair-b", W * 0.92, H * 0.8)
    d.text((W / 2, H / 2), text, font=f, fill=(226, 228, 232), anchor="mm")
    stitch = Image.effect_noise((W, H), 40).convert("L").point(lambda v: 255 if v > 150 else 215)
    img = Image.composite(img, Image.new("RGB", (W, H), (14, 14, 16)), stitch)
    return _save(img, key)


def baseball(text="Kore"):
    """Equirectangular skin for a ball: leather, two red seams, and the name in script."""
    key = "baseball" + text
    W, H = 1536, 768
    img = Image.new("RGB", (W, H), (226, 214, 188))
    d = ImageDraw.Draw(img)
    for phase in (0.0, math.pi):
        pts = [(x, H / 2 + math.sin(x / W * 2 * math.pi + phase) * H * 0.3 + (H * 0.0 if phase == 0 else 0)) for x in range(0, W + 8, 8)]
        if phase == 0:
            continue
    # one seam curve that wraps the ball twice, like the real thing
    def seam(u):
        return H / 2 + H * 0.27 * math.sin(2 * (u / W) * 2 * math.pi)
    for x in range(0, W, 14):
        y = seam(x)
        slope = (seam(x + 1) - y)
        ang = math.atan2(slope, 1)
        nx, ny = -math.sin(ang), math.cos(ang)
        for s in (-1, 1):
            ax, ay = x + nx * 5 * s, y + ny * 5 * s
            bx, by = x + nx * 20 * s + math.cos(ang) * 7, y + ny * 20 * s + math.sin(ang) * 7
            d.line([ax, ay, bx, by], fill=(170, 30, 34), width=4)
    d.line([(x, seam(x)) for x in range(0, W + 4, 4)], fill=(190, 176, 150), width=2)
    f = font("script", 230)
    d.text((W * 0.5, H * 0.5), text, font=f, fill=(24, 44, 92), anchor="mm")
    return _save(_wear(img, key, 0.5), key)


def ridge_poster(w, h, title="UTAH", sub="THE WASATCH RANGE"):
    key = f"ridgeposter{title}{w}{h}"
    W, H = int(w * 1800), int(h * 1800)
    img = Image.new("RGB", (W, H), (233, 218, 184))
    d = ImageDraw.Draw(img)
    m = int(W * 0.07)
    d.rectangle([m, m, W - m, int(H * 0.8)], fill=(226, 150, 78))
    for i in range(int(H * 0.5)):
        t = i / (H * 0.5)
        d.line([m, m + i, W - m, m + i], fill=(int(214 + 26 * t), int(96 + 96 * t), int(60 + 60 * t)))
    d.ellipse([W * 0.56, H * 0.2, W * 0.8, H * 0.2 + W * 0.24], fill=(250, 226, 170))
    r = random.Random(4)
    cols = [(150, 74, 70), (104, 52, 66), (62, 40, 62), (34, 30, 48)]
    for k, c in enumerate(cols):
        base = H * (0.42 + k * 0.09)
        ph = [r.uniform(0, 6.28) for _ in range(3)]
        pts = [(m, int(H * 0.8))]
        for x in range(m, W - m + 6, 6):
            u = x / W * 6.28
            pts.append((x, base - H * (0.06 * math.sin(1.4 * u + ph[0]) + 0.035 * math.sin(3.3 * u + ph[1]) + 0.015 * math.sin(8 * u + ph[2]))))
        pts.append((W - m, int(H * 0.8)))
        d.polygon(pts, fill=c)
    f = _fit(d, title, "gothic", W * 0.8, H * 0.105, W * 0.03)
    _text(d, (W / 2, H * 0.875), title, f, (34, 30, 48), "mm", W * 0.03)
    f2 = _fit(d, sub, "oswald", W * 0.7, H * 0.022, W * 0.012)
    _text(d, (W / 2, H * 0.945), sub, f2, (104, 52, 66), "mm", W * 0.012)
    return _save(_wear(img, key, 0.8), key)


def court_print(w, h):
    key = f"court{w}{h}"
    W, H = int(w * 2400), int(h * 2400)
    img = Image.new("RGB", (W, H), (232, 224, 204))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = W * 0.2, H * 0.12, W * 0.8, H * 0.88
    d.rectangle([x0, y0, x1, y1], fill=(170, 84, 52))
    lw = max(2, W // 110)
    white = (240, 234, 220)
    d.rectangle([x0, y0, x1, y1], outline=white, width=lw)
    sx = (x1 - x0) * 0.125
    d.line([x0 + sx, y0, x0 + sx, y1], fill=white, width=lw)
    d.line([x1 - sx, y0, x1 - sx, y1], fill=white, width=lw)
    my = (y0 + y1) / 2
    sy = (y1 - y0) * 0.27
    d.line([x0 + sx, my - sy, x1 - sx, my - sy], fill=white, width=lw)
    d.line([x0 + sx, my + sy, x1 - sx, my + sy], fill=white, width=lw)
    d.line([(x0 + x1) / 2, my - sy, (x0 + x1) / 2, my + sy], fill=white, width=lw)
    d.line([x0 - W * 0.03, my, x1 + W * 0.03, my], fill=(40, 36, 34), width=lw)
    return _save(_wear(img, key, 0.8), key)


def shapes_print(w, h):
    key = f"shapes{w}{h}"
    W, H = int(w * 2000), int(h * 2000)
    img = Image.new("RGB", (W, H), (228, 220, 200))
    d = ImageDraw.Draw(img)
    d.ellipse([W * 0.18, H * 0.14, W * 0.72, H * 0.14 + W * 0.54], fill=(30, 46, 84))
    d.rectangle([W * 0.42, H * 0.46, W * 0.86, H * 0.82], fill=(196, 92, 44))
    d.pieslice([W * 0.12, H * 0.52, W * 0.56, H * 0.52 + W * 0.44], 90, 270, fill=(222, 170, 60))
    for i in range(5):
        d.line([W * 0.14, H * (0.86 + i * 0.012), W * 0.5, H * (0.86 + i * 0.012)], fill=(40, 36, 34), width=max(1, H // 500))
    return _save(_wear(img, key, 0.8), key)


def certificate(w, h, lines, seal=(150, 110, 40)):
    key = f"cert{lines}{w}{h}"
    W, H = int(w * 3000), int(h * 3000)
    img = Image.new("RGB", (W, H), (236, 228, 206))
    d = ImageDraw.Draw(img)
    m = int(W * 0.04)
    d.rectangle([m, m, W - m, H - m], outline=seal, width=max(2, W // 160))
    d.rectangle([m * 1.5, m * 1.5, W - m * 1.5, H - m * 1.5], outline=seal, width=1)
    ys = [0.2, 0.36, 0.52, 0.64]
    fonts_ = ["cinzel", "playfair-b", "garamond-i", "cinzel"]
    hs = [0.055, 0.12, 0.06, 0.05]
    for ln, y, fn, hh in zip(lines, ys, fonts_, hs):
        f = _fit(d, ln, fn, W * 0.8, H * hh)
        d.text((W / 2, H * y), ln, font=f, fill=(44, 38, 30), anchor="mm")
    d.ellipse([W * 0.44, H * 0.72, W * 0.56, H * 0.72 + W * 0.12], fill=seal)
    d.line([W * 0.12, H * 0.84, W * 0.34, H * 0.84], fill=(44, 38, 30), width=2)
    d.line([W * 0.66, H * 0.84, W * 0.88, H * 0.84], fill=(44, 38, 30), width=2)
    return _save(_wear(img, key, 0.5), key)


def note(w, h, bg, lines, fname="script", ruled=False, seed=0):
    key = f"note{lines}{bg}{w}{h}{ruled}"
    W, H = int(w * 3000), int(h * 3000)
    img = Image.new("RGB", (W, H), rgb(bg))
    d = ImageDraw.Draw(img)
    if ruled:
        for y in range(int(H * 0.2), H, max(8, int(H * 0.09))):
            d.line([0, y, W, y], fill=(150, 170, 200), width=1)
        d.line([W * 0.12, 0, W * 0.12, H], fill=(210, 120, 120), width=1)
    n = len(lines)
    for i, ln in enumerate(lines):
        f = _fit(d, ln, fname, W * 0.8, H * min(0.22, 0.7 / n))
        d.text((W * 0.5, H * (0.5 + (i - (n - 1) / 2) * min(0.26, 0.8 / n))), ln, font=f, fill=(34, 40, 70), anchor="mm")
    return _save(_wear(img, key, 0.5), key)


def clock_face(size):
    key = f"clock{size}"
    W = int(size * 3000)
    bg = (234, 226, 204)
    img = Image.new("RGB", (W, W), bg)
    d = ImageDraw.Draw(img)
    c = W / 2
    f = font("playfair", W * 0.12)
    for i in range(1, 13):
        a = i / 12 * 2 * math.pi
        d.text((c + math.sin(a) * W * 0.38, c - math.cos(a) * W * 0.38), str(i), font=f, fill=(34, 30, 26), anchor="mm")
    for i in range(60):
        a = i / 60 * 2 * math.pi
        r0 = W * (0.47 if i % 5 else 0.455)
        d.line([c + math.sin(a) * r0, c - math.cos(a) * r0, c + math.sin(a) * W * 0.49, c - math.cos(a) * W * 0.49], fill=(34, 30, 26), width=max(1, W // 220))
    return _save(img, key)


def calculator_face(w, h):
    key = f"calc{w}{h}"
    W, H = int(w * 6000), int(h * 6000)
    img = Image.new("RGB", (W, H), (30, 26, 24))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H * 0.3], fill=(176, 138, 62))
    d.rounded_rectangle([W * 0.08, H * 0.06, W * 0.62, H * 0.25], radius=4, fill=(96, 108, 86))
    f = font("oswald", H * 0.12)
    d.text((W * 0.58, H * 0.155), "1,000.00", font=f, fill=(24, 30, 22), anchor="rm")
    for r_ in range(4):
        for c_ in range(10):
            x, y = W * (0.04 + c_ * 0.094), H * (0.36 + r_ * 0.155)
            col = (196, 140, 40) if (r_, c_) == (3, 0) else (60, 110, 160) if (r_, c_) == (3, 1) else (16, 14, 14)
            d.rounded_rectangle([x, y, x + W * 0.075, y + H * 0.11], radius=3, fill=col, outline=(70, 64, 58))
    return _save(img, key)


def plate(text, w, h, bg, fg, fname="cinzel", scale=0.5, spacing=0.0):
    """A horizontal label: one line of text centred on a flat colour."""
    key = f"plate{text}{w}{h}{bg}{fg}{fname}"
    W, H = int(w * PX), int(h * PX)
    img = Image.new("RGB", (W, H), rgb(bg))
    d = ImageDraw.Draw(img)
    f = _fit(d, text, fname, W * 0.9, H * scale, spacing * H)
    _text(d, (W / 2, H / 2), text, f, rgb(fg), "mm", spacing * H)
    return _save(_wear(img, key, 0.5), key)
