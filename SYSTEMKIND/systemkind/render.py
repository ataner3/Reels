"""Renderer: Pillow zeichnet die Bilder, FFmpeg kodiert.
Die Timeline wird in Abschnitte geteilt und parallel gerendert."""
from __future__ import annotations

import multiprocessing as mp
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw

from . import config as C
from . import gfx
from .gfx import clamp, ease_in_out, ease_out, prog, rgba
from .scenes import REGISTRY

W, H = C.W, C.H
_TL = None            # Timeline im Worker-Prozess
_BROLL = {}


# --- B-Roll ----------------------------------------------------------------
class Broll:
    """Liest einen Clip bildweise über FFmpeg: auf 9:16 beschnitten,
    entsättigt und abgedunkelt, damit er zur Marke passt. Läuft in Schleife."""
    VF = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={C.FPS},"
          "eq=saturation=0.3:contrast=1.1:brightness=-0.08,"
          "colorchannelmixer=rr=1.04:bb=0.9,gblur=sigma=1.0")

    def __init__(self, path):
        self.path, self.proc, self.next, self.last = path, None, -1, None

    def _open(self, idx):
        if self.proc:
            self.proc.kill()
        from .assets import probe
        start = (idx / C.FPS) % max(probe(self.path)["duration"] - 0.1, 0.1)
        self.proc = subprocess.Popen(
            ["ffmpeg", "-nostdin", "-v", "error", "-stream_loop", "-1", "-ss", f"{start:.3f}", "-i", self.path,
             "-an", "-vf", self.VF, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.next = idx

    def frame(self, idx) -> Image.Image:
        if self.last is not None and idx == self.next - 1:
            return self.last.copy()
        if self.proc is None or idx != self.next:
            self._open(idx)
        buf = self.proc.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            raise RuntimeError(f"B-Roll konnte nicht gelesen werden: {self.path}")
        self.next += 1
        self.last = Image.frombuffer("RGB", (W, H), buf, "raw", "RGB", 0, 1)
        return self.last.copy()


# --- Einzelbild ------------------------------------------------------------
def scene_frame(sc, t) -> Image.Image:
    tt = max(t, 0.0)
    if sc.get("broll_file"):
        rd = _BROLL.setdefault(sc["broll_file"], Broll(sc["broll_file"]))
        frame = rd.frame(int(round(tt * C.FPS)))
        gfx.scrim(frame, 0.68)
    else:
        frame = gfx.background(sc["background"], sc["start"] + tt, seed=sc["index"] + 1)
    d = ImageDraw.Draw(frame, "RGBA")
    REGISTRY[sc["type"]](frame, d, tt, sc)
    # sanfter Zoom, abwechselnd hinein und heraus
    u = clamp(t / sc["duration"], -0.1, 1.1)
    z = 1.0 + 0.04 * (u if sc["index"] % 2 == 0 else 1 - u) + 0.004
    bw, bh = W / z, H / z
    box = ((W - bw) / 2, (H - bh) / 2, (W + bw) / 2, (H + bh) / 2)
    return frame.resize((W, H), Image.BICUBIC, box=box)


_GRAD = None


def _transition(kind, a: Image.Image, b: Image.Image, p: float) -> Image.Image:
    global _GRAD
    e = ease_in_out(p)
    if kind == "cut":
        return b if p >= 0.5 else a
    if kind == "dip":
        bg = Image.new("RGB", (W, H), C.BG)
        return Image.blend(a, bg, ease_in_out(p * 2)) if p < 0.5 else Image.blend(bg, b, ease_in_out(p * 2 - 1))
    if kind == "push":
        out = Image.new("RGB", (W, H), C.BG)
        out.paste(Image.blend(a, Image.new("RGB", (W, H), C.BG), e * 0.7), (0, -int(e * H * 0.3)))
        out.paste(b, (0, int((1 - e) * H)))
        return out
    if kind == "sweep":
        if _GRAD is None:
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            _GRAD = 1 - (yy / H * 0.8 + xx / W * 0.2)      # Lichtkante läuft von unten nach oben
        edge = e * 1.3 - 0.15
        m = np.clip((edge - _GRAD) / 0.16 + 0.5, 0, 1)[..., None]
        band = np.exp(-((_GRAD - edge) / 0.05) ** 2)[..., None] * 0.55 * np.sin(p * np.pi)
        arr = np.asarray(a, np.float32) * (1 - m) + np.asarray(b, np.float32) * m
        arr += band * np.array(C.GOLD, np.float32)
        return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    return Image.blend(a, b, e)                              # fade


def _caption(frame, d, tl, T):
    cue = next((c for c in tl["cues"] if c["start"] <= T < c["end"]), None)
    if not cue:
        return
    size = 60
    f = gfx.fit_font(cue["text"], "sans", size, 700, C.SAFE_R - C.SAFE_L - 40)
    space = gfx.glen(f, " ")
    total = sum(gfx.glen(f, w) for w, _, _ in cue["words"]) + space * (len(cue["words"]) - 1)
    p = ease_out(prog(T, cue["start"], 0.12))
    x, y = W / 2 - total / 2, C.CAPTION_Y - f.size * 0.62
    gfx.rrect(d, [x - 34, y - 14, x + total + 34, y + f.size * 1.24 + 14], 22,
              fill=rgba(C.BG, 0.72 * p))
    for w, ws, we in cue["words"]:
        active = ws <= T < we
        col = C.GOLD if active else C.IVORY
        gfx.draw_text(frame, w, x, y, "sans", f.size, 700, col, alpha=p, dy=(1 - p) * 8)
        x += gfx.glen(f, w) + space


def _branding(frame, d, tl, T):
    scs = tl["scenes"]
    first = scs[1]["start"] if scs[0]["type"] == "title" and len(scs) > 1 else 0.0
    last = scs[-1]["start"] if scs[-1]["type"] == "outro" else tl["duration"]
    a = clamp((T - first) / 0.5) * clamp((last - T) / 0.4)
    if a <= 0:
        return
    gfx.draw_text(frame, C.BRAND, W / 2 + 5, 150, "sans", 26, 600, C.IVORY, alpha=0.62 * a,
                  anchor="c", tracking=10)
    x0, x1, y = W / 2 - 110, W / 2 + 110, 204
    d.line([(x0, y), (x1, y)], fill=rgba(C.IVORY, 0.14 * a), width=2)
    d.line([(x0, y), (x0 + (x1 - x0) * T / tl["duration"], y)], fill=rgba(C.GOLD, 0.9 * a), width=2)


def frame_at(tl, T) -> Image.Image:
    """Fertiges Bild zum Zeitpunkt T (Sekunden)."""
    scs = tl["scenes"]
    i = max(k for k, s in enumerate(scs) if s["start"] <= T + 1e-6)
    sc, half = scs[i], C.TRANSITION / 2
    if i + 1 < len(scs) and T > scs[i + 1]["start"] - half and scs[i + 1]["transition"] != "cut":
        nxt = scs[i + 1]
        p = (T - (nxt["start"] - half)) / C.TRANSITION
        frame = _transition(nxt["transition"], scene_frame(sc, T - sc["start"]),
                            scene_frame(nxt, T - nxt["start"]), p)
    elif i > 0 and T < sc["start"] + half and sc["transition"] != "cut":
        prev = scs[i - 1]
        p = (T - (sc["start"] - half)) / C.TRANSITION
        frame = _transition(sc["transition"], scene_frame(prev, T - prev["start"]),
                            scene_frame(sc, T - sc["start"]), p)
    else:
        frame = scene_frame(sc, T - sc["start"])
    d = ImageDraw.Draw(frame, "RGBA")
    _branding(frame, d, tl, T)
    _caption(frame, d, tl, T)
    return frame


# --- Parallel-Rendering ----------------------------------------------------
def _init(tl):
    global _TL
    _TL = tl


def _render_part(job):
    idx, a, b, path = job
    enc = subprocess.Popen(
        ["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(C.FPS), "-i", "-", "-c:v", "libx264", "-preset", "ultrafast", "-qp", "8",
         "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for fidx in range(a, b):
        enc.stdin.write(frame_at(_TL, fidx / C.FPS).tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError(f"FFmpeg-Fehler in Abschnitt {idx}")
    return idx, b - a


def render_video(tl, audio_path, out_path, work_dir, log=print):
    parts_dir = work_dir / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    n = tl["frames"]
    workers = max(1, min(os.cpu_count() or 2, 8))
    size = max(C.FPS, n // (workers * 3) + 1)
    jobs = [(i, a, min(a + size, n), str(parts_dir / f"part_{i:03d}.mp4"))
            for i, a in enumerate(range(0, n, size))]
    done = 0
    with mp.get_context("fork").Pool(workers, initializer=_init, initargs=(tl,)) as pool:
        for idx, cnt in pool.imap_unordered(_render_part, jobs):
            done += cnt
            log(f"  Bilder gerendert: {done}/{n}")
    lst = work_dir / "parts.txt"
    lst.write_text("".join(f"file '{j[3]}'\n" for j in jobs))
    dur = tl["duration"]
    vf = (f"noise=c0s=5:c0f=t+u,fade=t=in:st=0:d=0.4,"
          f"fade=t=out:st={dur - 0.45:.3f}:d=0.45,format=yuv420p")
    subprocess.run(
        ["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-i", str(audio_path), "-vf", vf, "-r", str(C.FPS),
         "-c:v", "libx264", "-profile:v", "high", "-level", "4.2", "-preset", "medium",
         "-crf", "19", "-maxrate", "10M", "-bufsize", "20M",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-c:a", "aac", "-b:a", "192k", "-ar", str(C.AUDIO_SR), "-ac", "2",
         "-t", f"{dur:.3f}", "-movflags", "+faststart", str(out_path)], check=True)
    for j in jobs:
        os.remove(j[3])


def contact_sheet(images, labels, path, cols=4):
    """Übersichtsbild aus Standbildern (für Review und Qualitätskontrolle)."""
    tw, th = 270, 480
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 12) + 12, rows * (th + 46) + 12), (30, 30, 34))
    d = ImageDraw.Draw(sheet)
    for i, (img, lab) in enumerate(zip(images, labels)):
        x, y = 12 + (i % cols) * (tw + 12), 12 + (i // cols) * (th + 46)
        sheet.paste(img.resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x, y + th + 8), lab, font=gfx.font("sans", 20, 500), fill=C.IVORY)
    sheet.save(path)
