"""
Enhanced Chess Game with Self-Learning AI
The AI learns from every game and improves over time!
"""
import sys
import time
sys.path.append(".")

import ChessEngine
import SelfLearningAI  # Our learning AI!

from ChessEngine import *
from SelfLearningAI import *
import pygame as p
import os
from multiprocessing import Process, Queue
from datetime import datetime

# Current path information
current_path = os.path.dirname(__file__)
image_path = os.path.join(current_path, "images")

# Board dimensions
BOARD_WIDTH = BOARD_HEIGHT = 640
MOVE_LOG_PANEL_WIDTH = 300
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}
RIGHT_BUTTON_RECTS = {}

# Professional chess colors
# Updated to a green/cream palette similar to popular chess sites
LIGHT_SQUARE = (232, 245, 221)  # pale green / cream
DARK_SQUARE = (140, 163, 110)   # darker green
HIGHLIGHT_COLOR = (186, 202, 68)
MOVE_CIRCLE_COLOR = (100, 100, 100, 128)
CAPTURE_CIRCLE_COLOR = (180, 50, 50, 128)

# Timer settings
INITIAL_TIME = 600  # 10 minutes


def loadImages():
    """Load and scale piece images"""
    pieces = ["wp", "wN", "wB", "wR", "wQ", "wK", "bp", "bN", "bB", "bR", "bQ", "bK"]
    for piece in pieces:
        img = os.path.join(image_path, piece + ".png")
        IMAGES[piece] = p.transform.scale(p.image.load(img), (SQ_SIZE, SQ_SIZE))


