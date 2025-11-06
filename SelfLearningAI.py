"""
FIXED: Self-Learning Chess AI with Proper Multiprocessing Support
Positions are tracked in main process, learning happens after game ends
"""
import random
import math
import pickle
import os
import json
from copy import deepcopy
from datetime import datetime
import ChessEngine

# === CONFIGURATION ===
LEARNING_DATA_FILE = "chess_ai_brain.pkl"
STATS_JSON_FILE = "ai_stats.json"
BACKUP_DIR = "ai_backups"

os.makedirs(BACKUP_DIR, exist_ok=True)


class ChessAIBrain:
    """AI Brain - Learns from complete games"""
    def __init__(self):
        # Core learning data
        self.position_values = {}  # position_hash -> learned value
        self.position_visits = {}  # position_hash -> visit count

        # Game statistics
        self.game_count = 0
        self.win_count = 0
        self.loss_count = 0
        self.draw_count = 0

        # Learning hyperparameters
        self.learning_rate = 0.3  # Increased for faster learning
        self.discount_factor = 0.98  # Increased to value future rewards more
        self.exploration_rate = 0.40  # More exploration early on
        self.min_exploration_rate = 0.10  # Higher minimum exploration

        # Load existing knowledge
        self.load_brain()

        print(f"\n{'='*70}")
        print(f"🧠 AI BRAIN INITIALIZED")
        print(f"   Games played: {self.game_count}")
        print(f"   Positions known: {len(self.position_values):,}")
        print(f"   Win rate: {self.get_win_rate():.1f}%")
        print(f"{'='*70}\n")

    def evaluate_position(self, game_state):
        """Evaluate a chess position"""
        pos_hash = self.get_position_hash(game_state)

        # Get learned value
        learned_value = self.position_values.get(pos_hash, 0)
        visits = self.position_visits.get(pos_hash, 0)

        # Calculate heuristic (material + position)
        heuristic = self.calculate_heuristic(game_state)

        # Combine: trust learned value more as it gets visited more
        trust_factor = min(0.7, visits / 30.0)
        final_eval = trust_factor * learned_value + (1 - trust_factor) * heuristic

        return final_eval

    def calculate_heuristic(self, game_state):
        """Traditional chess evaluation"""
        piece_values = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
        score = 0

        for r in range(8):
            for c in range(8):
                piece = game_state.board[r][c]
                if piece != "--":
                    value = piece_values[piece[1]]

                    # Center control bonus
                    if 2 <= r <= 5 and 2 <= c <= 5:
                        center_bonus = 0.15
                    else:
                        center_bonus = 0

                    if piece[0] == "w":
                        score += value + center_bonus
                    else:
                        score -= value + center_bonus

        return score

    def get_position_hash(self, game_state):
        """Create hash of board position"""
        board_str = ""
        for row in game_state.board:
            for piece in row:
                board_str += piece
        board_str += "W" if game_state.whiteToMove else "B"
        return hash(board_str)

    def learn_from_game(self, position_hashes, result):
        """
        MAIN LEARNING FUNCTION
        position_hashes: list of position hashes from the game
        result: 1.0 (win), 0.0 (draw), -1.0 (loss) from AI perspective
        """
        if not position_hashes:
            print("⚠️  Warning: No positions to learn from!")
            return

        n_positions = len(position_hashes)
        new_positions = 0

        print(f"\n{'='*70}")
        print(f"🎓 LEARNING SESSION - Game #{self.game_count + 1}")
        print(f"{'='*70}")
        print(f"📍 Positions in game: {n_positions}")
        print(f"🎯 Result: {'WIN ✅' if result > 0 else 'LOSS ❌' if result < 0 else 'DRAW ⚖️'}")

        # TD-Learning: Work backwards from final position
        for i in range(n_positions - 1, -1, -1):
            pos_hash = position_hashes[i]

            # Initialize if new position
            if pos_hash not in self.position_values:
                self.position_values[pos_hash] = 0.0
                self.position_visits[pos_hash] = 0
                new_positions += 1

            self.position_visits[pos_hash] += 1

            # Current estimated value
            current_value = self.position_values[pos_hash]

            # Calculate target value
            if i == n_positions - 1:
                # Final position: use actual game result
                target_value = result
            else:
                # Non-final: bootstrap from next position
                next_hash = position_hashes[i + 1]
                next_value = self.position_values.get(next_hash, 0.0)
                target_value = self.discount_factor * next_value

            # Temporal Difference error
            td_error = target_value - current_value

            # Weight recent positions more (exponential decay)
            recency_weight = 0.95 ** (n_positions - i - 1)

            # Update value
            self.position_values[pos_hash] += (
                self.learning_rate * recency_weight * td_error
            )

        # Update game stats
        self.game_count += 1
        if result > 0:
            self.win_count += 1
        elif result < 0:
            self.loss_count += 1
        else:
            self.draw_count += 1

        # Decay exploration rate (explore less as we learn more)
        self.exploration_rate = max(
            self.min_exploration_rate,
            self.exploration_rate * 0.995
        )

        # Print learning summary
        print(f"✨ New positions: {new_positions}")
        print(f"🧠 Total knowledge: {len(self.position_values):,} positions")
        print(f"🔍 Exploration rate: {self.exploration_rate:.1%}")

        # Save brain to disk
        self.save_brain()

        # Print overall statistics
        print(f"\n{'📊 OVERALL STATISTICS':^70}")
        print(f"{'='*70}")
        print(f"  Games: {self.game_count} | Record: {self.win_count}W-{self.loss_count}L-{self.draw_count}D")
        print(f"  Win Rate: {self.get_win_rate():.1f}%")
        print(f"  Knowledge: {len(self.position_values):,} positions")
        print(f"  Total Visits: {sum(self.position_visits.values()):,}")
        print(f"{'='*70}\n")

    def save_brain(self):
        """Save brain to disk"""
        try:
            data = {
                'position_values': self.position_values,
                'position_visits': self.position_visits,
                'game_count': self.game_count,
                'win_count': self.win_count,
                'loss_count': self.loss_count,
                'draw_count': self.draw_count,
                'exploration_rate': self.exploration_rate,
                'last_save': datetime.now().isoformat()
            }

            # Save pickle
            with open(LEARNING_DATA_FILE, 'wb') as f:
                pickle.dump(data, f)

            file_size = os.path.getsize(LEARNING_DATA_FILE)
            print(f"💾 Brain saved! ({file_size:,} bytes)")

            # Save JSON stats
            stats = {
                'games': self.game_count,
                'wins': self.win_count,
                'losses': self.loss_count,
                'draws': self.draw_count,
                'win_rate': self.get_win_rate(),
                'positions_learned': len(self.position_values),
                'exploration_rate': self.exploration_rate,
                'last_updated': datetime.now().isoformat()
            }

            with open(STATS_JSON_FILE, 'w') as f:
                json.dump(stats, f, indent=2)

            # Periodic backup
            if self.game_count % 10 == 0:
                backup_file = os.path.join(
                    BACKUP_DIR,
                    f"brain_game{self.game_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
                )
                with open(backup_file, 'wb') as f:
                    pickle.dump(data, f)
                print(f"📦 Backup created: {backup_file}")

        except Exception as e:
            print(f"❌ ERROR saving brain: {e}")

    def load_brain(self):
        """Load brain from disk"""
        if os.path.exists(LEARNING_DATA_FILE):
            try:
                with open(LEARNING_DATA_FILE, 'rb') as f:
                    data = pickle.load(f)

                self.position_values = data.get('position_values', {})
                self.position_visits = data.get('position_visits', {})
                self.game_count = data.get('game_count', 0)
                self.win_count = data.get('win_count', 0)
                self.loss_count = data.get('loss_count', 0)
                self.draw_count = data.get('draw_count', 0)
                self.exploration_rate = data.get('exploration_rate', 0.3)

                print(f"✅ Loaded existing brain:")
                print(f"   Previous games: {self.game_count}")
                print(f"   Knowledge: {len(self.position_values):,} positions")

            except Exception as e:
                print(f"⚠️  Error loading brain: {e}")
                print("   Starting fresh...")
        else:
            print("🆕 No existing brain found - starting fresh!")

    def get_win_rate(self):
        """Calculate win percentage"""
        total = self.win_count + self.loss_count + self.draw_count
        return (self.win_count / total * 100) if total > 0 else 0.0

    def get_stats(self):
        """Get statistics dictionary"""
        return {
            'games': self.game_count,
            'wins': self.win_count,
            'losses': self.loss_count,
            'draws': self.draw_count,
            'win_rate': self.get_win_rate(),
            'positions_learned': len(self.position_values),
            'positions_visited': sum(self.position_visits.values()),
            'exploration_rate': self.exploration_rate * 100
        }


