"""Lokales Voice-over mit Piper TTS (mit Cache pro Satz)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.request
import wave

import numpy as np

from . import config as C

_voice = None
CACHE = C.BUILD / "_tts_cache"


def voice_files():
    return C.VOICES / f"{C.VOICE}.onnx", C.VOICES / f"{C.VOICE}.onnx.json"


def voice_available():
    return all(p.exists() and p.stat().st_size > 1000 for p in voice_files())


def download_voice():
    """Lädt die freie Piper-Stimme (CC0) einmalig herunter."""
    C.VOICES.mkdir(parents=True, exist_ok=True)
    for path in voice_files():
        if path.exists() and path.stat().st_size > 1000:
            continue
        print(f"  Lade {path.name} …")
        urllib.request.urlretrieve(C.VOICE_URL + path.name, path)


def _load():
    global _voice
    if _voice is None:
        from piper import PiperVoice
        model, cfg = voice_files()
        try:    # Wortgenaue Zeiten brauchen das Paket "onnx" (piper-tts[alignment])
            import onnx  # noqa: F401
            _voice = PiperVoice.load(str(model), config_path=str(cfg), include_alignments=True)
        except Exception:
            _voice = PiperVoice.load(str(model), config_path=str(cfg))
    return _voice


def _word_times(alignments, sr):
    """Phonem-Dauern von Piper zu Wortgrenzen (Sekunden) zusammenfassen."""
    words, t, cur = [], 0.0, None
    for a in alignments or []:
        d = int(a.num_samples) / sr
        if a.phoneme in " ^$" or a.phoneme in ".,;:!?":
            if cur:
                words.append(cur)
                cur = None
        else:
            cur = [cur[0] if cur else t, t + d]
        t += d
    if cur:
        words.append(cur)
    return words


def synth(text: str, length_scale: float = 1.0):
    """Text -> (Mono float32 bei C.AUDIO_SR, Wortzeiten oder None).
    Wortzeiten: [[start, ende], ...] in Sekunden, ein Eintrag je gesprochenem Wort."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(f"{C.VOICE}|{length_scale}|{text}".encode()).hexdigest()[:20]
    raw, meta = CACHE / f"{key}.wav", CACHE / f"{key}.json"
    if not (raw.exists() and meta.exists()):
        from piper import SynthesisConfig
        tmp = raw.with_suffix(".tmp.wav")
        with wave.open(str(tmp), "wb") as wf:
            al = _load().synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=length_scale),
                                        include_alignments=True)
            sr = wf.getframerate()
        tmp.rename(raw)
        meta.write_text(json.dumps(_word_times(al, sr)))
    out = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-i", str(raw), "-ac", "1", "-ar", str(C.AUDIO_SR),
         "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(out, np.float32).copy()
    idx = np.flatnonzero(np.abs(x) > 0.012)     # Stille am Rand entfernen
    a, b = (max(idx[0] - int(0.03 * C.AUDIO_SR), 0), idx[-1] + int(0.03 * C.AUDIO_SR)) if len(idx) else (0, len(x))
    off = a / C.AUDIO_SR
    x = x[a:b]
    dur = len(x) / C.AUDIO_SR
    words = [[min(max(s - off, 0), dur), min(max(e - off, 0), dur)] for s, e in json.loads(meta.read_text())]
    return x, (words or None)
