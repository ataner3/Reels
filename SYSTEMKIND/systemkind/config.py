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
VOICE = "de_DE-thorsten-high"
VOICE_URL = ("https://huggingface.co/rhasspy/piper-voices/resolve/main/"
             "de/de_DE/thorsten/high/")
VOICE_LICENSE = "CC0 (Thorsten-Voice, https://github.com/thorstenMueller/Thorsten-Voice)"
VO_LEAD_IN, VO_GAP, VO_TAIL = 0.40, 0.26, 0.50

TRANSITION = 0.5                 # Sekunden, mittig auf dem Schnitt
