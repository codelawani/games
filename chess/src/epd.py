from __future__ import annotations
"""
Extended Position Description

An Extended Position Description (EPD) is a format for representing
the state of a chess board. It depicts which player's turn it is,
the availability of castling and en passant moves, and more.


EPD Representation Of Pieces
----------------------------
[+] black pawn:   id = -1, char = p
[+] black knight: id = -2, char = n
[+] black bishop: id = -3, char = b
[+] black rook:   id = -4, char = r
[+] black queen:  id = -5, char = q
[+] black king:   id = -6, char = k

[+] white pawn:   id = 1, char = P
[+] white knight: id = 2, char = N
[+] white bishop: id = 3, char = B
[+] white rook:   id = 4, char = R
[+] white queen:  id = 5, char = Q
[+] white king:   id = 6, char = K
"""

"""
Extended Position Description (EPD) Format
------------------------------------------
The EPD format is a string that describes the state of a chess board.
It is composed of four parts, separated by spaces:

1. The board position, in Forsyth-Edwards Notation (FEN) format.
2. The active color. "w" means white moves next, "b" means black.
3. Castling availability. If neither side can castle, this is "-".
   Otherwise, this has one or more letters:
   - "K" (white can castle kingside)
   - "Q" (white can castle queenside)
   - "k" (black can castle kingside)
   - "q" (black can castle queenside)
4. En passant target square in algebraic notation. If there's no en passant
   target square, this is "-". If a pawn has just made a two-square move,
   this is the position "behind" the pawn. This is recorded regardless of
   whether there is a pawn in position to make an en passant capture.
5. Halfmove clock: This is the number of halfmoves since the last capture
   or pawn advance. This is used to determine if a draw can be claimed under
   the fifty-move rule.
6. Fullmove number: The number of the full move. It starts at 1, and is
   incremented after black's move.

Example:
	rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, NewType, Optional
from .piece import (
	notations
)

if TYPE_CHECKING:
	from .game import Game


EPDString = NewType("EPDString", str)
X = "abcdefgh"
Y = "87654321"

CoordT = tuple[int, int]
"The coordinates of a cell on a chess board => tuple[row, col]"

BoardT = list[list[int]]
"A 8x8 matrix representing a chess board"


def switch_p_move(p_move: Literal[-1, 1]) -> Literal[-1, 1]:
	"""Switch active player"""
	return p_move * (-1)


def get_piece(game: 'Game', coord: CoordT) -> int:
	"""
	Get a piece on the game board.

	Args:
		game: an instance of the chess game
		coord: the coordinates of the cell where the piece is
	Return:
		the ID of the chess piece
	"""
	return game.board[coord[1]][coord[0]]


def get_coords(loc: str) -> CoordT:
	"""
	Converts chess board location to a tuple of [x, y] coordinates.

	Args:
		loc: A string containing the chess board location in the format
			"a1", "b2", etc.

	Returns:
		tuple or None: A tuple containing the row and column indexes for the chess board,
		or None if the input is invalid.

	Example:
	>>> get_coords("e4")
	(3, 4)
	"""
	cord = tuple(loc)
	if (
		len(cord) != 2
		or str(cord[0]).lower() not in X
		or str(cord[1]) not in Y
	): raise ValueError("Invalid location")

	return X.index(str(cord[0]).lower()), Y.index(str(cord[1]))
	

def get_loc(coords: CoordT) -> str:
	"""
	Converts chess board coordinates to location.
	Inverse of `get_coords`.

	Args:
		coords: A sequence of [x, y] coordinates
	Returns:
		A string representing the board location in the format
		"a1", "b2"....

	Example:
	>>> get_loc((3, 4))
	'e5'
	"""

	return X[coords[0]] + Y[coords[1]]



def load_EPD(game: Game, epd_string: EPDString) -> bool:
	"""
	Load a chess position in Extended Position Description (EPD) format.

	This method takes an EPD string and creates the chess board accordingly.

	Args:
		game (state): The game's state
		epd_string (str): The EPD string to be loaded.

	Returns:
		(bool): True if epd_string was parsed else false
	"""
	data = epd_string.split(" ")
	if len(data) != 4:
		return False
	for r, row in enumerate(data[0].split("/")):
		c = 0
		for piece in row:
			if piece.isdigit():
				for i in range(int(piece)):
					game.board[r][c] = 0
					c += 1
			else:
				game.board[r][c] = notations.get_id(piece, True)
				c += 1
	game.player = 1 if data[1] == "w" else -1
	# castling
	for i, row in enumerate("KQkq"):
		game.castling[i] = int(row in data[2])
	game.en_passant = (
		None if data[3] == "-" else get_coords(data[3])
	)
	return True


def get_EPD(game: Game) -> EPDString:
	"""
	Converts the current chess board state into Extended Position Description (EPD) format.

	Returns:
		str: The EPD hash string representing the current state of the chess board.
	"""
	rows: 'list[str]' = []
	epd_string = ""
	for r, row in enumerate(game.board):
		result = ""
		empty = 0
		for piece in row:
			if piece == 0:
				empty += 1
			else:
				if empty > 0:
					result += str(empty)
				empty = 0
				result += notations.get_char(piece, True)
		if empty > 0:
			result += str(empty)
		rows.append(result)
	epd_string += "/".join(rows)
	epd_string += f" {'b' if game.player == 1 else 'b'} "
	epd_string += "".join((
		"K" if game.castling[0] == 1 else "",
		"Q" if game.castling[1] == 1 else "",
		"k" if game.castling[2] == 1 else "",
		"q" if game.castling[3] == 1 else ""
	)) or "-"
	epd_string += f" {'-' if game.en_passant == None else get_loc(game.en_passant)}"
	return EPDString(epd_string)
