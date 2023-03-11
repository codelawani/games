"""
This module contains functions that help to work EPD hashes.

An Extended Position Description (EPD) is a format for representing
the state of a chess board. It depicts which player's turn it is,
the availability of castling and en passant moves, and more


def load_epd(epd_string): create a 8x8 board from an EPD string.
"""
from curses.ascii import isupper
from dataclasses import dataclass, field
from typing import Literal, NewType, Optional
from piece import (
	notations
)


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

@dataclass
class Game:
	"""
	represents the state of a chess game
	"""
	initial_pos: EPDString
	"game initial position"

	board: list[list[int]] = field(default_factory=
		lambda: [[0 for x in range(8)] for y in range(8)])
	"8x8 chess board"

	p_move: Literal[1, -1] = 1
	"current player move. black(-1), white(1)"

	castling: list[int] = field(default_factory=lambda: [1, 1, 1, 1])
	"castling control"

	en_passant: Optional[CoordT] = None
	"En passant control"

	epd_hash: dict[EPDString, int] = field(default_factory=dict)
	"A table that keeps track of all EPD hashes of the game"

	log: list[str] = field(default_factory=list)
	"chess game logs"


def get_coords(loc: str) -> Optional[CoordT]:
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
	): return None

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
	for x, rank in enumerate(data[0].split("/")):
		y = 0
		for p in rank:
			if p.isdigit():
				for i in range(int(p)):
					game.board[x][y] = 0
					y += 1
			else:
				game.board[x][y] = notations.get_id(p, True)
				y += 1
	game.p_move = 1 if data[1] == "w" else -1
	if "K" in data[2]:
		game.castling[0] = 1
	else:
		game.castling[0] = 0
	if "Q" in data[2]:
		game.castling[1] = 1
	else:
		game.castling[1] = 0
	if "k" in data[2]:
		game.castling[2] = 1
	else:
		game.castling[2] = 0
	if "q" in data[2]:
		game.castling[3] = 1
	else:
		game.castling[3] = 0
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
	result = ""
	for i, row in enumerate(game.board):
		e_count = 0
		for piece in row:
			if piece == 0:
				e_count += 1
			else:
				if e_count > 0:
					result += str(e_count)
				e_count = 0
				p_notation = notations.get_char(piece)
				result += p_notation if piece < 0 else p_notation.upper()
		if e_count > 0:
			result += str(e_count)
		if i < 7:
			result += "/"
	if game.p_move == -1:
		result += " w"
	else:
		result += " b"
	result += " "
	if sum(game.castling) == 0:
		result += "-"
	else:
		if game.castling[0] == 1:
			result += "K"
		if game.castling[1] == 1:
			result += "Q"
		if game.castling[2] == 1:
			result += "k"
		if game.castling[3] == 1:
			result += "q"
	result += " "
	if game.en_passant == None:
		result += "-"
	else:
		result += get_loc(game.en_passant)
	return EPDString(result)