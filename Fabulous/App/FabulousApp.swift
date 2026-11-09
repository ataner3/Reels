import SwiftUI
import SwiftData

@main
struct FabulousApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Goal.self, Entry.self])
    }
}

struct ContentView: View {
    var body: some View {
        TabView {
            TodayView()
                .tabItem { Label("Heute", systemImage: "sun.max.fill") }
            GoalsListView()
                .tabItem { Label("Ziele", systemImage: "target") }
            StatsView()
                .tabItem { Label("Statistik", systemImage: "chart.bar.fill") }
        }
    }
}
