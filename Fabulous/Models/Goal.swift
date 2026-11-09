import Foundation
import SwiftData
import SwiftUI

enum GoalKind: String, Codable, CaseIterable, Identifiable {
    /// Einfach abhaken (z. B. "Meditieren")
    case check
    /// Menge zählen (z. B. "8 Gläser Wasser")
    case count

    var id: String { rawValue }
    var label: String {
        switch self {
        case .check: "Abhaken"
        case .count: "Zählen"
        }
    }
}

enum GoalFrequency: String, Codable, CaseIterable, Identifiable {
    case daily
    case weekly

    var id: String { rawValue }
    var label: String {
        switch self {
        case .daily: "Täglich"
        case .weekly: "Wöchentlich"
        }
    }

    func streakUnit(_ count: Int) -> String {
        switch self {
        case .daily: count == 1 ? "Tag" : "Tage"
        case .weekly: count == 1 ? "Woche" : "Wochen"
        }
    }
}

@Model
final class Goal {
    var uid: UUID = UUID()
    var title: String = ""
    var emoji: String = "⭐️"
    var colorHex: String = "#FF6B6B"
    var kindRaw: String = GoalKind.check.rawValue
    var frequencyRaw: String = GoalFrequency.daily.rawValue
    /// Zielwert pro Zeitraum (Tag oder Woche).
    var target: Double = 1
    var unit: String = ""
    /// Wie viel ein Tipp auf "+" hinzufügt.
    var step: Double = 1
    var notes: String = ""
    var createdAt: Date = Date.now
    var isArchived: Bool = false
    var sortIndex: Int = 0
    var reminderEnabled: Bool = false
    var reminderTime: Date = Date.now
    /// Ritual, zu dem diese Gewohnheit gehört (nil = eigenständiges Ziel/Tracker).
    var ritual: Ritual?
    var ritualOrder: Int = 0
    /// Dauer im geführten Ritual-Modus (0 = kein Timer).
    var durationMinutes: Int = 0

    @Relationship(deleteRule: .cascade, inverse: \Entry.goal)
    var entries: [Entry]? = []

    init(
        title: String,
        emoji: String,
        colorHex: String,
        kind: GoalKind,
        frequency: GoalFrequency,
        target: Double,
        unit: String = "",
        step: Double = 1,
        sortIndex: Int = 0
    ) {
        self.uid = UUID()
        self.title = title
        self.emoji = emoji
        self.colorHex = colorHex
        self.kindRaw = kind.rawValue
        self.frequencyRaw = frequency.rawValue
        self.target = target
        self.unit = unit
        self.step = step
        self.sortIndex = sortIndex
        self.createdAt = .now
        self.reminderTime = Calendar.current.date(bySettingHour: 8, minute: 0, second: 0, of: .now) ?? .now
        self.entries = []
    }
}

// MARK: - Abgeleitete Werte

extension Goal {
    var kind: GoalKind {
        get { GoalKind(rawValue: kindRaw) ?? .check }
        set { kindRaw = newValue.rawValue }
    }

    var frequency: GoalFrequency {
        get { GoalFrequency(rawValue: frequencyRaw) ?? .daily }
        set { frequencyRaw = newValue.rawValue }
    }

    var color: Color { Color(hex: colorHex) }

    var allEntries: [Entry] { entries ?? [] }

    var summary: String {
        switch (kind, frequency) {
        case (.check, .daily): "Täglich abhaken"
        case (.check, .weekly): "\(target.clean)× pro Woche"
        case (.count, .daily): "\(target.clean) \(unit) pro Tag"
        case (.count, .weekly): "\(target.clean) \(unit) pro Woche"
        }
    }

    /// Zeitraum (Tag bzw. Woche), in dem `date` liegt.
    func period(containing date: Date) -> DateInterval {
        let cal = Calendar.app
        switch frequency {
        case .daily:
            return cal.dateInterval(of: .day, for: date) ?? DateInterval(start: cal.startOfDay(for: date), duration: 86_400)
        case .weekly:
            return cal.dateInterval(of: .weekOfYear, for: date) ?? DateInterval(start: cal.startOfDay(for: date), duration: 7 * 86_400)
        }
    }

    func total(in interval: DateInterval) -> Double {
        allEntries
            .filter { $0.date >= interval.start && $0.date < interval.end }
            .reduce(0) { $0 + $1.value }
    }

    func entriesOn(day date: Date) -> [Entry] {
        let cal = Calendar.app
        return allEntries.filter { cal.isDate($0.date, inSameDayAs: date) }
    }

    func total(onDay date: Date) -> Double {
        entriesOn(day: date).reduce(0) { $0 + $1.value }
    }

    /// Fortschritt im Zeitraum, der `date` enthält.
    func progress(for date: Date) -> Double {
        total(in: period(containing: date))
    }

    func fraction(for date: Date) -> Double {
        guard target > 0 else { return 0 }
        return min(progress(for: date) / target, 1)
    }

    func isCompleted(for date: Date) -> Bool {
        progress(for: date) >= target
    }

    func progressText(for date: Date) -> String {
        let p = progress(for: date)
        switch (kind, frequency) {
        case (.check, .daily): return p >= 1 ? "Erledigt 🎉" : "Noch offen"
        case (.check, .weekly): return "\(p.clean) von \(target.clean)× diese Woche"
        case (.count, .daily): return "\(p.clean) / \(target.clean) \(unit)"
        case (.count, .weekly): return "\(p.clean) / \(target.clean) \(unit) diese Woche"
        }
    }

