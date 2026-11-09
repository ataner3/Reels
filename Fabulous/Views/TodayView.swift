import SwiftUI
import SwiftData

struct TodayView: View {
    @Query(sort: \Goal.sortIndex) private var allGoals: [Goal]
    @State private var selectedDate = Date.now
    @State private var showEditor = false
    @State private var amountGoal: Goal?

    private var goals: [Goal] { allGoals.filter { !$0.isArchived } }

    private var isToday: Bool { Calendar.app.isDateInToday(selectedDate) }

    private var title: String {
        if isToday { return "Heute" }
        if Calendar.app.isDateInYesterday(selectedDate) { return "Gestern" }
        return selectedDate.formatted(.dateTime.weekday(.wide).day().month())
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 16) {
                    WeekStrip(selectedDate: $selectedDate, goals: goals)

                    if goals.isEmpty {
                        ContentUnavailableView {
                            Label("Noch keine Ziele", systemImage: "target")
                        } description: {
                            Text("Lege dein erstes Ziel an und fang an zu tracken.")
                        } actions: {
                            Button("Ziel hinzufügen") { showEditor = true }
                                .buttonStyle(.borderedProminent)
                        }
                        .padding(.top, 40)
                    } else {
                        SummaryCard(goals: goals, date: selectedDate)

                        ForEach(goals) { goal in
                            GoalCard(goal: goal, date: selectedDate) {
                                amountGoal = goal
                            }
                        }
                    }
                }
                .padding()
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle(title)
            .toolbar {
                if !isToday {
                    ToolbarItem(placement: .topBarLeading) {
                        Button("Heute") { withAnimation { selectedDate = .now } }
                    }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showEditor = true } label: {
                        Image(systemName: "plus.circle.fill").font(.title2)
                    }
                }
            }
            .navigationDestination(for: Goal.self) { GoalDetailView(goal: $0) }
            .sheet(isPresented: $showEditor) { GoalEditorView() }
            .sheet(item: $amountGoal) { goal in
                AmountSheet(goal: goal, date: selectedDate)
            }
        }
    }
}

// MARK: - Wochenleiste

struct WeekStrip: View {
    @Binding var selectedDate: Date
    let goals: [Goal]

    private var days: [Date] {
        let cal = Calendar.app
        let start = cal.dateInterval(of: .weekOfYear, for: selectedDate)?.start ?? cal.startOfDay(for: selectedDate)
        return (0..<7).compactMap { cal.date(byAdding: .day, value: $0, to: start) }
    }

    private var canGoForward: Bool {
        guard let last = days.last else { return false }
        return last < Calendar.app.startOfDay(for: .now)
    }

    var body: some View {
        HStack(spacing: 4) {
            Button { shift(by: -7) } label: { Image(systemName: "chevron.left") }
                .buttonStyle(.plain)
                .foregroundStyle(.secondary)

            ForEach(days, id: \.self) { day in
                dayCell(day)
            }

            Button { shift(by: 7) } label: { Image(systemName: "chevron.right") }
                .buttonStyle(.plain)
                .foregroundStyle(canGoForward ? .secondary : .quaternary)
                .disabled(!canGoForward)
        }
    }

    private func dayCell(_ day: Date) -> some View {
        let cal = Calendar.app
        let isSelected = cal.isDate(day, inSameDayAs: selectedDate)
        let isFuture = day > .now
        let done = goals.filter { $0.isCompleted(for: day) }.count
        let fraction = goals.isEmpty ? 0 : Double(done) / Double(goals.count)

        return Button {
            withAnimation(.snappy) { selectedDate = day }
        } label: {
            VStack(spacing: 6) {
                Text(day.formatted(.dateTime.weekday(.narrow)))
                    .font(.caption2.bold())
                    .foregroundStyle(.secondary)
                ProgressRing(progress: isFuture ? 0 : fraction, color: .accentColor, lineWidth: 3) {
                    Text(day.formatted(.dateTime.day()))
                        .font(.footnote.weight(isSelected ? .bold : .regular))
                }
                .frame(width: 34, height: 34)
            }
            .padding(.vertical, 8)
            .frame(maxWidth: .infinity)
            .background(isSelected ? Color.accentColor.opacity(0.15) : .clear, in: RoundedRectangle(cornerRadius: 12))
        }
        .buttonStyle(.plain)
        .disabled(isFuture)
        .opacity(isFuture ? 0.4 : 1)
    }

    private func shift(by days: Int) {
        guard let next = Calendar.app.date(byAdding: .day, value: days, to: selectedDate) else { return }
        withAnimation(.snappy) { selectedDate = min(next, .now) }
    }
}

// MARK: - Zusammenfassung

struct SummaryCard: View {
    let goals: [Goal]
    let date: Date

