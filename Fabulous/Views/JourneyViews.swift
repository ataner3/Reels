import SwiftUI
import SwiftData

// MARK: - Reisen-Tab

struct JourneysView: View {
    @Query private var progresses: [JourneyProgress]

    private var active: JourneyProgress? { progresses.first { $0.isActive && !$0.isCompleted } }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    if let active, let journey = Journey.find(active.journeyID) {
                        Text("Deine aktuelle Reise").font(.title3.bold())
                        NavigationLink(value: JourneyRoute(id: journey.id)) {
                            JourneyBanner(journey: journey, progress: active, large: true)
                        }
                        .buttonStyle(.plain)
                    }

                    Text(active == nil ? "Wähle eine Reise" : "Weitere Reisen")
                        .font(.title3.bold())
                        .padding(.top, 8)

                    ForEach(Journey.all.filter { $0.id != active?.journeyID }) { journey in
                        NavigationLink(value: JourneyRoute(id: journey.id)) {
                            JourneyTile(journey: journey,
                                        progress: progresses.first { $0.journeyID == journey.id })
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding()
            }
            .background(Color(uiColor: .systemGroupedBackground))
            .navigationTitle("Reisen")
            .navigationDestination(for: JourneyRoute.self) { JourneyDetailView(journeyID: $0.id) }
            .navigationDestination(for: Goal.self) { GoalDetailView(goal: $0) }
        }
    }
}

struct JourneyBanner: View {
    let journey: Journey
    let progress: JourneyProgress
    var large = false

    var body: some View {
        let stepIndex = min(progress.stepIndex, journey.steps.count - 1)
        let step = journey.steps[stepIndex]
        let fraction = Double(progress.stepIndex) / Double(journey.steps.count)

        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(journey.emoji).font(large ? .largeTitle : .title2)
                VStack(alignment: .leading, spacing: 2) {
                    Text(large ? journey.title : "Deine Reise · \(journey.title)")
                        .font(large ? .title2.bold() : .caption.bold())
                        .opacity(large ? 1 : 0.85)
                    Text("Schritt \(stepIndex + 1) von \(journey.steps.count): \(step.title)")
                        .font(large ? .subheadline : .headline)
                }
                Spacer()
                Image(systemName: "chevron.right").font(.headline).opacity(0.7)
            }
            ProgressView(value: fraction)
                .tint(.white)
        }
        .foregroundStyle(.white)
        .padding()
        .background(
            LinearGradient(colors: [Color(hex: journey.colorHex), Color(hex: journey.colorHex).opacity(0.7)],
                           startPoint: .leading, endPoint: .trailing),
            in: RoundedRectangle(cornerRadius: 20, style: .continuous)
        )
    }
}

struct JourneyTile: View {
    let journey: Journey
    let progress: JourneyProgress?

