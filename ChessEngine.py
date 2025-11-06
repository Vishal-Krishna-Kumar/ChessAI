"""
Chess Engine - Handles game state, move generation, and game logic
Updated to support custom pawn promotion
"""

class GameState:
    def __init__(self):
        # 2D representation of the board from white's perspective
        # First character: piece color (b=black, w=white)
        # Second character: piece type (K=King, Q=Queen, R=Rook, B=Bishop, N=Knight, p=pawn)
        # "--" represents empty squares
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  # 8th rank
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],  # 7th rank
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 6th rank
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 5th rank
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 4th rank
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 3rd rank
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],  # 2nd rank
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],  # 1st rank
        ]

        self.whiteToMove = True
        self.moveLog = []  # Move objects
        self.moveFunctions = {
            "p": self.getPawnMove,
            "N": self.getKnightMove,
            "B": self.getBishopMove,
            "R": self.getRockMove,
            "Q": self.getQueenMove,
            "K": self.getKingMove,
        }
        # Track king locations for castling, checks, checkmates and stalemates
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        # Coordinates where an en passant capture is possible
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightLog = [
            CastleRights(
                self.currentCastlingRights.wks,
                self.currentCastlingRights.bks,
                self.currentCastlingRights.wqs,
                self.currentCastlingRights.bqs,
            )
        ]

    def makeMove(self, move):
        """Execute a move on the board"""
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # Log the move so we can undo it later or print a PGN for the game
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove  # Switch turns

        # Update king location after making a move
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion with custom piece selection
        if move.isPawnPromotion:
            promotion_piece = getattr(move, 'promotionChoice', 'Q')  # Default to Queen
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotion_piece

        # En passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # Capture the pawn

        # Update enpassantPossible variable (only for 2 square pawn advance)
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # Castling
        if move.isCastleMove:
            # Check if it castles to left or right
            if move.endCol - move.startCol == 2:  # King side castle (right)
                # Copy the rook to the new square
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"  # Remove the old rook
            elif move.endCol - move.startCol == -2:  # Queen side castle (left)
                # Copy the rook to the new square
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"  # Remove the old rook

        # Update the enpassantPossibleLog
        self.enpassantPossibleLog.append(self.enpassantPossible)

        # Update castling rights whenever it's a rook or king move
        self.updateCastlRights(move)
        self.castleRightLog.append(
            CastleRights(
                self.currentCastlingRights.wks,
                self.currentCastlingRights.bks,
                self.currentCastlingRights.wqs,
                self.currentCastlingRights.bqs,
            )
        )

    def undoMove(self):
        """Undo the last move made on the board"""
        # Make sure there's a move to undo
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # Switch turns

            # Update king location after undo a move
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # Delete checkmate and stalemate states
            self.checkmate = False
            self.stalemate = False

            # Undo the en passant move
            if move.isEnpassantMove:
                # Make the landing square blank as it was
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # Undo castle rights
            # Get rid of the new castle rights from the move we're undoing
            self.castleRightLog.pop()
            # Set currentCastlingRights to last one we have now on the log list
            newRights = self.castleRightLog[-1]
            self.currentCastlingRights = CastleRights(
                newRights.wks, newRights.bks, newRights.wqs, newRights.bqs
            )

            # Undo the castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # King side castle
                    # Copy the rook to its starting square
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    # Remove the castled rook
                    self.board[move.endRow][move.endCol - 1] = "--"
                elif move.endCol - move.startCol == -2:  # Queen side castle
                    # Copy the rook to its starting square
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    # Remove the castled rook
                    self.board[move.endRow][move.endCol + 1] = "--"

    def updateCastlRights(self, move):
        """Update castle rights given a move"""
        # Check if the king moved or the rook moved
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:  # White's left rook
                    self.currentCastlingRights.wqs = False
                if move.startCol == 7:  # White's right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:  # Black's left rook
                    self.currentCastlingRights.bqs = False
                if move.startCol == 7:  # Black's right rook
                    self.currentCastlingRights.bks = False

        # Check if the rook is captured
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    def getValidMoves(self):
        """Get all valid moves considering checks"""
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(
            self.currentCastlingRights.wks,
            self.currentCastlingRights.bks,
            self.currentCastlingRights.wqs,
            self.currentCastlingRights.bqs,
        )

        # 1. Generate all possible moves and don't worry about the king's state
        moves = self.getAllPossibleMoves()

        # 2. For each move found, make that move
        # When removing from the list, go backwards
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # 3. Generate all opponent's moves
            # 4. For each of those moves, check if they attack your king
            # We need this as the makeMove() did swap the players once
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # 5. If they do, it's not a valid move
                moves.remove(moves[i])
            # We need this to return everything as before
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        # Check for checkmate or stalemate
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        # Generate castle moves
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves

    def inCheck(self):
        """Determine if the current player is in check"""
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        """Determine if the enemy can attack the square (r, c)"""
        # Switch to the opponent's move
        self.whiteToMove = not self.whiteToMove
        # Generate all of its moves
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # Switch the turns back

        # Check if any of those moves is attacking the king's location
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # King is under attack
                return True
        return False  # None of the opponent's moves will be attacking the king

    def getAllPossibleMoves(self):
        """Get all moves without considering checks"""
        moves = []
        for r in range(len(self.board)):  # Number of rows
            for c in range(len(self.board[r])):  # Number of columns in a given row
                turn = self.board[r][c][0]  # The piece color
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]  # The piece type
                    # Generate all possible valid moves for each piece
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMove(self, r, c, moves):
        """Get all moves for a pawn located at row r and column c"""
        if self.whiteToMove:  # White pawn move
            if self.board[r - 1][c] == "--":  # The square in front of a pawn is empty
                moves.append(Move((r, c), (r - 1, c), self.board))
                # Check if it's possible to advance two squares in the first move
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # Don't go outside the board from the left
                if self.board[r - 1][c - 1][0] == "b":  # There's an enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # Don't go outside the board from the right
                if self.board[r - 1][c + 1][0] == "b":  # There's an enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
        else:  # Black pawn move
            if self.board[r + 1][c] == "--":  # The square in front of a pawn is empty
                moves.append(Move((r, c), (r + 1, c), self.board))
                # Check if it's possible to advance two squares in the first move
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # Don't go outside the board from the left
                if self.board[r + 1][c - 1][0] == "w":  # There's an enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # Don't go outside the board from the right
                if self.board[r + 1][c + 1][0] == "w":  # There's an enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getKnightMove(self, r, c, moves):
        """Get all moves for a knight located at row r and column c"""
        # Knight is a short range piece with 8 possible moves
        knightMoves = ((-1, -2), (-1, 2), (-2, -1), (-2, 1), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMove(self, r, c, moves):
        """Get all moves for a bishop located at row r and column c"""
        # 4 diagonal directions
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Still on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Empty square
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break  # Can't go further after capture
                    else:  # Friendly piece
                        break  # Can't go through friendly pieces
                else:
                    break  # Out of bounds

    def getRockMove(self, r, c, moves):
        """Get all moves for a rook located at row r and column c"""
        # 4 directions: up, left, down, right
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Still on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Empty square
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break  # Can't go further after capture
                    else:  # Friendly piece
                        break  # Can't go through friendly pieces
                else:
                    break  # Out of bounds

    def getQueenMove(self, r, c, moves):
        """Get all moves for a queen located at row r and column c"""
        # Queen has the power of both rook and bishop
        self.getBishopMove(r, c, moves)
        self.getRockMove(r, c, moves)

    def getKingMove(self, r, c, moves):
        """Get all moves for a king located at row r and column c"""
        kingMoves = (
            (-1, 0), (0, -1), (1, 0), (0, 1),      # Rook-like moves
            (-1, -1), (-1, 1), (1, -1), (1, 1)     # Bishop-like moves
        )
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastleMoves(self, r, c, moves):
        """Generate all valid castle moves for king at (r, c)"""
        # Can't castle if king is in check
        if self.squareUnderAttack(r, c):
            return

        # Check king side castle
        if (self.whiteToMove and self.currentCastlingRights.wks) or \
           (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r, c, moves)

        # Check queen side castle
        if (self.whiteToMove and self.currentCastlingRights.wqs) or \
           (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        """Generate king side castle moves"""
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        """Generate queen side castle moves"""
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            # Only check squares the king moves through
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights:
    """Class to track castling rights"""
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # White king side
        self.bks = bks  # Black king side
        self.wqs = wqs  # White queen side
        self.bqs = bqs  # Black queen side


class Move:
    """Class to represent a chess move"""
    # Maps for converting between chess notation and array indices
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    fileToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in fileToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow, self.startCol = startSq
        self.endRow, self.endCol = endSq
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # En passant move
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"

        # Pawn promotion move
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or \
                               (self.pieceMoved == "bp" and self.endRow == 7)

        # Castle move
        self.isCastleMove = isCastleMove

        # Check if move is a capture
        self.isCapture = self.pieceCaptured != "--"

        # Unique ID for each move (0-7777)
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

        # For custom promotion piece selection (default Queen)
        self.promotionChoice = 'Q'

    def __eq__(self, other):
        """Override equals method for move comparison"""
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        """Get standard chess notation for the move"""
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        """Convert row and column to chess notation (e.g., e4)"""
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __str__(self):
        """String representation of the move in algebraic notation"""
        # Castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)

        # Pawn moves
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

        # Other piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare