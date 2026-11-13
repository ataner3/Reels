"""Szenen-Vorlagen (Motion Graphics). Jede Vorlage ist eine Funktion
draw(frame, d, t, sc): frame = RGB-Bild mit fertigem Hintergrund, d = ImageDraw
im RGBA-Modus, t = Sekunden seit Szenenbeginn, sc = Szenen-Dict aus der Timeline
(type, params, duration, beats = Startzeiten der Voice-over-Sätze).

Neue Vorlage: Funktion schreiben, mit @scene("name") registrieren, optional
Soundeffekte in events() ergänzen.
"""
from __future__ import annotations

import math

from . import config as C
from .gfx import (clamp, draw_text, ease_in_out, ease_out, ease_out_expo, fit_font,
                  fmt_int, fmt_num, font, lerp, mix, parse_marked, prog, reveal_words,
                  rgba, rrect, rule, text_w, wrap)

REGISTRY = {}
CX = C.W // 2
L, R = C.SAFE_L, C.SAFE_R


def scene(name):
    def deco(fn):
        REGISTRY[name] = fn
        return fn
    return deco


def beat(sc, i, default):
    """Zeitpunkt in der Szene: i = Nummer des Voice-over-Satzes (0, 1, …) oder
    ein gesprochenes Wort (z. B. "76") – dann der Moment, in dem es fällt."""
    if isinstance(i, str):
        for w, t in sc.get("word_times", []):      # exakt, mit Satzzeichen ("arbeitet,")
            if w == i:
                return t
        clean = [(w.strip(".,:;?!–\"'"), t) for w, t in sc.get("word_times", [])]
        for w, t in clean:
            if w == i:
                return t
        for w, t in clean:
            if w.lower().startswith(i.lower()):
                return t
        return default
    b = sc.get("beats") or []
    return b[i] if i is not None and i < len(b) else default


def kicker(frame, d, t, text, y=300, start=0.1):
    """Kleine Dachzeile mit goldener Linie – gibt jeder Szene einen Anker."""
    if not text:
        return
    p = ease_out(prog(t, start, 0.6))
    rule(d, L, L + 64, y + 22, p, width=3, center=False)
    draw_text(frame, text.upper(), L + 84, y + 2, "sans", 32, 600, C.GOLD, alpha=p,
              tracking=5, dy=(1 - p) * 10)


def headline(frame, t, lines, y, start, size=68, weight=600, gap=1.2, anchor="l", max_w=None):
    """Mehrzeilige Serif-Überschrift mit *Hervorhebung*. Gibt y nach dem Block zurück."""
    max_w = max_w or (R - L)
    longest = max(lines, key=lambda s: text_w(s.replace("*", ""), font("serif", size, weight)))
    f = fit_font(longest.replace("*", ""), "serif", size, weight, max_w)
    x = L if anchor == "l" else CX
    for i, line in enumerate(lines):
        reveal_words(frame, parse_marked(line), x, y, t, start + i * 0.22, "serif",
                     f.size, weight, anchor=anchor, glow=10)
        y += int(f.size * gap)
    return y


def source_line(frame, t, text, start, y=None):
    if not text:
        return
    y = y or C.SAFE_BOTTOM - 44
    p = ease_out(prog(t, start, 0.6))
    f = fit_font(text, "sans", 30, 400, R - L)
    draw_text(frame, text, L, y, "sans", f.size, 400, C.MUTED, alpha=p * 0.95)


def money(v):
    if v >= 1_000_000:
        return f"{fmt_num(v / 1_000_000, 2)} Mio. €"
    return f"{fmt_int(v)} €"


# --- title -----------------------------------------------------------------
@scene("title")
def title(frame, d, t, sc):
    p = sc["params"]
    lines = p["lines"]
    longest = max((l.replace("*", "") for l in lines), key=len)
    f = fit_font(longest, "serif", 138, 700, R - L)
    lh = int(f.size * 1.14)
    y0 = 760 - lh * len(lines) // 2
    pk = ease_out(prog(t, 0.15, 0.7))
    draw_text(frame, p.get("kicker", C.BRAND).upper(), CX, y0 - 120, "sans", 30, 600,
              C.GOLD, alpha=pk, anchor="c", tracking=9)
    rule(d, CX - 150, CX + 150, y0 - 56, ease_in_out(prog(t, 0.2, 0.9)), width=2)
    y = y0
    for i, line in enumerate(lines):
        reveal_words(frame, parse_marked(line), CX, y, t, 0.35 + i * 0.32, "serif",
                     f.size, 700, glow=14, per_word=0.12, dur=0.6, rise=34)
        y += lh
    if p.get("sub"):
        st = beat(sc, p.get("sub_beat", 1), 2.2)
        ps = ease_out(prog(t, st, 0.7))
        rule(d, CX - 40, CX + 40, y + 46, ps, width=3)
        for i, line in enumerate(p["sub"] if isinstance(p["sub"], list) else [p["sub"]]):
            pi = ease_out(prog(t, beat(sc, p.get("sub_beat", 1) + i, st + i * 0.8), 0.7))
            reveal_words(frame, parse_marked(line), CX, y + 84 + i * 80, t,
                         beat(sc, p.get("sub_beat", 1) + i, st + i * 0.8),
                         "serif", 56, 500, glow=8)


