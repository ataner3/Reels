import Foundation
import SwiftData
import SwiftUI

/// Tageszeit-Vorlage für Rituale.
enum RitualSlot: String, CaseIterable, Identifiable {
    case morning, afternoon, evening

    var id: String { rawValue }

    var defaultName: String {
        switch self {
        case .morning: "Morgenritual"
        case .afternoon: "Nachmittagsritual"
        case .evening: "Abendritual"
        }
    }

    var emoji: String {
        switch self {
        case .morning: "🌅"
        case .afternoon: "☀️"
        case .evening: "🌙"
        }
    }

    var colorHex: String {
        switch self {
        case .morning: "#FF9F43"
        case .afternoon: "#2E86DE"
        case .evening: "#5F27CD"
        }
    }

    var defaultHour: (Int, Int) {
        switch self {
        case .morning: (7, 0)
        case .afternoon: (13, 0)
        case .evening: (21, 30)
        }
    }

    func makeRitual(hour: Int? = nil, minute: Int? = nil, sortIndex: Int = 0) -> Ritual {
        Ritual(name: defaultName, emoji: emoji, colorHex: colorHex,
               hour: hour ?? defaultHour.0, minute: minute ?? defaultHour.1,
               slot: self, sortIndex: sortIndex)
    }
}

/// Eine Routine (z. B. Morgenritual), die aus mehreren Gewohnheiten besteht.
@Model
final class Ritual {
    var uid: UUID = UUID()
    var name: String = ""
    var emoji: String = "🌅"
    var colorHex: String = "#FF9F43"
    var time: Date = Date.now
    var reminderEnabled: Bool = true
    var slotRaw: String = ""
    var sortIndex: Int = 0
    var createdAt: Date = Date.now

    @Relationship(deleteRule: .nullify, inverse: \Goal.ritual)
    var habits: [Goal]? = []

    init(name: String, emoji: String, colorHex: String, hour: Int, minute: Int,
         slot: RitualSlot? = nil, sortIndex: Int = 0) {
        self.uid = UUID()
        self.name = name
        self.emoji = emoji
        self.colorHex = colorHex
        self.time = Calendar.current.date(bySettingHour: hour, minute: minute, second: 0, of: .now) ?? .now
        self.slotRaw = slot?.rawValue ?? ""
        self.sortIndex = sortIndex
        self.createdAt = .now
        self.habits = []
    }
}

extension Ritual {
    var color: Color { Color(hex: colorHex) }

    var orderedHabits: [Goal] {
        (habits ?? [])
            .filter { !$0.isArchived && !$0.isDeleted }
            .sorted { $0.ritualOrder < $1.ritualOrder }
    }

    var totalMinutes: Int {
        orderedHabits.reduce(0) { $0 + $1.durationMinutes }
    }

    var minutesOfDay: Int {
        let c = Calendar.current.dateComponents([.hour, .minute], from: time)
        return (c.hour ?? 0) * 60 + (c.minute ?? 0)
    }

    var timeText: String {
        time.formatted(date: .omitted, time: .shortened)
    }

    var infoText: String {
        let count = orderedHabits.count
        var parts = [timeText, count == 1 ? "1 Gewohnheit" : "\(count) Gewohnheiten"]
        if totalMinutes > 0 { parts.append("\(totalMinutes) Min.") }
        return parts.joined(separator: " · ")
    }

    func completedCount(on date: Date) -> Int {
        orderedHabits.filter { $0.isDone(onDay: date) }.count
    }

    func fraction(on date: Date) -> Double {
        let habits = orderedHabits
        guard !habits.isEmpty else { return 0 }
        return Double(completedCount(on: date)) / Double(habits.count)
    }

    func isCompleted(on date: Date) -> Bool {
        let habits = orderedHabits
        return !habits.isEmpty && habits.allSatisfy { $0.isDone(onDay: date) }
    }

    /// Tage in Folge, an denen das komplette Ritual erledigt wurde.
    var currentStreak: Int {
        let cal = Calendar.app
        var day = cal.startOfDay(for: .now)
        if !isCompleted(on: day) {
            guard let previous = cal.date(byAdding: .day, value: -1, to: day) else { return 0 }
            day = previous
        }
        var count = 0
        while count < 3650, isCompleted(on: day) {
            count += 1
            guard let previous = cal.date(byAdding: .day, value: -1, to: day) else { break }
            day = previous
        }
        return count
    }

    func add(_ habit: Goal) {
        habit.ritualOrder = (orderedHabits.map(\.ritualOrder).max() ?? -1) + 1
        habit.ritual = self
    }
}
