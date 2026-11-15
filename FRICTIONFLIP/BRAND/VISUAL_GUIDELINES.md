# FRICTIONFLIP – Visual Guidelines

Konkrete Anwendungsregeln zur Markenidentität in `BRAND_IDENTITY.md`.
Bei Widerspruch gilt `BRAND_IDENTITY.md`.

Leitsatz: **Industrial Editorial Design meets Inventor's Workshop** – gesetzt wie ein
Magazin, glaubwürdig wie eine Werkbank.

---

## 1. Farben

| Farbe | Hex | RGB | Flächenanteil (Richtwert) |
|---|---|---|---|
| Graphite | `#171816` | 23, 24, 22 | 60–70 % |
| Paper White | `#E6E0D4` | 230, 224, 212 | 20–30 % |
| Copper Orange | `#D96B32` | 217, 107, 50 | 5–10 % |
| Petrol | `#087F79` | 8, 127, 121 | max. 3 %, höchstens ein Element pro Bild |

**Zulässige Text-/Flächenkombinationen** (Kontrastwerte nach WCAG):

| Vordergrund | Hintergrund | Kontrast | Verwendung |
|---|---|---|---|
| Paper White | Graphite | 13,6 : 1 | Standard für alle Texte |
| Graphite | Paper White | 13,6 : 1 | Helle Karten, Etiketten |
| Graphite | Copper Orange | 5,2 : 1 | Text auf Akzentflächen |
| Copper Orange | Graphite | 5,2 : 1 | Hervorhebungen, große Schrift, Linien |
| Petrol | Graphite / Paper White | 3,7 : 1 | Nur Grafikelemente und große Schrift, kein Fließtext |

**Verboten:**

- Paper White auf Copper Orange (2,6 : 1) und Copper Orange neben/auf Petrol (1,4 : 1) als Textkombination
- Farbverläufe zwischen Markenfarben, Neon- und Leuchteffekte, Glow
- Reines Schwarz/Weiß, zusätzliche Farben, Transparenz-Mischtöne als neue Farbe
- Copper Orange als Vollflächen-Hintergrund eines ganzen Videos

**Regeln:**