# --- statement -------------------------------------------------------------
@scene("statement")
def statement(frame, d, t, sc):
    p = sc["params"]
    kicker(frame, d, t, p.get("kicker"))
    lines = p["lines"]
    size = p.get("size", 104)
    longest = max((l.replace("*", "") for l in lines), key=len)
    f = fit_font(longest, "serif", size, 700, R - L)
    lh = int(f.size * 1.18)
    y = 780 - lh * len(lines) // 2
    for i, line in enumerate(lines):
        st = beat(sc, p.get("line_beats", [None] * len(lines))[i], 0.4 + i * 0.5)
        reveal_words(frame, parse_marked(line), L, y, t, st, "serif", f.size, 700,
                     anchor="l", glow=12, per_word=0.11, dur=0.55)
        y += lh
    if p.get("sub"):
        st = beat(sc, p.get("sub_beat"), 1.6)
        ps = ease_out(prog(t, st, 0.7))
        rule(d, L, L + 120, y + 40, ps, width=3, center=False)
        for i, line in enumerate(wrap(p["sub"], font("sans", 42, 400), R - L)):
            draw_text(frame, line, L, y + 78 + i * 58, "sans", 42, 400, C.IVORY,
                      alpha=ps * 0.9, dy=(1 - ps) * 14)


# --- bars ------------------------------------------------------------------
def _bar_times(sc):
    items = sc["params"]["items"]
    return [beat(sc, it.get("beat"), 1.0 + i * 0.7) + it.get("delay", 0.15)
            for i, it in enumerate(items)]


