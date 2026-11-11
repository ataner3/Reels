"""Timeline: Voice-over bestimmt die Szenenlängen; daraus entstehen
Szenen-Zeiten, Untertitel (SRT) und Soundeffekt-Ereignisse."""
from __future__ import annotations

import re

import numpy as np

from . import config as C
from . import scenes, tts


def build(project: dict, log=print) -> tuple[dict, np.ndarray]:
    """Gibt (timeline, voice_over_audio) zurück."""
    sr = C.AUDIO_SR
    vs = tts.settings(project)
    out, vo_parts, cues, sfx = [], [], [], []
    cursor = 0.0
    for i, sc in enumerate(project["scenes"]):
        t = C.VO_LEAD_IN
        beats, sents, wtimes = [], [], []
        for s in sc.get("vo", []):
            audio, words = tts.synth(tts.text_for(s, vs), vs)
            dur = len(audio) / sr
            beats.append(t)
            sents.append({"text": s["text"], "start": cursor + t, "dur": dur})
            vo_parts.append((cursor + t, audio))
            new = _cues(s["text"], cursor + t, dur, words)
            cues += new
            wtimes += [(w, float(ws - cursor)) for c in new for w, ws, _ in c["words"]]
            t += dur + C.VO_GAP
        duration = max(t - C.VO_GAP + C.VO_TAIL if sents else 0, sc.get("min_duration", 2.5))
        duration = round(duration * C.FPS) / C.FPS
        item = {"index": i, "id": sc.get("id", f"s{i+1}"), "type": sc["type"],
                "params": sc.get("params", {}), "background": sc.get("background", "plain"),
                "transition": sc.get("transition", "fade"), "broll": sc.get("broll"),
                "start": cursor, "duration": duration, "beats": beats, "sentences": sents, "word_times": wtimes}
        for lt, kind, gain in scenes.events(item):
            sfx.append((cursor + lt, kind, gain))
        if i > 0:
            sfx.append((cursor - 0.32, "whoosh", 0.8))
        out.append(item)
        cursor += duration
        log(f"  Szene {i+1} [{item['type']:<9}] {item['start']:5.1f}s  +{duration:4.1f}s")
    total = cursor
    vo = np.zeros(int(total * sr) + sr, np.float32)
    for start, audio in vo_parts:
        a = int(start * sr)
        vo[a:a + len(audio)] += audio
    # Untertitel dürfen sich nicht überlappen
    for a, b in zip(cues, cues[1:]):
        a["end"] = min(a["end"], b["start"])
    tl = {"scenes": out, "duration": total, "frames": int(round(total * C.FPS)),
          "cues": cues, "sfx": sfx}
    return tl, vo[: int(total * sr)]


def _cues(text: str, start: float, dur: float, word_times=None, max_chars=22, max_words=4):
    """Satz in kurze Untertitel-Blöcke zerlegen. Wortzeiten kommen von Piper
    (phonemgenau); passt die Wortzahl nicht zum Anzeigetext, wird die Zeit je
    Wort proportional zur Wortlänge geschätzt."""
    words = text.split()
    spoken = [w for w in words if re.search(r"\w", w)]
    if word_times and len(word_times) == len(spoken):
        it = iter(word_times)
        times, last = [], start
        for w in words:
            if re.search(r"\w", w):
                ws, we = next(it)
                times.append((w, float(start + ws), float(start + we)))
                last = start + we
            else:               # reines Satzzeichen, z. B. Gedankenstrich
                times.append((w, last, last))
    else:
        weights = [len(re.sub(r"\W", "", w)) + 1.6 + (2.0 if w[-1] in ",.:;?!–" else 0) for w in words]
        total = sum(weights)
        times, t = [], start
        for w, wt in zip(words, weights):
            d = dur * wt / total
            times.append((w, t, t + d))
            t += d
    # Hervorhebung bleibt bis zum nächsten Wort stehen
    times = [(w, ws, nxt[1]) for (w, ws, _), nxt in zip(times, times[1:])] + [times[-1]]
    chunks, cur = [], []
    for item in times:
        trial = " ".join(x[0] for x in cur + [item])
        if cur and (len(trial) > max_chars or len(cur) >= max_words):
            chunks.append(cur)
            cur = []
        cur.append(item)
        if item[0][-1] in ".:;?!" or (item[0][-1] in ",–" and len(cur) >= 2):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    # einzelne Restwörter an den Vorgänger hängen, wenn es passt
    merged = []
    for ch in chunks:
        if merged and len(ch) == 1 and merged[-1][-1][0][-1] not in ".:;?!" and \
                len(" ".join(x[0] for x in merged[-1] + ch)) <= max_chars + 6:
            merged[-1] += ch
        else:
            merged.append(ch)
    # sehr kurze Einzelwörter nach vorn an den nächsten Block hängen
    k = 0
    while k < len(merged) - 1:
        ch = merged[k]
        if len(ch) == 1 and ch[0][2] - ch[0][1] < 0.45 and ch[0][0][-1] not in ".:;?!" and \
                len(" ".join(x[0] for x in ch + merged[k + 1])) <= 30:
            merged[k + 1] = ch + merged[k + 1]
            del merged[k]
        else:
            k += 1
    cues = []
    for k, ch in enumerate(merged):
        end = ch[-1][2] + (0.25 if k == len(merged) - 1 else 0.0)
        cues.append({"start": ch[0][1], "end": end,
                     "text": " ".join(x[0] for x in ch), "words": ch})
    return cues


def _ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(cues, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, c in enumerate(cues, 1):
            f.write(f"{i}\n{_ts(c['start'])} --> {_ts(c['end'])}\n{c['text']}\n\n")