    var body: some View {
        HStack(spacing: 14) {
            Text(journey.emoji)
                .font(.largeTitle)
                .frame(width: 64, height: 64)
                .background(Color(hex: journey.colorHex).opacity(0.2), in: RoundedRectangle(cornerRadius: 16))
            VStack(alignment: .leading, spacing: 4) {
                Text(journey.title).font(.headline)
                Text(journey.subtitle).font(.subheadline).foregroundStyle(.secondary)
                Group {
                    if let progress, progress.isCompleted {
                        Label("Abgeschlossen", systemImage: "trophy.fill").foregroundStyle(.yellow)
                    } else if let progress {
                        Text("Pausiert · Schritt \(progress.stepIndex + 1)/\(journey.steps.count)")
                            .foregroundStyle(.secondary)
                    } else {
                        Text("\(journey.steps.count) Schritte").foregroundStyle(.secondary)
                    }
                }
                .font(.caption.bold())
            }
            Spacer()
            Image(systemName: "chevron.right").foregroundStyle(.tertiary)
        }
        .padding()
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

// MARK: - Reise-Details

struct JourneyDetailView: View {
    @Environment(\.modelContext) private var context
    @Query private var progresses: [JourneyProgress]
    @Query private var goals: [Goal]
    let journeyID: String

    @State private var readingStep: JourneyStep?
    @State private var confirmSwitch = false

    private var journey: Journey? { Journey.find(journeyID) }
    private var progress: JourneyProgress? { progresses.first { $0.journeyID == journeyID } }
    private var otherActive: JourneyProgress? {
        progresses.first { $0.isActive && !$0.isCompleted && $0.journeyID != journeyID }
    }

    var body: some View {
        if let journey {
            content(journey)
        } else {
            ContentUnavailableView("Reise nicht gefunden", systemImage: "map")
        }
    }

    private func content(_ journey: Journey) -> some View {
        let color = Color(hex: journey.colorHex)
        let isRunning = progress.map { $0.isActive && !$0.isCompleted } ?? false

        return ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                VStack(spacing: 8) {
                    Text(journey.emoji).font(.system(size: 64))
                    Text(journey.title).font(.title.bold()).multilineTextAlignment(.center)
                    Text(journey.subtitle).foregroundStyle(.white.opacity(0.9)).multilineTextAlignment(.center)
                    if let progress {
                        ProgressView(value: Double(progress.stepIndex), total: Double(journey.steps.count))
                            .tint(.white)
                            .padding(.top, 6)
                    }
                }
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity)
                .padding(24)
                .background(LinearGradient(colors: [color, color.opacity(0.7)], startPoint: .top, endPoint: .bottom),
                            in: RoundedRectangle(cornerRadius: 24, style: .continuous))

                if progress?.isCompleted == true {
                    Card {
                        Label("Reise abgeschlossen!", systemImage: "trophy.fill")
                            .font(.headline)
                            .foregroundStyle(.yellow)
                        Button("Noch einmal starten") { start(journey) }
                            .buttonStyle(.bordered)
                    }
                } else if !isRunning {
                    Button {
                        if otherActive != nil { confirmSwitch = true } else { start(journey) }
                    } label: {
                        Text(progress == nil ? "Reise starten" : "Reise fortsetzen")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(color)
                    .controlSize(.large)
                }

                ForEach(Array(journey.steps.enumerated()), id: \.element.id) { offset, step in
                    let state = stepState(offset, isRunning: isRunning)
                    if state == .current, let progress {
                        CurrentStepCard(journey: journey, step: step, progress: progress,
                                        goals: goals, color: color, number: offset + 1)
                    } else {
                        StepRow(step: step, number: offset + 1, state: state, color: color)
                            .onTapGesture { if state == .done { readingStep = step } }
                    }
                }
            }
            .padding()
        }
        .background(Color(uiColor: .systemGroupedBackground))
        .navigationTitle(journey.title)
        .navigationBarTitleDisplayMode(.inline)
        .sheet(item: $readingStep) { step in
            NavigationStack {
                ScrollView {
                    Text(step.text).padding()
                }
                .navigationTitle(step.title)
                .toolbar {
                    ToolbarItem(placement: .confirmationAction) { Button("Fertig") { readingStep = nil } }
                }
            }
            .presentationDetents([.medium, .large])
        }
        .confirmationDialog("Reise wechseln?", isPresented: $confirmSwitch, titleVisibility: .visible) {
            Button("Wechseln") { start(journey) }
        } message: {
            Text("Deine aktuelle Reise wird pausiert. Du kannst sie später fortsetzen.")
        }
    }

    private func stepState(_ offset: Int, isRunning: Bool) -> StepState {
        guard let progress else { return .locked }
        if offset < progress.stepIndex || progress.isCompleted { return .done }
        if offset == progress.stepIndex && isRunning { return .current }
        return .locked
    }

    private func start(_ journey: Journey) {
        withAnimation { JourneyEngine.start(journey, in: context) }
    }
}

enum StepState { case done, current, locked }

private struct StepRow: View {
    let step: JourneyStep
    let number: Int
    let state: StepState
    let color: Color

