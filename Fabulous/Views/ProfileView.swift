import SwiftUI
import SwiftData

struct ProfileView: View {
    @Environment(\.modelContext) private var context
    @AppStorage("userName") private var userName = ""
    @AppStorage("onboardingDone") private var onboardingDone = true

    @Query private var goals: [Goal]
    @Query private var entries: [Entry]
    @Query private var rituals: [Ritual]
    @Query private var progresses: [JourneyProgress]

    @State private var confirmReset = false

    private var bestStreak: Int {
        let goalStreaks = goals.map(\.bestStreak)
        let ritualStreaks = rituals.map(\.currentStreak)
        return (goalStreaks + ritualStreaks).max() ?? 0
    }

    private var memberSince: Date {
        goals.map(\.createdAt).min() ?? .now
    }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    HStack(spacing: 16) {
                        Text(String(userName.first ?? "🙂"))
                            .font(.title.bold())
                            .foregroundStyle(.white)
                            .frame(width: 64, height: 64)
                            .background(
                                LinearGradient(colors: [Color(hex: "#FF9F43"), Color(hex: "#FF6B6B")],
                                               startPoint: .topLeading, endPoint: .bottomTrailing),
                                in: Circle()
                            )
                        VStack(alignment: .leading, spacing: 4) {
                            Text(userName.isEmpty ? "Du" : userName).font(.title2.bold())
                            Text("Dabei seit \(memberSince.formatted(.dateTime.day().month(.wide).year()))")
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                        }
                    }
                    .padding(.vertical, 6)
                }

                Section("Erfolge") {
                    LabeledContent {
                        Text("\(entries.count)")
                    } label: {
                        Label("Einträge insgesamt", systemImage: "checkmark.seal.fill")
                    }
                    LabeledContent {
                        Text("\(bestStreak)")
                    } label: {
                        Label("Längste Serie", systemImage: "flame.fill")
                    }
                    LabeledContent {
                        Text("\(progresses.filter(\.isCompleted).count) / \(Journey.all.count)")
                    } label: {
                        Label("Abgeschlossene Reisen", systemImage: "trophy.fill")
                    }
                }

                Section("Verwalten") {
                    NavigationLink { RitualsListView() } label: {
                        Label("Rituale", systemImage: "sunrise.fill")
                    }
                    NavigationLink { GoalsListView() } label: {
                        Label("Gewohnheiten & Ziele", systemImage: "target")
                    }
                }

                Section("Einstellungen") {
                    HStack {
                        Label("Name", systemImage: "person")
                        TextField("Dein Name", text: $userName)
                            .multilineTextAlignment(.trailing)
                    }
                    Button {
                        onboardingDone = false
                    } label: {
                        Label("Einführung erneut anzeigen", systemImage: "sparkles")
                    }
                }

                Section {
                    Button(role: .destructive) { confirmReset = true } label: {
                        Label("Alle Daten löschen", systemImage: "trash")
                    }
                } footer: {
                    Text("Fabulous ist komplett kostenlos. Alle Daten bleiben nur auf diesem Gerät.")
                }
            }
            .navigationTitle("Ich")
            .navigationDestination(for: Goal.self) { GoalDetailView(goal: $0) }
            .navigationDestination(for: Ritual.self) { RitualDetailView(ritual: $0) }
            .confirmationDialog("Wirklich alle Daten löschen?", isPresented: $confirmReset, titleVisibility: .visible) {
                Button("Alles löschen", role: .destructive, action: resetAll)
            } message: {
                Text("Alle Rituale, Gewohnheiten, Einträge und Reisen werden unwiderruflich gelöscht.")
            }
        }
    }

    private func resetAll() {
        ReminderScheduler.removeAll()
        try? context.delete(model: Entry.self)
        try? context.delete(model: Goal.self)
        try? context.delete(model: Ritual.self)
        try? context.delete(model: JourneyProgress.self)
        try? context.save()
        userName = ""
        onboardingDone = false
    }
}
