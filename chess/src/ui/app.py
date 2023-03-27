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
                       PieceSelected, Refresh, SwitchPlayer)
from .screens import GameOver, LoadPrevious, PawnPromotion, QuitGame, Welcome
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
    
    def on_refresh(self, message: Refresh):
        message.stop()
        self.current_player = self.app.game.player



class PlayerScore(DataTable):
    app: "ChessApp"

    DEFAULT_CSS = """
    PlayerScore {
        border: tall $accent;
        height: 5;
        align: center middle;
        content-align: center middle;
        text-align: center;
        margin-bottom: 2;
        margin-top: 1;
    }
    """

    def on_refresh(self, message: Refresh):
        message.stop()
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
        self.post_message(Refresh())

class CapturedPieces(Static):
    app: "ChessApp"

    DEFAULT_CSS = """
    CapturedPieces {
        border: round $accent;
        text-align: left;
        color: $accent;
        border-title-align: center;
        margin-bottom: 1;
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

    def on_refresh(self, message: Refresh):
        message.stop()
        self.pieces = self.app.game.captured[self.player]
        self.refresh(layout=True)

    def on_mount(self):
        self.border_title = self.app.game.players[0 if self.player == 1 else 1]
        self.post_message(Refresh())

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

    DEFAULT_CSS = """
    Stats Vertical {
        border: blank $accent;
        border-title-align: center;
        width: 100%;
        height: auto;
        margin-bottom: 1;
        padding-top: 2;
    }
        """

    def compose(self) -> ComposeResult:
        """Setup the stats."""
        yield ActivePlayer()
        yield PlayerScore()
        with Vertical():
            yield CapturedPieces(1)
            yield CapturedPieces(-1)
        # yield GameEPD()

    def on_mount(self):
        try:
            vert = self.query_one(Vertical)
            vert.border_title = "Captured Pieces"
        except Exception:
            pass
    
    def on_refresh(self, message: Refresh):
        if self.query_one(ActivePlayer).post_message(Refresh()):
            self.log.info("Refreshed ActivePlayer")
        if self.query_one(PlayerScore).post_message(Refresh()):
            self.log.info("Refreshed PlayerScore")
        for node in self.query(CapturedPieces):
            if node.post_message(Refresh()):
                self.log.info("Refreshed CapturedPieces")
        message.stop()

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
        def update_stats():
            try:
                refreshed = self.query_one(Stats).post_message(Refresh())
                self.log(f"Refreshed Stats: {refreshed}")
            except Exception:
                pass
        self.call_after_refresh(update_stats)
        return True

    def action_get_state(self):
        (
            self.on_check,
            self.is_checkmated,
            self.is_stalemated,
            self.valid_moves,
        ) = self.game.get_game_state()

        self.log(f"on_check: {self.on_check}")
        self.log(f"is_checkmated: {self.is_checkmated}")
        self.log(f"is_stalemated: {self.is_stalemated}")
        self.log(f"valid_moves: {self.valid_moves}")

        self.query("Box.valid").remove_class("valid")
        self.query("Box.check").remove_class("check")
        self.query("Box.selected").remove_class("selected")

        def add_check_indicator(king_pos: CoordT):
            try:
                self.query_one(
                    f"#box-{get_loc(king_pos)}",
                    Box).add_class("check")
            except Exception:
                pass

        if self.on_check:
            if self.is_checkmated:
                self.log(f"{self.game.player} is checkmated")
                self.push_screen(GameOver())
            else:
                self.log(f"{self.game.player} is in check")
                king_id = notations.get_id("k") * self.game.player
                king_pos = find_piece(self.game, king_id)
                self.call_after_refresh(add_check_indicator, king_pos)
        if self.is_stalemated:
            self.log(f"{self.game.player} is stalemated")
            self.push_screen(GameOver())
        return True

    def action_undo(self):
        if self.game.undo_move():
            updated = self.action_update_board()
            self.log(f"Updated Board: {updated}")
            if updated:
                gotten = self.action_get_state()
                self.log(f"Gotten State: {gotten}")
        else:
            self.bell()
            self.log.warning("No moves to undo")
        return True

    def action_save(self):
        self.game.save()
        self.is_saved = True
        return True

    def on_switch_player(self, message: SwitchPlayer):
        self.game.switch_player()
        player = self.game.players[0 if self.game.player == 1 else 1]
        self.sub_title = f"Player {player}"
        updated = self.action_update_board()
        self.log(f"Updated Board: {updated}")
        if updated:
            gotten = self.action_get_state()
            self.log(f"Gotten State: {gotten}")

    def on_piece_moved(self, message: PieceMoved):
        self.is_saved = False
        if self.game._is_pawn_promotion():
            self.push_screen(PawnPromotion())
        else:
            switched = self.post_message(SwitchPlayer())
            self.log(f"Switched Player: {switched}")

    def on_new_game(self, message: NewGame):
        self.is_saved = True
        player = self.game.players[0 if self.game.player == 1 else 1]
        self.sub_title = f"Player {player}"
        self.refresh(layout=True)
        updated = self.action_update_board()
        self.log(f"Updated Board: {updated}")
        if updated:
            gotten = self.action_get_state()
            self.log(f"Gotten State: {gotten}")

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
        # self.action_get_state()

    def on_piece_promotion(self, message: PiecePromotion):
        self.game.promote_pawn(message.promotion)
        if self.selected_piece:
            deselected = self.post_message(PieceDeselected(self.selected_piece))
            self.log(f"Deselected Piece: {deselected}")
        player_switched = self.post_message(SwitchPlayer())
        self.log(f"Switched Player: {player_switched}")
        self.call_after_refresh(self.post_message, PieceDeselected((0, 0)))
        self.call_after_refresh(self.action_update_board)

    def on_piece_selected(self, message: PieceSelected):
        """Handle a piece being selected."""
        if not isinstance(self.selected_piece, tuple):
            self.selected_piece = message.coords
            self.query_one(f"#box-{get_loc(message.coords)}", Box).select()
            for move in self.valid_moves.get(message.coords, []):
                # self.log(f"Valid Move: {get_loc(move)}")
                self.query_one(f"#box-{get_loc(move)}", Box).add_class("valid")
        else:
            self.move_piece(message.coords)
            self.post_message(PieceDeselected(self.selected_piece))

    def on_piece_deselected(self, message: PieceDeselected):
        """Handle a piece being deselected."""
        self.selected_piece = None
        self.query("Box.valid").remove_class("valid")
        for box in self.query("Box.selected"):
            box.deselect()  # type: ignore

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
        if moved:
            moved = self.post_message(PieceMoved())
            self.log(f"Piece Moved: {moved}")

    def compose(self) -> ComposeResult:
        """Setup the app."""
        yield Header(name="Chess")
        yield Horizontal(BoardArea(), Stats(), id="main")
        yield Footer()