"""
Learning Visualizer - Track and visualize AI's learning progress
Run this to see detailed statistics and learning curves
"""
import pickle
import os
import matplotlib.pyplot as plt
from collections import defaultdict

LEARNING_DATA_FILE = "chess_ai_brain.pkl"


def load_ai_brain():
    """Load AI brain data"""
    if not os.path.exists(LEARNING_DATA_FILE):
        print("❌ No AI brain file found! Play some games first.")
        return None

    try:
        with open(LEARNING_DATA_FILE, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"❌ Error loading brain: {e}")
        return None


def analyze_learning():
    """Detailed analysis of AI's learning"""
    data = load_ai_brain()
    if not data:
        return

    print("\n" + "=" * 60)
    print("🧠 AI BRAIN ANALYSIS")
    print("=" * 60)

    # Basic stats
    games = data.get('game_count', 0)
    wins = data.get('win_count', 0)
    losses = data.get('loss_count', 0)
    draws = data.get('draw_count', 0)
    positions = len(data.get('position_values', {}))
    exploration = data.get('exploration_rate', 0)

    print(f"\n📊 Overall Statistics:")
    print(f"   Total Games Played: {games}")
    print(f"   Record: {wins}W - {losses}L - {draws}D")

    if games > 0:
        win_rate = wins / games * 100
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Average Game Result: {(wins - losses) / games:.2f}")

    print(f"\n🧮 Learning Progress:")
    print(f"   Positions Learned: {positions:,}")
    print(f"   Current Exploration Rate: {exploration:.1%}")
    print(f"   Knowledge Growth Rate: {positions / games if games > 0 else 0:.1f} positions/game")

    # Position value analysis
    position_values = data.get('position_values', {})
    if position_values:
        values = list(position_values.values())
        print(f"\n📈 Position Evaluation Stats:")
        print(f"   Average Position Value: {sum(values) / len(values):.3f}")
        print(f"   Max Confidence: {max(values):.3f}")
        print(f"   Min Confidence: {min(values):.3f}")
        print(f"   Value Spread: {max(values) - min(values):.3f}")

    # Learning milestones
    print(f"\n🎯 Milestones Achieved:")
    milestones = [
        (10, "🥉 Novice"),
        (25, "🥈 Intermediate"),
        (50, "🥇 Advanced"),
        (100, "💎 Expert"),
        (250, "🏆 Master"),
        (500, "👑 Grandmaster")
    ]

    for threshold, title in milestones:
        if games >= threshold:
            print(f"   ✓ {title} ({threshold}+ games)")
        else:
            print(f"   ○ {title} (needs {threshold - games} more games)")
            break

    # Improvement trend
    if games >= 10:
        print(f"\n📉 Learning Trends:")
        recent_games = min(10, games)
        print(f"   Exploration decreased: {30 - exploration * 100:.1f}% (good!)")
        print(f"   Knowledge increased: {positions} positions learned")

        if games >= 20:
            learning_efficiency = positions / games
            print(f"   Learning Efficiency: {learning_efficiency:.1f} positions/game")

            if learning_efficiency > 100:
                print(f"   🚀 Excellent learning rate!")
            elif learning_efficiency > 50:
                print(f"   ✓ Good learning progress")
            else:
                print(f"   ⚠️  Play more diverse games to improve learning")

    print("\n" + "=" * 60)


