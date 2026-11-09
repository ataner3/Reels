import Foundation
import SwiftData

// MARK: - Inhalte (statisch)

struct HabitBlueprint {
    let title: String
    let emoji: String
    let colorHex: String
    let minutes: Int
    let slot: RitualSlot
    let tip: String
}

enum JourneyStepKind {
    /// Ein Brief / Gedanke zum Lesen.
    case letter
    /// Eine einmalige Aufgabe.
    case task(String)
    /// Eine neue Gewohnheit, die an `days` Tagen erledigt werden soll.
    case habit(HabitBlueprint, days: Int)
}

struct JourneyStep: Identifiable {
    let id: String
    let title: String
    let text: String
    let kind: JourneyStepKind
}

struct Journey: Identifiable {
    let id: String
    let title: String
    let subtitle: String
    let emoji: String
    let colorHex: String
    let steps: [JourneyStep]

    static func find(_ id: String) -> Journey? { all.first { $0.id == id } }
}

struct JourneyRoute: Hashable {
    let id: String
}

// MARK: - Fortschritt (gespeichert)

@Model
final class JourneyProgress {
    var journeyID: String = ""
    var startedAt: Date = Date.now
    var stepIndex: Int = 0
    var stepStartedAt: Date = Date.now
    var linkedHabitUID: UUID?
    var isActive: Bool = true
    var completedAt: Date?

    init(journeyID: String) {
        self.journeyID = journeyID
        self.startedAt = .now
        self.stepStartedAt = .now
        self.isActive = true
    }

    var isCompleted: Bool { completedAt != nil }
}

// MARK: - Logik

enum JourneyEngine {
    static func ritual(for slot: RitualSlot, in context: ModelContext) -> Ritual {
        let all = (try? context.fetch(FetchDescriptor<Ritual>())) ?? []
        if let existing = all.first(where: { $0.slotRaw == slot.rawValue }) {
            return existing
        }
        let ritual = slot.makeRitual(sortIndex: all.count)
        context.insert(ritual)
        ReminderScheduler.update(for: ritual)
        return ritual
    }

    /// Fügt die Gewohnheit dem passenden Ritual hinzu (oder findet eine bestehende gleichen Namens).
    @discardableResult
    static func addHabit(_ blueprint: HabitBlueprint, in context: ModelContext) -> Goal {
        let ritual = ritual(for: blueprint.slot, in: context)
        if let existing = ritual.orderedHabits.first(where: { $0.title == blueprint.title }) {
            return existing
        }
        let goals = (try? context.fetch(FetchDescriptor<Goal>())) ?? []
        if let existing = goals.first(where: { $0.title == blueprint.title && !$0.isArchived }) {
            if existing.ritual == nil { ritual.add(existing) }
            return existing
        }
        let habit = Goal(title: blueprint.title, emoji: blueprint.emoji, colorHex: blueprint.colorHex,
                         kind: .check, frequency: .daily, target: 1,
                         sortIndex: (goals.map(\.sortIndex).max() ?? -1) + 1)
        habit.durationMinutes = blueprint.minutes
        habit.notes = blueprint.tip
        context.insert(habit)
        ritual.add(habit)
        ReminderScheduler.update(for: ritual)
        return habit
    }

    static func linkedHabit(for progress: JourneyProgress, goals: [Goal]) -> Goal? {
        guard let uid = progress.linkedHabitUID else { return nil }
        return goals.first { $0.uid == uid && !$0.isDeleted }
    }

    /// An wie vielen Tagen seit Beginn des Schritts die Gewohnheit erledigt wurde.
    static func doneDays(for progress: JourneyProgress, goals: [Goal]) -> Int {
        guard let habit = linkedHabit(for: progress, goals: goals) else { return 0 }
        let cal = Calendar.app
        let start = cal.startOfDay(for: progress.stepStartedAt)
        let days = Set(habit.allEntries.filter { $0.date >= start }.map { cal.startOfDay(for: $0.date) })
        return days.filter { habit.isDone(onDay: $0) }.count
    }

    static func advance(_ progress: JourneyProgress, in journey: Journey) {
        progress.stepIndex += 1
        progress.stepStartedAt = .now
        progress.linkedHabitUID = nil
        if progress.stepIndex >= journey.steps.count {
            progress.completedAt = .now
            progress.isActive = false
        }
    }

