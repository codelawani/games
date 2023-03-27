from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from src.piece import notations

from ..chess import Chess
from ..game import FILE
from .messages import NewGame, PiecePromotion

if TYPE_CHECKING:
    from .app import ChessApp

# Welcome Ascii Art
WELCOME = r"""
█░█░█ █▀▀ █░░ █▀▀ █▀█ █▀▄▀█ █▀▀ 
▀▄▀▄▀ ██▄ █▄▄ █▄▄ █▄█ █░▀░█ ██▄ 
"""

EXIT = r"""
███████╗██╗░░██╗██╗████████╗ ░█████╗░
██╔════╝╚██╗██╔╝██║╚══██╔══╝ ██╔══██╗
█████╗░░░╚███╔╝░██║░░░██║░░░ ╚═╝███╔╝
██╔══╝░░░██╔██╗░██║░░░██║░░░ ░░░╚══╝░
███████╗██╔╝╚██╗██║░░░██║░░░ ░░░██╗░░
╚══════╝╚═╝░░╚═╝╚═╝░░░╚═╝░░░ ░░░╚═╝░░
"""

CONTINUE = r"""
░█████╗░░█████╗░███╗░░██╗████████╗██╗███╗░░██╗██╗░░░██╗███████╗ ░█████╗░
██╔══██╗██╔══██╗████╗░██║╚══██╔══╝██║████╗░██║██║░░░██║██╔════╝ ██╔══██╗
██║░░╚═╝██║░░██║██╔██╗██║░░░██║░░░██║██╔██╗██║██║░░░██║█████╗░░ ╚═╝███╔╝
██║░░██╗██║░░██║██║╚████║░░░██║░░░██║██║╚████║██║░░░██║██╔══╝░░ ░░░╚══╝░
╚█████╔╝╚█████╔╝██║░╚███║░░░██║░░░██║██║░╚███║╚██████╔╝███████╗ ░░░██╗░░
░╚════╝░░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░╚═╝╚═╝░░╚══╝░╚═════╝░╚══════╝ ░░░╚═╝░░
"""

PROMOTION = r"""
██████╗░██████╗░░█████╗░███╗░░░███╗░█████╗░████████╗██╗░█████╗░███╗░░██╗██╗
██╔══██╗██╔══██╗██╔══██╗████╗░████║██╔══██╗╚══██╔══╝██║██╔══██╗████╗░██║██║
██████╔╝██████╔╝██║░░██║██╔████╔██║██║░░██║░░░██║░░░██║██║░░██║██╔██╗██║██║
██╔═══╝░██╔══██╗██║░░██║██║╚██╔╝██║██║░░██║░░░██║░░░██║██║░░██║██║╚████║╚═╝
██║░░░░░██║░░██║╚█████╔╝██║░╚═╝░██║╚█████╔╝░░░██║░░░██║╚█████╔╝██║░╚███║██╗
╚═╝░░░░░╚═╝░░╚═╝░╚════╝░╚═╝░░░░░╚═╝░╚════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚══╝╚═╝
"""


