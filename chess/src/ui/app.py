from typing import Literal
from textual.containers import (
	Vertical, Horizontal
)
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.widget import Widget
from textual.reactive import reactive
from rich.table import Table
from rich import box
from rich.panel import Panel
from itertools import cycle
from rich.segment import Segment
from ..chess import Chess

from .board import Board, BoardArea, Box
from ..epd import get_loc, CoordT, get_piece
from ..piece import notations


class Stats(Widget):
	def compose(self) -> ComposeResult:
		"""Setup the stats."""
		yield Static("Stats")


class InputArea(Widget):
	def compose(self) -> ComposeResult:
		"""Setup the input area."""
		yield Static("Input")


class InfoArea(Widget):
	def compose(self) -> ComposeResult:
		"""Setup the info area."""
		yield Static("Info")


class ChessApp(App):
	"""Chess App."""

	CSS_PATH = "style.css"
	selected_piece: "CoordT | None" = None

	@property
	def game(self) -> Chess:
		if not hasattr(self, "_game"):
			self._game = Chess()
		return self._game

	def move_piece(self, coords: CoordT):
		"""Move the selected piece to the given coords."""
		if self.selected_piece is None:
			return
		piece = get_piece(self.game, self.selected_piece)
		from_loc = get_loc(self.selected_piece)
		to_loc = get_loc(coords)
		self.log(f"moving {notations.get_name(piece)} from {from_loc} to {to_loc}")
		self.game.move(from_loc, to_loc)
		for box in self.query(Box):
			box.piece = get_piece(self.game, box.coords) # type: ignore
		self.selected_piece = None
		self.game.switch_player()
		self.log(self.game.board)

	def compose(self) -> ComposeResult:
		"""Setup the app."""
		yield Header(name="Chess")
		yield InfoArea()
		yield BoardArea()
		yield Stats()
		yield InputArea()
		yield Footer()

	def on_mount(self):
		"""Handle mounting the app."""
		self.log("Chess App Started")
		# self.log(self.game)


if __name__ == "__main__":
	app = ChessApp()
	app.run()

