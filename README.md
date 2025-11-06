# 🎮 Advanced Chess Game with Self-Learning AI

A feature-rich chess game built with Python and Pygame, featuring multiple game modes, configurable timers, and a self-learning AI that improves with every game!

![Chess Game](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎯 Multiple Game Modes
- **Human vs Human** - Play against a friend on the same computer
- **Human vs AI** - Challenge the AI (play as White or Black)



### 🧠 Self-Learning AI
- **Temporal Difference Learning** - AI learns from every game
- **Position Evaluation** - Combines learned knowledge with chess heuristics
- **Adaptive Exploration** - Balances trying new moves vs using learned strategies
- **Persistent Memory** - Knowledge is saved between sessions
- **Learning Visualization** - Track AI's progress with detailed statistics



### ♟️ Complete Chess Rules
- All standard chess moves (including castling and en passant)
- Pawn promotion with piece selection dialog
- Check, checkmate, and stalemate detection
- Move validation ensuring legal moves only

## 📦 Installation

### Prerequisites
```bash
Python 3.7 or higher
```

### Required Libraries
```bash
pip install pygame
pip install matplotlib  # Optional, for learning visualization
```

### Quick Start
1. Clone the repository:
```bash
git clone https://github.com/yourusername/chess-game.git
cd chess-game
```

2. Create an `images` folder and add chess piece images (PNG format):
   - Naming convention: `wp.png` (white pawn), `bK.png` (black king), etc.
   - Pieces needed: wp, wN, wB, wR, wQ, wK, bp, bN, bB, bR, bQ, bK

3. Run the game:
```bash
python ChessMain_Enhanced.py
```

## 🎮 How to Play

### Starting a Game
1. Launch the game - you'll see the game mode selection menu
2. Choose your preferred game mode
3. Select time control (or no timer)
4. Start playing!

### Controls
- **Mouse Click** - Select and move pieces
- **Z Key** - Undo last move
- **ESC Key** - Return to main menu
- **R Key** - Reset game (in learning mode)

### Making Moves
1. Click on a piece to select it (must be your turn)
2. Valid moves will be highlighted with indicators
3. Click on a highlighted square to move
4. For pawn promotion, a dialog will appear to choose the piece

## 🧠 AI Learning System

### How It Works

The AI uses **Reinforcement Learning** with these key components:

1. **Position Evaluation**
   - Combines learned values with traditional chess heuristics
   - Material counting (Queen=9, Rook=5, etc.)
   - Positional bonuses (center control, piece placement)

2. **Temporal Difference Learning**
   - Learns from game outcomes (win/loss/draw)
   - Updates position values based on game results
   - Recent positions weighted more heavily

3. **Exploration vs Exploitation**
   - Starts with 40% exploration (random moves)
   - Gradually reduces to 10% as it learns
   - Balances trying new strategies vs using known good moves

4. **Monte Carlo Tree Search (MCTS)**
   - Uses learned evaluations to guide search
   - Simulates possible move sequences
   - Selects moves based on visit counts and win rates

### Training the AI

The more games the AI plays, the stronger it becomes!

**Training Tips:**
- Play multiple games to build the AI's knowledge base
- Try different openings to diversify its experience
- Check learning stats after each game


#### Detailed Analysis
Run the learning visualizer for comprehensive insights:
```bash
python LearningVisualizer.py
```

Features:
- 📊 Detailed learning analysis
- 📈 Learning curves (requires matplotlib)
- 🎯 Position confidence analysis
- 💡 Training recommendations



## 🎓 AI Learning Details

### Learning Algorithm

```python
# Temporal Difference Learning Update
TD_error = target_value - current_value
position_value += learning_rate * TD_error

# Target value calculation
if final_position:
    target = game_result  # 1.0 for win, -1.0 for loss, 0.0 for draw
else:
    target = discount_factor * next_position_value
```

### Hyperparameters

- **Learning Rate**: 0.3 (controls how quickly AI adapts)
- **Discount Factor**: 0.98 (values future rewards)
- **Initial Exploration**: 40% (starts exploring heavily)
- **Minimum Exploration**: 10% (maintains some randomness)
- **MCTS Iterations**: 100-800 (increases with experience)

### Data Persistence

The AI brain is automatically saved after each game:
- `chess_ai_brain.pkl` - Main brain file (pickle format)
- `ai_stats.json` - Human-readable statistics
- `ai_backups/` - Automatic backups every 10 games

## 📊 Statistics & Analytics

### Game Statistics
- Total games played
- Wins, losses, draws
- Win rate percentage
- Average game length

### Learning Metrics
- Positions learned (unique board states)
- Position visits (total evaluations)
- Knowledge growth rate
- Exploration rate decay

### Performance Tracking
- Win rate progression
- Position confidence levels
- Learning efficiency
- Strategic improvement

## 🔧 Customization

### Adjusting AI Difficulty

In `SelfLearningAI.py`, modify:
```python
# Make AI think longer
iterations = 100 + brain.game_count * 10  # Increase multiplier

# Adjust learning speed
self.learning_rate = 0.5  # Higher = faster learning

# Change exploration
self.exploration_rate = 0.20  # Lower = less random
```

### Changing Time Controls

In `ChessMain_Enhanced.py`, edit `TIMER_PRESETS`:
```python
TIMER_PRESETS = {
    "Your Custom Time": 120,  # 2 minutes in seconds
    # ... other presets
}
```

### Visual Customization

Modify colors in `ChessMain_Enhanced.py`:
```python
LIGHT_SQUARE = (232, 245, 221)  # Light square color
DARK_SQUARE = (140, 163, 110)   # Dark square color
HIGHLIGHT_COLOR = (186, 202, 68)  # Selected piece highlight
```

## 🐛 Troubleshooting

### Common Issues

**Images not loading:**
- Ensure `images/` folder exists
- Check image filenames match exactly (case-sensitive)
- Verify images are PNG format

**AI not learning:**
- Play complete games (don't quit early)
- Check if `chess_ai_brain.pkl` is being created
- Ensure write permissions in game directory

**Performance issues:**
- Reduce MCTS iterations for faster moves
- Disable animations for speed
- Close other heavy applications

**Multiprocessing errors:**
- Required on Windows: use `if __name__ == "__main__":`
- On some systems, may need to set multiprocessing start method

## 🚀 Future Enhancements

Potential features to add:
- [ ] Online multiplayer
- [ ] Opening book database
- [ ] Endgame tablebase
- [ ] Neural network evaluation
- [ ] Game analysis mode
- [ ] Puzzle trainer
- [ ] ELO rating system
- [ ] Game recording/replay
- [ ] Tournament mode

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Chess piece images from [source]
- Inspired by chess.com and lichess.org
- Built with Python and Pygame

## 👤 Author

Your Name
-Vishal
- Email: vishalkrishnakkr@gmail.com

## ⭐ Show Your Support

Give a ⭐️ if this project helped you learn or have fun!

## 📮 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to check [issues page](https://github.com/yourusername/chess-game/issues).

---

**Happy Chess Playing! ♟️🎮🧠**