class LoadPrevious(Screen):
    app: "ChessApp"
    DEFAULT_CSS = """
	#dialog {
		grid-size: 2;
		grid-gutter: 1 2;
		padding: 1 2;
	}

	#dialog #question {
		column-span: 2;
		content-align: center bottom;
		width: 100%;
		height: 100%;
	}

	#dialog Button {
		width: 100%;
	}

	#title {
		color: $accent;
	}
	"""

    def compose(self) -> ComposeResult:
        yield Static(CONTINUE, id="title")
        yield Grid(
            Static(
                "A previous game was found. Would you like to continue it?",
                id="question",
            ),
            Button("Yes", variant="primary", id="yes"),
            Button("No", variant="error", id="no"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            game = Chess.load(FILE)
            self.app._game = game
            _ = self.app.on_new_game(NewGame(self.app))
            self.app.pop_screen()
        elif event.button.id == "no":
            FILE.write_text("")
            self.app.pop_screen()
            self.app.push_screen(Welcome())


class QuitGame(Screen):
    app: "ChessApp"
    DEFAULT_CSS = """
	#dialog {
		grid-size: 2;
		grid-gutter: 1 2;
		padding: 1 2;
	}

	#dialog #question {
		column-span: 2;
		content-align: center bottom;
		width: 100%;
		height: 100%;
	}

	#dialog Button {
		width: 100%;
	}

	#title {
		color: $warning;
	}

	#stay-container {
		column-span: 2;
		width: 100%;
		height: 100%;
		align: center middle;
	}

	#stay {
		background: $primary-lighten-3;
		width: 100%
	}
	"""

    def compose(self) -> ComposeResult:
        yield Static(EXIT, id="title")
        yield Grid(
            Static(
                "You're about to quit this game, your progress can be saved?",
                id="question",
            ),
            Container(Button("Don't Exit", id="stay"), id="stay-container"),
            Button("Save And Exit", variant="primary", id="save"),
            Button("Don't Save", variant="error", id="exit"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed):
        self.app.pop_screen()
        if event.button.id == "save":
            self.app.action_save()
            self.app.exit()
        elif event.button.id == "exit":
            self.app.exit()
        elif event.button.id == "stay":
            pass


class Welcome(Screen):
    app: "ChessApp"

    DEFAULT_CSS = """
	#welcome {
		grid-size: 2;
		grid-gutter: 1 2;
		padding: 1 2;
		align: center middle;
	}

	#start-container {
		column-span: 2;
		width: 100%;
		height: 100%;
		align: center middle;
	}

	#start {
		width: 100%;
		min-width: 10;
		max-width: 30;
		background: $primary-lighten-3;
	}

	#title {
		width: 100%;
		color: $primary;
	}

	#info {
		column-span: 2;
		color: $error;
		text-style: bold;
	}

	#question {
		column-span: 2;
		width: 100%;
		content-align: center middle;
	}

	#welcome Input {
		width: 100%;
	}

	#welcome Input.error {
		border: tall $error;
	}

	#welcome Input.error:focus {
		border: tall $accent;
	}
	"""

    def compose(self) -> ComposeResult:
        yield Static(WELCOME, id="title")
        yield Grid(
            Static("Enter the names of the players", id="question"),
            Static("Hey, I'm hidden", id="info"),
            Input(
                value="White", id="input1", placeholder="Enter Player 1's name"
            ),
            Input(
                value="Black", id="input2", placeholder="Enter Player 2's name"
            ),
            Container(
                Button("Start Game", variant="primary", id="start"),
                id="start-container",
            ),
            id="welcome",
        )

    def on_button_pressed(self, message: Button.Pressed):
        if message.button.id != "start":
            return
        player1 = self.query_one("#input1", Input)
        player2 = self.query_one("#input2", Input)
        info = self.query_one("#info", Static)
        name1 = player1.value
        name2 = player2.value
        if not (name1 or name2):
            self.app.bell()
            player1.add_class("error")
            player2.add_class("error")
            info.update("Please enter the names of the players")
            info.visible = True
            player1.focus()
            return
        elif not name1:
            self.app.bell()
            player1.add_class("error")
            info.update("Please enter the name of Player 1")
            info.visible = True
            player1.focus()
            return
        elif not name2:
            self.app.bell()
            player2.add_class("error")
            info.update("Please enter the name of Player 2")
            info.visible = True
            player2.focus()
            return
        if name1 == name2:
            self.app.bell()
            player1.add_class("error")
            player2.add_class("error")
            info.update("The names of the players must be different")
            info.visible = True
            player1.focus()
            return
        game = Chess()
        game.players = [name1, name2]
        self.app._game = game
        _ = self.app.on_new_game(NewGame(self.app))
        self.app.pop_screen()

    def on_mount(self):
        Info = self.query_one("#info", Static)
        Info.visible = False

    def on_input_changed(self, message: Input.Changed):
        if message.input.id == "input1":
            message.input.remove_class("error")
        elif message.input.id == "input2":
            message.input.remove_class("error")
        Info = self.query_one("#info", Static)
        Info.visible = False


class PawnPromotion(Screen):
    app: "ChessApp"
    DEFAULT_CSS = """
	#dialog {
		grid-size: 2;
		grid-gutter: 1 2;
		padding: 1 2;
		align: center middle;
		width: 100%;
		height: 80%;
	}

	#title {
		column-span: 2;
		width: 100%;
		color: $primary;
	}

	#question {
		column-span: 2;
		width: 100%;
		content-align: center middle;
	}

	Horizontal {
		column-span: 2;
		width: 100%;
		height: 80%;
		align: center middle;
	}

	Horizontal Button {
		width: 50%;
	}

	#pieces Button {
		width: 20%;
		margin: 2;
	}
	"""

    def compose(self) -> ComposeResult:
        yield Static(PROMOTION, id="title")
        with Grid(id="dialog"):
            yield Static(
                "Choose a piece to promote your pawn to", id="question"
            )
            with Horizontal():
                yield Button("Skip Promotion", variant="error", id="skip")
            with Horizontal(id="pieces"):
                yield Button("Queen", variant="primary", id="queen")
                yield Button("Rook", variant="primary", id="rook")
                yield Button("Bishop", variant="primary", id="bishop")
                yield Button("Knight", variant="primary", id="knight")

    def on_button_pressed(self, message: Button.Pressed):
        piece = None
        if message.button.id == "skip":
            piece = None
        elif message.button.id == "queen":
            piece = notations.get_id("q")
        elif message.button.id == "rook":
            piece = notations.get_id("r")
        elif message.button.id == "bishop":
            piece = notations.get_id("b")
        elif message.button.id == "knight":
            piece = notations.get_id("n")
        if piece is not None:
            _ = self.app.on_piece_promotion(PiecePromotion(self, piece))
        self.app.pop_screen()
