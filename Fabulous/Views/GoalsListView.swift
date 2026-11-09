import SwiftUI
import SwiftData

struct GoalsListView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \Goal.sortIndex) private var allGoals: [Goal]
    @State private var showEditor = false

    private var active: [Goal] { allGoals.filter { !$0.isArchived } }
    private var archived: [Goal] { allGoals.filter { $0.isArchived } }

    var body: some View {
        List {
                if allGoals.isEmpty {
                    ContentUnavailableView("Keine Ziele", systemImage: "target",
                                           description: Text("Tippe auf +, um ein Ziel anzulegen."))
                }
                if !active.isEmpty {
                    Section("Aktiv") {
                        ForEach(active) { goal in
                            NavigationLink(value: goal) { GoalListRow(goal: goal) }
                        }
                        .onMove(perform: move)
                        .onDelete { offsets in delete(offsets.map { active[$0] }) }
                    }
                }
                if !archived.isEmpty {
                    Section("Archiviert") {
                        ForEach(archived) { goal in
                            NavigationLink(value: goal) { GoalListRow(goal: goal) }
                                .swipeActions(edge: .leading) {
                                    Button("Reaktivieren") {
                                        goal.isArchived = false
                                        ReminderScheduler.update(for: goal)
                                    }
                                    .tint(.green)
                                }
                        }
                        .onDelete { offsets in delete(offsets.map { archived[$0] }) }
                    }
                }
            }
        .navigationTitle("Gewohnheiten & Ziele")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) { EditButton() }
            ToolbarItem(placement: .topBarTrailing) {
                Button { showEditor = true } label: { Image(systemName: "plus") }
            }
        }
        .sheet(isPresented: $showEditor) { GoalEditorView() }
    }

    private func move(from source: IndexSet, to destination: Int) {
        var reordered = active
        reordered.move(fromOffsets: source, toOffset: destination)
        for (index, goal) in reordered.enumerated() {
            goal.sortIndex = index
        }
    }

    private func delete(_ goals: [Goal]) {
        for goal in goals {
            ReminderScheduler.remove(for: goal)
            context.delete(goal)
        }
    }
}

struct GoalListRow: View {
    let goal: Goal

    var body: some View {
        HStack(spacing: 12) {
            EmojiBadge(goal: goal, size: 40)
            VStack(alignment: .leading, spacing: 2) {
                Text(goal.title).font(.body.weight(.semibold))
                Text(goal.ritual.map { "\($0.emoji) \($0.name)" } ?? goal.summary)
                    .font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            if goal.reminderEnabled {
                Image(systemName: "bell.fill").font(.caption).foregroundStyle(.secondary)
            }
            let streak = goal.currentStreak
            if streak > 0 {
                Label("\(streak)", systemImage: "flame.fill")
                    .font(.caption.bold())
                    .foregroundStyle(.orange)
            }
        }
        .padding(.vertical, 2)
    }
}