    /// Startet (oder setzt fort) eine Reise und pausiert alle anderen.
    static func start(_ journey: Journey, in context: ModelContext) {
        let all = (try? context.fetch(FetchDescriptor<JourneyProgress>())) ?? []
        for p in all { p.isActive = false }
        if let existing = all.first(where: { $0.journeyID == journey.id }) {
            if existing.isCompleted {
                existing.stepIndex = 0
                existing.stepStartedAt = .now
                existing.linkedHabitUID = nil
                existing.completedAt = nil
                existing.startedAt = .now
            }
            existing.isActive = true
        } else {
            context.insert(JourneyProgress(journeyID: journey.id))
        }
    }
}

// MARK: - Reisen

extension Journey {
    static let all: [Journey] = [energy, sleep, focus, calm]

    static let energy = Journey(
        id: "energy",
        title: "Energie für jeden Tag",
        subtitle: "Starte wacher und fitter in deine Tage",
        emoji: "⚡️",
        colorHex: "#FF9F43",
        steps: [
            JourneyStep(id: "energy-1", title: "Der erste Schritt", text: """
                Schön, dass du hier bist.

                Große Veränderungen entstehen selten über Nacht. Sie entstehen aus kleinen Dingen, \
                die du jeden Tag wiederholst – so klein, dass du kaum scheitern kannst.

                Auf dieser Reise baust du dir Schritt für Schritt ein Morgenritual auf, das dir \
                Energie gibt. Jede Etappe bringt eine neue Gewohnheit. Erst wenn sie sitzt, geht es weiter.

                Bereit?
                """, kind: .task("Ich bin bereit")),
            JourneyStep(id: "energy-2", title: "Ein Glas Wasser", text: """
                Nach einer Nacht ohne Trinken ist dein Körper leicht dehydriert – und genau das \
                macht viele Menschen morgens müde und unkonzentriert.

                Deine erste Gewohnheit ist darum ganz einfach: Trink direkt nach dem Aufstehen \
                ein großes Glas Wasser. Stell es dir am besten schon abends neben das Bett.
                """, kind: .habit(HabitBlueprint(title: "Ein Glas Wasser trinken", emoji: "💧", colorHex: "#48DBFB",
                                                  minutes: 1, slot: .morning,
                                                  tip: "Stell dir das Glas schon am Abend bereit."), days: 3)),
            JourneyStep(id: "energy-3", title: "Warum willst du das?", text: """
                Gewohnheiten halten länger, wenn du weißt, wofür du sie machst.

                Nimm dir zwei Minuten und schreib auf: Was würdest du mit mehr Energie anfangen? \
                Mehr Zeit mit Freunden? Endlich Sport? Konzentrierter arbeiten?

                Trag deine Antwort bei einer deiner Gewohnheiten unter „Motivation“ ein – \
                dann siehst du sie jedes Mal wieder.
                """, kind: .task("Aufgeschrieben")),
            JourneyStep(id: "energy-4", title: "Ein gutes Frühstück", text: """
                Ein ausgewogenes Frühstück mit etwas Eiweiß und Ballaststoffen hält deinen \
                Blutzucker stabil – und damit auch deine Laune und Konzentration.

                Es muss nicht aufwendig sein: Haferflocken mit Obst, ein Joghurt mit Nüssen \
                oder ein Vollkornbrot reichen völlig.
                """, kind: .habit(HabitBlueprint(title: "Gesund frühstücken", emoji: "🥣", colorHex: "#FECA57",
                                                  minutes: 10, slot: .morning,
                                                  tip: "Bereite am Abend vorher schon etwas vor."), days: 3)),
            JourneyStep(id: "energy-5", title: "Kurz bewegen", text: """
                Schon fünf Minuten Bewegung bringen deinen Kreislauf in Schwung: Hampelmänner, \
                ein paar Kniebeugen, Dehnen oder einmal um den Block.

                Wichtig ist nicht, wie viel du machst – sondern dass du es jeden Morgen machst.
                """, kind: .habit(HabitBlueprint(title: "5 Minuten Bewegung", emoji: "🤸", colorHex: "#1DD1A1",
                                                  minutes: 5, slot: .morning,
                                                  tip: "Leg deine Lieblingsmusik dazu auf."), days: 5)),
            JourneyStep(id: "energy-6", title: "Geschafft!", text: """
                Schau, wie weit du gekommen bist: Dein Morgenritual besteht jetzt aus drei \
                Gewohnheiten, die dir jeden Tag Energie schenken.

                Gönn dir einen Moment Stolz. Und dann: Such dir deine nächste Reise aus.
                """, kind: .letter),
        ]
    )

