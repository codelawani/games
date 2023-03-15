#!/usr/bin/python3
import tkinter as tk
from tkinter import messagebox
import pydoc
import sys

HELP = """
Welcome to Tic Tac Toe!

To play, simply click on any cell on the board to place your symbol (X or O).
The first player to get three in a row (horizontal, vertical, or diagonal) wins the game.

To reset the game, click the "Reset" button.

Have fun!
"""


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")

        # Initialize game state
        self.board = [" "]*9
        self.current_player = "X"
        self.game_over = False

        # Create game board
        self.board_frame = tk.Frame(
            root, highlightbackground="blue")

        self.board_frame.pack()

        self.board_buttons = []
        for i in range(9):
            button = tk.Button(self.board_frame, text="", width=6, height=3, font=("Helvetica", 20),
                               command=lambda i=i: self.make_move(i))
            button.grid(row=i//3, column=i % 3)
            self.board_buttons.append(button)

        # Create reset button
        self.reset_button = tk.Button(
            root, text="Reset", width=10, command=self.reset_game)
        self.reset_button.pack(pady=10)

    def make_move(self, position):
        if not self.game_over and self.board[position] == " ":
            self.board[position] = self.current_player
            self.board_buttons[position].config(text=self.current_player)
            if self.check_win(self.current_player):
                messagebox.showinfo(
                    "Tic Tac Toe", f"Player {self.current_player} wins!")
                self.game_over = True
            elif self.check_draw():
                messagebox.showinfo("Tic Tac Toe", "It's a draw!")
                self.game_over = True
            self.current_player = "O" if self.current_player == "X" else "X"

    def check_win(self, player):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal wins
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical wins
            [0, 4, 8], [2, 4, 6]  # Diagonal wins
        ]
        for condition in win_conditions:
            if all(self.board[i] == player for i in condition):
                return True
        return False

    def check_draw(self):
        return all(cell != " " for cell in self.board)

    def reset_game(self):
        self.board = [" "]*9
        for button in self.board_buttons:
            button.config(text="")
        self.current_player = "X"
        self.game_over = False


if __name__ == '__main__':
    if sys.argv[1:] and sys.argv[1] in ("-h", "help"):
        print(HELP)
        exit(0)
    root = tk.Tk()
    TicTacToe(root)
    root.mainloop()