    var body: some View {
        HStack(spacing: 12) {
            ZStack {
                Circle().fill(state == .done ? color : Color.gray.opacity(0.2))
                switch state {
                case .done: Image(systemName: "checkmark").font(.caption.bold()).foregroundStyle(.white)
                case .locked: Image(systemName: "lock.fill").font(.caption).foregroundStyle(.secondary)
                case .current: Text("\(number)").font(.caption.bold())
                }
            }
            .frame(width: 32, height: 32)
            VStack(alignment: .leading, spacing: 2) {
                Text(step.title).font(.subheadline.weight(.semibold))
                Text(step.kindLabel).font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            if state == .done {
                Image(systemName: "text.book.closed").foregroundStyle(.tertiary)
            }
        }
        .padding(12)
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 16))
        .opacity(state == .locked ? 0.6 : 1)
        .contentShape(Rectangle())
    }
}

private struct CurrentStepCard: View {
    @Environment(\.modelContext) private var context
    let journey: Journey
    let step: JourneyStep
    let progress: JourneyProgress
    let goals: [Goal]
    let color: Color
    let number: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("SCHRITT \(number) · \(step.kindLabel.uppercased())")
                .font(.caption.bold())
                .foregroundStyle(color)
            Text(step.title).font(.title2.bold())
            Text(step.text).font(.body)

            switch step.kind {
            case .letter:
                actionButton(progress.stepIndex + 1 >= journey.steps.count ? "Reise abschließen" : "Weiter")
            case .task(let label):
                actionButton(label)
            case .habit(let blueprint, let days):
                habitSection(blueprint, days: days)
            }
        }
        .padding()
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(color, lineWidth: 2))
    }

    private func actionButton(_ label: String) -> some View {
        Button {
            withAnimation { JourneyEngine.advance(progress, in: journey) }
        } label: {
            Text(label).font(.headline).frame(maxWidth: .infinity)
        }
        .buttonStyle(.borderedProminent)
        .tint(color)
        .controlSize(.large)
    }

    @ViewBuilder
    private func habitSection(_ blueprint: HabitBlueprint, days: Int) -> some View {
        if let habit = JourneyEngine.linkedHabit(for: progress, goals: goals) {
            let done = JourneyEngine.doneDays(for: progress, goals: goals)
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text(habit.emoji).font(.title2)
                    VStack(alignment: .leading) {
                        Text(habit.title).font(.headline)
                        Text(habit.ritual.map { "Im \($0.name)" } ?? "Eigenständige Gewohnheit")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                }
                HStack(spacing: 6) {
                    ForEach(0..<days, id: \.self) { i in
                        Circle()
                            .fill(i < done ? color : Color.gray.opacity(0.2))
                            .frame(width: 22, height: 22)
                            .overlay {
                                if i < done {
                                    Image(systemName: "checkmark").font(.caption2.bold()).foregroundStyle(.white)
                                }
                            }
                    }
                }
                Text(done >= days
                     ? "Super! Die Gewohnheit sitzt."
                     : "Erledige sie an \(days) Tagen, um weiterzukommen (\(min(done, days))/\(days)).")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)

                if done >= days {
                    actionButton("Nächster Schritt")
                } else if !habit.isDone(onDay: .now) {
                    Button {
                        withAnimation { habit.completeForDay(.now, in: context) }
                    } label: {
                        Label("Heute erledigt", systemImage: "checkmark")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                    .tint(color)
                    .controlSize(.large)
                } else {
                    Label("Für heute erledigt – bis morgen!", systemImage: "checkmark.circle.fill")
                        .font(.subheadline.bold())
                        .foregroundStyle(color)
                }
            }
        } else {
            Button {
                withAnimation {
                    let habit = JourneyEngine.addHabit(blueprint, in: context)
                    progress.linkedHabitUID = habit.uid
                    progress.stepStartedAt = .now
                }
            } label: {
                Label("„\(blueprint.title)“ zu meinem \(blueprint.slot.defaultName) hinzufügen",
                      systemImage: "plus.circle.fill")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .tint(color)
            .controlSize(.large)
        }
    }
}

extension JourneyStep {
    var kindLabel: String {
        switch kind {
        case .letter: "Brief"
        case .task: "Aufgabe"
        case .habit(_, let days): "Neue Gewohnheit · \(days) Tage"
        }
    }
}
