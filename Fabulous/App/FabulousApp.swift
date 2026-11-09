import SwiftUI
import SwiftData

@main
struct FabulousApp: App {
    var body: some Scene {
        WindowGroup {
            RootView()
        }
        .modelContainer(for: [Goal.self, Entry.self, Ritual.self, JourneyProgress.self])
    }
}

struct RootView: View {
    @AppStorage("onboardingDone") private var onboardingDone = false

    var body: some View {
        if onboardingDone {
            ContentView()
        } else {
            OnboardingView()
        }
    }
}

struct ContentView: View {
    var body: some View {
        TabView {
            TodayView()
                .tabItem { Label("Heute", systemImage: "sun.max.fill") }
            JourneysView()
                .tabItem { Label("Reisen", systemImage: "map.fill") }
            StatsView()
                .tabItem { Label("Fortschritt", systemImage: "chart.bar.fill") }
            ProfileView()
                .tabItem { Label("Ich", systemImage: "person.crop.circle.fill") }
        }
    }
}
