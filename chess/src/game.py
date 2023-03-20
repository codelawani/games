"""
This module contains a base class that holds the game's state.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Optional
from typing_extensions import Self

import json
from pathlib import Path
from datetime import datetime

from .epd import get_EPD, load_EPD
from .piece import notations

if TYPE_CHECKING:
	from .epd import EPDString, CoordT
	from .piece import PlayerT

DIR = Path(__file__).parent.joinpath("data")
DIR.mkdir(exist_ok=True)
FILE = DIR.joinpath("game.json")
FILE.touch()


def create_board() -> list[list[int]]:
	"""Create a chess board."""
	return [[0 for x in range(8)] for y in range(8)]


@dataclass
class Move:
	"""A linked list that holds the game's move history."""

	player: int
	"player who made the move"

	from_loc: 'CoordT'
	"move origin"

	to_loc: 'CoordT'
	"move destination"

	piece: int
	"piece that was moved"

	log: list[str]
	"chess game logs at the time of the move"

	epd: 'EPDString'
	"EPD hash of the game's state before the move"

	next: Optional[Move] = None

	def serialize(self) -> dict:
		"""
		Serialize the move into a dictionary.

		Returns:
			dict: The serialized move.
		"""
		return {
			"player": self.player,
			"from_loc": self.from_loc,
			"to_loc": self.to_loc,
			"piece": self.piece,
			"log": self.log,
			"epd": self.epd,
			"next": self.next.serialize() if self.next else None
		}

	@classmethod
	def deserialize(cls, data: dict) -> Move:
		"""
		Deserialize a move from a dictionary.

		Args:
			data (dict): The serialized move.
		Returns:
			Move: The deserialized move.
		"""
		return cls(
			player=data["player"],
			from_loc=data["from_loc"],
			to_loc=data["to_loc"],
			piece=data["piece"],
			log=data["log"],
			epd=data["epd"],
			next=cls.deserialize(data["next"]) if data["next"] else None
		)


@dataclass
class Game:
	"""This class holds the game's state."""
	"""
	represents the state of a chess game
	"""
	initial_pos: 'EPDString'
	"game initial position"

	players: list[str] = field(default_factory=lambda:["White", "Black"])

	board: list[list[int]] = field(default_factory=create_board)
	"8x8 chess board"

	castling: list[int] = field(default_factory=lambda: [1, 1, 1, 1])
	"castling control"

	en_passant: Optional[CoordT] = None
	"En passant control"

	epd_hash: dict['EPDString', int] = field(default_factory=dict)
	"A table that keeps track of all EPD hashes of the game"

	log: list[str] = field(default_factory=list)
	"chess game logs"

	last_move: Optional[Move] = None

	def switch_player(self):
		"""Switch player's color."""
		self.player *= -1

	@property
	def player(self) -> PlayerT:
		"""Return the player's color."""
		return self._p_move # type: ignore
	
	@player.setter
	def player(self, value: PlayerT):
		"""Set the player's color."""
		if value not in [-1, 1]:
			raise ValueError("Invalid player color.")
		self._p_move = value

	def add_move_history(self, curr_pos: 'CoordT', new_pos: 'CoordT',
												   piece: int):
		"""Add a move to the move history."""
		self.last_move = Move(
			self.player,
			curr_pos,
			new_pos,
			piece,
			self.log.copy(),
			get_EPD(self),
			self.last_move
		)

	def undo_move(self):
		"""Undo the last move."""
		if self.last_move is None:
			return False
		load_EPD(self, self.last_move.epd)
		self.last_move = self.last_move.next
		return True

	def log_move(
		self, part, cur_cord, next_cord, cur_pos, next_pos, n_part=None
	):
		"""
		Logs the move made by the player into the game's move log.

		Args:
			part (int): The integer value of the piece that is being moved.
			cur_cord (str): The current coordinates of the piece in algebraic notation (e.g. "a1", "h8").
			next_cord (str): The coordinates of the square that the piece is moving to in algebraic notation.
			cur_pos (tuple): The current position of the piece on the board as a tuple (x, y) starting from (0,0).
			next_pos (tuple): The position of the square that the piece is moving to on the board as a tuple (x, y) starting from (0,0).
			n_part (int): The integer value of the promoted piece, if any (optional).
		Returns:
			None
		"""
		# to remove ambiguity where multiple pieces could make the move
		# add starting identifier after piece notation ex Rab8
		if part == 6 * self.player and next_pos[0] - cur_pos[0] == 2:
			move = "0-0"
		elif part == 6 * self.player and next_pos[0] - cur_pos[0] == -2:
			move = "0-0-0"
		elif part == 1 * self.player and n_part != None:
			move = f"{str(next_cord).lower()}={str(n_part).upper()}"
		else:
			move = notations.get_char(part)
			if self.board[next_pos[1]][next_pos[0]] != 0 or (
				next_pos == self.en_passant and (part == 1 or part == -1)
			):  # Check if there is a capture
				move += "x" if move != "" else str(cur_cord)[0] + "x"
			move += str(next_cord).lower()
		self.log.append(move)

	def serialize(self):
		"""
		Serialize the game into a dictionary.

		Returns:
			dict: The serialized game.
		"""
		return {
			"initial_pos": self.initial_pos,
			"players": self.players,
			"epd_hash": self.epd_hash,
			"epd": get_EPD(self),
			"log": self.log,
			"last_move": self.last_move.serialize() if self.last_move else None
		}

	@classmethod
	def deserialize(cls, data: dict) -> Game:
		"""
		Deserialize a game from a dictionary.

		Args:
			data (dict): The serialized game.
		Returns:
			Game: The deserialized game.
		"""
		new = cls(data['epd'])
		print(f"player: {new.player}")
		new.players = data["players"]
		new.log = data['log']
		new.last_move = Move.deserialize(data["last_move"]) if data["last_move"] else None
		
		return new

	def save(self):
		"""Save the game to a file."""
		with FILE.open("w") as f:
			json.dump(self.serialize(), f)

	@classmethod
	def load(cls, file: Path) -> Self:
		"""Load a game from a file."""
		with open(file, "r") as f:
			return cls.deserialize(json.load(f))