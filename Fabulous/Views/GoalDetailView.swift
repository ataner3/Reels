import SwiftUI
import SwiftData
import Charts

struct GoalDetailView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss
    let goal: Goal

    @State private var showEditor = false
    @State private var showAmount = false
    @State private var confirmDelete = false
    @State private var isDeleting = false

    var body: some View {
        Group {
            if isDeleting || goal.isDeleted {
                Color.clear
            } else {
                content
            }
        }
        .background(Color(uiColor: .systemGroupedBackground))
        .navigationBarTitleDisplayMode(.inline)
    }

    private var content: some View {
        ScrollView {
            VStack(spacing: 16) {
                header

                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                    let current = goal.currentStreak
                    let best = goal.bestStreak
                    StatTile(title: "Aktuelle Serie", value: "\(current) \(goal.frequency.streakUnit(current))",
                             icon: "flame.fill", color: .orange)
                    StatTile(title: "Beste Serie", value: "\(best) \(goal.frequency.streakUnit(best))",
                             icon: "trophy.fill", color: .yellow)
                    StatTile(title: "Erfolgsquote (30 Tage)",
                             value: "\(Int(goal.completionRate(days: 30) * 100))%",
                             icon: "chart.line.uptrend.xyaxis", color: .green)
                    StatTile(title: goal.kind == .check ? "Mal erledigt" : "Gesamt (\(goal.unit))",
                             value: goal.totalAmount.clean,
                             icon: "sum", color: goal.color)
                }

                Card("Verlauf") { HistoryChart(goal: goal) }

                Card("Kalender") { HeatmapView(goal: goal) }

                if !goal.notes.isEmpty {
                    Card("Meine Motivation") {
                        Text(goal.notes).foregroundStyle(.secondary)
                    }
                }

                EntriesList(goal: goal)
            }
            .padding()
        }
        .navigationTitle(goal.title)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Button { showEditor = true } label: { Label("Bearbeiten", systemImage: "pencil") }
                    Button {
                        goal.isArchived.toggle()
                        ReminderScheduler.update(for: goal)
                    } label: {
                        Label(goal.isArchived ? "Reaktivieren" : "Archivieren",
                              systemImage: goal.isArchived ? "tray.and.arrow.up" : "archivebox")
                    }
                    Divider()
                    Button(role: .destructive) { confirmDelete = true } label: {
                        Label("Löschen", systemImage: "trash")
                    }
                } label: {
                    Image(systemName: "ellipsis.circle")
                }
            }
        }
        .sheet(isPresented: $showEditor) { GoalEditorView(goal: goal) }
        .sheet(isPresented: $showAmount) { AmountSheet(goal: goal, date: .now) }
        .confirmationDialog("Ziel wirklich löschen?", isPresented: $confirmDelete, titleVisibility: .visible) {
            Button("Löschen", role: .destructive, action: deleteGoal)
        } message: {
            Text("Alle Einträge dieses Ziels werden ebenfalls gelöscht.")
        }
    }

    private var header: some View {
        VStack(spacing: 10) {
            ProgressRing(progress: goal.fraction(for: .now), color: goal.color, lineWidth: 10) {
                Text(goal.emoji).font(.system(size: 44))
            }
            .frame(width: 110, height: 110)

            Text(goal.title).font(.title2.bold())
            Text(goal.summary).font(.subheadline).foregroundStyle(.secondary)
            Text(goal.progressText(for: .now)).font(.headline).foregroundStyle(goal.color)

            HStack {
                Button {
                    withAnimation(.spring) { goal.primaryAction(on: .now, in: context) }
                } label: {
                    Label(primaryLabel, systemImage: goal.kind == .check ? "checkmark" : "plus")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)

                Button { showAmount = true } label: {
                    Label(goal.kind == .check ? "Notiz" : "Menge", systemImage: "square.and.pencil")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
            }
            .tint(goal.color)
            .controlSize(.large)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    private var primaryLabel: String {
        switch goal.kind {
        case .check: goal.total(onDay: .now) > 0 ? "Heute erledigt ✓" : "Heute abhaken"
        case .count: "+\(goal.step.clean) \(goal.unit)"
        }
    }

    private func deleteGoal() {
        isDeleting = true
        ReminderScheduler.remove(for: goal)
        dismiss()
        let goal = goal
        let context = context
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
            context.delete(goal)
        }
    }
}

// MARK: - Verlauf (Balkendiagramm)

private struct ChartPoint: Identifiable {
    let date: Date
    let value: Double
    var id: Date { date }
}

struct HistoryChart: View {
    let goal: Goal

    private var points: [ChartPoint] {
        let totals = goal.periodTotals()
        let count = goal.frequency == .daily ? 14 : 12
        var result: [ChartPoint] = []
        var p = goal.period(containing: .now)
        for _ in 0..<count {
            result.append(ChartPoint(date: p.start, value: totals[p.start] ?? 0))
            p = goal.period(containing: p.start.addingTimeInterval(-1))
        }
        return result.reversed()
    }

    var body: some View {
        let unit: Calendar.Component = goal.frequency == .daily ? .day : .weekOfYear
        Chart {
            ForEach(points) { point in
                BarMark(
                    x: .value("Datum", point.date, unit: unit),
                    y: .value("Wert", point.value)
                )
                .foregroundStyle(point.value >= goal.target ? goal.color : goal.color.opacity(0.4))
                .cornerRadius(4)
            }
            RuleMark(y: .value("Ziel", goal.target))
                .lineStyle(StrokeStyle(lineWidth: 1, dash: [4, 4]))
                .foregroundStyle(.secondary)
                .annotation(position: .top, alignment: .leading) {
                    Text("Ziel").font(.caption2).foregroundStyle(.secondary)
                }
        }
        .chartXAxis {
            AxisMarks(values: .stride(by: unit, count: 2)) {
                AxisValueLabel(format: .dateTime.day().month(.defaultDigits))
            }
        }
        .frame(height: 180)
    }
}

// MARK: - Kalender-Heatmap

struct HeatmapView: View {
    let goal: Goal
    private let weeks = 16

    var body: some View {
        let cal = Calendar.app
        let totals = goal.dailyTotals()
        let thisWeek = cal.dateInterval(of: .weekOfYear, for: .now)?.start ?? cal.startOfDay(for: .now)
        let start = cal.date(byAdding: .weekOfYear, value: -(weeks - 1), to: thisWeek) ?? thisWeek
        let today = cal.startOfDay(for: .now)
        // Bei täglichen Zählzielen: Intensität = Anteil am Tagesziel. Sonst: Eintrag ja/nein.
        let dayTarget = (goal.kind == .count && goal.frequency == .daily) ? goal.target : 1

        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .top, spacing: 3) {
                ForEach(0..<weeks, id: \.self) { w in
                    VStack(spacing: 3) {
                        ForEach(0..<7, id: \.self) { d in
                            let day = cal.date(byAdding: .day, value: w * 7 + d, to: start) ?? start
                            let value = totals[cal.startOfDay(for: day)] ?? 0
                            let intensity = min(value / max(dayTarget, 0.0001), 1)
                            RoundedRectangle(cornerRadius: 3)
                                .fill(day > today
                                      ? Color.clear
                                      : (value > 0 ? goal.color.opacity(0.25 + 0.75 * intensity) : Color.gray.opacity(0.15)))
                                .aspectRatio(1, contentMode: .fit)
                        }
                    }
                }
            }
            HStack {
                Text(start.formatted(.dateTime.day().month(.abbreviated)))
                Spacer()
                Text("Heute")
            }
            .font(.caption2)
            .foregroundStyle(.secondary)
        }
    }
}

// MARK: - Einträge

struct EntriesList: View {
    @Environment(\.modelContext) private var context
    let goal: Goal

    var body: some View {
        let recent = goal.allEntries.sorted { $0.date > $1.date }.prefix(30)
        Card("Letzte Einträge") {
            if recent.isEmpty {
                Text("Noch keine Einträge.").foregroundStyle(.secondary)
            } else {
                ForEach(Array(recent)) { entry in
                    HStack(alignment: .top) {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(entry.date.formatted(.dateTime.weekday(.abbreviated).day().month().hour().minute()))
                                .font(.subheadline)
                            if !entry.note.isEmpty {
                                Text(entry.note).font(.caption).foregroundStyle(.secondary)
                            }
                        }
                        Spacer()
                        Text(goal.kind == .check ? "✓" : "+\(entry.value.clean) \(goal.unit)")
                            .font(.subheadline.bold())
                            .foregroundStyle(goal.color)
                        Button {
                            withAnimation { goal.remove(entry, in: context) }
                        } label: {
                            Image(systemName: "trash").font(.caption)
                        }
                        .buttonStyle(.borderless)
                        .foregroundStyle(.secondary)
                        .padding(.leading, 6)
                    }
                    Divider()
                }
            }
        }
    }
}
