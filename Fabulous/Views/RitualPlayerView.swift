import SwiftUI
import SwiftData
import Combine

/// Geführter Modus: führt Schritt für Schritt durch alle Gewohnheiten eines Rituals.
struct RitualPlayerView: View {
    @Environment(\.modelContext) private var context
    @Environment(\.dismiss) private var dismiss
    let ritual: Ritual

    @State private var queue: [Goal] = []
    @State private var index = 0
    @State private var remaining = 0
    @State private var duration = 0
    @State private var running = false
    @State private var finished = false
    @State private var completedInSession = 0
    @State private var celebrate = false

    private let ticker = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    private var current: Goal? {
        queue.indices.contains(index) ? queue[index] : nil
    }

    var body: some View {
        ZStack {
            LinearGradient(colors: [ritual.color, ritual.color.opacity(0.6), .black.opacity(0.85)],
                           startPoint: .top, endPoint: .bottom)
                .ignoresSafeArea()

            if finished {
                celebration
            } else if let habit = current {
                stepView(habit)
                    .id(habit.persistentModelID)
                    .transition(.asymmetric(insertion: .move(edge: .trailing).combined(with: .opacity),
                                            removal: .move(edge: .leading).combined(with: .opacity)))
            }
        }
        .foregroundStyle(.white)
        .onAppear(perform: setup)
        .onReceive(ticker) { _ in tick() }
        .sensoryFeedback(.success, trigger: completedInSession)
        .sensoryFeedback(.impact(weight: .heavy), trigger: remaining == 0 && duration > 0)
    }

    // MARK: Schritt

    private func stepView(_ habit: Goal) -> some View {
        VStack(spacing: 20) {
            HStack {
                Button { dismiss() } label: {
                    Image(systemName: "xmark")
                        .font(.headline)
                        .padding(10)
                        .background(.white.opacity(0.2), in: Circle())
                }
                Spacer()
                Text("\(ritual.emoji) \(ritual.name)").font(.subheadline.bold())
                Spacer()
                Color.clear.frame(width: 40, height: 40)
            }

            HStack(spacing: 4) {
                ForEach(queue.indices, id: \.self) { i in
                    Capsule()
                        .fill(.white.opacity(i < index ? 1 : (i == index ? 0.7 : 0.25)))
                        .frame(height: 4)
                }
            }

            Spacer()

            Text(habit.emoji).font(.system(size: 90))
            Text(habit.title)
                .font(.largeTitle.bold())
                .multilineTextAlignment(.center)
            if !habit.notes.isEmpty {
                Text(habit.notes)
                    .font(.body)
                    .multilineTextAlignment(.center)
                    .opacity(0.85)
            }

            if duration > 0 {
                Button { running.toggle() } label: {
                    ProgressRing(progress: Double(duration - remaining) / Double(duration),
                                 color: .white, lineWidth: 8) {
                        VStack(spacing: 4) {
                            Text(timeString(remaining))
                                .font(.system(size: 34, weight: .bold, design: .rounded))
                                .monospacedDigit()
                                .contentTransition(.numericText(countsDown: true))
                            Image(systemName: running ? "pause.fill" : "play.fill")
                                .font(.headline)
                        }
                    }
                    .frame(width: 170, height: 170)
                }
                .buttonStyle(.plain)
                .padding(.top, 10)
            }

            Spacer()

            Button { complete(habit) } label: {
                Text(remaining == 0 || duration == 0 ? "Erledigt" : "Schon erledigt")
                    .font(.headline)
                    .foregroundStyle(ritual.color)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.white, in: Capsule())
            }
            .buttonStyle(.plain)

            Button("Überspringen") { next() }
                .font(.subheadline)
                .opacity(0.8)
        }
        .padding(24)
    }

    // MARK: Abschluss

    private var celebration: some View {
        VStack(spacing: 20) {
            Spacer()
            Text("🎉")
                .font(.system(size: 110))
                .scaleEffect(celebrate ? 1 : 0.3)
                .rotationEffect(.degrees(celebrate ? 0 : -30))
            Text("\(ritual.name) geschafft!")
                .font(.largeTitle.bold())
                .multilineTextAlignment(.center)
            Text("\(ritual.completedCount(on: .now)) von \(ritual.orderedHabits.count) Gewohnheiten erledigt")
                .opacity(0.9)
            let streak = ritual.currentStreak
            if streak > 0 {
                Label("\(streak) \(streak == 1 ? "Tag" : "Tage") in Folge", systemImage: "flame.fill")
                    .font(.title3.bold())
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .background(.white.opacity(0.2), in: Capsule())
            }
            Text(Motivation.quote(for: .now))
                .font(.callout)
                .italic()
                .multilineTextAlignment(.center)
                .opacity(0.8)
                .padding(.top, 8)
            Spacer()
            Button { dismiss() } label: {
                Text("Fertig")
                    .font(.headline)
                    .foregroundStyle(ritual.color)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.white, in: Capsule())
            }
            .buttonStyle(.plain)
        }
        .padding(24)
        .onAppear {
            withAnimation(.spring(response: 0.6, dampingFraction: 0.5)) { celebrate = true }
        }
    }

    // MARK: Logik

    private func setup() {
        let open = ritual.orderedHabits.filter { !$0.isDone(onDay: .now) }
        queue = open.isEmpty ? ritual.orderedHabits : open
        index = 0
        if queue.isEmpty {
            finished = true
        } else {
            prepareCurrent()
        }
    }

    private func prepareCurrent() {
        guard let habit = current else { return }
        duration = max(0, habit.durationMinutes) * 60
        remaining = duration
        running = duration > 0
    }

    private func tick() {
        guard running, !finished, remaining > 0 else { return }
        withAnimation { remaining -= 1 }
        if remaining == 0 { running = false }
    }

    private func complete(_ habit: Goal) {
        habit.completeForDay(.now, in: context)
        completedInSession += 1
        next()
    }

    private func next() {
        withAnimation(.easeInOut) {
            if index + 1 < queue.count {
                index += 1
                prepareCurrent()
            } else {
                running = false
                finished = true
            }
        }
    }

    private func timeString(_ seconds: Int) -> String {
        String(format: "%d:%02d", seconds / 60, seconds % 60)
    }
}
