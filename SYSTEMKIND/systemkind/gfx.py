"""Zeichen-Primitive: Fonts, Easing, Text-Sprites, Hintergründe."""
from __future__ import annotations

import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, features

from . import config as C


# --- Easing ----------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, start, dur):
    """Linearer Fortschritt 0..1 eines Zeitfensters."""
    return clamp((t - start) / dur) if dur > 0 else float(t >= start)


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_expo(x):
    x = clamp(x)
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def lerp(a, b, x):
    return a + (b - a) * x


def mix(c1, c2, x):
    return tuple(int(round(lerp(a, b, x))) for a, b in zip(c1, c2))


def rgba(color, a):
    return (*color, int(255 * clamp(a)))


# Versalziffern (lining figures) für Playfair – braucht libraqm in Pillow
FEAT = ["lnum"] if features.check("raqm") else None


def glen(f, s):
    return f.getlength(s, features=FEAT)


# --- Fonts -----------------------------------------------------------------
@lru_cache(maxsize=256)
def font(kind: str, size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    """kind: 'serif' | 'serif_italic' | 'sans'."""
    if kind.startswith("serif"):
        path = C.SERIF if kind == "serif" else C.SERIF_ITALIC
        f = ImageFont.truetype(str(path), size)
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
        return f
    w = min(C.SANS, key=lambda k: abs(k - weight))
    path = C.SANS_DIR / C.SANS[w]
    if not path.exists():
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(str(path), size)


def text_w(text, f, tracking=0):
    return glen(f, text) + tracking * max(len(text) - 1, 0)


def fit_font(text, kind, size, weight, max_w, tracking=0, min_size=24):
    """Größte Schrift <= size, mit der `text` in max_w passt."""
    while size > min_size and text_w(text, font(kind, size, weight), tracking) > max_w:
        size -= 2
    return font(kind, size, weight)


def wrap(text, f, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if cur and glen(f, trial) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


# --- Text-Sprites ----------------------------------------------------------
@lru_cache(maxsize=1024)
def sprite(text, kind, size, weight, color, tracking=0, glow=0):
    """Vorgerenderter Text als RGBA-Bild (optional mit weichem Schein)."""
    f = font(kind, size, weight)
    pad = 8 + glow * 3
    asc, desc = f.getmetrics()
    w = int(text_w(text, f, tracking)) + 2 * pad
    h = asc + desc + 2 * pad
    img = Image.new("RGBA", (w, h), (*color, 0))
    d = ImageDraw.Draw(img)
    if tracking:
        x = pad
        for ch in text:
            d.text((x, pad), ch, font=f, fill=(*color, 255), features=FEAT)
            x += glen(f, ch) + tracking
    else:
        d.text((pad, pad), text, font=f, fill=(*color, 255), features=FEAT)
    if glow:
        halo = img.filter(ImageFilter.GaussianBlur(glow))
        a = halo.getchannel("A").point(lambda v: int(v * 0.55))
        halo.putalpha(a)
        img = Image.alpha_composite(halo, img)
    img.info["pad"] = pad
    return img


def paste(frame, spr, x, y, alpha=1.0, scale=1.0):
    """Sprite mit Deckkraft einfügen. (x, y) = linke obere Textkante."""
    if alpha <= 0.004:
        return
    pad = spr.info.get("pad", 0)
    if abs(scale - 1.0) > 0.002:
        w, h = spr.size
        spr2 = spr.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BICUBIC)
        x -= (spr2.size[0] - w) / 2
        y -= (spr2.size[1] - h) / 2
        spr = spr2
    mask = spr.getchannel("A")
    if alpha < 0.996:
        mask = mask.point(lambda v: int(v * alpha))
    frame.paste(spr, (int(round(x - pad)), int(round(y - pad))), mask)


def draw_text(frame, text, x, y, kind="sans", size=40, weight=400, color=C.IVORY,
              alpha=1.0, anchor="l", tracking=0, glow=0, dy=0.0, scale=1.0):
    """Textzeile zeichnen. anchor: l | c | r (bezogen auf x). Gibt Breite zurück."""
    spr = sprite(text, kind, size, weight, tuple(color), tracking, glow)
    w = spr.size[0] - 2 * spr.info["pad"]
    if anchor == "c":
        x -= w / 2
    elif anchor == "r":
        x -= w
    paste(frame, spr, x, y + dy, alpha, scale)
    return w


def reveal_words(frame, segments, x, y, t, start, kind="serif", size=96, weight=700,
                 anchor="c", per_word=0.09, dur=0.5, rise=26, glow=0):
    """Wortweise Einblendung. segments: [(text, color), ...] für eine Zeile."""
    f = font(kind, size, weight)
    space = glen(f, " ")
    words = [(w, col) for seg, col in segments for w in seg.split()]
    total = sum(glen(f, w) for w, _ in words) + space * (len(words) - 1)
    cx = x - total / 2 if anchor == "c" else x - total if anchor == "r" else x
    for i, (w, col) in enumerate(words):
        p = ease_out(prog(t, start + i * per_word, dur))
        g = glow if tuple(col) == C.GOLD else 0
        draw_text(frame, w, cx, y, kind, size, weight, col, alpha=p,
                  dy=(1 - p) * rise, glow=g)
        cx += glen(f, w) + space
    return start + len(words) * per_word + dur


def parse_marked(text, base=C.IVORY, hi=C.GOLD):
    """'Das ist *wichtig*' -> [('Das ist', base), ('wichtig', hi)]."""
    out = []
    for i, part in enumerate(text.split("*")):
        if part.strip():
            out.append((part.strip(), hi if i % 2 else base))
    return out


# --- Formen ----------------------------------------------------------------
def rule(d, x0, x1, y, p=1.0, color=C.GOLD, width=3, alpha=1.0, center=True):
    """Goldene Linie, die sich aufzieht."""
    if p <= 0:
        return
    if center:
        mid, half = (x0 + x1) / 2, (x1 - x0) / 2 * p
        x0, x1 = mid - half, mid + half
    else:
        x1 = x0 + (x1 - x0) * p
    d.line([(x0, y), (x1, y)], fill=rgba(color, alpha), width=width)


def rrect(d, box, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def fmt_int(n):
    """Deutsche Tausendertrennung: 43219 -> '43.219'."""
    return f"{int(round(n)):,}".replace(",", ".")


def fmt_num(v, decimals=0):
    s = f"{v:,.{decimals}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# --- Hintergründe ----------------------------------------------------------
@lru_cache(maxsize=8)
def _base(variant: str) -> Image.Image:
    """Statischer Verlauf mit Lichtinsel – je Variante anders gesetzt."""
    centers = {"particles": (0.5, 0.38), "grid": (0.5, 0.55), "rings": (0.5, 0.42),
               "skyline": (0.5, 0.72), "plain": (0.5, 0.45), "beams": (0.3, 0.3)}
    cx, cy = centers.get(variant, (0.5, 0.45))
    yy, xx = np.mgrid[0:C.H, 0:C.W].astype(np.float32)
    r = np.sqrt(((xx / C.W - cx) * 1.25) ** 2 + (yy / C.H - cy) ** 2)
    glow = np.clip(1 - r / 0.75, 0, 1) ** 2
    bg = np.array(C.BG, np.float32)
    warm = np.array((0x2A, 0x25, 0x1E), np.float32)
    img = bg + (warm - bg)[None, None, :] * glow[..., None] * 0.9
    img *= (1 - np.clip(r - 0.45, 0, 1) * 0.55)[..., None]
    # Dithering gegen Banding im dunklen Verlauf
    img += np.random.default_rng(7).uniform(-0.6, 0.6, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


@lru_cache(maxsize=16)
def _bokeh(radius: int) -> Image.Image:
    s = radius * 4
    img = Image.new("L", (s, s), 0)
    ImageDraw.Draw(img).ellipse([radius, radius, s - radius, s - radius], fill=255)
    return img.filter(ImageFilter.GaussianBlur(radius * 0.45))


@lru_cache(maxsize=8)
def _particles(seed):
    rnd = random.Random(seed)
    return [(rnd.random(), rnd.random(), rnd.choice([6, 9, 14, 22, 34]),
             rnd.uniform(0.004, 0.02), rnd.uniform(0.05, 0.22), rnd.uniform(0, 6.28))
            for _ in range(34)]


@lru_cache(maxsize=4)
def _skyline(seed):
    rnd = random.Random(seed)
    layers = []
    for depth in range(3):
        x, blds = -60, []
        while x < C.W + 300:
            w = rnd.randint(70, 170)
            h = rnd.randint(180, 520) + depth * 90
            wins = [(rnd.random(), rnd.random()) for _ in range(rnd.randint(1, 5))]
            blds.append((x, w, h, wins))
            x += w + rnd.randint(4, 26)
        layers.append(blds)
    return layers


def background(variant: str, t: float, seed: int = 1) -> Image.Image:
    """Animierter Markenhintergrund. Gibt ein neues RGB-Bild zurück."""
    frame = _base(variant).copy()
    d = ImageDraw.Draw(frame, "RGBA")
    if variant in ("particles", "plain", "rings", "beams"):
        for x, y, r, speed, a, ph in _particles(seed):
            if variant != "particles" and r < 14:
                continue
            py = ((y - t * speed) % 1.2 - 0.1) * C.H
            px = (x + 0.012 * math.sin(t * 0.4 + ph)) * C.W
            tw = 0.75 + 0.25 * math.sin(t * 0.9 + ph)
            spr = _bokeh(r)
            mask = spr.point(lambda v, k=a * tw * 0.5: int(v * k))
            frame.paste(C.GOLD, (int(px - spr.size[0] / 2), int(py - spr.size[1] / 2)), mask)
    if variant == "grid":
        step, off = 108, (t * 14) % 108
        for i in range(-1, C.H // step + 2):
            y = i * step + off
            d.line([(0, y), (C.W, y)], fill=rgba(C.IVORY, 0.035), width=1)
        for i in range(C.W // step + 1):
            d.line([(i * step, 0), (i * step, C.H)], fill=rgba(C.IVORY, 0.03), width=1)
    if variant == "rings":
        cx, cy = C.W / 2, C.H * 0.42
        for i in range(6):
            r = ((i / 6 + t * 0.035) % 1) * 1100 + 80
            a = 0.10 * (1 - r / 1180)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgba(C.GOLD, a), width=2)
    if variant == "beams":
        for i in range(5):
            x = (i * 290 + t * 22) % (C.W + 700) - 350
            d.polygon([(x, 0), (x + 90, 0), (x - 420, C.H), (x - 560, C.H)],
                      fill=rgba(C.GOLD, 0.022))
    if variant == "skyline":
        base_y = C.H - 250
        for depth, blds in enumerate(_skyline(seed)):
            shade = mix(C.BG, (0x24, 0x22, 0x20), 0.9 - depth * 0.35)
            shift = t * (5 + depth * 7)
            for x, w, h, wins in blds:
                bx = x - shift
                d.rectangle([bx, base_y - h + depth * 150, bx + w, C.H], fill=(*shade, 255))
                if depth < 2:
                    for wx, wy in wins:
                        tw = 0.5 + 0.5 * math.sin(t * 0.7 + wx * 40)
                        px, py = bx + 10 + wx * (w - 26), base_y - h + depth * 150 + 16 + wy * (h - 60)
                        d.rectangle([px, py, px + 9, py + 13], fill=rgba(C.GOLD, 0.22 * tw + 0.08))
        # Bodennebel
        for i in range(8):
            d.rectangle([0, C.H - 330 + i * 40, C.W, C.H], fill=rgba(C.BG, 0.16))
    return frame


def scrim(frame, strength=0.62):
    """Abdunklung für B-Roll, damit Typografie lesbar bleibt."""
    d = ImageDraw.Draw(frame, "RGBA")
    d.rectangle([0, 0, C.W, C.H], fill=rgba(C.BG, strength))
