# FRICTIONFLIP – Projektregeln

FRICTIONFLIP ist eine internationale Content-Marke für clevere Alltagslösungen,
Problemlösungen und ehrliche Produktbewertungen. Dieses Verzeichnis ist die
Produktionsumgebung für KI-gestützt erstellte TikTok-Videos.

## Sprache
- Kommunikation mit dem Projektinhaber: **Deutsch**.
- Alle zur Veröffentlichung bestimmten Inhalte (Skripte, On-Screen-Text, Voiceover,
  Captions, Hashtags, Titel): **amerikanisches Englisch** (US-Schreibweise, US-Maßeinheiten, USD).
- Interne Dokumentation (READMEs, Notizen, Analysen): Deutsch.

## Branding
- Einzige Quelle der Wahrheit: `BRAND/BRAND_IDENTITY.md` und die Dateien in `BRAND/`.
- Das Branding wird **nicht eigenständig verändert, ergänzt oder interpretiert**
  (Name, Tonalität, Farben, Schriften, Logo, Claims). Änderungen nur auf ausdrückliche
  Anweisung des Projektinhabers.
- Fehlt eine Branding-Angabe, wird nachgefragt – nicht erfunden.

## Kosten und Dienste
- **Keine zusätzlichen kostenpflichtigen Dienste**, Abos, APIs oder Tools installieren
  oder anbinden. Kostenpflichtige Optionen nur als Vorschlag nennen; Entscheidung trifft
  der Projektinhaber.
- Bevorzugt lokale Open-Source-Werkzeuge (z. B. ffmpeg, ImageMagick, Python).

## Veröffentlichung
- **Keine externen Veröffentlichungen** (TikTok, andere Plattformen, öffentliche Links,
  Uploads zu Drittanbietern) ohne ausdrückliche Freigabe im Einzelfall.
- Material wird nicht an externe Dienste gesendet, sofern nicht ausdrücklich freigegeben.

## Inhaltliche Grundsätze
- Ehrliche Produktbewertungen: keine erfundenen Tests, Erfahrungen, Ergebnisse oder Zitate.
  Vor- und Nachteile benennen.
- Tatsachenbehauptungen müssen durch eine Quelle in `RESEARCH/` gedeckt sein.
- Keine Gesundheits-, Sicherheits- oder Finanzversprechen ohne Beleg.
- Werbung, Affiliate-Links und gestellte Produkte werden gekennzeichnet (FTC-Regeln, TikTok-Richtlinien).
- Nur Material mit geklärten Rechten verwenden (Bilder, Musik, Schriften, Clips);
  Herkunft/Lizenz in `VISUALS/` dokumentieren.

## Struktur und Workflow
`RESEARCH → SCRIPTS → STORYBOARDS → VOICEOVERS / VISUALS → VIDEOS → EXPORTS → ANALYTICS`

| Ordner | Inhalt |
|---|---|
| `BRAND/` | Markenidentität (schreibgeschützt für Claude) |
| `RESEARCH/` | Themen, Quellen, Produkt- und Trendrecherche |
| `SCRIPTS/` | Videoskripte (US-Englisch) |
| `STORYBOARDS/` | Szenenpläne, Shot-Listen, Timing |
| `VOICEOVERS/` | Sprechertexte und Audio |
| `VISUALS/` | Bilder, Grafiken, Overlays, B-Roll |
| `VIDEOS/` | Arbeitsstände, Rohschnitte |
| `EXPORTS/` | Finale, freigegebene Master |
| `ANALYTICS/` | Performance-Daten und Learnings |

- Video-ID: `FF-0001`, fortlaufend. Dateiname: `FF-0001_kurzer-slug.<ext>` – dieselbe ID in allen Ordnern.
- Zielformat: 9:16, 1080×1920, MP4 (H.264/AAC).
- Jeder Schritt wird vom Projektinhaber freigegeben, bevor der nächste beginnt
  (Skript → Storyboard → Produktion → Export).
