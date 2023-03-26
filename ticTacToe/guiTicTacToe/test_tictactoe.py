#!/usr/bin/python3
import unittest
import tkinter as tk
from tictactoe import TicTacToe


class TestTicTacToe(unittest.TestCase):
    def test_initialization(self):
        root = tk.Tk()
        game = TicTacToe(root)
        self.assertEqual(game.board, [" "]*9)
        self.assertEqual(game.current_player, "X")
        self.assertEqual(game.game_over, False)


if __name__ == '__main__':
    unittest.main()
