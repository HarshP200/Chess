import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import tkinter.simpledialog as simpledialog
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logic.board import Board
from logic.piece import Queen
from logic.piece import Rook
from logic.piece import Bishop
from logic.piece import Knight


class ChessGUI:
    def __init__(self, board):
        self.window = tk.Tk()
        self.window.title("Chess Game")
        self.turn = 'white'
        self.turn_label = tk.Label(self.window, text="White's Turn", font=("Arial", 16))
        self.turn_label.pack(pady=5)
        restart_btn = tk.Button(self.window, text="Restart Game", command=self.restart_game)
        restart_btn.pack(pady=5)

        self.game_over = False

        self.board = board
        self.cell_size = 80
        self.images = {}

        self.canvas = tk.Canvas(self.window, width=8 * self.cell_size, height=8 * self.cell_size)
        self.canvas.pack()

        self.load_images()
        self.selected = None
        self.draw_board()

        self.canvas.bind("<Button-1>", self.handle_click)

        self.dragging = False
        self.drag_start = None

        self.canvas.bind("<Button-3>", self.start_drag)
        self.canvas.bind("<B3-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-3>", self.end_drag)


    def start_drag(self, event):
        if self.game_over:
            return
        row = event.y // self.cell_size
        col = event.x // self.cell_size
        piece = self.board.get_piece(row, col)

        if piece and piece.color == self.turn:
            self.drag_start = (row, col)
            self.dragging = True
            self.selected = (row, col)
            self.draw_board()  # ✅ this will now show legal moves

    def on_drag(self, event):
        if self.dragging:
            self.draw_board()  # Still highlight squares
            # Optional: show a ghost image following cursor

    def end_drag(self, event):
        if not self.dragging or not self.drag_start:
            return

        self.dragging = False
        from_row, from_col = self.drag_start
        to_row = event.y // self.cell_size
        to_col = event.x // self.cell_size
        self.drag_start = None
        self.selected = None

        piece = self.board.get_piece(from_row, from_col)

        if piece and piece.color == self.turn:
            legal_moves = piece.get_legal_moves(self.board.board, (from_row, from_col))
            legal_moves = [
                move for move in legal_moves
                if not self.board.move_puts_king_in_check((from_row, from_col), move)
            ]
            if (to_row, to_col) in legal_moves:
                result = self.board.move_piece((from_row, from_col), (to_row, to_col))

                if isinstance(result, tuple) and result[0] == 'promote':
                    r, c = result[1]
                    promoted_piece = self.ask_promotion_choice(self.turn)
                    if promoted_piece == 'Queen':
                        self.board.board[r][c] = Queen(self.turn)
                    elif promoted_piece == 'Rook':
                        self.board.board[r][c] = Rook(self.turn)
                    elif promoted_piece == 'Bishop':
                        self.board.board[r][c] = Bishop(self.turn)
                    elif promoted_piece == 'Knight':
                        self.board.board[r][c] = Knight(self.turn)

                self.turn = 'black' if self.turn == 'white' else 'white'
                self.turn_label.config(text=f"{self.turn.capitalize()}'s Turn")

                if self.board.is_checkmate(self.turn):
                    self.draw_board()
                    tk.messagebox.showinfo("Game Over", f"{'White' if self.turn == 'black' else 'Black'} wins by checkmate!")
                    self.game_over = True
                    return
                elif self.board.is_stalemate(self.turn):
                    self.draw_board()
                    tk.messagebox.showinfo("Game Over", "Stalemate! It's a draw.")
                    self.game_over = True
                    return

        self.draw_board()



    def load_images(self):
        pieces = ['K', 'Q', 'R', 'B', 'N', 'P']
        for color in ['w', 'b']:
            for p in pieces:
                filename = f"{color}{p}.png"
                path = os.path.join("assets", filename)
                from PIL import Image

                image = Image.open(path).resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)

                self.images[f"{color}{p}"] = ImageTk.PhotoImage(image)


    def highlight_square(self, row, col):
        x0 = col * self.cell_size
        y0 = row * self.cell_size
        x1 = x0 + self.cell_size
        y1 = y0 + self.cell_size
        self.canvas.create_rectangle(x0, y0, x1, y1, outline='red', width=3)

    def handle_click(self, event):
        if self.game_over:
            return

        row = event.y // self.cell_size
        col = event.x // self.cell_size

        if self.selected:
            piece = self.board.get_piece(*self.selected)
            if piece and piece.color == self.turn:
                legal_moves = piece.get_legal_moves(self.board.board, self.selected)

                # Filter moves that don't leave king in check
                legal_moves = [
                    move for move in legal_moves
                    if not self.board.move_puts_king_in_check(self.selected, move)
                ]

                if (row, col) in legal_moves:
                    result = self.board.move_piece(self.selected, (row, col))

                    if result == True or (isinstance(result, tuple) and result[0] == 'promote'):
                        # Handle promotion if needed
                        if isinstance(result, tuple) and result[0] == 'promote':
                            r, c = result[1]
                            promoted_piece = self.ask_promotion_choice(self.turn)
                            if promoted_piece == 'Queen':
                                self.board.board[r][c] = Queen(self.turn)
                            elif promoted_piece == 'Rook':
                                self.board.board[r][c] = Rook(self.turn)
                            elif promoted_piece == 'Bishop':
                                self.board.board[r][c] = Bishop(self.turn)
                            elif promoted_piece == 'Knight':
                                self.board.board[r][c] = Knight(self.turn)

                        self.selected = None

                        # Switch turn first
                        self.turn = 'black' if self.turn == 'white' else 'white'
                        self.turn_label.config(text=f"{self.turn.capitalize()}'s Turn")

                        # Now check for game over conditions (for the new player)
                        if self.board.is_checkmate(self.turn):
                            self.draw_board()
                            tk.messagebox.showinfo("Game Over", f"{'White' if self.turn == 'black' else 'Black'} wins by checkmate!")
                            self.game_over = True
                            return
                        elif self.board.is_stalemate(self.turn):
                            self.draw_board()
                            tk.messagebox.showinfo("Game Over", "Stalemate! It's a draw.")
                            self.game_over = True
                            return
                    else:
                        self.selected = None

                    self.turn_label.config(text=f"{self.turn.capitalize()}'s Turn")

                    # Now check for game over conditions (for the new player)
                    if self.board.is_checkmate(self.turn):
                        self.draw_board()
                        tk.messagebox.showinfo("Game Over", f"{'White' if self.turn == 'black' else 'Black'} wins by checkmate!")
                        self.game_over = True
                        return
                    elif self.board.is_stalemate(self.turn):
                        self.draw_board()
                        tk.messagebox.showinfo("Game Over", "Stalemate! It's a draw.")
                        self.game_over = True
                        return
                else:
                    self.selected = None

            else:
                self.selected = None
        else:
            piece = self.board.get_piece(row, col)
            if piece and piece.color == self.turn:
                self.selected = (row, col)

        self.draw_board()



    def ask_promotion_choice(self, color):
        choice_window = tk.Toplevel(self.window)
        choice_window.title("Choose Promotion")

        tk.Label(choice_window, text=f"{color.capitalize()} Pawn Promotion", font=("Arial", 14)).pack(pady=10)

        # Store selected piece
        selected = {'piece': None}

        def choose(piece_name):
            selected['piece'] = piece_name
            choice_window.destroy()

        frame = tk.Frame(choice_window)
        frame.pack(pady=10)

        for piece_name in ['Queen', 'Rook', 'Bishop', 'Knight']:
            symbol = piece_name[0]
            if symbol == "K": symbol = "N"
            image_tag = color[0] + symbol
            btn = tk.Button(frame, image=self.images[image_tag], command=lambda p=piece_name: choose(p))
            btn.pack(side='left', padx=10)

        self.window.wait_window(choice_window)
        return selected['piece']


    def draw_board(self):
        self.canvas.delete("all")  # Clear previous drawings
        colors = ["#EEEED2", "#769656"]

        # ✅ Get king position once before loop
        king_pos = self.board.find_king(self.turn)
        in_check = self.board.is_in_check(self.turn)

        for row in range(8):
            for col in range(8):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                fill = colors[(row + col) % 2]

                # ✅ Highlight if king is in check
                if in_check and king_pos == (row, col):
                    fill = "#ffaaaa"  # light red

                # ✅ Highlight legal moves
                if self.selected:
                    piece = self.board.get_piece(*self.selected)
                    if piece and piece.color == self.turn:
                        legal_moves = piece.get_legal_moves(self.board.board, self.selected)

                        # Filter out illegal moves that would leave king in check
                        legal_moves = [
                            move for move in legal_moves
                            if not self.board.move_puts_king_in_check(self.selected, move)
                        ]

                        if (row, col) in legal_moves:
                            fill = "#ccffcc"  # Light green


                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="black")

                # Draw piece
                piece = self.board.get_piece(row, col)
                if piece:
                    tag = piece.color[0] + piece.symbol
                    image = self.images.get(tag)
                    if image:
                        self.canvas.create_image(x1, y1, anchor='nw', image=image)

        # ✅ Draw red border on selected square
        if self.selected:
            row, col = self.selected
            self.highlight_square(row, col)

    def restart_game(self):

        self.board = Board()
        self.turn = 'white'
        self.game_over = False
        self.turn_label.config(text="White's Turn")
        self.selected = None
        self.draw_board()



    def run(self):
        self.window.mainloop()

