# Fabulous – Ziele & Gewohnheiten tracken

Fabulous gibt es in zwei Varianten:

1. **Web-App** (`web/`): läuft im Browser auf iPhone, iPad und überall sonst. Kein Mac nötig.
2. **Native iOS-App** (`Fabulous/`, SwiftUI): braucht einen Mac mit Xcode zum Installieren.

## Web-App (empfohlen)

**Direkt nutzen:** Die App ist als claude.ai-Artifact veröffentlicht. Link in Safari öffnen, mit dem
claude.ai-Konto anmelden, über *Teilen → Zum Home-Bildschirm* ablegen. Die Daten werden über das
claude.ai-Konto zwischen iPhone und iPad synchronisiert.

**Selbst hosten (optional):** `web/index.html` ist eine eigenständige Web-App mit App-Icon und Offline-Modus.
Daten liegen dann nur im Browser des Geräts (Backup über *Ich → Backup sichern*).
Für GitHub Pages: im Repo unter *Settings → Pages* als Quelle „GitHub Actions“ wählen; der Workflow
`.github/workflows/pages.yml` veröffentlicht `web/` bei jedem Push auf `main`.

Aufbau:

```
web/
├── src/content.js     Reisen, Vorlagen, Farben, Sprüche
├── src/app.js         App-Logik, Ansichten, Sync, Ritual-Modus
├── src/style.css      Design (hell & dunkel)
├── build.py           baut app.html (Artifact) und index.html (eigenständig)
├── manifest.webmanifest, sw.js, icons/   für „Zum Home-Bildschirm“ & offline
```

Nach Änderungen in `web/src/` einmal `python3 web/build.py` ausführen.

---

# Native iOS-App (SwiftUI)

## Funktionen

Aufgebaut nach dem Prinzip „kleine Gewohnheiten, feste Rituale, geführte Reisen“ – komplett kostenlos, ohne Abo, ohne Konto.

- **Einführung** beim ersten Start: Name, erste Reise auswählen, Aufstehzeit
- **Heute** – Begrüßung, Wochenleiste, Tagesfortschritt, aktuelle Reise und deine Rituale
  - **Rituale** (Morgen / Nachmittag / Abend) bestehen aus mehreren Gewohnheiten, die du direkt abhakst
  - **Ritual starten** ▶ – geführter Vollbild-Modus: eine Gewohnheit nach der anderen, mit Countdown-Timer, Tipp und Abschluss-Feier 🎉
  - Eigenständige **Ziele & Tracker** zum Zählen (Wasser, Seiten, Schritte, € …), auch wöchentlich
- **Reisen** – Programme mit Schritten: Briefe, einmalige Aufgaben und neue Gewohnheiten, die automatisch
  deinem Ritual hinzugefügt werden. Ein Schritt ist geschafft, wenn du die Gewohnheit an X Tagen erledigt hast.
  - ⚡️ Energie für jeden Tag · 🌙 Besser schlafen · 🎯 Fokus & Klarheit · 🧘 Ruhe & Achtsamkeit
- **Fortschritt** – Erfolgsquote (7/30 Tage), Diagramme, Serien 🔥, Kalender-Heatmap pro Gewohnheit
- **Ich** – Profil, Erfolge, Rituale & Gewohnheiten verwalten, alle Daten löschen
- **Erinnerungen** pro Ritual (und optional pro Gewohnheit)
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
├── App/FabulousApp.swift          App-Einstieg, Einführung oder Tab-Leiste
├── Models/
│   ├── Goal.swift                 Gewohnheit/Ziel, Fortschritt, Serien, Aktionen
│   ├── Entry.swift                Einzelner Tracking-Eintrag
│   ├── Ritual.swift               Rituale (Morgen/Nachmittag/Abend)
│   ├── Journey.swift              Reisen: Inhalte, Fortschritt, Logik
│   └── GoalTemplate.swift         Vorlagen
├── Views/
│   ├── OnboardingView.swift       Einführung beim ersten Start
│   ├── TodayView.swift            Heute-Ansicht, Wochenleiste, Karten
│   ├── RitualViews.swift          Ritual-Karte, Details, Editor, Liste
│   ├── RitualPlayerView.swift     Geführter Ritual-Modus mit Timer
│   ├── JourneyViews.swift         Reisen-Tab und Reise-Details
│   ├── GoalsListView.swift        Liste aller Gewohnheiten & Ziele
│   ├── GoalEditorView.swift       Gewohnheit/Ziel anlegen/bearbeiten
│   ├── GoalDetailView.swift       Details, Diagramm, Heatmap, Einträge
│   ├── StatsView.swift            Fortschritt
│   ├── ProfileView.swift          Ich / Einstellungen
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