def plot_learning_curves():
    """Create visualizations of learning progress"""
    data = load_ai_brain()
    if not data:
        return

    games = data.get('game_count', 0)
    if games < 5:
        print("⚠️  Need at least 5 games to create meaningful plots.")
        return

    # Simulate learning curve (since we don't store per-game history)
    # In a full implementation, you'd track this per game
    game_numbers = list(range(1, games + 1))

    # Estimate win rate progression (simplified)
    wins = data.get('win_count', 0)
    losses = data.get('loss_count', 0)
    draws = data.get('draw_count', 0)

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('🧠 AI Learning Evolution', fontsize=16, fontweight='bold')

    # Plot 1: Win Rate Progression (estimated)
    ax1 = axes[0, 0]
    # Simulate progressive improvement
    win_rate_curve = [min(100, i * (wins / games * 100) / games) for i in game_numbers]
    ax1.plot(game_numbers, win_rate_curve, 'b-', linewidth=2, label='Win Rate')
    ax1.axhline(y=50, color='r', linestyle='--', alpha=0.5, label='50% Target')
    ax1.set_xlabel('Game Number')
    ax1.set_ylabel('Win Rate (%)')
    ax1.set_title('Win Rate Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Knowledge Growth
    ax2 = axes[0, 1]
    positions = len(data.get('position_values', {}))
    knowledge_curve = [int(i * positions / games) for i in game_numbers]
    ax2.plot(game_numbers, knowledge_curve, 'g-', linewidth=2)
    ax2.set_xlabel('Game Number')
    ax2.set_ylabel('Positions Learned')
    ax2.set_title('Knowledge Accumulation')
    ax2.grid(True, alpha=0.3)

    # Plot 3: Exploration Rate Decay
    ax3 = axes[1, 0]
    exploration_rate = data.get('exploration_rate', 0.3)
    # Simulate decay from 30% to current
    initial_exploration = 0.3
    decay_curve = [max(0.05, initial_exploration * (0.995 ** i)) for i in game_numbers]
    ax3.plot(game_numbers, [e * 100 for e in decay_curve], 'orange', linewidth=2)
    ax3.set_xlabel('Game Number')
    ax3.set_ylabel('Exploration Rate (%)')
    ax3.set_title('Exploration vs Exploitation')
    ax3.grid(True, alpha=0.3)

    # Plot 4: Game Outcomes Distribution
    ax4 = axes[1, 1]
    outcomes = [wins, losses, draws]
    labels = [f'Wins\n({wins})', f'Losses\n({losses})', f'Draws\n({draws})']
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']
    ax4.pie(outcomes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax4.set_title('Game Outcomes Distribution')

    plt.tight_layout()
    plt.savefig('ai_learning_curves.png', dpi=300, bbox_inches='tight')
    print("\n✓ Learning curves saved as 'ai_learning_curves.png'")
    plt.show()


def compare_position_values():
    """Analyze most confident positions"""
    data = load_ai_brain()
    if not data:
        return

    position_values = data.get('position_values', {})
    if len(position_values) < 10:
        print("⚠️  Not enough positions learned yet for detailed analysis.")
        return

    print("\n" + "=" * 60)
    print("🎯 POSITION CONFIDENCE ANALYSIS")
    print("=" * 60)

    # Sort positions by confidence
    sorted_positions = sorted(position_values.items(), key=lambda x: abs(x[1]), reverse=True)

    print("\n🏆 Most Confident Positions (AI is sure about these):")
    for i, (pos_hash, value) in enumerate(sorted_positions[:10], 1):
        confidence = abs(value)
        evaluation = "Winning" if value > 0 else "Losing"
        print(f"   {i}. Position #{pos_hash % 10000}: {evaluation} (confidence: {confidence:.3f})")

    print("\n❓ Least Confident Positions (AI is uncertain):")
    sorted_uncertain = sorted(position_values.items(), key=lambda x: abs(x[1]))
    for i, (pos_hash, value) in enumerate(sorted_uncertain[:10], 1):
        print(f"   {i}. Position #{pos_hash % 10000}: Uncertain (value: {value:.3f})")

    print("\n" + "=" * 60)


def recommend_training():
    """Provide training recommendations"""
    data = load_ai_brain()
    if not data:
        return

    games = data.get('game_count', 0)
    wins = data.get('win_count', 0)
    losses = data.get('loss_count', 0)
    exploration = data.get('exploration_rate', 0.3)
    positions = len(data.get('position_values', {}))

    print("\n" + "=" * 60)
    print("💡 TRAINING RECOMMENDATIONS")
    print("=" * 60 + "\n")

    if games < 10:
        print("🎯 Early Learning Phase:")
        print("   • Play 10-20 more games to build initial knowledge")
        print("   • Try different opening moves")
        print("   • Focus on completing games (no rage quits!)")
        print("   • AI is still exploring randomly - be patient!")

    elif games < 50:
        print("🎯 Development Phase:")
        print("   • AI is recognizing patterns now")
        print("   • Play 30-50 more games for solid improvement")
        print("   • Mix up your strategies to challenge the AI")
        print("   • Expected win rate: 30-50%")

    elif games < 100:
        print("🎯 Advanced Training Phase:")
        print("   • AI has developed strategic understanding")
        print("   • Play 50 more games to refine tactics")
        print("   • Try endgame positions specifically")
        print("   • Expected win rate: 40-60%")

    else:
        print("🎯 Expert Level:")
        print("   • AI is now a formidable opponent!")
        print("   • Continue playing to maintain sharpness")
        print("   • Consider increasing AI depth for stronger play")
        print("   • Expected win rate: 50-70%")

    # Specific recommendations
    print("\n📋 Specific Suggestions:")

    if exploration > 0.15:
        print(f"   • High exploration ({exploration:.0%}) - AI still learning basics")
        print("     → Play 20+ more games to reduce randomness")

    if positions < games * 50:
        print(f"   • Low knowledge diversity ({positions} positions)")
        print("     → Try new openings and mid-game positions")

    win_rate = wins / games if games > 0 else 0
    if win_rate > 0.7 and games > 20:
        print("   • You're dominating! AI needs more challenges")
        print("     → Consider increasing AI strength in settings")
    elif win_rate < 0.3 and games > 20:
        print("   • AI is getting strong! Keep practicing")
        print("     → Focus on tactical patterns and endgames")

    print("\n" + "=" * 60)


def main():
    """Main visualization program"""
    print("\n" + "🧠" * 30)
    print("     CHESS AI LEARNING ANALYZER")
    print("🧠" * 30 + "\n")

    # Check if brain exists
    if not os.path.exists(LEARNING_DATA_FILE):
        print("❌ No AI brain found!")
        print("   Play some games first using ChessMain_Learning.py")
        return

    # Menu
    while True:
        print("\nWhat would you like to see?")
        print("1. 📊 Detailed Learning Analysis")
        print("2. 📈 Learning Curves (graphs)")
        print("3. 🎯 Position Confidence Analysis")
        print("4. 💡 Training Recommendations")
        print("5. 🔄 Full Report (everything)")
        print("0. ❌ Exit")

        choice = input("\nEnter choice (0-5): ").strip()

        if choice == '1':
            analyze_learning()
        elif choice == '2':
            try:
                plot_learning_curves()
            except ImportError:
                print("⚠️  Matplotlib not installed. Run: pip install matplotlib")
        elif choice == '3':
            compare_position_values()
        elif choice == '4':
            recommend_training()
        elif choice == '5':
            analyze_learning()
            compare_position_values()
            recommend_training()
            try:
                plot_learning_curves()
            except ImportError:
                print("\n⚠️  Matplotlib not installed for graphs.")
        elif choice == '0':
            print("\n👋 Good luck training your AI!")
            break
        else:
            print("❌ Invalid choice!")


if __name__ == "__main__":
    main()