    static let sleep = Journey(
        id: "sleep",
        title: "Besser schlafen",
        subtitle: "Ruhiger einschlafen, erholter aufwachen",
        emoji: "🌙",
        colorHex: "#5F27CD",
        steps: [
            JourneyStep(id: "sleep-1", title: "Schlaf ist deine Superkraft", text: """
                Guter Schlaf ist die Grundlage für fast alles: Laune, Konzentration, Gesundheit.

                Auf dieser Reise baust du dir ein Abendritual, das deinem Körper signalisiert: \
                Jetzt ist Zeit zum Runterfahren.
                """, kind: .task("Los geht's")),
            JourneyStep(id: "sleep-2", title: "Bildschirme aus", text: """
                Helles Licht und ständige Reize halten dein Gehirn wach. \
                Leg dein Handy 30 Minuten vor dem Schlafen weg – am besten außerhalb des Schlafzimmers.
                """, kind: .habit(HabitBlueprint(title: "Handy weglegen", emoji: "📵", colorHex: "#576574",
                                                  minutes: 1, slot: .evening,
                                                  tip: "Ein normaler Wecker statt Handy hilft enorm."), days: 3)),
            JourneyStep(id: "sleep-3", title: "Dein Schlafzimmer", text: """
                Dunkel, ruhig und eher kühl (ca. 18 °C) – so schläft es sich am besten. \
                Lüfte heute einmal richtig durch und schau, was dich beim Einschlafen stört.
                """, kind: .task("Erledigt")),
            JourneyStep(id: "sleep-4", title: "Runterkommen", text: """
                Ein festes kleines Ritual hilft beim Abschalten: ein Kräutertee, ein paar Seiten \
                in einem Buch oder ruhige Musik.
                """, kind: .habit(HabitBlueprint(title: "Tee & Lesen", emoji: "🍵", colorHex: "#A55EEA",
                                                  minutes: 15, slot: .evening,
                                                  tip: "Am besten ein Papierbuch, kein Bildschirm."), days: 3)),
            JourneyStep(id: "sleep-5", title: "Feste Aufstehzeit", text: """
                Dein innerer Rhythmus liebt Regelmäßigkeit. Steh jeden Tag zur gleichen Zeit auf – \
                auch am Wochenende, so gut es geht.
                """, kind: .habit(HabitBlueprint(title: "Pünktlich aufstehen", emoji: "⏰", colorHex: "#FF6B6B",
                                                  minutes: 1, slot: .morning,
                                                  tip: "Kein Snooze – sofort aufstehen."), days: 5)),
            JourneyStep(id: "sleep-6", title: "Gute Nacht", text: """
                Du hast dir ein richtiges Abendritual aufgebaut. Bleib dran – \
                guter Schlaf wird mit jeder Woche selbstverständlicher.
                """, kind: .letter),
        ]
    )

