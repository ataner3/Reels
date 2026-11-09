import Foundation
import SwiftData

/// Ein einzelner Tracking-Eintrag (z. B. "+1 Glas Wasser" oder "Meditation erledigt").
@Model
final class Entry {
    var date: Date = Date.now
    var value: Double = 1
    var note: String = ""
    var goal: Goal?

    init(date: Date, value: Double, note: String = "") {
        self.date = date
        self.value = value
        self.note = note
    }
}
