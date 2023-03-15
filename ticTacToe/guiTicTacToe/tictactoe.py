#!/usr/bin/python3
import tkinter as tk
from tkinter import messagebox
import sys

HELP = """
Welcome to Tic Tac Toe!

To play, simply click on any cell on the board to place your symbol (X or O).
The first player to get three in a row (horizontal, vertical, or diagonal) wins the game.

To reset the game, click the "Reset" button.

Have fun!
"""


class CustomMessageBox(tk.Toplevel):
    def __init__(self, title, message, bg_color, fg_color):
        super().__init__()

        # Set the window title
        self.title_bg_color = "#f25f4c"
        self.title(" " * 20)
        self.title(title)
        self.configure(background='#a7a9be')

        # Create a frame to hold the message text
        frame = tk.Frame(self, bg=bg_color)
        frame.pack(padx=10, pady=10)

        # Create a label to display the message text
        label = tk.Label(frame, text=message, bg=bg_color, fg=fg_color,
                         font=('Arial', 24))
        label.pack(padx=10, pady=10)

        # Add a button to close the window
        button = tk.Button(self, text="OK", background="#f25f4c", activebackground="#e53170", width=10, command=self.destroy,
                           relief='flat', borderwidth=0)
        button.pack(padx=10, pady=10)


class TicTacToe:
    def __init__(self, root):
        """
        Initialize the TicTacToe game with a blank board and X as the starting player.

        Args:
        - root (Tk): The root window for the game.
        """

        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.configure(background='#a7a9be')
        # Initialize game state
        self.board = [" "]*9
        self.current_player = "X"
        self.game_over = False

        # Create game board
        self.board_frame = tk.Frame(
            root, background="blue", )

        self.board_frame.pack()

        self.board_buttons = []
        for i in range(9):
            button = tk.Button(self.board_frame, text="", width=6, height=3, font=("Helvetica", 20),
                               background="#0f0e17", fg="#fffffe", activebackground="#ff8906", highlightbackground="#a7a9be", command=lambda i=i: self.make_move(i))
            button.grid(row=i//3, column=i % 3)
            self.board_buttons.append(button)

        # Create reset button
        self.reset_button = tk.Button(
            root, text="Restart", width=10, background="#f25f4c", activebackground="#e53170", command=self.reset_game)
        self.reset_button.pack(pady=10)

    def make_move(self, position):
        """
        Updates the game board and checks for a win or draw when a move is made.

        Args:
        - position (int): The position of the move made.

        Returns:
        None
        """
        if not self.game_over and self.board[position] == " ":
            self.board[position] = self.current_player
            self.board_buttons[position].config(text=self.current_player)
            if self.check_win(self.current_player):
                # Create a new custom message box
                message_box = CustomMessageBox("Tic Tac Toe", f"Player {self.current_player} wins!",
                                               bg_color="#0f0e17", fg_color="#ff8906")
                # Make the message box modal
                message_box.grab_set()
                message_box.focus_set()

                # Wait for the message box to close
                message_box.wait_window()

                # Set the game over flag
                self.game_over = True
            elif self.check_draw():
                # Create a new custom message box
                message_box = CustomMessageBox("Tic Tac Toe", "It's a draw!",
                                               bg_color="#0f0e17", fg_color="#ff8906")
                # Make the message box modal
                message_box.grab_set()
                message_box.focus_set()

                # Wait for the message box to close
                message_box.wait_window()

                # Set the game over flag
                self.game_over = True
            self.current_player = "O" if self.current_player == "X" else "X"

    def check_win(self, player):
        """
        Checks if the specified player has won the game.

        Args:
        - player (str): The player to check for a win.

        Returns:
        - bool: True if the player has won, False otherwise.
        """
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
        """
        Checks if the game has ended in a draw.

        Returns:
        - bool: True if the game has ended in a draw, False otherwise.
        """
        return all(cell != " " for cell in self.board)

    def reset_game(self):
        """
        Resets the game board to a blank state.

        Returns:
        None
        """
        self.board = [" "]*9
        for button in self.board_buttons:
            button.config(text="")
        self.current_player = "X"
        self.game_over = False


if __name__ == '__main__':
    # sys.argv[1:] generates an empty list
    # if no arguments are passed
    if sys.argv[1:] and sys.argv[1] in ("-h", "help"):
        print(HELP)
        exit(0)
    root = tk.Tk()
    TicTacToe(root)
    root.mainloop()
