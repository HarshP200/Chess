from logic.board import Board
from logic.piece import King
from copy import deepcopy
import copy



class Game:
    def __init__(self):
        self.board = Board()
        self.current_player = 'white'

    def parse_move(self, move_str):
        try:
            start_str, end_str = move_str.split()
            return self.algebraic_to_index(start_str), self.algebraic_to_index(end_str)
        except:
            return None, None

    def algebraic_to_index(self, pos):
        col = ord(pos[0].lower()) - ord('a')  # a-h -> 0-7
        row = 8 - int(pos[1])                 # 8-1 -> 0-7
        return (row, col)

    def play(self):
        while True:
            self.board.display()
            move_input = input(f"{self.current_player}'s move (e.g. e2 e4): ").strip()
            start, end = self.parse_move(move_input)

            if not start or not end:
                print("Invalid input format. Try again.")
                continue

            piece = self.board.get_piece(*start)
            if not piece:
                print("No piece at that position.")
                continue

            if piece.color != self.current_player:
                print("That's not your piece!")
                continue

            legal_moves = piece.get_legal_moves(self.board.board, start)
            if end not in legal_moves:
                print("Illegal move for this piece!")
                continue

            # Simulate move for check validation
            import copy
            temp_board = copy.deepcopy(self.board)
            temp_board.move_piece(start, end)
            if self.is_in_check(self.current_player, temp_board.board):
                print("That move would leave your king in check!")
                continue

            # Perform actual move
            self.board.move_piece(start, end)

            # Check game state AFTER the move
            opponent = 'black' if self.current_player == 'white' else 'white'
            if self.is_in_check(opponent):
                if not self.has_legal_moves(opponent):
                    self.board.display()
                    print(f"Checkmate! {self.current_player.capitalize()} wins!")
                    break
                else:
                    print(f"{opponent.capitalize()} is in check!")
            else:
                if not self.has_legal_moves(opponent):
                    self.board.display()
                    print(f"Stalemate! It's a draw.")
                    break

            # Toggle turn
            self.current_player = opponent




    def is_in_check(self, color, board=None):
        from logic.piece import King

        board = board if board else self.board.board
        king_pos = None

        # Locate the king
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and isinstance(piece, King) and piece.color == color:
                    king_pos = (r, c)
                    break

        if not king_pos:
            return False

        # Check if any opponent piece can move to the king's position
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.color != color:
                    if king_pos in piece.get_legal_moves(board, (r, c)):
                        return True

        return False

    def is_legal_move(self, from_pos, to_pos):
        piece = self.board.get_piece(from_pos)
        if not piece or piece.color != self.current_turn:
            return False

        legal_moves = piece.get_legal_moves(self.board.board, from_pos)
        if to_pos not in legal_moves:
            return False

        # Simulate move and check if king is left in check
        backup_board = copy.deepcopy(self.board.board)
        self.board.move_piece(from_pos, to_pos)

        in_check = self.is_in_check(self.current_turn)

        # Undo the move
        self.board.board = backup_board

        return not in_check

    def has_legal_moves(self, color):
        for r in range(8):
            for c in range(8):
                piece = self.board.board[r][c]
                if piece and piece.color == color:
                    legal_moves = piece.get_legal_moves(self.board.board, (r, c))
                    for move in legal_moves:
                        temp_board = deepcopy(self.board)
                        temp_board.move_piece((r, c), move)
                        if not self.is_in_check(color, temp_board.board):
                            return True
        return False

