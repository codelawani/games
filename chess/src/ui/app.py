from typing import Literal
from textual.containers import (
	Vertical, Horizontal, Grid
)
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button
from textual.widget import Widget
from textual.reactive import reactive
from rich.table import Table
from rich import box
from rich.panel import Panel
from textual.binding import Binding
from itertools import cycle
from rich.segment import Segment
from ..chess import Chess, EPD
from rich.console import RenderableType
from textual.screen import Screen
from .board import Board, BoardArea, Box
from ..epd import EPDString, find_piece, get_EPD, get_loc, CoordT, get_piece
from ..piece import notations
from ..game import FILE


class ActivePlayer(Static):
	app: 'ChessApp'

	current_player = reactive(1, layout=True)

	def render(self):
		"""Setup the stats."""
		if self.current_player == 1:
			return f"[white bold]{self.app.game.players[0].upper()}'s TURN!"
		else:
			return f"[white bold]{self.app.game.players[1].upper()}'s TURN!"


class GameEPD(Static):
	app: 'ChessApp'

	epd = reactive(EPD, layout=True)

	def render(self) -> RenderableType:
		epds = [self.epd]
		move = self.app.game.last_move
		while move is not None:
			epds.append(move.epd)
			move = move.next
		
		return "\n".join(epds)


class LoadPrevious(Screen):
	app: 'ChessApp'

	def compose(self) -> ComposeResult:
		yield Grid(
			Static("A previous game was found. Would you like to load it?", id="question"),
			Button("Yes", variant="primary", id="yes"),
			Button("No", variant="error", id="no"),
			id="dialog"
		)
	
	def on_button_pressed(self, event: Button.Pressed):
		if event.button.id == "yes":
			game = Chess.load(FILE)
			self.app._game = game
			self.app.is_saved = True
		elif event.button.id == "no":
			FILE.write_text('')
		self.app.pop_screen()


class QuitGame(Screen):
	app: 'ChessApp'

	def compose(self) -> ComposeResult:
		yield Grid(
			Static("You're about to quit this game, do yo want to save your progress?", id="question"),
			Button("Yes", variant="primary", id="yes"),
			Button("No", variant="error", id="no"),
			id="dialog"
		)
	
	def on_button_pressed(self, event: Button.Pressed):
		if event.button.id == "yes":
			self.app.action_save()
		elif event.button.id == "no":
			FILE.write_text('')
		self.app.pop_screen()
		self.app.exit()


class Stats(Widget):
	app: 'ChessApp'


	def compose(self) -> ComposeResult:
		"""Setup the stats."""
		yield ActivePlayer()
		yield GameEPD()

class ChessApp(App):
	"""Chess App."""

	CSS_PATH = "style.css"
	BINDINGS = [
		Binding("ctrl+u", "undo", "Undo Last Move"),
		Binding("ctrl+s", "save", "Save Progress"),
		Binding("ctrl+r", "refresh", "Refresh Board"),
		Binding("ctrl+q", "request_quit", "Quit Game"),
	]
	selected_piece: "CoordT | None" = None

	@property
	def game(self) -> Chess:
		if not hasattr(self, "_game"):
			self._game = Chess()
		return self._game

	@property
	def is_saved(self) -> bool:
		if not hasattr(self, "_saved"):
			if len(FILE.read_text()) < 5:
				new = Chess.load(FILE)
				self._saved = get_EPD(self.game) == get_EPD(new)
			else:
				self._saved = self.game.last_move is None
		return self._saved

	@is_saved.setter
	def is_saved(self, value: bool):
		self._saved = value

	def action_request_quit(self):
		if not self.is_saved:
			self.push_screen(QuitGame())
		else:
			self.exit()

	def perform_refresh(self):
		for box in self.query(Box):
			box.piece = get_piece(self.game, box.coords) # type: ignore
		for el in self.query(ActivePlayer):
			el.current_player = self.game.player
			break
		for el in self.query(GameEPD):
			el.epd = get_EPD(self.game)
			break

	def action_undo(self):
		if self.game.undo_move():
			self.perform_refresh()
		else:
			self.bell()
			self.log.warning("No moves to undo")

	def action_refresh(self):
		self.perform_refresh()

	def action_save(self):
		self.game.save()
		self.is_saved = True

	def move_piece(self, coords: CoordT):
		"""Move the selected piece to the given coords."""
		if self.selected_piece is None:
			return
		piece = get_piece(self.game, self.selected_piece)
		from_loc = get_loc(self.selected_piece)
		to_loc = get_loc(coords)
		self.log(f"moving {notations.get_name(piece)} from {from_loc} to {to_loc}")
		moved = self.game.move(from_loc, to_loc)
		self.log(f"Moved: {moved}")
		self.game.switch_player()
		self.perform_refresh()
		self.selected_piece = None
		is_check, escape = self.game._on_check()
		self.query("Box.check").remove_class("check")
		if is_check:
			self.log(f"{self.game.player} is in check")
			king_id = notations.get_id('k') * self.game.player
			king_pos = find_piece(self.game, king_id)
			self.query_one(f"#box-{get_loc(king_pos)}", Box).add_class("check")
		self.is_saved = False

	def compose(self) -> ComposeResult:
		"""Setup the app."""
		# yield Header(name="Chess")
		yield Horizontal(
			BoardArea(),
			Stats(),
			id="main"
		)
		yield Footer()

	def on_mount(self):
		"""Handle mounting the app."""
		self.log("Chess App Started")
		if FILE.exists():
			if len(FILE.read_text()) > 5:
				self.push_screen(LoadPrevious(id="load_screen"))
			if not hasattr(self, "_game"):
				self._game = Chess()
		# self.game.possible_board_moves()
		# self.log(self.game)


if __name__ == "__main__":
	app = ChessApp()
	app.run()

