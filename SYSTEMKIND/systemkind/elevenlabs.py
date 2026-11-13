"""ElevenLabs als zweite Sprachausgabe neben Piper.

Kostenfrei:  check()  – prüft Schlüssel, Kontingent und die Stimme.
Kostenpflichtig: synth() – verbraucht Zeichen aus dem ElevenLabs-Kontingent.
Jeder Satz wird nur einmal erzeugt und danach aus dem Cache gelesen.

Der API-Schlüssel steht nie im Code oder im Repository: Er kommt aus der
Umgebungsvariable ELEVENLABS_API_KEY oder aus der Datei SYSTEMKIND/.env
(von Git ausgeschlossen). Einrichten: python main.py --elevenlabs-setup
"""
from __future__ import annotations

import base64
import getpass
import hashlib
import json
import os
import re
import urllib.error
import urllib.request

from . import config as C

API = "https://api.elevenlabs.io"
ENV_FILE = C.ROOT / ".env"
CACHE = C.ASSETS / "voice_cache" / "elevenlabs"   # bleibt erhalten, damit nichts doppelt bezahlt wird


class ElevenLabsError(RuntimeError):
    pass


# --- Schlüssel -------------------------------------------------------------
def api_key() -> str | None:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key and ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*ELEVENLABS_API_KEY\s*=\s*(.+?)\s*$", line)
            if m:
                key = m.group(1).strip("'\"")
    return key or None


def save_key_interactive() -> bool:
    """Fragt den Schlüssel verdeckt ab (keine Anzeige, kein Verlauf) und
    speichert ihn in .env mit Zugriffsrechten nur für dich."""
    print("ElevenLabs-Schlüssel erstellen: elevenlabs.io → Profil → API Keys → Create API Key.")
    print("Die Eingabe bleibt unsichtbar.")
    key = getpass.getpass("API-Schlüssel: ").strip()
    if not key:
        print("Keine Eingabe – nichts gespeichert.")
        return False
    lines = [l for l in ENV_FILE.read_text(encoding="utf-8").splitlines()
             if not l.strip().startswith("ELEVENLABS_API_KEY")] if ENV_FILE.exists() else []
    ENV_FILE.write_text("\n".join(lines + [f"ELEVENLABS_API_KEY={key}"]) + "\n", encoding="utf-8")
    os.chmod(ENV_FILE, 0o600)
    print(f"Gespeichert in {ENV_FILE} (von Git ausgeschlossen).")
    return True


# --- HTTP ------------------------------------------------------------------
def _request(method: str, path: str, body: dict | None = None) -> dict:
    key = api_key()
    if not key:
        raise ElevenLabsError("Kein ElevenLabs-Schlüssel gefunden. Bitte: python main.py --elevenlabs-setup")
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:400]
        hint = {401: "Schlüssel ungültig oder ohne Berechtigung.",
                402: "Kontingent oder Tarif reicht nicht aus.",
                429: "Zu viele Anfragen oder Kontingent erschöpft."}.get(e.code, "")
        raise ElevenLabsError(f"ElevenLabs antwortet mit {e.code}. {hint} {detail}") from None
    except urllib.error.URLError as e:
        raise ElevenLabsError(f"ElevenLabs nicht erreichbar: {e.reason}") from None


