from logic.piece import Pawn, Rook, Knight, Bishop, Queen, King
from collections import defaultdict


class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.move_history = []
        self.en_passant_target = None
        self.position_counts = defaultdict(int)
        self.setup_board()
        self.update_repetition_counter()

    def get_board_hash(self):
        board_state = []
        for row in self.board:
            for piece in row:
                if piece:
                    board_state.append(f"{piece.symbol}{piece.color[0]}")
                else:
                    board_state.append(".")
        turn = 'w' if len(self.move_history) % 2 == 0 else 'b'
        castling = self.get_castling_rights()
        ep = str(self.en_passant_target) if self.en_passant_target else "-"
        return "".join(board_state) + turn + castling + ep


    def get_position_key(self):
        key = ""
        for row in self.board:
            for piece in row:
                if piece is None:
                    key += "."
                else:
                    key += piece.symbol if piece.color == 'white' else piece.symbol.lower()
        if self.en_passant_target:
            key += f"ep{self.en_passant_target[0]}{self.en_passant_target[1]}"
        return key


    def update_repetition_counter(self):
        board_hash = self.get_board_hash()
        self.position_counts[board_hash] += 1


    def is_threefold_repetition(self):
        board_hash = self.get_board_hash()
        return self.position_counts[board_hash] >= 3


    def get_castling_rights(self):
        rights = ""
        back_ranks = {'white': 7, 'black': 0}
        for color in ['white', 'black']:
            row = back_ranks[color]
            king = self.get_piece(row, 4)
            ks_rook = self.get_piece(row, 7)
            qs_rook = self.get_piece(row, 0)
            if isinstance(king, King) and not king.has_moved:
                if isinstance(ks_rook, Rook) and not ks_rook.has_moved:
                    rights += 'K' if color == 'white' else 'k'
                if isinstance(qs_rook, Rook) and not qs_rook.has_moved:
                    rights += 'Q' if color == 'white' else 'q'
        return rights or "-"


    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False

        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    moves = piece.get_legal_moves(self.board, (row, col))
                    for move in moves:
                        if not self.move_puts_king_in_check((row, col), move):
                            return False
        return True


    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False

        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    moves = piece.get_legal_moves(self.board, (row, col))
                    for move in moves:
                        if not self.move_puts_king_in_check((row, col), move):
                            return False
        return True


    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False  # King is missing for some reason

        opponent_color = 'black' if color == 'white' else 'white'

        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == opponent_color:
                    moves = piece.get_legal_moves(self.board, (row, col))
                    if king_pos in moves:
                        return True
        return False
    
    def move_puts_king_in_check(self, from_pos, to_pos):
        import copy
        temp_board = copy.deepcopy(self)

        temp_board.move_piece(from_pos, to_pos)
        return temp_board.is_in_check(self.get_piece(*from_pos).color)


    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color and piece.symbol == 'K':
                    return (row, col)
        return None

    def setup_board(self):
        # Place pawns
        for col in range(8):
            self.board[1][col] = Pawn('black')
            self.board[6][col] = Pawn('white')

        # Place major pieces
        layout = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(layout):
            self.board[0][col] = piece_class('black')
            self.board[7][col] = piece_class('white')

    def get_piece(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None



    def move_piece(self, start_pos, end_pos):
        sr, sc = start_pos
        er, ec = end_pos
        piece = self.board[sr][sc]

        if piece:
            legal_moves = piece.get_legal_moves(self.board, (sr, sc), self.en_passant_target)
            if (er, ec) in legal_moves:

                # ✅ En passant capture handling
                if isinstance(piece, Pawn) and self.en_passant_target == (er, ec) and sc != ec and self.board[er][ec] is None:
                    captured_piece = self.board[sr][ec]  # Captured pawn beside the moving pawn
                    self.board[sr][ec] = None
                else:
                    captured_piece = self.board[er][ec]

                # ✅ Move piece
                self.board[er][ec] = piece
                self.board[sr][sc] = None

                # ✅ Save move history
                self.move_history.append({
                    "piece": piece,
                    "start": (sr, sc),
                    "end": (er, ec),
                    "captured": captured_piece,
                    "was_first_move": piece.has_moved if hasattr(piece, "has_moved") else None
                })

                # ✅ Mark pawn as moved
                if hasattr(piece, "has_moved"):
                    piece.has_moved = True

                # Handle en passant target update
                if isinstance(piece, Pawn) and abs(er - sr) == 2:
                    self.en_passant_target = ((sr + er) // 2, sc)
                    # print("En passant target:", self.en_passant_target)
                else:
                    self.en_passant_target = None


                # ✅ Handle promotion
                if piece.symbol == 'P' and ((piece.color == 'white' and er == 0) or (piece.color == 'black' and er == 7)):
                    return 'promote', (er, ec)
                
                                # ✅ Handle castling
                if isinstance(piece, King) and abs(ec - sc) == 2:
                    if ec == 6:  # Kingside castling
                        rook = self.board[sr][7]
                        self.board[sr][5] = rook
                        self.board[sr][7] = None
                        if hasattr(rook, "has_moved"):
                            rook.has_moved = True
                    elif ec == 2:  # Queenside castling
                        rook = self.board[sr][0]
                        self.board[sr][3] = rook
                        self.board[sr][0] = None
                        if hasattr(rook, "has_moved"):
                            rook.has_moved = True

                self.update_repetition_counter()

                return True

        return False



    def display(self):
        print("   a b c d e f g h")
        for row in range(8):
            print(f"{8 - row} ", end="")
            for col in range(8):
                piece = self.board[row][col]
                print(piece if piece else ".", end=" ")
            print(f"{8 - row}")
        print("   a b c d e f g h")