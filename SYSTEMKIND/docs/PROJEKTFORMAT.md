# Format der Projektdatei

`projects/<thema>/project.json` beschreibt ein Video vollständig.

## Kopf

| Feld | Bedeutung |
|---|---|
| `topic` | Thema, wie bei `--topic` angegeben |
| `status` | `draft` (Review nötig) oder `approved` |
| `voice` | optional, überschreibt die Markenstimme: `name`, `speaker`, `pitch`, `length_scale` |
| `music.seed` | Variante der Musik |

## Recherche

`research.facts` – jede Zahl und jede These im Video braucht einen Eintrag:

| Feld | Bedeutung |
|---|---|
| `id` | Kurzname, auf den Szenen mit `facts` verweisen |
| `claim` | die Aussage |
| `source`, `url` | Herausgeber und Link. Bei `"kind": "calculation"` darf die URL leer sein. |
| `verified` | `true` nur, wenn an der Quelle geprüft |
| `confidence`, `note` | Einschätzung und Einschränkungen |

`research.uncertainties` – was umstritten oder unsicher ist.

Szenen vom Typ `bars`, `growth` und `formula` müssen mit `facts` auf mindestens einen Fakt verweisen.

## Szenen

Gemeinsame Felder:

| Feld | Bedeutung |
|---|---|
| `type` | Vorlage, siehe unten |
| `background` | `particles`, `grid`, `rings`, `skyline`, `beams`, `plain` |
| `transition` | Übergang in die Szene: `fade`, `dip`, `push`, `sweep`, `cut` |
| `broll` | optional: Schlagworte für einen Clip aus der Bibliothek |
| `vo` | Sätze: `text` (Untertitel) und optional `say` (Aussprache, z. B. Zahlen ausgeschrieben, Wort für Wort) |
| `params` | Inhalt der Vorlage |

Die Länge einer Szene ergibt sich aus ihrem Voice-over.

Hervorhebung in Gold: `*Wort*`.

**Zeitpunkte** (`beat`-Felder) sind entweder die Nummer eines Satzes (`0`, `1`, …)
oder ein gesprochenes Wort aus `text` (`"76"`) – dann startet die Animation genau
bei diesem Wort. `delay` verschiebt in Sekunden.

| Typ | `params` |
|---|---|
| `title` | `kicker`, `lines`, `sub` (Liste), `sub_beat` |
| `statement` | `kicker`, `lines`, `line_beats`, `sub`, `sub_beat`, `size` |
| `bars` | `kicker`, `title` (Zeilen), `unit`, `max`, `items`: `label`, `value`, `highlight`, `beat`, `delay`, `decimals`, `note`; `source` |
| `compare` | `kicker`, `title`, `cards`: `head`, `flow` (zwei Begriffe), `note`, `beat`, `highlight`, `loop` |
| `growth` | `kicker`, `title`, `rate`, `years`, `principals`: `label`, `value`; `start_beat`, `end_beat`, `end_offset`, `chip`, `footnote` |
| `formula` | `kicker`, `formula` (Teile), `formula_beat`, `formula_delay`, `legend`, `legend_beat`, `note`, `note_beat`, `source` |
| `outro` | `lines`, `line_beats`, `brand_beat`, `tagline`, `sources` |

Ein vollständiges Beispiel: `projects/warum-werden-die-reichen-immer-reicher/project.json`.

## Eigene Vorlage

In `systemkind/scenes.py` eine Funktion `draw(frame, d, t, sc)` schreiben und mit
`@scene("name")` registrieren. Soundeffekte der Vorlage in `events()` ergänzen.
