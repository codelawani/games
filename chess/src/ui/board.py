from itertools import cycle
import pickle
from typing import TYPE_CHECKING, Literal, Optional
from textual.widget import Widget
from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message, MessageTarget
from ..epd import CoordT, get_loc, X, Y, get_piece
from ..game import Game
from ..piece import notations
from rich.text import Text

if TYPE_CHECKING:
	from .app import ChessApp


class Left(Widget):
	"""Left board Indicators."""

	def compose(self) -> ComposeResult:
		"""Setup left indicators."""
		for char in Y:
			yield Static(char, classes="indicator")


class Bottom(Widget):
	"""Bottom board indicators."""

	def compose(self) -> ComposeResult:
		"""Setup bottom indicators."""
		for char in  X:
			yield Static(char, classes="indicator")


class Box(Static):
	"""A box on the chess board."""
	app: 'ChessApp'


	piece: reactive[Text] = reactive(Text(''))

	def __init__(
		self, coords: CoordT,
		variant: Literal['light', 'dark']):
		self.coords = coords
		location = get_loc(coords)
		self.variant = variant
		super().__init__(self.piece, classes=variant, id=f"box-{location}")

	def is_empty(self) -> bool:
		"""Check if this box is empty."""
		return not self.piece

	def on_mount(self):
		"""Handle mounting this box."""
		self.piece = get_piece(self.app.game, self.coords) # type: ignore

	def render(self) -> Text:
		"""Render this box."""
		return self.piece # type: ignore
	
	def validate_piece(self, piece_id: int):
		symbol = notations.get_symbol(piece_id)
		color = "black" if piece_id < 0 else "white"
		return Text(symbol, style=color)

	def select(self):
		"""Select this box."""
		for box in self.app.query(Box):
			box.deselect()
		self.add_class("selected")
		player = self.app.game.player
		piece = get_piece(self.app.game, self.coords)
		self.log(f"selecting box {get_loc(self.coords)}")
		self.log(f"piece on selected box: {'white' if piece > 1 else 'black'} {notations.get_name(piece)}")
		piece_type = notations.get_class(piece)
		valid_moves = piece_type.moves(self.app.game, player, self.coords)
		for move in valid_moves:
			self.app.query_one(f"#box-{get_loc(move)}", Box).add_class("valid")
		self.app.selected_piece = self.coords

	def deselect(self):
		"""Deselect this box."""
		if not self.has_class("selected"):
			return
		piece = get_piece(self.app.game, self.coords)
		self.log(f"deselecting box {get_loc(self.coords)!r}")
		self.log(f"piece on deselected box: {'white' if piece > 1 else 'black'} {notations.get_name(piece)}")
		self.remove_class("selected")
		self.app.query("Box.valid").remove_class("valid")
		self.app.selected_piece = None

	def on_click(self):
		"""Handle a click on this box."""
		if self.has_class("selected"):
			return self.deselect()
		piece = get_piece(self.app.game, self.coords)
		player = self.app.game.player
		# if the current player selects his piece again,
		# the new piece selected should act as the new
		# .selected piece
		if (selected:= self.app.selected_piece):
			# a box is already selected
			if piece * player > 0:
				# the current player owns the piece in this box
				# select this box inplace of the previously
				# selected box
				box_id = "#box-" + get_loc(selected)
				self.app.query_one(box_id, Box).deselect()
				self.select()
			elif self.has_class("valid"):
				# the player is trying to move to this box
				# it's a valid move!
				self.app.move_piece(self.coords)
				box_id = "#box-" + get_loc(selected)
				self.app.query_one(box_id, Box).deselect()
			else:
				self.app.bell()
				self.log.error("Clicked on wrong box")
		elif not self.is_empty():
			if piece * player > 0:
				# the piece belongs to the current player
				self.select()
			else:
				self.app.bell()
				if piece:
					self.log.error("Clicked on opponent's piece")
				else:
					self.log.error("Clicked on empty box")
		else:
			self.app.bell()
			self.log.error("Clicked on empty box")
			return self.app.bell()


class Board(Widget):
	"""The chess board."""

	def compose(self) -> ComposeResult:
		game: Game = self.app.game # type: ignore
		style = cycle(("light", "dark"))
		for row in range(8):
			for col in range(8):
				yield Box((col, row), variant=next(style))
			next(style)


class BoardArea(Widget):
	"""The board with it's immediate surrounding components."""

	def compose(self) -> ComposeResult:
		"""Setup the board area."""
		yield Left(id="left")
		yield Board(id="board")
		yield Static("")
		yield Bottom(id="bottom")