    static let focus = Journey(
        id: "focus",
        title: "Fokus & Klarheit",
        subtitle: "Weniger Ablenkung, mehr geschafft",
        emoji: "🎯",
        colorHex: "#2E86DE",
        steps: [
            JourneyStep(id: "focus-1", title: "Weniger, aber besser", text: """
                Produktiv zu sein heißt nicht, mehr zu machen – sondern das Richtige. \
                Auf dieser Reise lernst du, deine Aufmerksamkeit zu schützen.
                """, kind: .task("Verstanden")),
            JourneyStep(id: "focus-2", title: "Deine Top 3", text: """
                Schreib jeden Morgen die drei wichtigsten Dinge des Tages auf. \
                Wenn du nur diese drei schaffst, war der Tag ein Erfolg.
                """, kind: .habit(HabitBlueprint(title: "Top 3 des Tages planen", emoji: "📝", colorHex: "#2E86DE",
                                                  minutes: 5, slot: .morning,
                                                  tip: "Die wichtigste Aufgabe zuerst erledigen."), days: 3)),
            JourneyStep(id: "focus-3", title: "Benachrichtigungen aufräumen", text: """
                Jede Benachrichtigung reißt dich raus. Geh heute durch deine Einstellungen und \
                schalte alles aus, was nicht wirklich wichtig ist.
                """, kind: .task("Aufgeräumt")),
            JourneyStep(id: "focus-4", title: "Fokuszeit", text: """
                Arbeite 25 Minuten an einer einzigen Sache – Handy außer Reichweite. \
                Danach 5 Minuten Pause. Der Timer im Ritual-Modus hilft dir dabei.
                """, kind: .habit(HabitBlueprint(title: "Fokuszeit ohne Handy", emoji: "🧠", colorHex: "#5F27CD",
                                                  minutes: 25, slot: .afternoon,
                                                  tip: "Handy in einen anderen Raum legen."), days: 3)),
            JourneyStep(id: "focus-5", title: "Den Tag abschließen", text: """
                Schau abends kurz zurück: Was lief gut? Was nimmst du mit? \
                So wird dein Kopf frei für den Feierabend.
                """, kind: .habit(HabitBlueprint(title: "Tag reflektieren", emoji: "✍️", colorHex: "#576574",
                                                  minutes: 5, slot: .evening,
                                                  tip: "Drei Sätze reichen."), days: 5)),
            JourneyStep(id: "focus-6", title: "Klarer Kopf", text: """
                Du planst, du fokussierst, du reflektierst. Damit hast du ein System, \
                das dich jeden Tag ein Stück weiterbringt.
                """, kind: .letter),
        ]
    )

    static let calm = Journey(
        id: "calm",
        title: "Ruhe & Achtsamkeit",
        subtitle: "Weniger Stress, mehr Gelassenheit",
        emoji: "🧘",
        colorHex: "#1DD1A1",
        steps: [
            JourneyStep(id: "calm-1", title: "Innehalten", text: """
                Stress lässt sich nicht immer vermeiden – aber du kannst lernen, anders damit \
                umzugehen. Diese Reise schenkt dir jeden Tag kleine Momente der Ruhe.
                """, kind: .task("Ich bin dabei")),
            JourneyStep(id: "calm-2", title: "Meditation", text: """
                Setz dich bequem hin, schließ die Augen und beobachte fünf Minuten lang deinen Atem. \
                Wenn Gedanken kommen, lass sie ziehen und kehr zum Atem zurück.
                """, kind: .habit(HabitBlueprint(title: "Meditieren", emoji: "🧘", colorHex: "#1DD1A1",
                                                  minutes: 5, slot: .morning,
                                                  tip: "Gleicher Ort, gleiche Zeit."), days: 3)),
            JourneyStep(id: "calm-3", title: "Dankbarkeit", text: """
                Schreib jeden Abend drei Dinge auf, für die du heute dankbar bist. \
                Das lenkt den Blick auf das, was gut läuft.
                """, kind: .habit(HabitBlueprint(title: "Dankbarkeit notieren", emoji: "🙏", colorHex: "#FF6B9D",
                                                  minutes: 3, slot: .evening,
                                                  tip: "Auch Kleinigkeiten zählen."), days: 3)),
            JourneyStep(id: "calm-4", title: "Ein Spaziergang", text: """
                Geh heute 15 Minuten spazieren – ohne Handy, ohne Kopfhörer. \
                Achte nur auf das, was du siehst, hörst und riechst.
                """, kind: .task("Gemacht")),
            JourneyStep(id: "calm-5", title: "Atempause", text: """
                Mitten am Tag: Atme 4 Sekunden ein, halte 4 Sekunden, atme 6 Sekunden aus. \
                Zwei Minuten reichen, um dein Nervensystem zu beruhigen.
                """, kind: .habit(HabitBlueprint(title: "Tief durchatmen", emoji: "🌬️", colorHex: "#48DBFB",
                                                  minutes: 2, slot: .afternoon,
                                                  tip: "Länger aus- als einatmen."), days: 5)),
            JourneyStep(id: "calm-6", title: "Gelassenheit", text: """
                Morgens, mittags und abends hast du jetzt einen ruhigen Moment für dich. \
                Das ist ein Geschenk, das du dir jeden Tag selbst machst.
                """, kind: .letter),
        ]
    )
}
