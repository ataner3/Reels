import SwiftUI
import SwiftData

struct GoalEditorView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss
    @Query(sort: \Goal.sortIndex) private var allGoals: [Goal]
    @Query private var rituals: [Ritual]

    let goal: Goal?

    @State private var title: String
    @State private var emoji: String
    @State private var colorHex: String
    @State private var kind: GoalKind
    @State private var frequency: GoalFrequency
    @State private var target: Double
    @State private var unit: String
    @State private var step: Double
    @State private var reminderEnabled: Bool
    @State private var reminderTime: Date
    @State private var notes: String
    @State private var selectedRitual: Ritual?
    @State private var durationMinutes: Int

    init(goal: Goal? = nil, ritual: Ritual? = nil) {
        self.goal = goal
        _selectedRitual = State(initialValue: goal?.ritual ?? ritual)
        _durationMinutes = State(initialValue: goal?.durationMinutes ?? 2)
        _title = State(initialValue: goal?.title ?? "")
        _emoji = State(initialValue: goal?.emoji ?? "⭐️")
        _colorHex = State(initialValue: goal?.colorHex ?? Palette.colors[0])
        _kind = State(initialValue: goal?.kind ?? .check)
        _frequency = State(initialValue: goal?.frequency ?? .daily)
        _target = State(initialValue: goal?.target ?? 1)
        _unit = State(initialValue: goal?.unit ?? "")
        _step = State(initialValue: goal?.step ?? 1)
        _reminderEnabled = State(initialValue: goal?.reminderEnabled ?? false)
        _reminderTime = State(initialValue: goal?.reminderTime
            ?? Calendar.current.date(bySettingHour: 8, minute: 0, second: 0, of: .now) ?? .now)
        _notes = State(initialValue: goal?.notes ?? "")
    }

    private var isValid: Bool {
        !title.trimmingCharacters(in: .whitespaces).isEmpty && target > 0 && step > 0
    }

    var body: some View {
        NavigationStack {
            Form {
                if goal == nil {
                    Section("Vorlagen") {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 10) {
                                ForEach(GoalTemplate.all) { template in
                                    Button { apply(template) } label: {
                                        VStack(spacing: 4) {
                                            Text(template.emoji).font(.title2)
                                            Text(template.title).font(.caption2).lineLimit(1)
                                        }
                                        .frame(width: 76, height: 64)
                                        .background(Color(hex: template.colorHex).opacity(0.18),
                                                    in: RoundedRectangle(cornerRadius: 12))
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }

                Section("Ziel") {
                    HStack {
                        Text(emoji)
                            .font(.title)
                            .frame(width: 48, height: 48)
                            .background(Color(hex: colorHex).opacity(0.2), in: Circle())
                        TextField("Name, z. B. Wasser trinken", text: $title)
                            .font(.headline)
                    }

                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 6) {
                            ForEach(Palette.emojis, id: \.self) { e in
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
                                    .overlay(
                                        Circle().stroke(Color.primary, lineWidth: hex == colorHex ? 2.5 : 0)
                                            .padding(-4)
                                    )
                                    .padding(4)
                                    .onTapGesture { colorHex = hex }
                            }
                        }
                    }
                }

                Section {
                    Picker("Art", selection: $kind) {
                        ForEach(GoalKind.allCases) { Text($0.label).tag($0) }
                    }
                    .pickerStyle(.segmented)

                    Picker("Rhythmus", selection: $frequency) {
                        ForEach(GoalFrequency.allCases) { Text($0.label).tag($0) }
                    }
                    .pickerStyle(.segmented)

                    switch (kind, frequency) {
                    case (.check, .daily):
                        EmptyView()
                    case (.check, .weekly):
                        Stepper("\(Int(target))× pro Woche", value: $target, in: 1...7, step: 1)
                    case (.count, _):
                        HStack {
                            Text("Ziel")
                            Spacer()
                            TextField("8", value: $target, format: .number)
                                .keyboardType(.decimalPad)
                                .multilineTextAlignment(.trailing)
                                .frame(width: 90)
                            TextField("Einheit", text: $unit)
                                .frame(width: 100)
                        }
                        HStack {
                            Text("Pro Tipp auf +")
                            Spacer()
                            TextField("1", value: $step, format: .number)
                                .keyboardType(.decimalPad)
                                .multilineTextAlignment(.trailing)
                                .frame(width: 90)
                            Text(unit).foregroundStyle(.secondary)
                        }
                    }
                } header: {
                    Text("Tracking")
                } footer: {
                    Text(kind == .check
                         ? "Hake das Ziel ab, sobald du es erledigt hast."
                         : "Zähle Mengen wie Gläser, Seiten, Minuten oder Euro.")
                }

                Section {
                    Picker("Ritual", selection: $selectedRitual) {
                        Text("Keins (eigenständig)").tag(Ritual?.none)
                        ForEach(rituals.sorted { $0.minutesOfDay < $1.minutesOfDay }) { ritual in
                            Text("\(ritual.emoji) \(ritual.name)").tag(Ritual?.some(ritual))
                        }
                    }
                    if selectedRitual != nil {
                        Stepper(durationMinutes == 0 ? "Dauer: ohne Timer" : "Dauer: \(durationMinutes) Min.",
                                value: $durationMinutes, in: 0...120)
                    }
                } header: {
                    Text("Ritual")
                } footer: {
                    Text("Gewohnheiten in einem Ritual erscheinen im geführten Ritual-Modus – mit Timer, wenn du eine Dauer angibst.")
                }

                Section("Erinnerung") {
                    Toggle("Eigene tägliche Erinnerung", isOn: $reminderEnabled.animation())
                    if reminderEnabled {
                        DatePicker("Uhrzeit", selection: $reminderTime, displayedComponents: .hourAndMinute)
                    }
                }

                Section("Tipp / Motivation") {
                    TextField("z. B. Warum ist dir das wichtig?", text: $notes, axis: .vertical)
                        .lineLimit(2...6)
                }
            }
            .navigationTitle(goal == nil ? (selectedRitual == nil ? "Neues Ziel" : "Neue Gewohnheit") : "Bearbeiten")
            .navigationBarTitleDisplayMode(.inline)
            .onChange(of: kind) { normalizeTarget() }
            .onChange(of: frequency) { normalizeTarget() }
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Abbrechen") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Sichern") { save() }
                        .disabled(!isValid)
                }
            }
        }
    }

    private func normalizeTarget() {
        switch (kind, frequency) {
        case (.check, .daily): target = 1
        case (.check, .weekly): target = min(max(target.rounded(), 1), 7)
        case (.count, _): if target <= 0 { target = 1 }
        }
    }

    private func apply(_ template: GoalTemplate) {
        title = template.title
        emoji = template.emoji
        colorHex = template.colorHex
        kind = template.kind
        frequency = template.frequency
        unit = template.unit
        step = template.step
        target = template.target
    }

    private func save() {
        let trimmed = title.trimmingCharacters(in: .whitespaces)
        let finalTarget = (kind == .check && frequency == .daily) ? 1 : target

        let model: Goal
        if let goal {
            model = goal
        } else {
            let nextIndex = (allGoals.map(\.sortIndex).max() ?? -1) + 1
            model = Goal(title: trimmed, emoji: emoji, colorHex: colorHex, kind: kind,
                         frequency: frequency, target: finalTarget, sortIndex: nextIndex)
            context.insert(model)
        }

        model.title = trimmed
        model.emoji = emoji
        model.colorHex = colorHex
        model.kind = kind
        model.frequency = frequency
        model.target = finalTarget
        model.unit = kind == .count ? unit.trimmingCharacters(in: .whitespaces) : ""
        model.step = kind == .count ? step : 1
        model.reminderEnabled = reminderEnabled
        model.reminderTime = reminderTime
        model.notes = notes
        model.durationMinutes = selectedRitual == nil ? 0 : durationMinutes
        if model.ritual?.persistentModelID != selectedRitual?.persistentModelID {
            let oldRitual = model.ritual
            if let selectedRitual {
                selectedRitual.add(model)
                ReminderScheduler.update(for: selectedRitual)
            } else {
                model.ritual = nil
            }
            if let oldRitual { ReminderScheduler.update(for: oldRitual) }
        }

        ReminderScheduler.update(for: model)
        dismiss()
    }
}
