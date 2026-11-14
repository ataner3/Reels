"""Zentrale Konfiguration: Marke, Videoformat, Pfade."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
BROLL = ASSETS / "broll"
VOICES = ROOT / "voices"
BUILD = ROOT / "build"
EXPORTS = ROOT / "EXPORTS"

# --- Videoformat -----------------------------------------------------------
W, H, FPS = 1080, 1920, 30
MIN_DURATION, MAX_DURATION = 30.0, 60.0
AUDIO_SR = 48000
TARGET_LUFS = -14.0

# --- Marke -----------------------------------------------------------------
BRAND = "SYSTEMKIND"
BG = (0x10, 0x11, 0x14)
GOLD = (0xC9, 0xA7, 0x6A)
IVORY = (0xF4, 0xF1, 0xEA)
MUTED = (0x8C, 0x8A, 0x84)      # gedämpftes Ivory für Nebentexte
PANEL = (0x1A, 0x1B, 0x20)      # leicht aufgehellte Fläche

SERIF = FONTS / "PlayfairDisplay.ttf"
SERIF_ITALIC = FONTS / "PlayfairDisplay-Italic.ttf"
SANS_DIR = FONTS
SANS = {  # Gewicht -> Datei; Fallback siehe gfx.font()
    400: "Inter-Regular.otf", 500: "Inter-Medium.otf",
    600: "Inter-SemiBold.otf", 700: "Inter-Bold.otf",
}

# Sicherer Bereich für Shorts (UI-Überlagerungen oben/unten/rechts)
SAFE_L, SAFE_R = 84, 996
SAFE_TOP, SAFE_BOTTOM = 250, 1330
CAPTION_Y = 1455                 # Mittelpunkt der Untertitelzeile

# --- Voice-over ------------------------------------------------------------
# Markenstimme für alle Videos. Ein Projekt kann einzelne Werte unter "voice"
# überschreiben. Hörproben: python main.py --voice-samples
VOICE = {
    "provider": "piper",             # "piper" (lokal, kostenlos) oder "elevenlabs" (Konto nötig)
    "name": "de_DE-karlsson-low",    # Piper-Stimme (wird bei Bedarf geladen)
    "speaker": None,                 # nur bei Mehrsprecher-Modellen, z. B. de_DE-mls-medium
    "pitch": -1.0,                   # Halbtöne; negativ = tiefer
    "length_scale": 0.8,             # Sprechtempo; kleiner = schneller
    "noise_scale": None,             # None = Standard der Stimme (natürliche Betonung)
    "noise_w": None,
}
# ElevenLabs – gilt, wenn provider "elevenlabs" ist (python main.py --voice elevenlabs).
ELEVENLABS = {
    "voice_id": "6IEvIqBOPOMUc5HwR9sQ",     # Lenny – Casual Creator (deutsche Stimme)
    "voice_name": "Lenny",
    "model_id": "eleven_multilingual_v2",    # spricht Deutsch
    "stability": 0.5,                        # höher = gleichmäßiger, niedriger = lebendiger
    "similarity_boost": 0.75,
    "style": 0.0,
    "speed": 1.0,                            # 0.7 bis 1.2
    "output_format": "mp3_44100_128",
}
# Aufbereitung für ElevenLabs: die Stimme ist bereits studiofertig, daher nur leicht
VOICE_FILTER_CLEAN = "highpass=f=60,acompressor=threshold=-20dB:ratio=2:attack=10:release=200:makeup=1.5"
VOICE_PRESETS = {                    # für --voice-samples
    "A_thorsten_tief": {"name": "de_DE-thorsten-high", "pitch": -2.0, "length_scale": 1.0, "noise_scale": 0.5, "noise_w": 0.7},
    "B_hoerbuch_253": {"name": "de_DE-mls-medium", "speaker": 39, "pitch": 0.0, "length_scale": 0.92},
    "C_hoerbuch_5055": {"name": "de_DE-mls-medium", "speaker": 6, "pitch": 0.0, "length_scale": 0.9},
    "D_karlsson": {"name": "de_DE-karlsson-low", "pitch": -1.0, "length_scale": 0.8},
}
VOICE_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
VOICE_LICENSES = {      # laut Modellkarten unter huggingface.co/rhasspy/piper-voices (Stand November 2026)
    "de_DE-karlsson-low": "Datensatz M-AILABS (gemeinfreie LibriVox-Aufnahmen, BSD-artige Lizenz). Das Modell wurde "
                          "aus der englischen Stimme „Ryan“ weitertrainiert, deren Datensatz unter CC BY-NC-SA 4.0 "
                          "steht (nicht kommerziell) – für kommerzielle Nutzung nicht eindeutig geklärt",
    "de_DE-thorsten-medium": "CC0 – Datensatz Thorsten-Voice (CC0), weitertrainiert aus dem Basismodell „rdh“ (CC0)",
    "de_DE-thorsten-high": "Datensatz Thorsten-Voice (CC0). Das Modell wurde aus der englischen Stimme „lessac“ "
                           "weitertrainiert, deren Datensatz eine eigene Lizenz hat (Blizzard Challenge 2013)",
    "de_DE-mls-medium": "CC BY 4.0 (Multilingual LibriSpeech, https://www.openslr.org/94/) – Namensnennung nötig",
}
# Aufbereitung der Stimme in der Mischung: warm und weich statt scharf
VOICE_FILTER = ("highpass=f=60,bass=g=3:f=130:w=0.7,equalizer=f=320:t=q:w=1.2:g=-1.5,"
                "equalizer=f=3400:t=q:w=1.2:g=-2,deesser=i=0.35,treble=g=-1.5:f=9000,"
                "acompressor=threshold=-22dB:ratio=2.5:attack=10:release=180:makeup=2.5")
VO_LEAD_IN, VO_GAP, VO_TAIL = 0.35, 0.22, 0.45

# Pegel der Stimme vor der Mischung (aktive Sprache, dBFS RMS). Stimmen, die deutlich
# leiser oder lauter geliefert werden – ElevenLabs liegt rund 10 dB unter Piper –,
# werden darauf angeglichen. Sonst ginge die Stimme in Musik und Effekten unter.
VO_LEVEL_DB = -13.0                # Rohpegel, auf den vor der Aufbereitung angeglichen wird
VO_LEVEL_TOLERANCE_DB = 2.0        # innerhalb dieser Spanne bleibt die Stimme unverändert
VO_STEM_DB = -17.0                 # Pegel nach der Aufbereitung (Referenz: die Piper-Mischung)
MIN_VOICE_OVER_BG_DB = 12.0        # Qualitätskontrolle: Abstand Stimme zu Musik + Effekten

TRANSITION = 0.5                 # Sekunden, mittig auf dem Schnitt