# === GLOBAL BRAIN (loaded once) ===
_global_brain = None

def get_brain():
    """Get or create global brain instance"""
    global _global_brain
    if _global_brain is None:
        _global_brain = ChessAIBrain()
    return _global_brain


# === POSITION TRACKER (in main process) ===
_position_history = []

def record_position(game_state):
    """Record a position (called from main process before AI move)"""
    brain = get_brain()
    pos_hash = brain.get_position_hash(game_state)
    _position_history.append(pos_hash)


def clear_position_history():
    """Clear position history for new game"""
    global _position_history
    _position_history = []


def get_position_history():
    """Get recorded positions"""
    return _position_history.copy()


# === AI MOVE FINDER (runs in subprocess) ===
def findBestMoveLearning(game_state, valid_moves, return_queue):
    """
    Find best move (called in subprocess)
    Note: Brain is loaded fresh here, but that's OK - we only need evaluation
    """
    if not valid_moves:
        return_queue.put(None)
        return

    # Load brain for evaluation (read-only in subprocess)
    brain = ChessAIBrain()

    # Exploration vs Exploitation
    if random.random() < brain.exploration_rate:
        # Explore: random move
        move = random.choice(valid_moves)
        return_queue.put(move)
        return

    # Exploitation: MCTS with learned evaluation
    root = MCTSNode(game_state)
    iterations = 100 + brain.game_count * 5
    iterations = min(iterations, 800)

    for _ in range(iterations):
        node = root
        state = deepcopy(game_state)

        # Selection
        while node.untried_moves == [] and node.children != []:
            node = node.select_child()
            state.makeMove(node.move)

        # Expansion
        if node.untried_moves != []:
            move = random.choice(node.untried_moves)
            state.makeMove(move)
            node = node.add_child(move, state)

        # Simulation (using learned evaluation)
        eval_score = brain.evaluate_position(state)
        result = 1 / (1 + math.exp(-eval_score))  # Sigmoid

        # Backpropagation
        while node is not None:
            node.update(result)
            node = node.parent
            result = 1 - result

    # Return most visited move
    if not root.children:
        return_queue.put(random.choice(valid_moves))
        return

    best_child = max(root.children, key=lambda c: c.visits)
    return_queue.put(best_child.move)


