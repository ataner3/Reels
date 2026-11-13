# SYSTEMKIND Video Factory

Lokale Pipeline für YouTube-Shorts im SYSTEMKIND-Stil (Dark Documentary):
aus einer Projektdatei mit geprüften Fakten entsteht ein fertiges MP4 mit
Voice-over, Motion Graphics, Untertiteln, Musik und Soundeffekten.

Ausgabe: MP4 · H.264 · AAC · 1080 × 1920 · 30 FPS · 30–60 Sekunden.

## Installation

Voraussetzungen: Python ≥ 3.10 und FFmpeg (mit libx264).

```bash
cd SYSTEMKIND
pip install -r requirements.txt
python main.py --setup      # lädt die freie deutsche Piper-Stimme (ca. 60 MB) und prüft die Umgebung
```

FFmpeg installieren: macOS `brew install ffmpeg`, Ubuntu `sudo apt install ffmpeg`,
Windows `winget install ffmpeg`.

## Start

```bash
python main.py --topic "Warum werden die Reichen immer reicher?"
```

Ergebnis in `EXPORTS/`:

- `<thema>.mp4` – das fertige Video
- `<thema>.srt` – Untertitel (zusätzlich ins Bild eingebrannt)
- `<thema>_bericht.md` – Produktionsbericht mit Prüfergebnissen, Quellen und Lizenzen

## Befehle

| Befehl | Wirkung |
|---|---|
| `python main.py --topic "…"` | Video produzieren. Unbekanntes Thema: Projektordner mit Auftrag anlegen. |
| `python main.py --topic "…" --review` | Skript, Szenen, Quellen und Storyboard prüfen, dann freigeben oder abbrechen. |
| `python main.py --topic "…" --approve` | Entwurf ohne Rückfrage freigeben und rendern. |
| `python main.py --check` | Hardware und Software prüfen. |
| `python main.py --list` | Projekte anzeigen. |
| `python main.py --voice-samples` | Hörproben der Stimm-Presets erzeugen. |
| `python main.py --topic "…" --voice elevenlabs` | Mit ElevenLabs statt Piper sprechen (fragt vor Kosten nach). |
| `python main.py --assets` | B-Roll-Bibliothek anzeigen. |
| `python main.py --add-asset clip.mp4 --tags stadt,nacht --source Pexels --url <Link> --license "Pexels License" --author <Name>` | Clip mit Quelle und Lizenz aufnehmen. |

## Ablauf

| Phase | Was passiert |
|---|---|
| A Research | Fakten der Projektdatei werden geprüft: Quelle, URL, `verified`. Ungeprüftes blockiert das Rendering. |
| B Script | Voice-over-Sätze bestimmen die Szenenlängen. |
| C Assets | Szenen mit B-Roll-Wunsch bekommen einen Clip aus der Bibliothek. Fehlendes wird gemeldet und durch einen animierten Hintergrund ersetzt. |
| D Audio | Piper spricht das Voice-over. Musik und Soundeffekte werden erzeugt, die Musik weicht der Stimme aus, die Mischung wird auf −14 LUFS normalisiert. |
| E Video | Pillow zeichnet jedes Bild, FFmpeg kodiert. Untertitel laufen wortgenau mit der Stimme. |
| F Quality Control | 21 Prüfungen: Format, Länge, Schwarzbilder, Tonlücken, Lautheit, Untertitel, leere Szenen. |

## Stimme

Die Markenstimme steht in `systemkind/config.py` unter `VOICE`: Piper-Modell,
Sprecher, Tonhöhe in Halbtönen (`pitch`, negativ = tiefer), Tempo (`length_scale`).
Ein Projekt kann einzelne Werte unter `"voice"` überschreiben.

```bash
python main.py --voice-samples     # Hörproben aller Presets nach EXPORTS/stimmproben/
```

Fehlende Stimmen werden beim ersten Gebrauch geladen. Die Aufbereitung in der
Mischung (`VOICE_FILTER`) ist auf einen warmen, weichen Klang eingestellt.

### ElevenLabs (optional)

Neben Piper kann ElevenLabs sprechen – eingestellt ist die Stimme „Lenny – Casual Creator“
(`ELEVENLABS` in `systemkind/config.py`). Piper bleibt der Standard.

```bash
python main.py --elevenlabs-setup     # Schlüssel verdeckt eingeben; landet in .env (nicht in Git)
python main.py --elevenlabs-check     # prüft Schlüssel, Kontingent und Stimme – kostenfrei
python main.py --topic "…" --voice elevenlabs
```

