import SwiftUI
import SwiftData

struct OnboardingView: View {
    @Environment(\.modelContext) private var context
    @AppStorage("userName") private var userName = ""
    @AppStorage("onboardingDone") private var onboardingDone = false

    @State private var page = 0
    @State private var name = ""
    @State private var journeyID = Journey.all[0].id
    @State private var wakeTime = Calendar.current.date(bySettingHour: 7, minute: 0, second: 0, of: .now) ?? .now

    private let pageCount = 4

    var body: some View {
        ZStack {
            LinearGradient(colors: [Color(hex: "#FF9F43"), Color(hex: "#FF6B6B"), Color(hex: "#5F27CD")],
                           startPoint: .topLeading, endPoint: .bottomTrailing)
                .ignoresSafeArea()

            VStack {
                TabView(selection: $page) {
                    welcome.tag(0)
                    namePage.tag(1)
                    journeyPage.tag(2)
                    wakePage.tag(3)
                }
                .tabViewStyle(.page(indexDisplayMode: .always))

                Button {
                    if page < pageCount - 1 {
                        withAnimation { page += 1 }
                    } else {
                        finish()
                    }
                } label: {
                    Text(page < pageCount - 1 ? "Weiter" : "Los geht's")
                        .font(.headline)
                        .foregroundStyle(Color(hex: "#5F27CD"))
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(.white, in: Capsule())
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 24)
            }
        }
        .foregroundStyle(.white)
    }

    private var welcome: some View {
        VStack(spacing: 20) {
            Spacer()
            Text("✨").font(.system(size: 90))
            Text("Willkommen bei\nFabulous")
                .font(.largeTitle.bold())
                .multilineTextAlignment(.center)
            Text("Baue dir Schritt für Schritt Gewohnheiten auf, die dich gesünder, glücklicher und fokussierter machen.")
                .multilineTextAlignment(.center)
                .opacity(0.9)
            Spacer()
            Spacer()
        }
        .padding(32)
    }

    private var namePage: some View {
        VStack(spacing: 20) {
            Spacer()
            Text("👋").font(.system(size: 70))
            Text("Wie heißt du?").font(.title.bold())
            TextField("", text: $name, prompt: Text("Dein Vorname").foregroundStyle(.white.opacity(0.6)))
                .font(.title2)
                .multilineTextAlignment(.center)
                .padding()
                .background(.white.opacity(0.2), in: RoundedRectangle(cornerRadius: 16))
                .textInputAutocapitalization(.words)
            Spacer()
            Spacer()
        }
        .padding(32)
    }

    private var journeyPage: some View {
        VStack(spacing: 16) {
            Spacer()
            Text("Was möchtest du verändern?")
                .font(.title.bold())
                .multilineTextAlignment(.center)
            Text("Wähle deine erste Reise. Du kannst später jederzeit wechseln.")
                .multilineTextAlignment(.center)
                .opacity(0.9)
            ForEach(Journey.all) { journey in
                Button { journeyID = journey.id } label: {
                    HStack(spacing: 14) {
                        Text(journey.emoji).font(.title)
                        VStack(alignment: .leading) {
                            Text(journey.title).font(.headline)
                            Text(journey.subtitle).font(.caption).opacity(0.85)
                        }
                        Spacer()
                        Image(systemName: journeyID == journey.id ? "checkmark.circle.fill" : "circle")
                            .font(.title2)
                    }
                    .padding()
                    .background(.white.opacity(journeyID == journey.id ? 0.3 : 0.12),
                                in: RoundedRectangle(cornerRadius: 16))
                }
                .buttonStyle(.plain)
            }
            Spacer()
        }
        .padding(24)
    }

    private var wakePage: some View {
        VStack(spacing: 20) {
            Spacer()
            Text("⏰").font(.system(size: 70))
            Text("Wann stehst du auf?").font(.title.bold())
            Text("Dann erinnern wir dich an dein Morgenritual.")
                .multilineTextAlignment(.center)
                .opacity(0.9)
            DatePicker("", selection: $wakeTime, displayedComponents: .hourAndMinute)
                .datePickerStyle(.wheel)
                .labelsHidden()
                .colorScheme(.dark)
            Spacer()
            Spacer()
        }
        .padding(32)
    }

    private func finish() {
        userName = name.trimmingCharacters(in: .whitespaces)
        let cal = Calendar.current
        let hour = cal.component(.hour, from: wakeTime)
        let minute = cal.component(.minute, from: wakeTime)
        OnboardingSetup.createDefaults(wakeHour: hour, wakeMinute: minute, journeyID: journeyID, in: context)
        withAnimation { onboardingDone = true }
    }
}

enum OnboardingSetup {
    static func createDefaults(wakeHour: Int, wakeMinute: Int, journeyID: String, in context: ModelContext) {
        let rituals = (try? context.fetch(FetchDescriptor<Ritual>())) ?? []
        if rituals.isEmpty {
            let morning = RitualSlot.morning.makeRitual(hour: wakeHour, minute: wakeMinute, sortIndex: 0)
            let evening = RitualSlot.evening.makeRitual(sortIndex: 1)
            context.insert(morning)
            context.insert(evening)

            let water = Goal(title: "Ein Glas Wasser trinken", emoji: "💧", colorHex: "#48DBFB",
                             kind: .check, frequency: .daily, target: 1, sortIndex: 0)
            water.durationMinutes = 1
            water.notes = "Stell dir das Glas schon am Abend bereit."
            context.insert(water)
            morning.add(water)

            let reflect = Goal(title: "Tag reflektieren", emoji: "✍️", colorHex: "#576574",
                               kind: .check, frequency: .daily, target: 1, sortIndex: 1)
            reflect.durationMinutes = 5
            reflect.notes = "Was lief heute gut? Drei Sätze reichen."
            context.insert(reflect)
            evening.add(reflect)

            ReminderScheduler.update(for: morning)
            ReminderScheduler.update(for: evening)
        }

        if let journey = Journey.find(journeyID) {
            JourneyEngine.start(journey, in: context)
        }
    }
}
