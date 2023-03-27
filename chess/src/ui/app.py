from typing import Literal

from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Static, Header, DataTable, Label, TextLog

from ..chess import EPD, Chess
from ..epd import CoordT, find_piece, get_EPD, get_loc, get_piece
from ..game import FILE
from ..piece import notations
from .board import BoardArea, Box
from .messages import (NewGame, PieceDeselected, PieceMoved, PiecePromotion,
                       PieceSelected, SwitchPlayer)
from .screens import LoadPrevious, PawnPromotion, QuitGame, Welcome
from rich.text import Text
from rich.console import Group

class ActivePlayer(Static):
    app: "ChessApp"

    current_player = reactive(1, layout=True)

    def render(self):
        """Setup the stats."""
        if self.current_player == 1:
            return f"[white bold]{self.app.game.players[0].upper()}'s TURN!"
        else:
            return f"[white bold]{self.app.game.players[1].upper()}'s TURN!"


class PlayerScore(DataTable):
    app: "ChessApp"

    DEFAULT_CSS = """
    PlayerScore {
        border: tall $accent;
        height: 5;
        align: center middle;
        content-align: center middle;
        text-align: center;
    }
    """

    def on_refresh(self):
        scores = [0, 0]
        scores[0] = sum(notations.get_points(p) for p in self.app.game.captured[1])
        scores[1] = sum(notations.get_points(p) for p in self.app.game.captured[-1])
        names = self.app.game.players
        if len(self.columns) == 0:
            self.add_column("Player", key="player", width=10)
            self.add_column("Score", key="score", width=5)
        if len(self.rows) == 0:
            self.add_row(names[0], scores[0], key="player1")
            self.add_row(names[1], scores[1], key="player2")
        else:
            self.update_cell("player1", "player", names[0])
            self.update_cell("player1", "score", scores[0])
            self.update_cell("player2", "player", names[1])
            self.update_cell("player2", "score", scores[1])

    def on_mount(self):
        self.show_cursor = False
        self.on_refresh()

class CapturedPieces(Static):
    app: "ChessApp"

    DEFAULT_CSS = """
    CapturedPieces {
        border: solid $accent;
        text-align: left;
        color: $accent;
    }
    """

    pieces: 'reactive[list[int]]' = reactive([], layout=True)

    def __init__(self, player: int):
        self.player = player
        super().__init__()

    def render(self) -> RenderableType:
        symbols = []
        for piece in self.pieces:
            symbol = notations.get_symbol(piece)
            if not symbol:
                self.log.error(f"Symbol not found for piece: {piece}")
                continue
            symbols.append(symbol)
        return " ".join(symbols)

    def on_refresh(self):
        self.pieces = self.app.game.captured[self.player]
        self.refresh(layout=True)

    def on_mount(self):
        self.on_refresh()


class GameEPD(Static):
    app: "ChessApp"

    epd = reactive(EPD, layout=True)

    def render(self) -> RenderableType:
        epds = [self.epd]
        move = self.app.game.last_move
        while move is not None:
            epds.append(move.epd)
            move = move.next
        return "\n".join(epds)


class Stats(Widget):
    app: "ChessApp"

    def compose(self) -> ComposeResult:
        """Setup the stats."""
        yield ActivePlayer()
        yield PlayerScore()
        yield Label(f"Captured By {self.app.game.players[0]}:")
        yield CapturedPieces(1)
        yield Label(f"Captured By {self.app.game.players[1]}:")
        yield CapturedPieces(-1)
        # yield GameEPD()