class MCTSNode:
    """MCTS Node for tree search"""
    def __init__(self, game_state, move=None, parent=None):
        self.game_state = game_state
        self.move = move
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = game_state.getValidMoves()

    def uct_value(self, c=1.41):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + c * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

    def select_child(self):
        return max(self.children, key=lambda node: node.uct_value())

    def add_child(self, move, game_state):
        child = MCTSNode(game_state, move, self)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child

    def update(self, result):
        self.visits += 1
        self.wins += result


# === PUBLIC API ===

def notifyGameResult(result, is_ai_white):
    """
    Call this when game ends!
    result: 'white_win', 'black_win', or 'draw'
    is_ai_white: True if AI was playing white
    """
    positions = get_position_history()

    if not positions:
        print("⚠️  No positions recorded! Make sure record_position() is being called.")
        return

    # Determine result from AI perspective
    if result == 'draw':
        ai_result = 0.0
    elif (result == 'white_win' and is_ai_white) or \
         (result == 'black_win' and not is_ai_white):
        ai_result = 1.0  # AI won
    else:
        ai_result = -1.0  # AI lost

    # LEARN!
    brain = get_brain()
    brain.learn_from_game(positions, ai_result)

    # Clear for next game
    clear_position_history()


def resetLearningAI(ai_plays_white=False):
    """Start new game"""
    clear_position_history()
    print(f"\n♟️  New game started! AI plays {'White ⚪' if ai_plays_white else 'Black ⚫'}")


def getAIStats():
    """Get AI statistics"""
    brain = get_brain()
    return brain.get_stats()


def resetAIBrain():
    """Reset AI brain completely"""
    global _global_brain

    # Backup first
    if os.path.exists(LEARNING_DATA_FILE):
        backup = f"brain_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        backup_path = os.path.join(BACKUP_DIR, backup)
        os.rename(LEARNING_DATA_FILE, backup_path)
        print(f"✅ Backed up old brain to {backup_path}")

    _global_brain = ChessAIBrain()
    print("🔄 AI brain reset!")