    var body: some View {
        let done = goals.filter { $0.isCompleted(for: date) }.count
        let fraction = goals.isEmpty ? 0 : Double(done) / Double(goals.count)

        HStack(spacing: 18) {
            ProgressRing(progress: fraction, color: .accentColor, lineWidth: 10) {
                Text("\(Int(fraction * 100))%")
                    .font(.headline)
                    .contentTransition(.numericText())
            }
            .frame(width: 76, height: 76)

            VStack(alignment: .leading, spacing: 6) {
                Text(done == goals.count ? "Alles geschafft! 🎉" : "\(done) von \(goals.count) Zielen erreicht")
                    .font(.headline)
                Text(Motivation.quote(for: date))
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            Spacer(minLength: 0)
        }
        .padding()
        .background(
            LinearGradient(colors: [Color.accentColor.opacity(0.18), Color.accentColor.opacity(0.05)],
                           startPoint: .topLeading, endPoint: .bottomTrailing),
            in: RoundedRectangle(cornerRadius: 20, style: .continuous)
        )
    }
}

// MARK: - Ziel-Karte

struct GoalCard: View {
    @Environment(\.modelContext) private var context
    let goal: Goal
    let date: Date
    var onCustomAmount: () -> Void

    var body: some View {
        let done = goal.isCompleted(for: date)
        let checkedThatDay = goal.total(onDay: date) > 0
        let filled = goal.kind == .check ? checkedThatDay : done
        let streak = goal.currentStreak

        HStack(spacing: 14) {
            NavigationLink(value: goal) {
                HStack(spacing: 14) {
                    EmojiBadge(goal: goal, size: 48)
                    VStack(alignment: .leading, spacing: 4) {
                        Text(goal.title)
                            .font(.headline)
                            .foregroundStyle(.primary)
                        Text(goal.progressText(for: date))
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                        if streak > 0 {
                            Label("\(streak) \(goal.frequency.streakUnit(streak))", systemImage: "flame.fill")
                                .font(.caption.bold())
                                .foregroundStyle(.orange)
                        }
                    }
                    Spacer(minLength: 0)
                }
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            Button {
                withAnimation(.spring) { goal.primaryAction(on: date, in: context) }
            } label: {
                ZStack {
                    Circle()
                        .fill(filled ? goal.color : .clear)
                        .padding(3)
                    ProgressRing(progress: goal.fraction(for: date), color: goal.color, lineWidth: 5) {
                        Image(systemName: goal.kind == .check ? "checkmark" : "plus")
                            .font(.headline.bold())
                            .foregroundStyle(filled ? Color.white : goal.color)
                    }
                }
                .frame(width: 50, height: 50)
            }
            .buttonStyle(.plain)
            .accessibilityLabel(goal.kind == .check ? "Abhaken" : "\(goal.step.clean) hinzufügen")
        }
        .padding(14)
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(done ? goal.color.opacity(0.7) : .clear, lineWidth: 2)
        )
        .sensoryFeedback(trigger: done) { _, new in
            new ? .success : nil
        }
        .contextMenu {
            if goal.kind == .count {
                Button { onCustomAmount() } label: {
                    Label("Menge eingeben …", systemImage: "number")
                }
                Button(role: .destructive) {
                    withAnimation { goal.undoLast(on: date, in: context) }
                } label: {
                    Label("Letzten Eintrag entfernen", systemImage: "arrow.uturn.backward")
                }
            } else {
                Button { onCustomAmount() } label: {
                    Label("Mit Notiz abhaken …", systemImage: "square.and.pencil")
                }
            }
        }
    }
}

// MARK: - Menge eingeben

struct AmountSheet: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss
    let goal: Goal
    let date: Date

    @State private var amount: Double
    @State private var note = ""

    init(goal: Goal, date: Date) {
        self.goal = goal
        self.date = date
        _amount = State(initialValue: goal.kind == .check ? 1 : goal.step)
    }

    var body: some View {
        NavigationStack {
            Form {
                if goal.kind == .count {
                    Section("Menge") {
                        HStack {
                            Text(goal.emoji)
                            TextField("Menge", value: $amount, format: .number)
                                .keyboardType(.decimalPad)
                                .font(.title3.bold())
                            Text(goal.unit).foregroundStyle(.secondary)
                        }
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack {
                                ForEach(quickValues, id: \.self) { value in
                                    Button(value.clean) { amount = value }
                                        .buttonStyle(.bordered)
                                        .tint(goal.color)
                                }
                            }
                        }
                    }
                }
                Section("Notiz") {
                    TextField("Optional, z. B. wie es lief", text: $note, axis: .vertical)
                        .lineLimit(2...5)
                }
            }
            .navigationTitle(goal.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Abbrechen") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Speichern") {
                        guard amount > 0 else { return }
                        goal.log(amount, note: note, on: date, in: context)
                        dismiss()
                    }
                    .disabled(amount <= 0)
                }
            }
        }
        .presentationDetents([.medium, .large])
    }

    private var quickValues: [Double] {
        let s = max(goal.step, 1)
        return [s, s * 2, s * 5, s * 10]
    }
}