- Copper Orange markiert pro Bild genau **eine** Sache: das Schlüsselwort, die Zahl oder das Ergebnis.
- Petrol nur für sekundäre Signale (z. B. „verified", Maßlinie, Häkchen) – nie gleichzeitig mit einer großen Copper-Fläche.
- Aufnahmen werden leicht entsättigt und warm-neutral gegradet, damit Realbild und Markenfarben zusammenpassen. Keine Teal-Orange-Filter, kein HDR-Look.

---

## 2. Bildsprache

**So:**

- Echte Hände, echte Produkte, echte Umgebung; Werkbank, Arbeitsplatte, Küche, Garage
- Materialien: Metall, Holz, Karton, Papier, Beton, Werkzeugstahl
- Seitliches, gerichtetes Licht mit sichtbaren Schatten; Gebrauchsspuren sind erlaubt
- Draufsicht (Top-down) und Nahaufnahme als Standardperspektiven
- Technische Anmutung: Maßlinien, Beschriftungen, Explosionsdarstellungen, Skizzen

**Nicht so:**

- Generische KI-Bilder: glatte Plastikhaut, verformte Hände, unlesbare Schrift, überglänzte Oberflächen
- Stockfoto-Ästhetik (lächelnde Menschen vor weißer Wand)
- Sci-Fi, Hologramme, HUD-Interfaces, Chrom, Lens Flares, Partikel
- 3D-Maskottchen, Emojis als Gestaltungselement, Cliparts

KI-generiertes Bildmaterial ist nur zulässig, wenn es von einer echten Aufnahme nicht zu
unterscheiden ist und kein Produkt oder Testergebnis darstellt, das es so nicht gab.

---

## 3. Typografie

> Die verbindlichen Markenschriften sind noch nicht festgelegt. Bis zur Entscheidung
> des Projektinhabers gilt der folgende **Arbeitsstandard** (alle kostenlos, SIL Open Font License).

| Rolle | Schrift | Schnitt | Einsatz |
|---|---|---|---|
| Headline | Barlow Condensed | SemiBold / Bold, Versalien | Hooks, Titel, Thumbnails, Zahlen |
| Text | IBM Plex Sans | Regular / Medium | Untertitel, Erklärtext |
| Technik | IBM Plex Mono | Regular / Medium, Versalien | Labels, Maße, Schrittnummern, Quellen |

**Regeln:**

- Höchstens **zwei** Schriftrollen gleichzeitig im Bild.
- Headlines: Versalien, Laufweite +1 bis +3 %, Zeilenabstand 0,95–1,05, linksbündig.
- Mono-Labels: Versalien, Laufweite +6 bis +10 %, klein.
- Untertitel: Satzschreibweise, max. 2 Zeilen, max. ca. 32 Zeichen pro Zeile.
- Hervorhebung durch **Farbe (Copper Orange) oder Schnitt** – nie durch beides plus Größe.
- Keine Konturschrift, keine Schlagschatten, keine Verzerrung, keine Schreibschrift, kein Blocksatz.
- Lesbarkeit über Realbild: Graphite-Balken oder -Fläche (85–100 % Deckkraft) hinter dem Text, kein weicher Schatten.

**Mindestgrößen im 1080 × 1920-Format:**

| Element | Größe |
|---|---|
| Hook / Headline | 96–140 px |
| Untertitel | 52–64 px |
| Mono-Label | 28–36 px |
| Kleinster zulässiger Text | 28 px |

---

## 4. Videos

**Technik:** 9:16 · 1080 × 1920 · 30 fps · MP4 (H.264, AAC) · Lautheit ca. −14 LUFS

**Sicherheitszonen** (TikTok-Bedienelemente überdecken die Ränder):

| Rand | Abstand | Grund |
|---|---|---|
| Oben | 220 px | Kopfzeile |
| Unten | 420 px | Beschreibung, Sound-Zeile |
| Rechts | 180 px | Schaltflächen |
| Links | 64 px | Rand |

Text, Logo und Kernaussage liegen immer innerhalb dieser Zone.

**Aufbau (Richtwert 20–45 Sekunden):**

| Abschnitt | Zeit | Inhalt |
|---|---|---|
| Hook | 0–2 s | Das Problem im Bild + Headline in Versalien. Kein Intro, kein Logo vorab |
| Problem | 2–6 s | Die Reibung zeigen, nicht erklären |
| Flip | 6–25 s | Die Lösung in klaren, nummerierten Schritten |
| Beweis | 25–35 s | Ergebnis, Vorher/Nachher, ehrliches Urteil inkl. Schwäche |
| Outro | letzte 1,5–2 s | Endkarte mit Marke und Claim |

**Regeln:**

- Eine Aussage pro Einstellung. Einstellungen 1,5–4 s.
- Untertitel durchgehend eingebrannt, synchron zum gesprochenen Wort.
- Produktbewertungen zeigen das echte Produkt in Benutzung; Urteil als feste Bewertungskarte (siehe Abschnitt 7).
- Werbung/Affiliate wird im Bild gekennzeichnet (Mono-Label) und zusätzlich über die Plattformfunktion.

---

## 5. Thumbnails / Cover

- Format 1080 × 1920; Kernmotiv und Text in der **mittleren 4:5-Fläche** (1080 × 1350), da Profilraster beschneiden.
- **Ein** Motiv, **eine** Headline (max. 4 Wörter, Versalien), **ein** Copper-Akzent.
- Motiv: Nahaufnahme des Problems oder des Ergebnisses – real fotografiert.
- Hintergrund Graphite oder echtes Bild mit Graphite-Fläche für den Text.
- Laufendes Mono-Label oben links: `FF-0001` (Video-ID) bzw. Serienname.
- Keine Gesichter mit übertriebener Mimik, keine Pfeile-und-Kreise-Ästhetik, keine Emojis, keine Clickbait-Aussagen, die das Video nicht einlöst.
- Alle Cover folgen demselben Raster, damit das Profil als Reihe wirkt.

---

## 6. Animationen

Charakter: **mechanisch, präzise, kurz** – wie ein Schieber, ein Stempel, ein Schalter.

| Bewegung | Dauer | Einsatz |
|---|---|---|
| Harter Schnitt | 0 | Standardübergang |
| Schieben / Maskenreveal (linear oder kurzes Ease-out) | 6–10 Frames | Text, Balken, Karten |
| Linie zeichnen | 8–12 Frames | Maßlinien, Unterstreichung |
| Stempel (100 % → 104 % → 100 %) | 4–6 Frames | Urteil, Schrittnummer |
| „Flip" (Drehung um die horizontale Achse) | 8–10 Frames | **Nur** beim Wechsel Problem → Lösung, max. einmal pro Video |

**Verboten:** Bounce und Elastic-Easing, Glitch, Zoom-Wackeln, Partikel, Glow, 3D-Kamerafahrten
durch Text, Regenbogen-/Farbwechsel, Dauerbewegung ohne Funktion, Übergangseffekte aus
Vorlagenpaketen.

Wort-für-Wort-Untertitel: aktuelles Wort wechselt auf Copper Orange – ohne Springen oder Skalieren.

---

## 7. Wiederkehrende Gestaltungselemente

| Element | Beschreibung |
|---|---|
| **Flip-Balken** | Copper-Orange-Balken, 12 px hoch, links neben oder unter der Headline. Kennzeichen der Marke im Bild |
| **Schrittnummer** | Mono, Versalien: `01`, `02`, `03` – Graphite auf Paper White oder Copper Orange, rechteckig, ohne Rundung |
| **Mono-Label** | Kleines technisches Etikett: `PROBLEM`, `FIX`, `TESTED`, `VERDICT`, `AD` |
| **Maßlinie** | 2-px-Linie mit Endstrichen und Maßangabe (US-Einheiten), Paper White oder Petrol |
| **Raster** | 12 Spalten, 64 px Außenrand; alles richtet sich daran aus |
| **Passmarken** | Feine Eck- und Schnittmarken als redaktionelles Detail – dezent, nie dominant |
| **Bewertungskarte** | Feste Karte bei Reviews: Produktname, `WORKS` / `WORKS, BUT` / `SKIP IT`, ein Plus, ein Minus |
| **Endkarte** | Graphite-Fläche, `FRICTIONFLIP` in Versalien, darunter der Claim `SMALL PROBLEMS. SMARTER SOLUTIONS.`, Flip-Balken |

**Formensprache:** rechte Winkel, Eckenradius 0–4 px, Linien 2 px, keine Schatten, keine
Glaseffekte. Körnung/Papierstruktur dezent zulässig (max. 4 % Deckkraft).

**Logo:** Bis eine Logodatei in `BRAND/` vorliegt, wird ausschließlich der Schriftzug
`FRICTIONFLIP` in der Headline-Schrift verwendet. Es wird kein Bildzeichen entworfen.

---

## 8. Prüfliste vor jeder Freigabe

- [ ] Nur die vier Markenfarben, Petrol höchstens ein Element
- [ ] Kein Verlauf, kein Glow, keine KI-Anmutung
- [ ] Höchstens zwei Schriftrollen, Mindestgrößen eingehalten
- [ ] Text und Kernmotiv innerhalb der Sicherheitszonen
- [ ] Schreibweise `FRICTIONFLIP` und Claim exakt
- [ ] Alle Texte in amerikanischem Englisch
- [ ] Endkarte vorhanden
- [ ] Aussagen belegt, Werbung gekennzeichnet
