# Brand Preview

Visuelle Vorschau der Marke – **Entwürfe, nicht freigegeben**. Grundlage: `BRAND/BRAND_IDENTITY.md` und `BRAND/VISUAL_GUIDELINES.md`.
`BRAND_IDENTITY.md` wird erst nach Freigabe durch den Projektinhaber angepasst.

| Ordner | Stand |
|---|---|
| `v02/` | **Aktueller Entwurf** (Draft 02) |
| `v01/` | Erster Entwurf, eingefroren zum Vergleich |

## Draft 02 (`v02/`)

| Datei | Inhalt |
|---|---|
| `00_overview.png` | Übersicht aller Entwürfe |
| `01_logo_sheet.png`, `01_logo_wordmark_dark.png`, `01_logo_wordmark_light.png` | Wortmarke – unverändert gegenüber Draft 01 |
| `02_profile_picture.png` | Profilbild 1080 × 1080, Monogramm mit zwei aufrechten F |
| `02_profile_picture_size_check.png` | Größenprüfung 400 / 160 / 60 / 48 / 40 px, dunkler und heller Hintergrund |
| `03_video_frame_a_hook.png`, `_b_fix.png`, `_c_verdict.png` | Frames 9:16 mit Slots für echtes Filmmaterial |
| `03_video_frame_safezones.png` | Hook-Frame mit eingeblendeten TikTok-Sicherheitszonen (Produktionsvorlage) |
| `04_title_card.png` | Titelkarte mit Claim – unverändert gegenüber Draft 01 |

**Änderungen gegenüber Draft 01**

- Profilbild: zwei aufrechte F, aus Rechtecken konstruiert (etwas breiter und kräftiger als die Wortmarke), damit es bei 40–60 px lesbar bleibt. Farbaufteilung wie Wortmarke.
- Video-Frames: grauer Bereich mit Diagonalkreuz = Platz für echte Produktaufnahmen. Redaktioneller Graphite-Kopf oben, technische Elemente (Callouts, Maßlinie, Detail-Zeichnung) liegen nur ergänzend darüber.
- Bewertungskarte: alle Angaben als `DEMO · PLACEHOLDER` / `NOT A REAL TEST` gekennzeichnet, Inhalte als `[TBD]`-Platzhalter. Video-ID `FF-0000 · DEMO`.

## Technik

- Quellen in `src/` (HTML/CSS). Neu rendern: `node src/render.js` (Playwright + Chromium) – schreibt nach `v02/`.
- Schriften in `src/fonts/`: Barlow Condensed, IBM Plex Sans, IBM Plex Mono – SIL Open Font License (kostenlos).
