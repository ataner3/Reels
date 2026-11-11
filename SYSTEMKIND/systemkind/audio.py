"""Sounddesign: prozedurale Musik + Soundeffekte (eigene Assets, keine
Fremdlizenzen), Mischung mit Ducking und Lautheits-Normalisierung (FFmpeg)."""
from __future__ import annotations

import json
import re
import subprocess
import wave

import numpy as np

from . import config as C

SR = C.AUDIO_SR
NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def hz(name: str) -> float:
    m = re.match(r"([A-G]#?)(\d)", name)
    return 440.0 * 2 ** ((NOTE[m[1]] + (int(m[2]) + 1) * 12 - 69) / 12)


def _fftconv(x, ir):
    n = len(x) + len(ir) - 1
    size = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:n]


def reverb(x, seconds=2.2, wet=0.3, seed=1):
    """Einfacher Faltungshall mit abklingendem Rauschen. x: (n, 2)."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    env = np.exp(-np.arange(n) / (seconds * SR / 6.5))
    out = np.empty_like(x)
    for ch in range(2):
        ir = rng.standard_normal(n) * env
        ir /= np.sqrt(np.sum(ir ** 2))
        out[:, ch] = x[:, ch] + wet * _fftconv(x[:, ch], ir)[: len(x)]
    return out


def _band(noise, lo, hi):
    spec = np.fft.rfft(noise)
    f = np.fft.rfftfreq(len(noise), 1 / SR)
    spec[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(spec, len(noise))


# --- Musik -----------------------------------------------------------------
PROGRESSION = [  # d-Moll, je 8 Sekunden
    ["D2", "A2", "D3", "F3", "A3"],
    ["A#1", "F2", "D3", "F3", "A#3"],
    ["F2", "C3", "F3", "A3", "C4"],
    ["C2", "G2", "E3", "G3", "C4"],
]
MELODY = ["D4", "F4", "A4", "D5", "E4", "G4", "C5", "A4"]


def music(duration: float, seed: int = 3) -> np.ndarray:
    """Dunkles Ambient-Bett: Pad-Akkorde, tiefer Puls, vereinzelte Klaviertöne."""
    rng = np.random.default_rng(seed)
    n = int(duration * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    bar = 8.0
    for k in range(int(duration / bar) + 1):
        chord = PROGRESSION[k % len(PROGRESSION)]
        a, b = int(max(k * bar - 1.5, 0) * SR), int(min((k + 1) * bar + 1.5, duration) * SR)
        if a >= b:
            continue
        tt = t[a:b] - t[a]
        env = np.clip(tt / 2.5, 0, 1) * np.clip((tt[-1] - tt) / 2.5, 0, 1)
        env = np.sin(env * np.pi / 2) ** 2
        for j, name in enumerate(chord):
            f0 = hz(name)
            for ch, det in enumerate((1 - 0.0016, 1 + 0.0016)):
                sig = np.zeros(b - a)
                for h in range(1, 6):
                    sig += np.sin(2 * np.pi * f0 * det * h * tt + rng.uniform(0, 6.28)) / h ** 1.9
                lfo = 0.8 + 0.2 * np.sin(2 * np.pi * (0.07 + 0.03 * j) * tt + j)
                out[a:b, ch] += sig * env * lfo * (0.11 if j else 0.16)
    # tiefer Puls (60 BPM, jede zweite Zählzeit)
    pulse_len = int(0.9 * SR)
    pt = np.arange(pulse_len) / SR
    pulse = np.sin(2 * np.pi * (hz("D2") * pt + 18 * np.exp(-pt * 9) / 9)) * np.exp(-pt * 5.5)
    for beat_t in np.arange(4.0, duration - 2.5, 2.0):
        a = int(beat_t * SR)
        seg = pulse[: n - a]
        out[a:a + len(seg), :] += seg[:, None] * 0.20
    # Klaviertöne: sparsam, mit Echo
    for k, beat_t in enumerate(np.arange(2.0, duration - 4.0, 4.0)):
        f0 = hz(MELODY[(k * 3 + seed) % len(MELODY)])
        ln = int(3.2 * SR)
        nt = np.arange(ln) / SR
        tone = (np.sin(2 * np.pi * f0 * nt) + 0.35 * np.sin(2 * np.pi * 2 * f0 * nt) * np.exp(-nt * 3)
                + 0.12 * np.sin(2 * np.pi * 3 * f0 * nt) * np.exp(-nt * 6)) * np.exp(-nt * 1.5)
        tone *= np.clip(nt / 0.008, 0, 1)
        pan = 0.35 + 0.3 * ((k * 7) % 5) / 4
        for echo, g in ((0.0, 1.0), (0.375, 0.38), (0.75, 0.16)):
            a = int((beat_t + echo) * SR)
            seg = tone[: max(n - a, 0)]
            out[a:a + len(seg), 0] += seg * g * 0.085 * (1 - pan)
            out[a:a + len(seg), 1] += seg * g * 0.085 * pan
    out = reverb(out, 2.6, 0.35, seed)
    fade = np.clip(t / 1.2, 0, 1) * np.clip((duration - t) / 2.2, 0, 1)
    out *= fade[:, None]
    return (out / np.max(np.abs(out)) * 0.5).astype(np.float32)


# --- Soundeffekte ----------------------------------------------------------
def sfx(kind: str, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed + 11)
    if kind == "hit":
        t = np.arange(int(1.4 * SR)) / SR
        body = np.sin(2 * np.pi * (42 * t + 55 * (1 - np.exp(-t * 14)) / 14)) * np.exp(-t * 3.6)
        click = _band(rng.standard_normal(len(t)), 200, 2500) * np.exp(-t * 60) * 0.25
        mono = body * 0.9 + click
    elif kind == "tick":
        t = np.arange(int(0.25 * SR)) / SR
        mono = (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t * 45) * 0.35
        mono += np.sin(2 * np.pi * 110 * t) * np.exp(-t * 30) * 0.4
    elif kind == "whoosh":
        ln = int(0.8 * SR)
        t = np.arange(ln) / SR
        noise = rng.standard_normal(ln)
        lo, mid, hi = _band(noise, 150, 700), _band(noise, 700, 2500), _band(noise, 2500, 7000)
        u = t / t[-1]
        mono = (lo * (1 - u) + mid * np.sin(u * np.pi) + hi * u * 0.6) * np.sin(u * np.pi) ** 2 * 0.5
    elif kind.startswith("riser"):
        dur = float(kind.split(":")[1]) if ":" in kind else 3.0
        ln = int(dur * SR)
        t = np.arange(ln) / SR
        u = t / dur
        phase = 2 * np.pi * np.cumsum(110 + 180 * u ** 2) / SR
        mono = (np.sin(phase) * 0.25 + np.sin(phase * 1.5) * 0.1) * u ** 2
        mono += _band(rng.standard_normal(ln), 1500, 6000) * u ** 3 * 0.08
        mono *= np.clip((dur - t) / 0.05, 0, 1)
    elif kind == "shimmer":
        t = np.arange(int(3.2 * SR)) / SR
        mono = sum(np.sin(2 * np.pi * hz(nm) * t + i) * np.exp(-t * (1.1 + 0.3 * i))
                   for i, nm in enumerate(["D5", "A5", "D6", "F6"])) * np.clip(t / 0.25, 0, 1) * 0.12
    else:
        raise ValueError(f"Unbekannter Soundeffekt: {kind}")
    st = np.stack([mono, mono], 1)
    if kind in ("hit", "shimmer", "tick"):
        st = reverb(np.concatenate([st, np.zeros((SR, 2))]), 1.6, 0.25, seed + 5)
    return st.astype(np.float32)


def sfx_track(events, duration: float) -> np.ndarray:
    n = int(duration * SR)
    out = np.zeros((n, 2), np.float32)
    level = {"hit": 0.55, "tick": 0.32, "whoosh": 0.42, "riser": 0.2, "shimmer": 0.6}
    cache = {}
    for i, (t, kind, gain) in enumerate(events):
        if kind not in cache:
            cache[kind] = sfx(kind, len(cache))
        a = max(int(t * SR), 0)
        seg = cache[kind][: n - a]
        out[a:a + len(seg)] += seg * gain * level[kind.split(":")[0]]
    return out


# --- Dateien & Mischung ----------------------------------------------------
def write_wav(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1:
        x = x[:, None]
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(x.shape[1])
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((x * 32767).astype("<i2").tobytes())


def mix(vo_path, music_path, sfx_path, out_path, duration: float) -> dict:
    """Stimme aufbereiten, Musik unter der Stimme absenken (Sidechain),
    alles mischen und in zwei Durchgängen auf Ziel-Lautheit normalisieren."""
    graph = (
        "[0:a]highpass=f=70,equalizer=f=220:t=q:w=1.2:g=-2,equalizer=f=4200:t=q:w=1.0:g=2,"
        "acompressor=threshold=-21dB:ratio=3:attack=6:release=140:makeup=2.5,"
        "aformat=channel_layouts=stereo,asplit=2[vo][key];"
        "[1:a]volume=0.62[mus];"
        "[mus][key]sidechaincompress=threshold=0.02:ratio=5:attack=20:release=420[duck];"
        "[vo][duck][2:a]amix=inputs=3:normalize=0:duration=longest[mix]"
    )
    inputs = ["-i", str(vo_path), "-i", str(music_path), "-i", str(sfx_path)]
    base = ["ffmpeg", "-nostdin", "-y", "-v", "info"] + inputs
    ln = f"loudnorm=I={C.TARGET_LUFS}:TP=-2.0:LRA=11"
    p = subprocess.run(base + ["-filter_complex", graph + f";[mix]{ln}:print_format=json[o]",
                               "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr)
    if not m:
        raise RuntimeError("Lautheitsmessung fehlgeschlagen:\n" + p.stderr[-800:])
    st = json.loads(m.group(0))
    ln2 = (f"{ln}:measured_I={st['input_i']}:measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}"
           f":measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error"] + inputs + [
        "-filter_complex", graph + f";[mix]{ln2},alimiter=limit=0.8:level=disabled[o]", "-map", "[o]",
        "-t", f"{duration:.3f}", "-ar", str(SR), "-ac", "2", str(out_path)], check=True)
    return st