    /// Summen je Zeitraum-Start.
    func periodTotals() -> [Date: Double] {
        Dictionary(grouping: allEntries) { period(containing: $0.date).start }
            .mapValues { $0.reduce(0) { $0 + $1.value } }
    }

    /// Summen je Kalendertag.
    func dailyTotals() -> [Date: Double] {
        let cal = Calendar.app
        return Dictionary(grouping: allEntries) { cal.startOfDay(for: $0.date) }
            .mapValues { $0.reduce(0) { $0 + $1.value } }
    }

    var trackingStart: Date {
        min(createdAt, allEntries.map(\.date).min() ?? createdAt)
    }

    var currentStreak: Int {
        let totals = periodTotals()
        var p = period(containing: .now)
        // Der laufende Zeitraum bricht die Serie nicht, solange er noch nicht vorbei ist.
        if (totals[p.start] ?? 0) < target {
            p = period(containing: p.start.addingTimeInterval(-1))
        }
        var count = 0
        while (totals[p.start] ?? 0) >= target {
            count += 1
            p = period(containing: p.start.addingTimeInterval(-1))
        }
        return count
    }

    var bestStreak: Int {
        let totals = periodTotals()
        guard let first = totals.keys.min() else { return 0 }
        var best = 0
        var run = 0
        var p = period(containing: first)
        let now = Date.now
        while p.start <= now {
            if (totals[p.start] ?? 0) >= target {
                run += 1
                best = max(best, run)
            } else {
                run = 0
            }
            p = period(containing: p.end)
        }
        return best
    }

    /// Anteil erreichter Zeiträume in den letzten `days` Tagen (0...1).
    func completionRate(days: Int) -> Double {
        let totals = periodTotals()
        let periods = frequency == .daily ? days : max(1, Int((Double(days) / 7).rounded(.up)))
        let startLimit = period(containing: trackingStart).start
        var p = period(containing: .now)
        var counted = 0
        var done = 0
        for i in 0..<periods {
            if p.start < startLimit { break }
            let reached = (totals[p.start] ?? 0) >= target
            // Laufenden Zeitraum nur zählen, wenn er schon erreicht ist.
            if !(i == 0 && !reached) {
                counted += 1
                if reached { done += 1 }
            }
            p = period(containing: p.start.addingTimeInterval(-1))
        }
        return counted == 0 ? 0 : Double(done) / Double(counted)
    }

    var totalAmount: Double {
        allEntries.reduce(0) { $0 + $1.value }
    }
}

// MARK: - Aktionen

extension Goal {
    /// Für Rituale: Ist die Gewohnheit an diesem Tag erledigt?
    func isDone(onDay date: Date) -> Bool {
        switch (kind, frequency) {
        case (.count, .daily): isCompleted(for: date)
        default: total(onDay: date) > 0
        }
    }

    /// Markiert die Gewohnheit für diesen Tag als erledigt.
    func completeForDay(_ date: Date, in context: ModelContext) {
        guard !isDone(onDay: date) else { return }
        switch (kind, frequency) {
        case (.count, .daily):
            log(max(target - total(onDay: date), step), on: date, in: context)
        case (.count, .weekly):
            log(step, on: date, in: context)
        case (.check, _):
            log(1, on: date, in: context)
        }
    }

    /// Hebt die Erledigung für diesen Tag auf.
    func resetDay(_ date: Date, in context: ModelContext) {
        for entry in entriesOn(day: date) { remove(entry, in: context) }
    }

    func toggleDone(on date: Date, in context: ModelContext) {
        if isDone(onDay: date) {
            resetDay(date, in: context)
        } else {
            completeForDay(date, in: context)
        }
    }

    /// Haupt-Aktion des runden Buttons: abhaken bzw. einen Schritt hinzufügen.
    func primaryAction(on date: Date, in context: ModelContext) {
        switch kind {
        case .check:
            if total(onDay: date) > 0 {
                for entry in entriesOn(day: date) { remove(entry, in: context) }
            } else {
                log(1, on: date, in: context)
            }
        case .count:
            log(step, on: date, in: context)
        }
    }

    func log(_ value: Double, note: String = "", on date: Date, in context: ModelContext) {
        let entry = Entry(date: Self.timestamp(for: date), value: value, note: note)
        context.insert(entry)
        if entries == nil {
            entries = [entry]
        } else {
            entries?.append(entry)
        }
    }

    func undoLast(on date: Date, in context: ModelContext) {
        guard let last = entriesOn(day: date).max(by: { $0.date < $1.date }) else { return }
        remove(last, in: context)
    }

    func remove(_ entry: Entry, in context: ModelContext) {
        entries?.removeAll { $0.persistentModelID == entry.persistentModelID }
        context.delete(entry)
    }

    /// Heute → aktuelle Uhrzeit, vergangene Tage → 12:00 Uhr.
    static func timestamp(for date: Date) -> Date {
        let cal = Calendar.app
        if cal.isDateInToday(date) { return .now }
        return cal.date(bySettingHour: 12, minute: 0, second: 0, of: date) ?? date
    }
}
