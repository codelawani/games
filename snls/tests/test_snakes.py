#!/usr/bin/python3
import snakes as s
import unittest


class TestSnakes(unittest.TestCase):
    def test_prepare_board(self):
        print("hi")
        board = s.prepare_board()
        players = s.create_player_dict(2)
        colors = s.assign_bead_colors(players)
        s.display_board(players, board, colors)
