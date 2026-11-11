"""Lokales Voice-over mit Piper TTS (mit Cache pro Satz)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.request
import wave

import numpy as np

from . import config as C

_voices = {}
CACHE = C.BUILD / "_tts_cache"


def settings(project: dict | None = None) -> dict:
    """Markenstimme aus der Konfiguration, ergänzt um Projektwerte."""
    return {**C.VOICE, **((project or {}).get("voice") or {})}


def voice_files(name=None):
    name = name or C.VOICE["name"]
    return C.VOICES / f"{name}.onnx", C.VOICES / f"{name}.onnx.json"


def voice_available(name=None):
    return all(p.exists() and p.stat().st_size > 1000 for p in voice_files(name))


def voice_license(name=None):
    name = name or C.VOICE["name"]
    return next((v for k, v in C.VOICE_LICENSES.items() if f"-{k}" in name),
                "siehe MODEL_CARD der Stimme unter huggingface.co/rhasspy/piper-voices")


def download_voice(name=None):
    """Lädt eine freie Piper-Stimme einmalig herunter (Name: sprache-sprecher-qualität)."""
    name = name or C.VOICE["name"]
    lang, speaker, quality = name.split("-")
    url = f"{C.VOICE_BASE_URL}{lang.split('_')[0]}/{lang}/{speaker}/{quality}/"
    C.VOICES.mkdir(parents=True, exist_ok=True)
    for path in voice_files(name):
        if path.exists() and path.stat().st_size > 1000:
            continue
        print(f"  Lade {path.name} …")
        urllib.request.urlretrieve(url + path.name, path)


def _load(name):
    if name not in _voices:
        from piper import PiperVoice
        model, cfg = voice_files(name)
        try:    # Wortgenaue Zeiten brauchen das Paket "onnx" (piper-tts[alignment])
            import onnx  # noqa: F401
            _voices[name] = PiperVoice.load(str(model), config_path=str(cfg), include_alignments=True)
        except Exception:
            _voices[name] = PiperVoice.load(str(model), config_path=str(cfg))
        v = _voices[name]
        # Ältere Stimmen kennen einzelne Zusatzzeichen der Lautschrift nicht. Piper
        # überspringt sie beim Sprechen, liefert dann aber keine Wortzeiten mehr.
        # Deshalb hier vorab entfernen – der Klang bleibt identisch.
        known, orig = v.config.phoneme_id_map, v.phonemize
        v.phonemize = lambda text: [[p for p in sent if p in known] for sent in orig(text)]
    return _voices[name]


_lex = None


def lexicon() -> dict:
    global _lex
    if _lex is None:
        path = C.ASSETS / "aussprache.json"
        _lex = {k: v for k, v in json.loads(path.read_text(encoding="utf-8")).items()
                if not k.startswith("_")} if path.exists() else {}
    return _lex


def spoken(text: str) -> str:
    """Wendet das Aussprache-Wörterbuch an. Satzzeichen wandern mit in den
    Lautschrift-Block, weil Piper sie dahinter sonst verschluckt."""
    out = []
    for tok in text.split():
        core = tok.rstrip(".,:;?!")
        punct = tok[len(core):]
        rep = lexicon().get(core)
        if rep is None:
            out.append(tok)
        elif rep.startswith("[["):
            out.append(f"[[ {rep.strip('[] ')}{punct} ]]")
        else:
            out.append(rep + punct)
    return " ".join(out)


def phonemes(text: str, vs: dict | None = None) -> str:
    """Lautschrift, wie die Stimme den Text sprechen wird (zur Kontrolle)."""
    vs = {**C.VOICE, **(vs or {})}
    return " | ".join("".join(p) for p in _load(vs["name"]).phonemize(spoken(text)))


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


def synth(text: str, vs: dict | None = None):
    """Text -> (Mono float32 bei C.AUDIO_SR, Wortzeiten oder None).
    vs = Stimm-Einstellungen (siehe config.VOICE). Wortzeiten: [[start, ende], ...]
    in Sekunden, ein Eintrag je gesprochenem Wort."""
    vs = {**C.VOICE, **(vs or {})}
    CACHE.mkdir(parents=True, exist_ok=True)
    text = spoken(text)
    # Tonhöhe ohne Artefakte: langsamer abspielen (tiefer) und dafür entsprechend
    # schneller synthetisieren. Kein Time-Stretching, das metallisch klingen kann.
    f = 2 ** (float(vs.get("pitch") or 0) / 12)
    scale = round(float(vs.get("length_scale") or 1.0) * f, 4)
    ident = [vs["name"], vs.get("speaker"), scale, vs.get("noise_scale"), vs.get("noise_w"), text]
    key = hashlib.sha1(json.dumps(ident).encode()).hexdigest()[:20]
    raw, meta = CACHE / f"{key}.wav", CACHE / f"{key}.json"
    if not (raw.exists() and meta.exists()):
        from piper import SynthesisConfig
        cfg = SynthesisConfig(speaker_id=vs.get("speaker"), length_scale=scale,
                              noise_scale=vs.get("noise_scale"), noise_w_scale=vs.get("noise_w"))
        tmp = raw.with_suffix(".tmp.wav")
        with wave.open(str(tmp), "wb") as wf:
            al = _load(vs["name"]).synthesize_wav(text, wf, syn_config=cfg, include_alignments=True)
            sr = wf.getframerate()
        tmp.rename(raw)
        meta.write_text(json.dumps({"sr": sr, "words": _word_times(al, sr)}))
    info = json.loads(meta.read_text())
    af = f"asetrate={info['sr'] * f:.0f},aresample={C.AUDIO_SR}:resampler=soxr" if abs(f - 1) > 1e-3 else "anull"
    out = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-i", str(raw), "-af", af, "-ac", "1", "-ar", str(C.AUDIO_SR),
         "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(out, np.float32).copy()
    idx = np.flatnonzero(np.abs(x) > 0.012)     # Stille am Rand entfernen
    a, b = (max(idx[0] - int(0.03 * C.AUDIO_SR), 0), idx[-1] + int(0.03 * C.AUDIO_SR)) if len(idx) else (0, len(x))
    off = a / C.AUDIO_SR
    x = x[a:b]
    dur = len(x) / C.AUDIO_SR
    words = [[min(max(s / f - off, 0), dur), min(max(e / f - off, 0), dur)] for s, e in info["words"]]
    return x, (words or None)


SAMPLE_TEXT = ("Warum werden die Reichen immer reicher? Nicht durch Zufall. Sondern durch ein System. "
               "Wer arbeitet, tauscht Zeit gegen Geld. Wer Vermögen besitzt, erhält Erträge – und kann sie wieder anlegen.")


def samples(out_dir):
    """Hörproben aller Presets mit derselben Aufbereitung wie im Video."""
    out_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for label, vs in C.VOICE_PRESETS.items():
        if not voice_available(vs["name"]):
            download_voice(vs["name"])
        x, _ = synth(SAMPLE_TEXT, vs)
        path = out_dir / f"stimme_{label}.mp3"
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "f32le", "-ar", str(C.AUDIO_SR), "-ac", "1",
                        "-i", "-", "-af", C.VOICE_FILTER + ",loudnorm=I=-16:TP=-2", "-b:a", "160k", str(path)],
                       input=x.tobytes(), check=True)
        made.append((label, vs, path))
    return made
