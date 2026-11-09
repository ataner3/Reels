import Foundation

struct GoalTemplate: Identifiable {
    let id = UUID()
    let title: String
    let emoji: String
    let colorHex: String
    let kind: GoalKind
    let frequency: GoalFrequency
    let target: Double
    let unit: String
    let step: Double

    static let all: [GoalTemplate] = [
        .init(title: "Wasser trinken", emoji: "💧", colorHex: "#48DBFB", kind: .count, frequency: .daily, target: 8, unit: "Gläser", step: 1),
        .init(title: "Meditieren", emoji: "🧘", colorHex: "#A55EEA", kind: .check, frequency: .daily, target: 1, unit: "", step: 1),
        .init(title: "Lesen", emoji: "📚", colorHex: "#FF9F43", kind: .count, frequency: .daily, target: 20, unit: "Seiten", step: 5),
        .init(title: "Sport", emoji: "🏃", colorHex: "#1DD1A1", kind: .check, frequency: .weekly, target: 3, unit: "", step: 1),
        .init(title: "Schritte", emoji: "👟", colorHex: "#2E86DE", kind: .count, frequency: .daily, target: 10000, unit: "Schritte", step: 1000),
        .init(title: "Früh aufstehen", emoji: "☀️", colorHex: "#FECA57", kind: .check, frequency: .daily, target: 1, unit: "", step: 1),
        .init(title: "Kein Zucker", emoji: "🍬", colorHex: "#FF6B9D", kind: .check, frequency: .daily, target: 1, unit: "", step: 1),
        .init(title: "Tagebuch", emoji: "✍️", colorHex: "#576574", kind: .check, frequency: .daily, target: 1, unit: "", step: 1),
        .init(title: "Sparen", emoji: "💰", colorHex: "#10AC84", kind: .count, frequency: .weekly, target: 50, unit: "€", step: 5),
    ]
}