# --- Kostenfreie Prüfung ---------------------------------------------------
def check() -> dict:
    """Prüft Schlüssel, Kontingent und Stimme. Verbraucht keine Zeichen."""
    el = C.ELEVENLABS
    out = {"voice_ok": False, "voice_name": None, "used": None, "limit": None, "tier": None, "notes": [],
           "library_voice": None, "api_ok": None}
    try:
        sub = _request("GET", "/v1/user/subscription")
        out.update(used=sub.get("character_count"), limit=sub.get("character_limit"), tier=sub.get("tier"))
    except ElevenLabsError as e:      # Schlüssel ohne Leserecht auf das Konto ist kein Hindernis
        if "missing_permissions" not in str(e):
            raise
        out["notes"].append("Der Schlüssel hat kein Leserecht für das Konto (user_read) – "
                            "das freie Kontingent lässt sich nicht anzeigen.")
    try:
        voices = _request("GET", "/v1/voices").get("voices", [])
    except ElevenLabsError as e:
        if "missing_permissions" not in str(e):
            raise                      # echter Fehler, z. B. ungültiger Schlüssel
        out["voice_ok"] = None         # Schlüssel gültig, darf die Stimmenliste aber nicht lesen
        out["notes"].append("Der Schlüssel hat kein Leserecht für Stimmen (voices_read) – "
                            "die Stimme lässt sich vorab nicht prüfen.")
        return out
    by_id = {v.get("voice_id"): v for v in voices}
    if el["voice_id"] in by_id:
        v = by_id[el["voice_id"]]
        # Stimmen aus der Voice Library sind „kopiert“; die mitgelieferten Standardstimmen nicht.
        library = (v.get("sharing") or {}).get("status") == "copied"
        out.update(voice_ok=True, voice_name=v.get("name"), library_voice=library, api_ok=True)
        if library and out["tier"] == "free":
            # ElevenLabs lehnt das mit 402 ab: „Free users cannot use library voices via the API.“
            out["api_ok"] = False
            out["notes"].append(
                "Die Stimme stammt aus der Voice Library. Im kostenlosen Tarif sperrt ElevenLabs solche Stimmen "
                "für die API – nutzbar sind dort nur die mitgelieferten Standardstimmen. Für diese Stimme ist "
                "ein bezahlter Tarif nötig.")
        elif library and out["tier"] is None:
            out["api_ok"] = None
    else:
        match = [v for v in voices if el["voice_name"].lower() in (v.get("name") or "").lower()]
        out["notes"].append(
            f"Stimme {el['voice_id']} nicht in deinem Konto gefunden. "
            + ("Gleichnamige Stimmen: " + ", ".join(f"{v['name']} ({v['voice_id']})" for v in match)
               if match else f"Auch keine Stimme mit „{el['voice_name']}“ im Namen."))
    return out


def remaining(info: dict) -> int | None:
    if info.get("used") is None or info.get("limit") is None:
        return None
    return info["limit"] - info["used"]


# --- Sprachausgabe (kostenpflichtig) --------------------------------------
def _key(text: str, el: dict) -> str:
    ident = [el["voice_id"], el["model_id"], el.get("stability"), el.get("similarity_boost"),
             el.get("style"), el.get("speed"), el.get("output_format"), text]
    return hashlib.sha1(json.dumps(ident).encode()).hexdigest()[:20]


def cached(text: str, el: dict | None = None) -> bool:
    k = _key(text, {**C.ELEVENLABS, **(el or {})})
    return (CACHE / f"{k}.mp3").exists() and (CACHE / f"{k}.json").exists()


def word_times(text: str, alignment: dict) -> list[list[float]]:
    """Zeichengenaue Zeiten von ElevenLabs zu Wortgrenzen zusammenfassen."""
    chars = alignment.get("characters") or alignment.get("chars") or []
    if "character_start_times_seconds" in alignment:
        starts, ends = alignment["character_start_times_seconds"], alignment["character_end_times_seconds"]
    elif "char_start_times_ms" in alignment:
        starts = [t / 1000 for t in alignment["char_start_times_ms"]]
        ends = [s + d / 1000 for s, d in zip(starts, alignment.get("chars_durations_ms") or [0] * len(starts))]
    else:
        return []
    words, cur, has_letter = [], None, False
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if cur and has_letter:
                words.append(cur)
            cur, has_letter = None, False
        else:
            cur = [cur[0] if cur else s, e]
            has_letter |= ch.isalnum()
    if cur and has_letter:
        words.append(cur)
    return words


def synth_file(text: str, el: dict | None = None):
    """Gibt (Pfad zur MP3, Wortzeiten) zurück. Ruft ElevenLabs nur auf, wenn
    der Satz noch nicht im Cache liegt."""
    el = {**C.ELEVENLABS, **(el or {})}
    k = _key(text, el)
    mp3, meta = CACHE / f"{k}.mp3", CACHE / f"{k}.json"
    if not (mp3.exists() and meta.exists()):
        settings = {"stability": el.get("stability"), "similarity_boost": el.get("similarity_boost"),
                    "style": el.get("style"), "speed": el.get("speed"), "use_speaker_boost": True}
        body = {"text": text, "model_id": el["model_id"],
                "voice_settings": {a: b for a, b in settings.items() if b is not None}}
        res = _request("POST", f"/v1/text-to-speech/{el['voice_id']}/with-timestamps"
                               f"?output_format={el.get('output_format', 'mp3_44100_128')}", body)
        audio = res.get("audio_base64")
        if not audio:
            raise ElevenLabsError("Antwort ohne Audiodaten: " + json.dumps(res)[:300])
        CACHE.mkdir(parents=True, exist_ok=True)
        mp3.write_bytes(base64.b64decode(audio))
        meta.write_text(json.dumps({"text": text, "voice": el["voice_name"], "model": el["model_id"],
                                    "words": word_times(text, res.get("alignment") or {})},
                                   ensure_ascii=False), encoding="utf-8")
    return mp3, json.loads(meta.read_text(encoding="utf-8"))["words"]
