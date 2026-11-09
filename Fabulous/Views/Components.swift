import SwiftUI

struct ProgressRing<Content: View>: View {
    var progress: Double
    var color: Color
    var lineWidth: CGFloat = 6
    let content: Content

    init(progress: Double, color: Color, lineWidth: CGFloat = 6, @ViewBuilder content: () -> Content) {
        self.progress = progress
        self.color = color
        self.lineWidth = lineWidth
        self.content = content()
    }

    var body: some View {
        ZStack {
            Circle()
                .stroke(color.opacity(0.2), lineWidth: lineWidth)
            Circle()
                .trim(from: 0, to: max(0, min(progress, 1)))
                .stroke(color, style: StrokeStyle(lineWidth: lineWidth, lineCap: .round))
                .rotationEffect(.degrees(-90))
            content
        }
        .animation(.spring(duration: 0.4), value: progress)
    }
}

extension ProgressRing where Content == EmptyView {
    init(progress: Double, color: Color, lineWidth: CGFloat = 6) {
        self.init(progress: progress, color: color, lineWidth: lineWidth) { EmptyView() }
    }
}

struct StatTile: View {
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(systemName: icon)
                .font(.headline)
                .foregroundStyle(color)
            Text(value)
                .font(.title2.bold())
                .contentTransition(.numericText())
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

struct EmojiBadge: View {
    let goal: Goal
    var size: CGFloat = 44

    var body: some View {
        Text(goal.emoji)
            .font(.system(size: size * 0.5))
            .frame(width: size, height: size)
            .background(goal.color.opacity(0.18), in: Circle())
    }
}

struct Card<Content: View>: View {
    let title: String?
    let content: Content

    init(_ title: String? = nil, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            if let title {
                Text(title).font(.headline)
            }
            content
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}