class ChessApp(App):
    """Chess App."""

    CSS_PATH = "style.css"
    BINDINGS = [
        Binding("ctrl+u", "undo", "Undo Last Move"),
        Binding("ctrl+s", "save", "Save Progress"),
        Binding("ctrl+r", "update_board", "Refresh Board"),
        Binding("ctrl+q", "request_quit", "Quit Game"),
    ]
    selected_piece: "CoordT | None" = None
    piece_variant: Literal["outline", "filled"] = "filled"
    on_check: bool
    is_checkmated: bool
    is_stalemated: bool
    valid_moves: "dict[CoordT, list[CoordT]]"

    @property
    def game(self) -> Chess:
        if not hasattr(self, "_game"):
            self._game = Chess()
        return self._game

    @property
    def is_saved(self) -> bool:
        if not hasattr(self, "_saved"):
            try:
                new = Chess.load(FILE)
                self._saved = get_EPD(self.game) == get_EPD(new)
            except Exception:
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

    def action_update_board(self):
        for box in self.query(Box):
            box.piece = get_piece(self.game, box.coords)  # type: ignore
        for el in self.query(ActivePlayer):
            el.current_player = self.game.player
            break
        for el in self.query(GameEPD):
            el.epd = get_EPD(self.game)
            break
        try:
            self.query_one(PlayerScore).on_refresh()
            for widget in self.query(CapturedPieces):
                widget.on_refresh()
        except Exception:
            pass

    def action_get_state(self):
        (
            self.on_check,
            self.is_checkmated,
            self.is_stalemated,
            self.valid_moves,
        ) = self.game.get_game_state()

        self.query("Box.valid").remove_class("valid")
        self.query("Box.check").remove_class("check")
        self.query("Box.selected").remove_class("selected")

        if self.on_check:
            self.log(f"{self.game.player} is in check")
            king_id = notations.get_id("k") * self.game.player
            king_pos = find_piece(self.game, king_id)
            self.call_after_refresh(
                lambda: self.query_one(
                    f"#box-{get_loc(king_pos)}", Box
                ).add_class("check")
            )

    def on_piece_moved(self, message: PieceMoved):
        self.is_saved = False
        if self.game._is_pawn_promotion():
            self.push_screen(PawnPromotion())
        else:
            self.on_switch_player(SwitchPlayer(self))

    def action_undo(self):
        if self.game.undo_move():
            self.action_update_board()
            self.action_get_state()
        else:
            self.bell()
            self.log.warning("No moves to undo")

    def action_save(self):
        self.game.save()
        self.is_saved = True

    def on_switch_player(self, message: SwitchPlayer):
        self.game.switch_player()
        player = self.game.players[0 if self.game.player == 1 else 1]
        self.sub_title = f"Player {player}"
        self.action_update_board()
        self.action_get_state()

    def move_piece(self, coords: CoordT):
        """Move the selected piece to the given coords."""
        if self.selected_piece is None:
            return
        self.log(f"Current Player: {self.game.player}")
        piece = get_piece(self.game, self.selected_piece)
        from_loc = get_loc(self.selected_piece)
        to_loc = get_loc(coords)
        self.log(
            f"moving {notations.get_name(piece)} from {from_loc} to {to_loc}"
        )
        moved = self.game.move(from_loc, to_loc)
        self.log(f"Moved: {moved}")
        if moved:
            self.on_piece_moved(PieceMoved(self))

    def on_new_game(self, message: NewGame):
        self.is_saved = True
        player = self.game.players[0 if self.game.player == 1 else 1]
        self.sub_title = f"Player {player}"
        self.refresh(layout=True)
        self.action_get_state()

    def compose(self) -> ComposeResult:
        """Setup the app."""
        yield Header(name="Chess")
        yield Horizontal(BoardArea(), Stats(), id="main")
        yield Footer()

    def on_mount(self):
        """Handle mounting the app."""
        self.log("Chess App Started")
        if FILE.exists():
            try:
                old = Chess.load(FILE)
            except Exception:
                self.log.warning("Failed to load previous game")
                self.push_screen(Welcome())
            else:
                self.push_screen(LoadPrevious())
        else:
            self.push_screen(Welcome())
        self.action_get_state()

    def on_piece_promotion(self, message: PiecePromotion):
        self.game.promote_pawn(message.promotion)
        if self.selected_piece:
            self.on_piece_deselected(
                PieceDeselected(self, self.selected_piece)
            )
        self.on_switch_player(SwitchPlayer(self))
        self.call_after_refresh(
            self.on_piece_deselected, PieceDeselected(self, (0, 0))
        )
        self.call_after_refresh(self.action_update_board)

    def on_piece_selected(self, message: PieceSelected):
        """Handle a piece being selected."""
        if not isinstance(self.selected_piece, tuple):
            self.selected_piece = message.coords
            self.query_one(f"#box-{get_loc(message.coords)}", Box).select()
            for move in self.valid_moves.get(message.coords, []):
                self.log(f"Valid Move: {get_loc(move)}")
                self.query_one(f"#box-{get_loc(move)}", Box).add_class("valid")
        else:
            self.move_piece(message.coords)
            self.on_piece_deselected(
                PieceDeselected(self, self.selected_piece)
            )

    def on_piece_deselected(self, message: PieceDeselected):
        """Handle a piece being deselected."""
        self.selected_piece = None
        self.query("Box.valid").remove_class("valid")
        for box in self.query("Box.selected"):
            box.deselect()  # type: ignore


if __name__ == "__main__":
    app = ChessApp()
    app.run()
