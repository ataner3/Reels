import SwiftUI
import SwiftData

// MARK: - Ritual-Karte (Heute)

struct RitualCard: View {
    let ritual: Ritual
    let date: Date
    var onStart: () -> Void
    var onAddHabit: () -> Void

    var body: some View {
        let habits = ritual.orderedHabits
        let done = ritual.completedCount(on: date)
        let completed = ritual.isCompleted(on: date)
        let isToday = Calendar.app.isDateInToday(date)

        VStack(alignment: .leading, spacing: 12) {
            NavigationLink(value: ritual) {
                HStack(spacing: 12) {
                    Text(ritual.emoji)
                        .font(.title2)
                        .frame(width: 46, height: 46)
                        .background(.white.opacity(0.25), in: Circle())
                    VStack(alignment: .leading, spacing: 2) {
                        Text(ritual.name).font(.title3.bold())
                        Text(ritual.infoText).font(.caption).opacity(0.85)
                    }
                    Spacer()
                    ProgressRing(progress: ritual.fraction(on: date), color: .white, lineWidth: 4) {
                        if completed {
                            Image(systemName: "checkmark").font(.caption.bold())
                        } else {
                            Text("\(done)/\(habits.count)").font(.caption2.bold())
                        }
                    }
                    .frame(width: 40, height: 40)
                }
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            if habits.isEmpty {
                Button(action: onAddHabit) {
                    Label("Erste Gewohnheit hinzufügen", systemImage: "plus.circle")
                        .font(.subheadline.bold())
                }
                .buttonStyle(.plain)
            } else {
                VStack(spacing: 6) {
                    ForEach(habits) { habit in
                        HabitRow(habit: habit, date: date)
                    }
                }
            }

            if !habits.isEmpty && isToday {
                Button(action: onStart) {
                    Label(completed ? "Erneut durchgehen" : "Ritual starten",
                          systemImage: completed ? "arrow.clockwise" : "play.fill")
                        .font(.headline)
                        .foregroundStyle(ritual.color)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(.white, in: Capsule())
                }
                .buttonStyle(.plain)
            }
        }
        .foregroundStyle(.white)
        .padding()
        .background(
            LinearGradient(colors: [ritual.color, ritual.color.opacity(0.75)],
                           startPoint: .topLeading, endPoint: .bottomTrailing),
            in: RoundedRectangle(cornerRadius: 24, style: .continuous)
        )
        .sensoryFeedback(trigger: completed) { _, new in new ? .success : nil }
    }
}

struct HabitRow: View {
    @Environment(\.modelContext) private var context
    let habit: Goal
    let date: Date

    var body: some View {
        let done = habit.isDone(onDay: date)
        HStack(spacing: 10) {
            NavigationLink(value: habit) {
                HStack(spacing: 10) {
                    Text(habit.emoji)
                        .frame(width: 32, height: 32)
                        .background(.white.opacity(0.2), in: Circle())
                    VStack(alignment: .leading, spacing: 0) {
                        Text(habit.title)
                            .font(.subheadline.weight(.semibold))
                            .strikethrough(done, color: Color.white.opacity(0.7))
                        if habit.durationMinutes > 0 || habit.kind == .count {
                            Text(habit.kind == .count ? habit.progressText(for: date) : "\(habit.durationMinutes) Min.")
                                .font(.caption2)
                                .opacity(0.8)
                        }
                    }
                    Spacer(minLength: 0)
                }
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            Button {
                withAnimation(.spring) { habit.toggleDone(on: date, in: context) }
            } label: {
                Image(systemName: done ? "checkmark.circle.fill" : "circle")
                    .font(.title2)
                    .symbolEffect(.bounce, value: done)
            }
            .buttonStyle(.plain)
        }
        .padding(8)
        .background(.white.opacity(done ? 0.25 : 0.12), in: RoundedRectangle(cornerRadius: 14))
        .opacity(done ? 0.85 : 1)
    }
}

// MARK: - Ritual-Details

struct RitualDetailView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss
    let ritual: Ritual

    @State private var showEditor = false
    @State private var showAddHabit = false
    @State private var playing: Ritual?

    var body: some View {
        if ritual.isDeleted {
            Color.clear
        } else {
            content
        }
    }

