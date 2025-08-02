from abc import ABC, abstractmethod

class Piece(ABC):
    def __init__(self, color):
        self.color = color  # 'white' or 'black'

    @abstractmethod
    def get_legal_moves(self, board, position):
        pass

    def is_opponent(self, piece):
        return piece is not None and piece.color != self.color

    def __str__(self):
        return self.symbol.upper() if self.color == 'white' else self.symbol.lower()


class Pawn(Piece):
    symbol = 'P'

    def get_legal_moves(self, board, pos):
        row, col = pos
        direction = -1 if self.color == 'white' else 1
        legal_moves = []

        # Move forward 1 square
        next_row = row + direction
        if 0 <= next_row < 8 and board[next_row][col] is None:
            legal_moves.append((next_row, col))

            # Move forward 2 squares on first move
            start_row = 6 if self.color == 'white' else 1
            if row == start_row:
                jump_row = row + 2 * direction
                if board[jump_row][col] is None:
                    legal_moves.append((jump_row, col))

        # Diagonal captures
        for dc in [-1, 1]:
            new_col = col + dc
            if 0 <= new_col < 8 and 0 <= next_row < 8:
                target = board[next_row][new_col]
                if self.is_opponent(target):
                    legal_moves.append((next_row, new_col))

        return legal_moves



class Rook(Piece):
    symbol = 'R'

    def get_legal_moves(self, board, pos):
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

    def get_legal_moves(self, board, pos):
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

    def get_legal_moves(self, board, pos):
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

    def get_legal_moves(self, board, pos):
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

    def get_legal_moves(self, board, pos):
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