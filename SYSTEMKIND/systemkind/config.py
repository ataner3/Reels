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
    "name": "de_DE-thorsten-high",   # Piper-Stimme (wird bei --setup geladen)
    "speaker": None,                 # nur bei Mehrsprecher-Modellen, z. B. de_DE-mls-medium
    "pitch": -2.0,                   # Halbtöne; negativ = tiefer
    "length_scale": 1.0,             # Sprechtempo; größer = langsamer
    "noise_scale": 0.5,              # kleiner = ruhigere, gleichmäßigere Betonung
    "noise_w": 0.7,
}
VOICE_PRESETS = {                    # für --voice-samples
    "A_thorsten_tief": {"name": "de_DE-thorsten-high", "pitch": -2.0, "length_scale": 1.0, "noise_scale": 0.5, "noise_w": 0.7},
    "B_hoerbuch_253": {"name": "de_DE-mls-medium", "speaker": 39, "pitch": 0.0, "length_scale": 0.92},
    "C_hoerbuch_5055": {"name": "de_DE-mls-medium", "speaker": 6, "pitch": 0.0, "length_scale": 0.9},
    "D_karlsson": {"name": "de_DE-karlsson-low", "pitch": -1.0, "length_scale": 1.05},
}
VOICE_BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
VOICE_LICENSES = {
    "thorsten": "CC0 (Thorsten-Voice, https://github.com/thorstenMueller/Thorsten-Voice)",
    "mls": "CC BY 4.0 (Multilingual LibriSpeech, https://www.openslr.org/94/)",
}
# Aufbereitung der Stimme in der Mischung: warm und weich statt scharf
VOICE_FILTER = ("highpass=f=60,bass=g=3:f=130:w=0.7,equalizer=f=320:t=q:w=1.2:g=-1.5,"
                "equalizer=f=3400:t=q:w=1.2:g=-2,deesser=i=0.35,treble=g=-1.5:f=9000,"
                "acompressor=threshold=-22dB:ratio=2.5:attack=10:release=180:makeup=2.5")
VO_LEAD_IN, VO_GAP, VO_TAIL = 0.40, 0.26, 0.50

TRANSITION = 0.5                 # Sekunden, mittig auf dem Schnitt