def drawPromotionDialog(screen, color):
    """Draw promotion dialog and return selected piece"""
    overlay = p.Surface((BOARD_WIDTH, BOARD_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    dialog_width = 400
    dialog_height = 200
    dialog_x = (BOARD_WIDTH - dialog_width) // 2
    dialog_y = (BOARD_HEIGHT - dialog_height) // 2

    p.draw.rect(screen, (240, 240, 240), (dialog_x, dialog_y, dialog_width, dialog_height))
    p.draw.rect(screen, (0, 0, 0), (dialog_x, dialog_y, dialog_width, dialog_height), 3)

    font = p.font.SysFont("Arial", 28, True)
    text = font.render("Choose Promotion Piece", True, (0, 0, 0))
    text_rect = text.get_rect(center=(BOARD_WIDTH // 2, dialog_y + 40))
    screen.blit(text, text_rect)

    pieces = ['Q', 'R', 'B', 'N']
    piece_size = 80
    spacing = 90
    start_x = dialog_x + (dialog_width - (spacing * 4 - 10)) // 2
    piece_y = dialog_y + 90

    piece_rects = []
    for i, piece in enumerate(pieces):
        piece_x = start_x + i * spacing
        rect = p.Rect(piece_x, piece_y, piece_size, piece_size)
        piece_rects.append((rect, piece))

        p.draw.rect(screen, (200, 200, 200), rect)
        p.draw.rect(screen, (0, 0, 0), rect, 2)

        piece_str = color + piece
        if piece_str in IMAGES:
            img = p.transform.scale(IMAGES[piece_str], (piece_size - 10, piece_size - 10))
            screen.blit(img, (piece_x + 5, piece_y + 5))

    p.display.flip()

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                return 'Q'
            if event.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                for rect, piece in piece_rects:
                    if rect.collidepoint(mouse_pos):
                        return piece


def drawGameOverDialog(screen, winner_text):
    """Draw game over dialog with AI learning stats"""
    overlay = p.Surface((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    dialog_width = 500
    dialog_height = 350
    dialog_x = (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH - dialog_width) // 2
    dialog_y = (BOARD_HEIGHT - dialog_height) // 2

    p.draw.rect(screen, (240, 240, 240), (dialog_x, dialog_y, dialog_width, dialog_height))
    p.draw.rect(screen, (50, 50, 50), (dialog_x, dialog_y, dialog_width, dialog_height), 5)

    # Winner text
    font_large = p.font.SysFont("Arial", 32, True)
    text = font_large.render(winner_text, True, (0, 100, 0))
    text_rect = text.get_rect(center=(dialog_x + dialog_width // 2, dialog_y + 40))
    screen.blit(text, text_rect)

    # AI Stats
    stats = getAIStats()
    font_small = p.font.SysFont("Arial", 18, False)

    stats_y = dialog_y + 90
    stats_lines = [
        f"🧠 AI Learning Progress",
        f"Games Played: {stats['games']}",
        f"Record: {stats['wins']}W - {stats['losses']}L - {stats['draws']}D",
        f"Win Rate: {stats['win_rate']:.1f}%",
        f"Positions Learned: {stats['positions_learned']}",
        f"The AI is evolving! 🚀"
    ]

    for i, line in enumerate(stats_lines):
        color = (0, 0, 0) if i != 0 else (100, 50, 150)
        bold = i == 0
        font_stat = p.font.SysFont("Arial", 18, bold)
        stat_text = font_stat.render(line, True, color)
        screen.blit(stat_text, (dialog_x + 30, stats_y + i * 25))

    # Buttons
    button_width = 200
    button_height = 50
    button_y = dialog_y + 260

    new_game_rect = p.Rect(dialog_x + 40, button_y, button_width, button_height)
    review_rect = p.Rect(dialog_x + 260, button_y, button_width, button_height)

    p.draw.rect(screen, (100, 200, 100), new_game_rect)
    p.draw.rect(screen, (0, 0, 0), new_game_rect, 3)

    p.draw.rect(screen, (100, 150, 200), review_rect)
    p.draw.rect(screen, (0, 0, 0), review_rect, 3)

    font_button = p.font.SysFont("Arial", 22, True)
    new_text = font_button.render("New Game", True, (0, 0, 0))
    review_text = font_button.render("Review", True, (0, 0, 0))

    screen.blit(new_text, new_text.get_rect(center=new_game_rect.center))
    screen.blit(review_text, review_text.get_rect(center=review_rect.center))

    p.display.flip()

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                return "quit"
            if event.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                if new_game_rect.collidepoint(mouse_pos):
                    return "new"
                elif review_rect.collidepoint(mouse_pos):
                    return "review"


def formatTime(seconds):
    """Format time in MM:SS format"""
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02d}:{secs:02d}"


def main():
    p.init()
    p.display.set_caption("Chess with Self-Learning AI 🧠")
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    # Dark outer background to match modern chess sites
    screen.fill((30, 30, 30))
    moveLogFont = p.font.SysFont("Arial", 18, False, False)

    # Game state
    gs = GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    reviewMode = False

    # Timer variables
    whiteTime = INITIAL_TIME
    blackTime = INITIAL_TIME
    lastTime = time.time()

    # AI settings - LEARNING AI!
    playerOne = True  # White is human
    playerTwo = False  # Black is AI (learning)
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False

    # 🔥 IMPORTANT: Track if AI is white
    ai_is_white = not playerOne  # AI plays black in this setup

    # Initialize learning AI
    resetLearningAI(ai_is_white)

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        # Update timer
        if not gameOver and not reviewMode:
            currentTime = time.time()
            elapsed = currentTime - lastTime
            lastTime = currentTime

            if gs.whiteToMove:
                whiteTime -= elapsed
                if whiteTime <= 0:
                    whiteTime = 0
                    gameOver = True
                    winner_text = "Black Wins on Time!"
                    # 🔥 LEARNING: AI learns from time loss
                    notifyGameResult('black_win', ai_is_white)
            else:
                blackTime -= elapsed
                if blackTime <= 0:
                    blackTime = 0
                    gameOver = True
                    winner_text = "White Wins on Time!"
                    # 🔥 LEARNING: AI learns from time loss
                    notifyGameResult('white_win', ai_is_white)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and not reviewMode:
                    location = p.mouse.get_pos()
                    # Check if click was on the right menu buttons
                    if location[0] >= BOARD_WIDTH:
                        for label, rect in RIGHT_BUTTON_RECTS.items():
                            if rect.collidepoint(location):
                                if label == "Save PGN":
                                    saved = save_pgn(gs)
                                    if saved:
                                        print(f"Saved PGN to {saved}")
                                elif label == "Toggle AI":
                                    playerTwo = not playerTwo
                                    ai_is_white = not playerOne and playerTwo
                                    print(f"PlayerTwo (AI)={'ON' if playerTwo else 'OFF'}")
                                else:
                                    print(f"Button pressed: {label}")
                        # don't process as a board click
                        continue

                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2 and humanTurn:
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if validMoves[i].isPawnPromotion:
                                    color = 'w' if gs.whiteToMove else 'b'
                                    promotion_piece = drawPromotionDialog(screen, color)
                                    validMoves[i].promotionChoice = promotion_piece

                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    reviewMode = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                    lastTime = time.time()

                if e.key == p.K_r:  # Reset
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    reviewMode = False
                    running = True
                    whiteTime = INITIAL_TIME
                    blackTime = INITIAL_TIME
                    lastTime = time.time()
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = False
                    # Reset learning AI for new game
                    resetLearningAI(ai_is_white)

        # 🔥🔥🔥 AI MOVE LOGIC - CRITICAL SECTION 🔥🔥🔥
        if not gameOver and not humanTurn and not moveUndone and not reviewMode:
            if not AIThinking:
                AIThinking = True

                # 🔥 RECORD POSITION BEFORE AI THINKS (THIS IS CRITICAL!)
                SelfLearningAI.record_position(gs)

                print("🧠 AI thinking...")
                returnQueue = Queue()
                moveFinderProcess = Process(
                    target=findBestMoveLearning,
                    args=(gs, validMoves, returnQueue),
                )
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                print("✓ AI move decided")
                if AIMove is None:
                    AIMove = random.choice(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, whiteTime, blackTime)

        # 🔥🔥🔥 GAME OVER DETECTION - LEARNING HAPPENS HERE 🔥🔥🔥
        if gs.checkmate and not reviewMode:
            gameOver = True
            if gs.whiteToMove:
                winner_text = "Black Wins by Checkmate!"
                # 🔥 AI LEARNS: Black won
                notifyGameResult('black_win', ai_is_white)
            else:
                winner_text = "White Wins by Checkmate!"
                # 🔥 AI LEARNS: White won
                notifyGameResult('white_win', ai_is_white)

        elif gs.stalemate and not reviewMode:
            gameOver = True
            winner_text = "Stalemate - Draw!"
            # 🔥 AI LEARNS: Game was a draw
            notifyGameResult('draw', ai_is_white)

        # Show game over dialog
        if gameOver and not reviewMode:
            choice = drawGameOverDialog(screen, winner_text)
            if choice == "new":
                gs = GameState()
                validMoves = gs.getValidMoves()
                sqSelected = ()
                playerClicks = []
                moveMade = False
                animate = False
                gameOver = False
                whiteTime = INITIAL_TIME
                blackTime = INITIAL_TIME
                lastTime = time.time()
                moveUndone = False
                # Start new learning session
                resetLearningAI(ai_is_white)
            elif choice == "review":
                reviewMode = True
                gameOver = False
            elif choice == "quit":
                running = False

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, whiteTime, blackTime):
    """Draw the complete game state"""
    drawBoard(screen)
    drawRightMenu(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)
    drawTimers(screen, whiteTime, blackTime, gs.whiteToMove)
    drawAIStats(screen)  # Show AI learning progress!


def save_pgn(gs):
    """Save the current game's moves to a simple PGN-like file"""
    if not gs.moveLog:
        return None

    # Build simple move list (algebraic via Move.__str__)
    moves = []
    for i, mv in enumerate(gs.moveLog):
        moves.append(str(mv))

    # Format into numbered pairs
    pgn_lines = []
    for i in range(0, len(moves), 2):
        move_no = i // 2 + 1
        s = f"{move_no}. {moves[i]}"
        if i + 1 < len(moves):
            s += f" {moves[i+1]}"
        pgn_lines.append(s)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(current_path, f"game_{timestamp}.pgn")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(" ".join(pgn_lines))
        print(f"💾 Saved PGN: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving PGN: {e}")
        return None


def drawBoard(screen):
    """Draw the chess board"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, validMoves, sqSelected):
    """Highlight selected square and show move indicators"""
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(HIGHLIGHT_COLOR)
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    center_x = move.endCol * SQ_SIZE + SQ_SIZE // 2
                    center_y = move.endRow * SQ_SIZE + SQ_SIZE // 2
                    circle_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)

                    if move.pieceCaptured != "--":
                        p.draw.circle(circle_surface, CAPTURE_CIRCLE_COLOR,
                                    (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 2 - 5, 8)
                    else:
                        p.draw.circle(circle_surface, MOVE_CIRCLE_COLOR,
                                    (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 6)

                    screen.blit(circle_surface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawPieces(screen, board):
    """Draw the pieces"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock):
    """Animate piece movement"""
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        r = move.startRow + dR * frame / frameCount
        c = move.startCol + dC * frame / frameCount

        drawBoard(screen)
        drawPieces(screen, board)

        color = LIGHT_SQUARE if (move.endRow + move.endCol) % 2 == 0 else DARK_SQUARE
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enpassantRow = (move.endRow + 1) if move.pieceCaptured[0] == "b" else (move.endRow - 1)
                endSquare = p.Rect(move.endCol * SQ_SIZE, enpassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(120)


def drawTimers(screen, whiteTime, blackTime, whiteToMove):
    """Draw timers"""
    timer_width = MOVE_LOG_PANEL_WIDTH - 20
    timer_height = 60
    timer_x = BOARD_WIDTH + 10

    white_timer_y = BOARD_HEIGHT - timer_height - 10
    black_timer_y = 10

    font = p.font.SysFont("Arial", 32, True)

    white_bg_color = (80, 80, 90) if whiteToMove else (50, 50, 60)
    p.draw.rect(screen, white_bg_color, (timer_x, white_timer_y, timer_width, timer_height), 0, border_radius=6)
    p.draw.rect(screen, (0, 0, 0), (timer_x, white_timer_y, timer_width, timer_height), 2, border_radius=6)

    white_text = font.render(formatTime(whiteTime), True, (240, 240, 240))
    white_label = p.font.SysFont("Arial", 16).render("White (You)", True, (220, 220, 220))
    screen.blit(white_label, (timer_x + 10, white_timer_y + 5))
    screen.blit(white_text, (timer_x + timer_width // 2 - white_text.get_width() // 2,
                             white_timer_y + 25))
    black_bg_color = (80, 80, 90) if not whiteToMove else (50, 50, 60)
    p.draw.rect(screen, black_bg_color, (timer_x, black_timer_y, timer_width, timer_height), 0, border_radius=6)
    p.draw.rect(screen, (0, 0, 0), (timer_x, black_timer_y, timer_width, timer_height), 2, border_radius=6)

    black_text = font.render(formatTime(blackTime), True, (240, 240, 240))
    black_label = p.font.SysFont("Arial", 16).render("Black (AI 🧠)", True, (220, 220, 220))
    screen.blit(black_label, (timer_x + 10, black_timer_y + 5))
    screen.blit(black_text, (timer_x + timer_width // 2 - black_text.get_width() // 2,
                             black_timer_y + 25))


def drawAIStats(screen):
    """Draw AI learning statistics in real-time"""
    stats = getAIStats()

    stats_x = BOARD_WIDTH + 10
    stats_y = 520
    stats_width = MOVE_LOG_PANEL_WIDTH - 20
    # Dark themed background box
    p.draw.rect(screen, (50, 50, 60), (stats_x, stats_y, stats_width, 110), 0, border_radius=6)
    p.draw.rect(screen, (90, 60, 150), (stats_x, stats_y, stats_width, 110), 2, border_radius=6)

    # Title
    font_title = p.font.SysFont("Arial", 14, True)
    title = font_title.render("🧠 AI EVOLUTION", True, (220, 200, 255))
    screen.blit(title, (stats_x + 5, stats_y + 5))

    # Stats
    font_stats = p.font.SysFont("Arial", 12, False)
    lines = [
        f"Games: {stats['games']}",
        f"Win Rate: {stats['win_rate']:.1f}%",
        f"Learned: {stats['positions_learned']} positions",
        f"Exploration: {stats['exploration_rate']:.1f}%"
    ]

    for i, line in enumerate(lines):
        text = font_stats.render(line, True, (220, 220, 220))
        screen.blit(text, (stats_x + 10, stats_y + 30 + i * 18))


def drawRightMenu(screen):
    """Draw the right-side menu with action buttons similar to chess.com"""
    menu_x = BOARD_WIDTH
    menu_y = 10
    menu_w = MOVE_LOG_PANEL_WIDTH

    # Dark panel background
    p.draw.rect(screen, (40, 40, 40), (menu_x, menu_y, menu_w, 420), 0, border_radius=6)

    # Buttons list (label, color)
    buttons = [
        ("Play Online", (70, 70, 70)),
        ("Play Bots", (60, 90, 120)),
        ("Play Coach", (90, 70, 40)),
        ("Play a Friend", (100, 100, 60)),
        ("Tournaments", (70, 90, 70)),
        ("Save PGN", (80, 120, 80)),
        ("Toggle AI", (120, 80, 120)),
    ]

    btn_h = 56
    spacing = 12
    x = menu_x + 12
    y = menu_y + 12

    font_btn = p.font.SysFont("Arial", 20, True)
    for label, color in buttons:
        rect = p.Rect(x, y, menu_w - 24, btn_h)
        # register rect for click handling
        RIGHT_BUTTON_RECTS[label] = rect
        p.draw.rect(screen, color, rect, border_radius=6)
        p.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=6)
        text = font_btn.render(label, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=rect.center))
        y += btn_h + spacing

    # Small footer / branding area
    footer_rect = p.Rect(menu_x + 10, menu_y + 320, menu_w - 20, 80)
    p.draw.rect(screen, (50, 50, 50), footer_rect, border_radius=6)
    footer_text = p.font.SysFont("Arial", 14).render("Chess - Self Learning AI", True, (200, 200, 200))
    screen.blit(footer_text, (footer_rect.x + 12, footer_rect.y + 12))


def drawMoveLog(screen, gs, font):
    """Draw the move log panel"""
    moveLogRect = p.Rect(BOARD_WIDTH, 90, MOVE_LOG_PANEL_WIDTH, 420)
    p.draw.rect(screen, (40, 40, 48), moveLogRect, 0, border_radius=6)
    p.draw.rect(screen, (0, 0, 0), moveLogRect, 2, border_radius=6)

    moveLog = gs.moveLog
    moveTexts = []

    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1])
        moveTexts.append(moveString)

    padding = 8
    textY = padding
    lineSpacing = 4

    for i, move_text in enumerate(moveTexts):
        textObject = font.render(move_text, True, (230, 230, 230))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


if __name__ == "__main__":
    main()