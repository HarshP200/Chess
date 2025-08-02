from logic.piece import Pawn, Rook, Knight, Bishop, Queen, King

class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()

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
            legal_moves = piece.get_legal_moves(self.board, (sr, sc))
            if (er, ec) in legal_moves:
                self.board[er][ec] = piece
                self.board[sr][sc] = None
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