from abc import ABC, abstractmethod

# Abstract base class for all chess pieces
class Piece(ABC):
    def __init__(self, color):
        self.color = color  # 'white' or 'black'
        self.has_moved = False  # Track if the piece has moved (important for castling/pawn double-move)

    @abstractmethod
    def get_legal_moves(self, board, position):
        pass

    # Check if a given piece is an opponent
    def is_opponent(self, piece):
        return piece is not None and piece.color != self.color

    # Represent piece with symbol (uppercase for white, lowercase for black)
    def __str__(self):
        return self.symbol.upper() if self.color == 'white' else self.symbol.lower()


# Pawn class with en passant and promotion logic
class Pawn(Piece):
    symbol = 'P'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        moves = []
        row, col = pos
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        # Normal forward move
        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            moves.append((row + direction, col))
            # First double step
            if row == start_row and board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))

        # Diagonal captures
        for dc in [-1, 1]:
            new_col = col + dc
            new_row = row + direction
            if 0 <= new_col < 8 and 0 <= new_row < 8:
                target = board[new_row][new_col]
                if target and target.color != self.color:
                    moves.append((new_row, new_col))

        # ✅ En passant capture
        if en_passant_target:
            ep_row, ep_col = en_passant_target
            if ep_row == row + direction and abs(ep_col - col) == 1:
                if board[row][ep_col] and isinstance(board[row][ep_col], Pawn) and board[row][ep_col].color != self.color:
                    moves.append((ep_row, ep_col))

        return moves


# Rook class with straight-line movement logic
class Rook(Piece):
    symbol = 'R'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        row, col = pos
        legal_moves = []

        # Movement in 4 straight directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]
                if target is None:
                    legal_moves.append((r, c))
                elif self.is_opponent(target):
                    legal_moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

        return legal_moves


# Knight class with L-shaped moves
class Knight(Piece):
    symbol = 'N'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        row, col = pos
        legal_moves = []

        # 8 L-shaped jump possibilities
        deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2), (1, 2), (2, -1), (2, 1)]

        for dr, dc in deltas:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]
                if target is None or self.is_opponent(target):
                    legal_moves.append((r, c))

        return legal_moves


# Bishop class with diagonal movement
class Bishop(Piece):
    symbol = 'B'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        row, col = pos
        legal_moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]
                if target is None:
                    legal_moves.append((r, c))
                elif self.is_opponent(target):
                    legal_moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

        return legal_moves


# Queen combines rook and bishop moves
class Queen(Piece):
    symbol = 'Q'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        row, col = pos
        legal_moves = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Rook moves
            (-1, -1), (-1, 1), (1, -1), (1, 1) # Bishop moves
        ]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]
                if target is None:
                    legal_moves.append((r, c))
                elif self.is_opponent(target):
                    legal_moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

        return legal_moves


# King class with castling logic
class King(Piece):
    symbol = 'K'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        row, col = pos
        legal_moves = []

        # All 8 adjacent squares
        deltas = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),          (0, 1),
                  (1, -1), (1, 0), (1, 1)]

        for dr, dc in deltas:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]
                if target is None or self.is_opponent(target):
                    legal_moves.append((r, c))

        # ✅ Castling: move king 2 squares, rook jumps over
        if not getattr(self, "has_moved", False):
            # Kingside castling (rook at h-file)
            kingside_rook = board[row][7]
            if isinstance(kingside_rook, Rook) and not getattr(kingside_rook, "has_moved", False):
                if board[row][5] is None and board[row][6] is None:
                    if not self.is_square_attacked(board, (row, col)) and \
                       not self.is_square_attacked(board, (row, 5)) and \
                       not self.is_square_attacked(board, (row, 6)):
                        legal_moves.append((row, 6))

            # Queenside castling (rook at a-file)
            queenside_rook = board[row][0]
            if isinstance(queenside_rook, Rook) and not getattr(queenside_rook, "has_moved", False):
                if board[row][1] is None and board[row][2] is None and board[row][3] is None:
                    if not self.is_square_attacked(board, (row, col)) and \
                       not self.is_square_attacked(board, (row, 2)) and \
                       not self.is_square_attacked(board, (row, 3)):
                        legal_moves.append((row, 2))

        return legal_moves

    # Helper: Check if square is attacked by any opponent piece
    def is_square_attacked(self, board, square):
        r_sq, c_sq = square
        opponent_color = 'black' if self.color == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.color == opponent_color:
                    if square in piece.get_legal_moves(board, (r, c)):
                        return True
        return False
