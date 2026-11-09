import SwiftUI
import SwiftData
import Charts

struct StatsView: View {
    @Query(sort: \Goal.sortIndex) private var allGoals: [Goal]
    @State private var range = 7

    private var goals: [Goal] { allGoals.filter { !$0.isArchived } }
    private var dailyGoals: [Goal] { goals.filter { $0.frequency == .daily } }

    private struct DayRate: Identifiable {
        let date: Date
        let rate: Double
        var id: Date { date }
    }

    private var dayRates: [DayRate] {
        let cal = Calendar.app
        let today = cal.startOfDay(for: .now)
        return (0..<range).reversed().compactMap { offset -> DayRate? in
            guard let day = cal.date(byAdding: .day, value: -offset, to: today) else { return nil }
            let relevant = dailyGoals.filter { cal.startOfDay(for: $0.trackingStart) <= day }
            guard !relevant.isEmpty else { return DayRate(date: day, rate: 0) }
            let done = relevant.filter { $0.isCompleted(for: day) }.count
            return DayRate(date: day, rate: Double(done) / Double(relevant.count))
        }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                if goals.isEmpty {
                    ContentUnavailableView("Noch keine Daten", systemImage: "chart.bar",
                                           description: Text("Lege Ziele an und tracke sie – hier siehst du dann deinen Fortschritt."))
                        .padding(.top, 60)
                } else {
                    VStack(spacing: 16) {
                        Picker("Zeitraum", selection: $range) {
                            Text("7 Tage").tag(7)
                            Text("30 Tage").tag(30)
                        }
                        .pickerStyle(.segmented)

                        overview

                        if !dailyGoals.isEmpty {
                            Card("Tägliche Ziele erreicht") {
                                Chart(dayRates) { item in
                                    BarMark(
                                        x: .value("Tag", item.date, unit: .day),
                                        y: .value("Quote", item.rate * 100)
                                    )
                                    .foregroundStyle(Color.accentColor.gradient)
                                    .cornerRadius(4)
                                }
                                .chartYScale(domain: 0...100)
                                .chartYAxis {
                                    AxisMarks(values: [0, 50, 100]) { value in
                                        AxisGridLine()
                                        AxisValueLabel { Text("\(value.as(Int.self) ?? 0)%") }
                                    }
                                }
                                .frame(height: 180)
                            }
                        }

                        Card("Ziele im Überblick") {
                            ForEach(goals.sorted { $0.currentStreak > $1.currentStreak }) { goal in
                                NavigationLink(value: goal) {
                                    GoalStatRow(goal: goal, days: range)
                                }
                                .buttonStyle(.plain)
                                Divider()
                            }
                        }
                    }
                    .padding()
                }
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle("Statistik")
            .navigationDestination(for: Goal.self) { GoalDetailView(goal: $0) }
        }
    }

    private var overview: some View {
        let doneToday = goals.filter { $0.isCompleted(for: .now) }.count
        let avgRate = goals.isEmpty ? 0 : goals.map { $0.completionRate(days: range) }.reduce(0, +) / Double(goals.count)
        let bestStreakGoal = goals.max { $0.currentStreak < $1.currentStreak }
        let streak = bestStreakGoal?.currentStreak ?? 0
        let cal = Calendar.app
        let since = cal.date(byAdding: .day, value: -range, to: .now) ?? .now
        let entryCount = goals.flatMap(\.allEntries).filter { $0.date >= since }.count

        return LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
            StatTile(title: "Heute erreicht", value: "\(doneToday)/\(goals.count)",
                     icon: "checkmark.circle.fill", color: .green)
            StatTile(title: "Ø Erfolgsquote", value: "\(Int(avgRate * 100))%",
                     icon: "percent", color: .blue)
            StatTile(title: "Längste Serie" + (bestStreakGoal.map { " · \($0.emoji)" } ?? ""),
                     value: "\(streak)", icon: "flame.fill", color: .orange)
            StatTile(title: "Einträge (\(range) Tage)", value: "\(entryCount)",
                     icon: "list.bullet", color: .purple)
        }
    }
}

struct GoalStatRow: View {
    let goal: Goal
    let days: Int

    var body: some View {
        let rate = goal.completionRate(days: days)
        let streak = goal.currentStreak
        HStack(spacing: 12) {
            EmojiBadge(goal: goal, size: 38)
            VStack(alignment: .leading, spacing: 4) {
                Text(goal.title).font(.subheadline.weight(.semibold))
                ProgressView(value: rate)
                    .tint(goal.color)
            }
            VStack(alignment: .trailing, spacing: 2) {
                Text("\(Int(rate * 100))%").font(.subheadline.bold())
                Label("\(streak)", systemImage: "flame.fill")
                    .font(.caption)
                    .foregroundStyle(streak > 0 ? Color.orange : Color.secondary)
            }
            .frame(width: 56, alignment: .trailing)
        }
        .contentShape(Rectangle())
    }
}
