from abc import ABC, abstractmethod

class Piece(ABC):
    def __init__(self, color):
        self.color = color  # 'white' or 'black'
        self.has_moved = False

    @abstractmethod
    def get_legal_moves(self, board, position):
        pass

    def is_opponent(self, piece):
        return piece is not None and piece.color != self.color

    def __str__(self):
        return self.symbol.upper() if self.color == 'white' else self.symbol.lower()


class Pawn(Piece):
    symbol = 'P'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        moves = []
        row, col = pos
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        # Forward move
        if 0 <= row + direction < 8 and board[row + direction][col] is None:
            moves.append((row + direction, col))
            if row == start_row and board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))

        # Captures
        for dc in [-1, 1]:
            new_col = col + dc
            new_row = row + direction
            if 0 <= new_col < 8 and 0 <= new_row < 8:
                target = board[new_row][new_col]
                if target and target.color != self.color:
                    moves.append((new_row, new_col))

        # ✅ En passant
        if en_passant_target:
            ep_row, ep_col = en_passant_target
            if ep_row == row + direction and abs(ep_col - col) == 1:
                if board[row][ep_col] and isinstance(board[row][ep_col], Pawn) and board[row][ep_col].color != self.color:
                    moves.append((ep_row, ep_col))

        return moves




class Rook(Piece):
    symbol = 'R'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        row, col = pos
        legal_moves = []

        # Directions: up, down, left, right
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


class Knight(Piece):
    symbol = 'N'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        row, col = pos
        legal_moves = []

        # All 8 possible L-shaped moves
        deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2), (1, 2), (2, -1), (2, 1)]

        for dr, dc in deltas:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]
                if target is None or self.is_opponent(target):
                    legal_moves.append((r, c))

        return legal_moves


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


class Queen(Piece):
    symbol = 'Q'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        row, col = pos
        legal_moves = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # rook moves
            (-1, -1), (-1, 1), (1, -1), (1, 1) # bishop moves
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


class King(Piece):
    symbol = 'K'

    def get_legal_moves(self, board, pos, en_passant_target=None):
        row, col = pos
        legal_moves = []

        # All 8 adjacent directions
        deltas = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),          (0, 1),
                  (1, -1), (1, 0), (1, 1)]

        for dr, dc in deltas:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]
                if target is None or self.is_opponent(target):
                    legal_moves.append((r, c))

        return legal_moves