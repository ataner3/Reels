"""Qualitätskontrolle der fertigen Datei."""
from __future__ import annotations

import json
import re
import subprocess

import numpy as np

from . import config as C


def _run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path) -> dict:
    out = _run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]).stdout
    j = json.loads(out)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    return {"video": v, "audio": a, "format": j["format"]}


def check(path, tl, srt_path=None, audio_stats=None) -> list[dict]:
    """Gibt eine Liste von Prüfungen zurück: {name, ok, detail}."""
    res = []

    def add(name, ok, detail):
        res.append({"name": name, "ok": bool(ok), "detail": str(detail)})

    info = probe(path)
    v, a, fmt = info["video"], info["audio"], info["format"]
    dur = float(fmt["duration"])
    add("Container MP4", "mp4" in fmt["format_name"], fmt["format_name"])
    add("Video-Codec H.264", v["codec_name"] == "h264", f"{v['codec_name']} ({v.get('profile')})")
    add("Auflösung 1080 × 1920", (v["width"], v["height"]) == (C.W, C.H), f"{v['width']} × {v['height']}")
    add("Seitenverhältnis 9:16", v["width"] * 16 == v["height"] * 9, f"{v['width']}:{v['height']}")
    add("Bildrate 30 FPS", v["r_frame_rate"] == f"{C.FPS}/1", v["r_frame_rate"])
    add("Pixelformat yuv420p", v["pix_fmt"] == "yuv420p", v["pix_fmt"])
    add("Audio-Codec AAC", a and a["codec_name"] == "aac", a and f"{a['codec_name']}, {a['sample_rate']} Hz, {a['channels']} Kanäle")
    add(f"Länge {C.MIN_DURATION:.0f}–{C.MAX_DURATION:.0f} s", C.MIN_DURATION <= dur <= C.MAX_DURATION, f"{dur:.2f} s")
    if a:
        diff = abs(float(v.get("duration", dur)) - float(a.get("duration", dur)))
        add("Bild und Ton gleich lang", diff < 0.12, f"Abweichung {diff:.3f} s")

    dec = _run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-f", "null", "-"])
    add("Datei vollständig dekodierbar", dec.returncode == 0 and not dec.stderr.strip(),
        dec.stderr.strip()[:200] or "keine Fehler")

    det = _run(["ffmpeg", "-nostdin", "-v", "info", "-i", str(path), "-vf", "blackdetect=d=0.6:pic_th=0.995:pix_th=0.04",
                "-af", "silencedetect=n=-45dB:d=1.2", "-f", "null", "-"]).stderr
    black = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", det)
    add("Keine Schwarzbilder", not black, black or "keine")
    sil = re.findall(r"silence_start: ([\d.]+)", det)
    add("Keine Tonlücken", not sil, [f"{float(s):.1f}s" for s in sil] or "keine")

    ln = _run(["ffmpeg", "-nostdin", "-v", "info", "-i", str(path), "-af", "loudnorm=print_format=json", "-f", "null", "-"]).stderr
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", ln)
    if m:
        st = json.loads(m.group(0))
        i, tp = float(st["input_i"]), float(st["input_tp"])
        add(f"Lautheit {C.TARGET_LUFS:.0f} LUFS (±1,5)", abs(i - C.TARGET_LUFS) <= 1.5, f"{i:.1f} LUFS")
        add("True Peak ≤ −1 dBTP", tp <= -0.9, f"{tp:.1f} dBTP")
    else:
        add("Lautheit messbar", False, "Messung fehlgeschlagen")

    if audio_stats and "voice_over_bg_db" in audio_stats:
        v, g = audio_stats["voice_over_bg_db"], audio_stats.get("vo_gain_db") or 0
        add(f"Stimme ≥ {C.MIN_VOICE_OVER_BG_DB:.0f} dB über Musik und Effekten", v >= C.MIN_VOICE_OVER_BG_DB,
            f"{v:.1f} dB" + (f" (Stimme um {g + (audio_stats.get('vo_trim_db') or 0):+.1f} dB angeglichen)" if g else ""))

    cues = tl["cues"]
    overlaps = sum(1 for x, y in zip(cues, cues[1:]) if x["end"] > y["start"] + 1e-6)
    add("Untertitel vorhanden", len(cues) > 0, f"{len(cues)} Einblendungen")
    add("Untertitel ohne Überlappung", overlaps == 0, f"{overlaps} Überlappungen")
    add("Untertitel innerhalb der Laufzeit", cues and cues[-1]["end"] <= dur + 0.05, f"letzte endet bei {cues[-1]['end']:.2f} s" if cues else "-")
    longest = max((len(c["text"]) for c in cues), default=0)
    add("Untertitel-Zeilenlänge ≤ 30 Zeichen", longest <= 30, f"längste Zeile: {longest} Zeichen")
    short = [c["text"] for c in cues if c["end"] - c["start"] < 0.3]
    add("Untertitel lang genug lesbar", not short, short or "alle ≥ 0,3 s")
    if srt_path:
        n = len(re.findall(r"-->", open(srt_path, encoding="utf-8").read()))
        add("SRT-Datei vollständig", n == len(cues), f"{n} Einträge")

    # Jede Szene muss sichtbaren Inhalt haben (keine leeren Platzhalter)
    empty = []
    for sc in tl["scenes"]:
        T = sc["start"] + sc["duration"] * 0.8
        raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{T:.3f}", "-i", str(path), "-frames:v", "1",
                              "-vf", "scale=270:480,crop=270:330:0:50", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                             capture_output=True).stdout
        img = np.frombuffer(raw, np.uint8)
        if not len(img) or (img > 120).mean() < 0.004:
            empty.append(sc["id"])
    add("Alle Szenen haben Bildinhalt", not empty, empty or f"{len(tl['scenes'])} Szenen geprüft")
    return res


def frame_grab(path, T):
    from PIL import Image
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{T:.3f}", "-i", str(path), "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return Image.frombuffer("RGB", (C.W, C.H), raw, "raw", "RGB", 0, 1)
