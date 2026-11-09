import SwiftUI

extension Calendar {
    /// Kalender mit Montag als Wochenbeginn.
    static var app: Calendar {
        var cal = Calendar.current
        cal.firstWeekday = 2
        return cal
    }
}

extension Color {
    init(hex: String) {
        let cleaned = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var value: UInt64 = 0
        Scanner(string: cleaned).scanHexInt64(&value)
        guard cleaned.count == 6 else {
            self.init(red: 0.5, green: 0.5, blue: 0.5)
            return
        }
        self.init(
            red: Double((value >> 16) & 0xFF) / 255,
            green: Double((value >> 8) & 0xFF) / 255,
            blue: Double(value & 0xFF) / 255
        )
    }
}

enum Palette {
    static let colors = [
        "#FF6B6B", "#FF9F43", "#FECA57", "#1DD1A1", "#10AC84", "#48DBFB",
        "#2E86DE", "#5F27CD", "#A55EEA", "#FF6B9D", "#576574", "#00B894",
    ]

    static let emojis = [
        "⭐️", "💧", "🧘", "📚", "🏃", "👟", "☀️", "🍎", "🥗", "💪", "🛌", "✍️",
        "🎯", "💰", "🧹", "🎸", "🚭", "🍬", "📵", "🙏", "🧠", "❤️", "🌱", "☕️",
    ]
}

extension Double {
    /// 3 statt 3.0, aber 2,5 bleibt 2,5.
    var clean: String {
        formatted(.number.precision(.fractionLength(0...1)))
    }
}

enum Motivation {
    static let quotes = [
        "Kleine Schritte führen zu großen Zielen.",
        "Fortschritt schlägt Perfektion.",
        "Du musst nicht perfekt sein – nur dranbleiben.",
        "Heute ist ein guter Tag, um anzufangen.",
        "Gewohnheiten formen, wer du wirst.",
        "Jeder Haken zählt.",
        "Ein bisschen jeden Tag ist mehr als viel ab und zu.",
    ]

    static func quote(for date: Date) -> String {
        let day = Calendar.app.ordinality(of: .day, in: .era, for: date) ?? 0
        return quotes[day % quotes.count]
    }
}