@scene("bars")
def bars(frame, d, t, sc):
    p = sc["params"]
    kicker(frame, d, t, p.get("kicker"))
    y = headline(frame, t, p["title"], 380, 0.3)
    items, times = p["items"], _bar_times(sc)
    vmax = p.get("max") or max(it["value"] for it in items)
    unit = p.get("unit", "")
    row_h = min(250, (C.SAFE_BOTTOM - 80 - (y + 60)) // len(items))
    y += 60
    bar_w = R - L - 280
    for it, st in zip(items, times):
        pa = ease_out(prog(t, st, 0.5))
        pg = ease_out_expo(prog(t, st + 0.1, 1.5))
        hi = it.get("highlight")
        col = C.GOLD if hi else C.IVORY
        draw_text(frame, it["label"], L, y, "sans", 42, 500, C.IVORY if hi else C.MUTED,
                  alpha=pa, dy=(1 - pa) * 10)
        by = y + 72
        rrect(d, [L, by, L + bar_w, by + 76], 6, fill=rgba(C.IVORY, 0.05 * pa))
        w = max(6, bar_w * it["value"] / vmax * pg)
        if pa > 0:
            if hi:  # weicher Schein hinter dem Hauptbalken
                rrect(d, [L - 6, by - 6, L + w + 6, by + 82], 10, fill=rgba(C.GOLD, 0.10 * pa))
            rrect(d, [L, by, L + w, by + 76], 6, fill=rgba(col, (1.0 if hi else 0.78) * pa))
        val = it["value"] * pg
        txt = fmt_num(val, it.get("decimals", 0)) + (f" {unit}" if unit else "")
        draw_text(frame, txt, R, by - 26 if hi else by - 12, "serif", 96 if hi else 72, 700, col,
                  alpha=pa, anchor="r", glow=12 if hi else 0)
        if it.get("note"):
            draw_text(frame, it["note"], L, by + 72, "sans", 28, 400, C.MUTED, alpha=pa * 0.9)
        y += row_h
    source_line(frame, t, p.get("source"), times[0] + 0.3)


# --- compare ---------------------------------------------------------------
@scene("compare")
def compare(frame, d, t, sc):
    p = sc["params"]
    kicker(frame, d, t, p.get("kicker"))
    y = headline(frame, t, p["title"], 380, 0.3) + 50
    cards = p["cards"]
    ch = min(330, (C.SAFE_BOTTOM - y - 40 * (len(cards) - 1)) // len(cards))
    for i, card in enumerate(cards):
        st = beat(sc, card.get("beat"), 1.2 + i * 1.4)
        pa = ease_out(prog(t, st, 0.7))
        hi = card.get("highlight")
        col = C.GOLD if hi else C.IVORY
        top = y + (1 - pa) * 30
        rrect(d, [L, top, R, top + ch], 18, fill=rgba(C.PANEL, 0.82 * pa),
              outline=rgba(col, (0.9 if hi else 0.22) * pa), width=3 if hi else 2)
        draw_text(frame, card["head"].upper(), L + 44, top + 36, "sans", 30, 600,
                  col if hi else C.MUTED, alpha=pa, tracking=6)
        # Fluss: A ——> B, ein Lichtpunkt wandert dauerhaft über den Pfeil
        a, b = card["flow"]
        fy = top + 104
        f = fit_font(a + b, "serif", 76, 700, R - L - 88 - 200)
        wa = draw_text(frame, a, L + 44, fy, "serif", f.size, 700, C.IVORY, alpha=pa)
        wb = text_w(b, f)
        draw_text(frame, b, R - 44, fy, "serif", f.size, 700, col, alpha=pa, anchor="r",
                  glow=10 if hi else 0)
        x0, x1 = L + 44 + wa + 30, R - 44 - wb - 30
        ay = fy + f.size * 0.72
        pl = ease_in_out(prog(t, st + 0.35, 0.8))
        xe = lerp(x0, x1, pl)
        if pl > 0:
            d.line([(x0, ay), (xe, ay)], fill=rgba(col, 0.75 * pa), width=3)
            d.polygon([(xe + 4, ay), (xe - 16, ay - 10), (xe - 16, ay + 10)], fill=rgba(col, pa))
        if pl >= 1:
            cyc = ((t - st) * (0.9 if hi else 0.45)) % 1
            dx = lerp(x0, x1 - 16, cyc)
            fade = math.sin(cyc * math.pi)
            for rad, al in ((16, 0.14), (9, 0.3), (5, 1.0)):
                d.ellipse([dx - rad, ay - rad, dx + rad, ay + rad], fill=rgba(col, al * fade))
        if hi and card.get("loop") and pl >= 1:
            # Rückfluss: Ertrag wird wieder zu Kapital (gestrichelter Bogen)
            pb = ease_in_out(prog(t, st + 1.3, 1.0))
            n = int(22 * pb)
            for k in range(n):
                u = k / 21
                bx = lerp(x1, x0, u)
                byy = ay + 20 + math.sin(u * math.pi) * 30
                d.ellipse([bx - 3, byy - 3, bx + 3, byy + 3], fill=rgba(C.GOLD, 0.65))
        note_y = top + ch - 78
        nf = fit_font(card["note"], "sans", 38, 400, R - L - 88)
        draw_text(frame, card["note"], L + 44, note_y, "sans", nf.size, 400, C.IVORY,
                  alpha=pa * 0.88)
        y += ch + 40


# --- growth ----------------------------------------------------------------
def _growth_window(sc):
    p = sc["params"]
    st = beat(sc, p.get("start_beat"), 1.4) + 0.2
    end = beat(sc, p.get("end_beat"), sc["duration"] - 2.0) + p.get("end_offset", 1.6)
    return st, max(2.5, min(end, sc["duration"] - 0.8) - st)


@scene("growth")
def growth(frame, d, t, sc):
    p = sc["params"]
    kicker(frame, d, t, p.get("kicker"))
    y = headline(frame, t, p["title"], 380, 0.3)
    rate, years = p["rate"], p["years"]
    series = p["principals"]
    st, dur = _growth_window(sc)
    pa = ease_out(prog(t, st - 0.5, 0.6))
    yr = years * ease_in_out(prog(t, st, dur))
    x0, x1, y1 = L + 10, R - 20, C.SAFE_BOTTOM - 170
    y0 = y + 320
    vmax = max(s["value"] for s in series) * (1 + rate) ** years

    # Parameter-Chip + Jahreszähler
    chip = p.get("chip", f"{fmt_num(rate * 100, 0)} % Rendite pro Jahr")
    cw = text_w(chip, font("sans", 30, 600)) + 48
    rrect(d, [L, y + 26, L + cw, y + 86], 30, outline=rgba(C.GOLD, 0.8 * pa), width=2)
    draw_text(frame, chip, L + 24, y + 36, "sans", 30, 600, C.GOLD, alpha=pa)
    draw_text(frame, f"Jahr {int(yr):d}", R, y + 14, "serif", 64, 700, C.IVORY, alpha=pa, anchor="r")

    # Achsen
    for g in range(5):
        gy = lerp(y1, y0, g / 4)
        d.line([(x0, gy), (x1, gy)], fill=rgba(C.IVORY, (0.16 if g == 0 else 0.055) * pa), width=2 if g == 0 else 1)
    for k in range(0, years + 1, 10):
        gx = lerp(x0, x1, k / years)
        draw_text(frame, str(k), gx, y1 + 16, "sans", 28, 400, C.MUTED, alpha=pa, anchor="c")
    draw_text(frame, "Jahre", x1, y1 + 56, "sans", 26, 400, C.MUTED, alpha=pa * 0.9, anchor="r")

    order = sorted(series, key=lambda s: s["value"])
    # Legende mit laufenden Werten (über dem Diagramm, kollidiert nie mit den Kurven)
    colw = (R - L) / len(order)
    for idx, s in enumerate(order):
        hi = s is order[-1]
        col = C.GOLD if hi else C.IVORY
        lx = L + idx * colw
        v = s["value"] * (1 + rate) ** yr
        d.ellipse([lx, y + 136, lx + 18, y + 154], fill=rgba(col, pa))
        draw_text(frame, s["label"], lx + 30, y + 124, "sans", 32, 500, C.MUTED, alpha=pa)
        vf = fit_font(money(vmax), "serif", 66 if hi else 56, 700, colw - 24)
        draw_text(frame, money(v), lx, y + 170 + (0 if hi else 8), "serif", vf.size if hi else min(vf.size, 56),
                  700, col, alpha=pa, glow=10 if hi else 0)
    if t < st:
        return
    for idx, s in enumerate(order):
        hi = s is order[-1]
        col = C.GOLD if hi else C.IVORY
        steps = max(2, int(yr * 4) + 1)
        pts = []
        for k in range(steps + 1):
            a = yr * k / steps
            v = s["value"] * (1 + rate) ** a
            pts.append((lerp(x0, x1, a / years), lerp(y1, y0, v / vmax)))
        if hi:  # Fläche unter der Kurve
            d.polygon(pts + [(pts[-1][0], y1), (x0, y1)], fill=rgba(C.GOLD, 0.10))
        d.line(pts, fill=rgba(col, 0.95), width=6 if hi else 4, joint="curve")
        ex, ey = pts[-1]
        for rad, al in ((22, 0.12), (13, 0.28), (7, 1.0)):
            d.ellipse([ex - rad, ey - rad, ex + rad, ey + rad], fill=rgba(col, al))
    source_line(frame, t, p.get("footnote"), st)


# --- formula ---------------------------------------------------------------
@scene("formula")
def formula(frame, d, t, sc):
    p = sc["params"]
    kicker(frame, d, t, p.get("kicker"))
    st = beat(sc, p.get("formula_beat"), 0.6) + p.get("formula_delay", 0.0)
    # Hintergrund: zwei auseinanderlaufende Kurven (r oben, g unten)
    pc = ease_in_out(prog(t, st, 3.0))
    if pc > 0:
        for k, (growth_k, col, a) in enumerate(((1.9, C.GOLD, 0.30), (0.75, C.IVORY, 0.14))):
            pts = []
            n = int(60 * pc) + 1
            for i in range(n + 1):
                u = i / 60
                pts.append((lerp(L, R, u), 1180 - (math.exp(u * growth_k) - 1) * 150))
            d.line(pts, fill=rgba(col, a), width=4, joint="curve")
    parts = p["formula"]            # z. B. ["r", ">", "g"]
    size = 330
    f = font("serif_italic", size, 600)
    gap = 70
    total = sum(text_w(s, f) for s in parts) + gap * (len(parts) - 1)
    x = CX - total / 2
    for i, s in enumerate(parts):
        pi = ease_out(prog(t, st + i * 0.38, 0.7))
        col = C.GOLD if i == 0 else C.IVORY
        draw_text(frame, s, x, 520, "serif_italic", size, 600, col, alpha=pi,
                  glow=18 if i == 0 else 0, scale=lerp(1.12, 1.0, pi))
        x += text_w(s, f) + gap
    y = 990
    for i, (sym, txt) in enumerate(p.get("legend", [])):
        pi = ease_out(prog(t, beat(sc, p.get("legend_beat"), st + 1.4) + i * 0.45, 0.6))
        draw_text(frame, sym, L + 20, y - 14, "serif_italic", 70, 600,
                  C.GOLD if i == 0 else C.IVORY, alpha=pi)
        draw_text(frame, "=", L + 96, y, "sans", 40, 400, C.MUTED, alpha=pi)
        draw_text(frame, txt, L + 150, y, "sans", 42, 500, C.IVORY, alpha=pi, dy=(1 - pi) * 10)
        y += 92
    if p.get("note"):
        pn = ease_out(prog(t, beat(sc, p.get("note_beat"), sc["duration"] - 3.0), 0.6))
        nf = fit_font(p["note"], "sans", 30, 500, R - L - 60)
        w = text_w(p["note"], nf) + 56
        rrect(d, [L, y + 16, L + w, y + 78], 31, outline=rgba(C.GOLD, 0.7 * pn), width=2)
        draw_text(frame, p["note"], L + 28, y + 27, "sans", nf.size, 500, C.GOLD, alpha=pn)
    source_line(frame, t, p.get("source"), st + 0.8)


# --- outro -----------------------------------------------------------------
@scene("outro")
def outro(frame, d, t, sc):
    p = sc["params"]
    lines = p.get("lines", [])
    longest = max((l.replace("*", "") for l in lines), key=len) if lines else ""
    f = fit_font(longest, "serif", 92, 700, R - L)
    lh = int(f.size * 1.2)
    y = 430
    for i, line in enumerate(lines):
        st = beat(sc, p.get("line_beats", [None] * len(lines))[i], 0.3 + i * 0.9)
        reveal_words(frame, parse_marked(line), CX, y, t, st, "serif", f.size, 700, glow=12)
        y += lh
    st = beat(sc, p.get("brand_beat"), 0.3 + len(lines) * 0.9)
    pb = ease_out(prog(t, st, 0.9))
    by = y + 150
    rule(d, CX - 210, CX + 210, by, ease_in_out(prog(t, st, 1.0)), width=2)
    draw_text(frame, C.BRAND, CX + 9, by + 44, "sans", 66, 600, C.IVORY, alpha=pb,
              anchor="c", tracking=18, scale=lerp(1.06, 1.0, pb))
    if p.get("tagline"):
        pt = ease_out(prog(t, st + 0.5, 0.8))
        draw_text(frame, p["tagline"], CX, by + 150, "serif_italic", 46, 500, C.GOLD,
                  alpha=pt, anchor="c", glow=8)
    src = p.get("sources", [])
    if src:
        ps = ease_out(prog(t, st + 0.9, 0.8))
        sy = C.SAFE_BOTTOM - 30 - 42 * len(src)
        draw_text(frame, "QUELLEN", CX, sy - 50, "sans", 24, 600, C.MUTED, alpha=ps,
                  anchor="c", tracking=5)
        for i, s in enumerate(src):
            sf = fit_font(s, "sans", 29, 400, R - L)
            draw_text(frame, s, CX, sy + i * 42, "sans", sf.size, 400, C.MUTED,
                      alpha=ps * 0.95, anchor="c")


# --- Soundeffekt-Ereignisse je Szene --------------------------------------
def events(sc):
    """[(lokale Zeit, Art, Lautstärke)] – Arten: hit, tick, riser, shimmer."""
    typ, ev = sc["type"], []
    if typ == "title":
        ev.append((0.35, "hit", 1.0))
    elif typ == "bars":
        for it, st in zip(sc["params"]["items"], _bar_times(sc)):
            ev.append((st, "hit" if it.get("highlight") else "tick", 0.8))
    elif typ == "compare":
        for i, card in enumerate(sc["params"]["cards"]):
            ev.append((beat(sc, card.get("beat"), 1.2 + i * 1.4), "tick", 0.9))
    elif typ == "growth":
        st, dur = _growth_window(sc)
        ev.append((st, f"riser:{dur:.2f}", 0.8))
        ev.append((st + dur, "hit", 0.9))
    elif typ == "formula":
        p = sc["params"]
        ev.append((beat(sc, p.get("formula_beat"), 0.6) + p.get("formula_delay", 0.0), "hit", 1.0))
    elif typ == "outro":
        p = sc["params"]
        ev.append((beat(sc, p.get("brand_beat"), 0.3 + len(p.get("lines", [])) * 0.9), "shimmer", 1.0))
    return ev
