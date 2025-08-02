import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import tkinter.simpledialog as simpledialog
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import custom logic
from logic.board import Board
from logic.piece import Queen
from logic.piece import Rook
from logic.piece import Bishop
from logic.piece import Knight


class ChessGUI:
    def __init__(self, board):
        self.window = tk.Tk()
        self.window.title("Chess Game")

        # Track current turn
        self.turn = 'white'
        self.turn_label = tk.Label(self.window, text="White's Turn", font=("Arial", 16))
        self.turn_label.pack(pady=5)

        # Restart button
        restart_btn = tk.Button(self.window, text="Restart Game", command=self.restart_game)
        restart_btn.pack(pady=5)

        self.game_over = False
        self.board = board

        # Board display settings
        self.cell_size = 80
        self.images = {}

        self.canvas = tk.Canvas(self.window, width=8 * self.cell_size, height=8 * self.cell_size)
        self.canvas.pack()

        self.load_images()
        self.selected = None
        self.draw_board()

        # Left click to move
        self.canvas.bind("<Button-1>", self.handle_click)

        # Drag-to-move variables
        self.dragging = False
        self.drag_start = None

        # Right click for drag-based movement
        self.canvas.bind("<Button-3>", self.start_drag)
        self.canvas.bind("<B3-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-3>", self.end_drag)


    def start_drag(self, event):
        """Start drag operation on right-click"""
        if self.game_over:
            return
        row = event.y // self.cell_size
        col = event.x // self.cell_size
        piece = self.board.get_piece(row, col)

        if piece and piece.color == self.turn:
            self.drag_start = (row, col)
            self.dragging = True
            self.selected = (row, col)
            self.draw_board()  # Show legal moves


    def on_drag(self, event):
        """Update UI while dragging (no visual ghost here)"""
        if self.dragging:
            self.draw_board()


    def end_drag(self, event):
        """Complete drag-based move"""
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
            # Filter out illegal moves that leave king in check
            legal_moves = piece.get_legal_moves(self.board.board, (from_row, from_col), self.board.en_passant_target)
            legal_moves = [
                move for move in legal_moves
                if not self.board.move_puts_king_in_check((from_row, from_col), move)
            ]

            if (to_row, to_col) in legal_moves:
                result = self.board.move_piece((from_row, from_col), (to_row, to_col))

                # Handle promotion
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

                # Switch turn
                self.turn = 'black' if self.turn == 'white' else 'white'
                self.turn_label.config(text=f"{self.turn.capitalize()}'s Turn")

                # Check for draw by repetition
                if self.board.is_threefold_repetition():
                    self.draw_board()
                    tk.messagebox.showinfo("Game Over", "Draw by threefold repetition!")
                    self.game_over = True
                    return

                # Checkmate or stalemate
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
        """Load all piece images from assets folder"""
        pieces = ['K', 'Q', 'R', 'B', 'N', 'P']
        for color in ['w', 'b']:
            for p in pieces:
                filename = f"{color}{p}.png"
                path = os.path.join("assets", filename)
                image = Image.open(path).resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
                self.images[f"{color}{p}"] = ImageTk.PhotoImage(image)


    def highlight_square(self, row, col):
        """Draw red border around a square"""
        x0 = col * self.cell_size
        y0 = row * self.cell_size
        x1 = x0 + self.cell_size
        y1 = y0 + self.cell_size
        self.canvas.create_rectangle(x0, y0, x1, y1, outline='red', width=3)


    def handle_click(self, event):
        """Handle left-click for selecting and moving pieces"""
        if self.game_over:
            return

        row = event.y // self.cell_size
        col = event.x // self.cell_size

        if self.selected:
            piece = self.board.get_piece(*self.selected)
            if piece and piece.color == self.turn:
                legal_moves = piece.get_legal_moves(self.board.board, self.selected, self.board.en_passant_target)
                legal_moves = [
                    move for move in legal_moves
                    if not self.board.move_puts_king_in_check(self.selected, move)
                ]

                if (row, col) in legal_moves:
                    result = self.board.move_piece(self.selected, (row, col))

                    if result == True or (isinstance(result, tuple) and result[0] == 'promote'):
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
                        self.turn = 'black' if self.turn == 'white' else 'white'
                        self.turn_label.config(text=f"{self.turn.capitalize()}'s Turn")

                        # Draw repetition check
                        if self.board.is_threefold_repetition():
                            self.draw_board()
                            tk.messagebox.showinfo("Game Over", "Draw by threefold repetition!")
                            self.game_over = True
                            return

                        # Game end check
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
                self.selected = None
        else:
            piece = self.board.get_piece(row, col)
            if piece and piece.color == self.turn:
                self.selected = (row, col)

        self.draw_board()


    def ask_promotion_choice(self, color):
        """Dialog to ask user which piece to promote to"""
        choice_window = tk.Toplevel(self.window)
        choice_window.title("Choose Promotion")

        tk.Label(choice_window, text=f"{color.capitalize()} Pawn Promotion", font=("Arial", 14)).pack(pady=10)
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
        """Render board and pieces"""
        self.canvas.delete("all")
        colors = ["#EEEED2", "#769656"]
        king_pos = self.board.find_king(self.turn)
        in_check = self.board.is_in_check(self.turn)

        for row in range(8):
            for col in range(8):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                fill = colors[(row + col) % 2]

                if in_check and king_pos == (row, col):
                    fill = "#ffaaaa"  # Highlight checked king

                # Highlight legal moves
                if self.selected:
                    piece = self.board.get_piece(*self.selected)
                    if piece and piece.color == self.turn:
                        legal_moves = piece.get_legal_moves(self.board.board, self.selected, self.board.en_passant_target)
                        legal_moves = [
                            move for move in legal_moves
                            if not self.board.move_puts_king_in_check(self.selected, move)
                        ]
                        if (row, col) in legal_moves:
                            fill = "#ccffcc"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="black")

                piece = self.board.get_piece(row, col)
                if piece:
                    tag = piece.color[0] + piece.symbol
                    image = self.images.get(tag)
                    if image:
                        self.canvas.create_image(x1, y1, anchor='nw', image=image)

        # Draw red border for selected square
        if self.selected:
            row, col = self.selected
            self.highlight_square(row, col)


    def restart_game(self):
        """Reset the game state"""
        self.board = Board()
        self.turn = 'white'
        self.game_over = False
        self.turn_label.config(text="White's Turn")
        self.selected = None
        self.draw_board()


    def run(self):
        """Launch the GUI"""
        self.window.mainloop()
