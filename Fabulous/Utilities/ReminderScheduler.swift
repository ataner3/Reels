import Foundation
import UserNotifications

/// Plant tägliche Erinnerungen für Ziele.
enum ReminderScheduler {
    static func update(for goal: Goal) {
        let center = UNUserNotificationCenter.current()
        let id = goal.uid.uuidString
        center.removePendingNotificationRequests(withIdentifiers: [id])

        guard goal.reminderEnabled, !goal.isArchived else { return }

        let title = "\(goal.emoji) \(goal.title)"
        let body = goal.kind == .check
            ? "Zeit für dein Ziel – hak es heute ab!"
            : "Denk an dein Ziel: \(goal.summary)."
        let components = Calendar.current.dateComponents([.hour, .minute], from: goal.reminderTime)

        center.requestAuthorization(options: [.alert, .sound, .badge]) { granted, _ in
            guard granted else { return }
            let content = UNMutableNotificationContent()
            content.title = title
            content.body = body
            content.sound = .default
            let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: true)
            center.add(UNNotificationRequest(identifier: id, content: content, trigger: trigger))
        }
    }

    static func remove(for goal: Goal) {
        UNUserNotificationCenter.current()
            .removePendingNotificationRequests(withIdentifiers: [goal.uid.uuidString])
    }
}