    private var content: some View {
        List {
            Section {
                VStack(spacing: 10) {
                    Text(ritual.emoji).font(.system(size: 56))
                    Text(ritual.name).font(.title2.bold())
                    Text(ritual.infoText).font(.subheadline).foregroundStyle(.secondary)
                    HStack(spacing: 24) {
                        VStack {
                            Text("\(ritual.currentStreak)").font(.title3.bold())
                            Text("Tage in Folge").font(.caption).foregroundStyle(.secondary)
                        }
                        VStack {
                            Text("\(ritual.completedCount(on: .now))/\(ritual.orderedHabits.count)").font(.title3.bold())
                            Text("Heute").font(.caption).foregroundStyle(.secondary)
                        }
                    }
                    .padding(.top, 4)
                    if !ritual.orderedHabits.isEmpty {
                        Button { playing = ritual } label: {
                            Label("Ritual starten", systemImage: "play.fill")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(ritual.color)
                        .controlSize(.large)
                        .padding(.top, 6)
                    }
                }
                .frame(maxWidth: .infinity)
                .listRowBackground(Color.clear)
            }

            Section {
                ForEach(ritual.orderedHabits) { habit in
                    NavigationLink(value: habit) {
                        HStack(spacing: 12) {
                            EmojiBadge(goal: habit, size: 36)
                            VStack(alignment: .leading) {
                                Text(habit.title)
                                Text(habit.durationMinutes > 0 ? "\(habit.durationMinutes) Min." : "Ohne Timer")
                                    .font(.caption).foregroundStyle(.secondary)
                            }
                        }
                    }
                }
                .onMove(perform: move)
                .onDelete(perform: removeHabits)

                Button { showAddHabit = true } label: {
                    Label("Gewohnheit hinzufügen", systemImage: "plus")
                }
            } header: {
                Text("Gewohnheiten")
            } footer: {
                Text("Wische nach links, um eine Gewohnheit aus dem Ritual zu entfernen (sie bleibt als eigenes Ziel erhalten). Mit „Bearbeiten“ änderst du die Reihenfolge.")
            }
        }
        .navigationTitle(ritual.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Button { showEditor = true } label: { Label("Ritual bearbeiten", systemImage: "pencil") }
                    EditButton()
                } label: {
                    Image(systemName: "ellipsis.circle")
                }
            }
        }
        .sheet(isPresented: $showEditor) { RitualEditorView(ritual: ritual, onDelete: { dismiss() }) }
        .sheet(isPresented: $showAddHabit) { GoalEditorView(ritual: ritual) }
        .fullScreenCover(item: $playing) { RitualPlayerView(ritual: $0) }
    }

    private func move(from source: IndexSet, to destination: Int) {
        var habits = ritual.orderedHabits
        habits.move(fromOffsets: source, toOffset: destination)
        for (index, habit) in habits.enumerated() { habit.ritualOrder = index }
    }

    private func removeHabits(at offsets: IndexSet) {
        let habits = ritual.orderedHabits
        for index in offsets { habits[index].ritual = nil }
    }
}

// MARK: - Ritual anlegen / bearbeiten

