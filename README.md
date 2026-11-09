# Fabulous – Ziele & Gewohnheiten tracken

Eine native iOS-App (SwiftUI + SwiftData), mit der du dir Ziele setzt und täglich bzw. wöchentlich trackst.

## Funktionen

- **Heute** – alle aktiven Ziele auf einen Blick, mit Tagesfortschritt und Motivationsspruch
  - Ein Tipp auf den runden Button hakt ein Ziel ab oder zählt hoch (z. B. +1 Glas Wasser)
  - Gedrückt halten: eigene Menge eingeben, Notiz hinzufügen oder den letzten Eintrag rückgängig machen
  - Über die Wochenleiste kannst du vergangene Tage nachtragen
- **Zwei Arten von Zielen**
  - *Abhaken*: täglich (z. B. Meditieren) oder X-mal pro Woche (z. B. 3× Sport)
  - *Zählen*: Mengen mit Einheit (Gläser, Seiten, Schritte, €), täglich oder wöchentlich
- **Serien** 🔥 – aktuelle und beste Serie pro Ziel
- **Detailansicht** – Balkendiagramm, Kalender-Heatmap (16 Wochen), Erfolgsquote, Einträge mit Notizen
- **Statistik** – Erfolgsquote über 7/30 Tage, Tagesübersicht, alle Ziele im Vergleich
- **Erinnerungen** – tägliche Push-Benachrichtigung zur gewünschten Uhrzeit
- **Vorlagen** – Wasser trinken, Meditieren, Lesen, Sport, Schritte, Sparen …
- Ziele sortieren, archivieren, löschen; Dark Mode wird unterstützt
- Alle Daten bleiben lokal auf dem Gerät (SwiftData)

## Voraussetzungen

- Mac mit **Xcode 16** oder neuer
- iOS **17.0** oder neuer (iPhone oder Simulator)

## Starten

1. `Fabulous.xcodeproj` in Xcode öffnen
2. Oben das Ziel-Gerät wählen (z. B. „iPhone 16“-Simulator)
3. **⌘R** drücken

Auf einem echten iPhone: unter *Signing & Capabilities* dein Team auswählen und ggf. den
Bundle Identifier (`com.example.fabulous`) auf etwas Eigenes ändern.

## Aufbau

```
Fabulous/
├── App/FabulousApp.swift          App-Einstieg + Tab-Leiste
├── Models/
│   ├── Goal.swift                 Ziel-Modell, Fortschritt, Serien, Aktionen
│   ├── Entry.swift                Einzelner Tracking-Eintrag
│   └── GoalTemplate.swift         Vorlagen
├── Views/
│   ├── TodayView.swift            Heute-Ansicht, Wochenleiste, Ziel-Karten
│   ├── GoalsListView.swift        Liste aller Ziele
│   ├── GoalEditorView.swift       Ziel anlegen/bearbeiten
│   ├── GoalDetailView.swift       Details, Diagramm, Heatmap, Einträge
│   ├── StatsView.swift            Statistik
│   └── Components.swift           Fortschrittsring, Kacheln, Karten
└── Utilities/
    ├── Helpers.swift              Farben, Kalender, Formatierung
    └── ReminderScheduler.swift    Benachrichtigungen
```

## Ideen für später

- App-Icon (unter `Assets.xcassets/AppIcon` ein 1024×1024-Bild ablegen)
- iCloud-Sync über CloudKit
- Widgets für den Homescreen
- Apple-Health-Anbindung für Schritte/Schlaf