- Vor jedem kostenpflichtigen Aufruf zeigt die Pipeline die Zeichenzahl und fragt nach.
  `--confirm-paid` bestätigt ohne Rückfrage.
- Jeder Satz wird nur einmal erzeugt und liegt danach in `assets/voice_cache/elevenlabs/`.
  Ein zweiter Lauf mit demselben Text kostet nichts.
- ElevenLabs liest den normalen Text (`text`). Für Sonderfälle gibt es je Satz `say_elevenlabs`.
- Der Schlüssel kann statt in `.env` auch in der Umgebungsvariable `ELEVENLABS_API_KEY` stehen.
- Stimmen aus der Voice Library (z. B. Lenny) sperrt ElevenLabs im kostenlosen Tarif für die API;
  dort funktionieren nur die mitgelieferten Standardstimmen. `--elevenlabs-check` zeigt das an.
- ElevenLabs liefert die Stimme rund 10 dB leiser als Piper. Die Mischung gleicht den Pegel
  automatisch an; die Qualitätskontrolle prüft den Abstand der Stimme zu Musik und Effekten.
- Dauerhaft umstellen: `"provider": "elevenlabs"` in `VOICE`.

### Aussprache

Piper spricht manche Wörter falsch (z. B. „reichsten“, „Aktien“, „Zufall“). Vor dem
Rendern lässt sich das prüfen, ohne zuzuhören:

```bash
python main.py --topic "…" --phonemes    # zeigt die Lautschrift jedes Satzes
```

Korrekturen stehen in `assets/aussprache.json` und gelten für alle Videos:
entweder Lautschrift in `[[…]]` oder eine andere Schreibweise.

## Neues Thema

`python main.py --topic "Neues Thema"` legt `projects/<thema>/` mit einer
Vorlage und `AUFTRAG.md` an. Die Pipeline enthält bewusst kein Sprachmodell:
Recherche und Skript entstehen in der Projektdatei – von dir oder mit Claude Code
(„Recherchiere und fülle projects/<thema>/project.json nach docs/PROJEKTFORMAT.md
aus“). Solange Platzhalter oder ungeprüfte Fakten enthalten sind, wird nicht gerendert.

Das Format der Projektdatei steht in [docs/PROJEKTFORMAT.md](docs/PROJEKTFORMAT.md).

## Aufbau

```
main.py                 Einstieg und Ablaufsteuerung
systemkind/config.py    Marke (Farben, Schriften), Videoformat, Pfade
systemkind/project.py   Projektdatei laden, prüfen, neu anlegen
systemkind/tts.py       Voice-over mit Piper, wortgenaue Zeiten
systemkind/elevenlabs.py  ElevenLabs-Anbindung (Schlüssel, Prüfung, Cache)
systemkind/timeline.py  Szenenzeiten, Untertitel, SRT
systemkind/scenes.py    Szenen-Vorlagen (title, statement, bars, compare, growth, formula, outro)
systemkind/gfx.py       Typografie, Easing, animierte Hintergründe
systemkind/audio.py     Musik, Soundeffekte, Mischung
systemkind/render.py    Übergänge, Untertitel, Branding, paralleles Rendering
systemkind/assets.py    B-Roll-Bibliothek mit Quelle und Lizenz
systemkind/qc.py        Qualitätskontrolle
systemkind/review.py    Review-Modus
systemkind/report.py    Produktionsbericht
projects/               ein Ordner je Video
assets/                 Schriften, B-Roll
EXPORTS/                fertige Videos
```

## Grenzen

- B-Roll wird nicht automatisch heruntergeladen. Clips von Pexels oder Pixabay
  lädst du selbst und nimmst sie mit `--add-asset` samt Quelle und Lizenz auf.
- Es gibt keinen Upload zu YouTube. Veröffentlicht wird nur von Hand.
- Die Musik ist ein erzeugtes Ambient-Bett, kein komponierter Soundtrack.

## Lizenzen

- Stimme `de_DE-karlsson-low` (Standard): M-AILABS Speech Dataset, BSD-artige Lizenz
- Stimme `de_DE-thorsten-high`: CC0 (Thorsten-Voice)
- Stimmen aus `de_DE-mls-medium`: CC BY 4.0 (Multilingual LibriSpeech) – Namensnennung nötig
- Schriften Playfair Display und Inter: SIL Open Font License 1.1