struct RitualEditorView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss
    @Query private var rituals: [Ritual]

    let ritual: Ritual?
    var onDelete: (() -> Void)?

    @State private var name: String
    @State private var emoji: String
    @State private var colorHex: String
    @State private var time: Date
    @State private var reminderEnabled: Bool
    @State private var confirmDelete = false

    private let emojis = ["🌅", "☀️", "🌙", "🌤️", "🏋️", "💼", "🍽️", "📚", "🧘", "🛁", "⭐️", "🌿"]

    init(ritual: Ritual? = nil, onDelete: (() -> Void)? = nil) {
        self.ritual = ritual
        self.onDelete = onDelete
        _name = State(initialValue: ritual?.name ?? "")
        _emoji = State(initialValue: ritual?.emoji ?? "🌤️")
        _colorHex = State(initialValue: ritual?.colorHex ?? "#2E86DE")
        _time = State(initialValue: ritual?.time
            ?? Calendar.current.date(bySettingHour: 13, minute: 0, second: 0, of: .now) ?? .now)
        _reminderEnabled = State(initialValue: ritual?.reminderEnabled ?? true)
    }

    var body: some View {
        NavigationStack {
            Form {
                if ritual == nil {
                    Section("Vorlagen") {
                        ForEach(RitualSlot.allCases) { slot in
                            Button {
                                name = slot.defaultName
                                emoji = slot.emoji
                                colorHex = slot.colorHex
                                time = Calendar.current.date(bySettingHour: slot.defaultHour.0,
                                                             minute: slot.defaultHour.1, second: 0, of: .now) ?? time
                            } label: {
                                Label(slot.defaultName, systemImage: "wand.and.stars")
                            }
                        }
                    }
                }

                Section("Ritual") {
                    HStack {
                        Text(emoji)
                            .font(.title)
                            .frame(width: 48, height: 48)
                            .background(Color(hex: colorHex).opacity(0.25), in: Circle())
                        TextField("Name, z. B. Morgenritual", text: $name)
                            .font(.headline)
                    }
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 6) {
                            ForEach(emojis, id: \.self) { e in
                                Text(e)
                                    .font(.title3)
                                    .frame(width: 38, height: 38)
                                    .background(e == emoji ? Color(hex: colorHex).opacity(0.3) : .clear,
                                                in: RoundedRectangle(cornerRadius: 10))
                                    .onTapGesture { emoji = e }
                            }
                        }
                    }
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 10) {
                            ForEach(Palette.colors, id: \.self) { hex in
                                Circle()
                                    .fill(Color(hex: hex))
                                    .frame(width: 30, height: 30)
                                    .overlay(Circle().stroke(Color.primary, lineWidth: hex == colorHex ? 2.5 : 0).padding(-4))
                                    .padding(4)
                                    .onTapGesture { colorHex = hex }
                            }
                        }
                    }
                }

                Section("Zeit") {
                    DatePicker("Uhrzeit", selection: $time, displayedComponents: .hourAndMinute)
                    Toggle("Erinnerung", isOn: $reminderEnabled)
                }

                if ritual != nil {
                    Section {
                        Button("Ritual löschen", role: .destructive) { confirmDelete = true }
                    } footer: {
                        Text("Die Gewohnheiten bleiben als eigene Ziele erhalten.")
                    }
                }
            }
            .navigationTitle(ritual == nil ? "Neues Ritual" : "Ritual bearbeiten")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Abbrechen") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Sichern", action: save)
                        .disabled(name.trimmingCharacters(in: .whitespaces).isEmpty)
                }
            }
            .confirmationDialog("Ritual löschen?", isPresented: $confirmDelete, titleVisibility: .visible) {
                Button("Löschen", role: .destructive, action: deleteRitual)
            }
        }
    }

    private func save() {
        let model: Ritual
        if let ritual {
            model = ritual
        } else {
            model = Ritual(name: name, emoji: emoji, colorHex: colorHex, hour: 13, minute: 0,
                           sortIndex: rituals.count)
            context.insert(model)
        }
        model.name = name.trimmingCharacters(in: .whitespaces)
        model.emoji = emoji
        model.colorHex = colorHex
        model.time = time
        model.reminderEnabled = reminderEnabled
        ReminderScheduler.update(for: model)
        dismiss()
    }

    private func deleteRitual() {
        guard let ritual else { return }
        ReminderScheduler.remove(for: ritual)
        for habit in ritual.orderedHabits { habit.ritual = nil }
        dismiss()
        onDelete?()
        let context = context
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) {
            context.delete(ritual)
        }
    }
}

// MARK: - Liste aller Rituale

struct RitualsListView: View {
    @Environment(\.modelContext) private var context
    @Query private var rituals: [Ritual]
    @State private var showEditor = false

    var body: some View {
        List {
            if rituals.isEmpty {
                ContentUnavailableView("Keine Rituale", systemImage: "sunrise",
                                       description: Text("Lege ein Ritual an, z. B. für morgens oder abends."))
            }
            ForEach(rituals.sorted { $0.minutesOfDay < $1.minutesOfDay }) { ritual in
                NavigationLink(value: ritual) {
                    HStack(spacing: 12) {
                        Text(ritual.emoji)
                            .frame(width: 40, height: 40)
                            .background(ritual.color.opacity(0.2), in: Circle())
                        VStack(alignment: .leading) {
                            Text(ritual.name).font(.body.weight(.semibold))
                            Text(ritual.infoText).font(.caption).foregroundStyle(.secondary)
                        }
                    }
                }
            }
        }
        .navigationTitle("Rituale")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button { showEditor = true } label: { Image(systemName: "plus") }
            }
        }
        .sheet(isPresented: $showEditor) { RitualEditorView() }
    }
}
