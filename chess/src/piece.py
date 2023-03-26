from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Literal, NamedTuple, Type

if TYPE_CHECKING:
    from epd import Game


CoordT = tuple[int, int]
"The coordinates of a cell on a chess board => tuple[row, col]"

PlayerT = Literal[-1, 1]
"Chess player ID"

MovesList = list[CoordT]
"list of moves available to a chess piece"

SymbolVariant = Literal["outline", "filled"]
"""chess piece variant. filled: ♟; outline: ♙"""


class PieceNotation(NamedTuple):
    """Notation of a chess piece"""

    id: int
    name: str
    char: str
    symbol: tuple[str, str]
    points: int


class Piece(ABC):
    id: int

    @classmethod
    @abstractmethod
    def moves(cls, game: "Game", player: PlayerT, pos: CoordT) -> MovesList:
        pass


class notations:
    pieces = (
        PieceNotation(1, "pawn", "p", ("♙", "♟"), 1),
        PieceNotation(2, "knight", "n", ("♘", "♞"), 3),
        PieceNotation(3, "bishop", "b", ("♗", "♝"), 3),
        PieceNotation(4, "rook", "r", ("♖", "♜"), 5),
        PieceNotation(5, "queen", "q", ("♕", "♛"), 8),
        PieceNotation(6, "king", "k", ("♔", "♚"), 0),
    )

    @classmethod
    def get_symbol(cls, id: int, variant: SymbolVariant = "filled") -> str:
        """
        get a chess piece symbol.

        Args:
                id: the ID of the chess piece
                variant: the variant of the symbol to return.
                        filled or outline.
        Return:
                A chess piece symbol or an empty string if
                ID isn't associated with a chess piece.
        """
        v = 0 if variant == "outline" else 1
        for piece in cls.pieces:
            if piece.id == abs(id):
                return piece.symbol[v]
        return ""

    @classmethod
    def get_name(cls, id: int) -> str:
        """
        get a chess piece's name.

        Args:
                id: the ID of the chess piece
        Return:
                A chess piece's name or an empty string if
                ID isn't associated with a chess piece.
        """
        for piece in cls.pieces:
            if piece.id == abs(id):
                return piece.name
        return ""

    @classmethod
    def get_char(cls, id: int, epd_mode: bool = False) -> str:
        """
        get the character used to represent a chess piece in a EPD string.

        Args:
                id: the ID of the chess piece
                epd_mode: if True then it'll return an uppercase or
                        lowecase character based of the color of the piece.
        Return:
                A chess piece's EPD character or an empty string if
                ID isn't associated with a chess piece.
        """
        for piece in cls.pieces:
            if piece.id == abs(id):
                if epd_mode and id > 0:
                    return piece.char.upper()
                return piece.char
        return ""

    @classmethod
    def get_class(cls, id: int) -> Type[Piece]:
        """
        get the logical implementation for a piece on the chessboard.

        Args:
                id: the ID of the chess piece
        Return:
                A Piece subclass or None if ID isn't associated with
                a chess piece.
        """
        name = cls.get_name(id)
        if not name:
            return None  # type: ignore
        for subclass in Piece.__subclasses__():
            if subclass.__name__.lower() == name.lower():
                return subclass
        return None  # type: ignore

    @classmethod
    def get_id(cls, name_or_char: str, epd_mode: bool = False) -> int:
        """
        get the id of a chess piece.

        Args:
                name_or_char: the chess piece's name or EPD character.
                epd_mode: if True then it'll return a negative or positive
                        id based of the color of the piece
        Return:
                the ID of a chess pice or 0 if the piece doesn't exist
        """
        name_or_char = name_or_char.strip()
        if not name_or_char:
            return 0
        if len(name_or_char) == 1:
            for piece in cls.pieces:
                if piece.char == name_or_char.lower():
                    if epd_mode and name_or_char.islower():
                        return piece.id * -1
                    return piece.id
        else:
            for piece in cls.pieces:
                if piece.name == name_or_char.lower():
                    return piece.id
        return 0


class King(Piece):
    """Chess King"""

    id = 6
    "the ID of the King"

    @classmethod
    def moves(cls, game: "Game", player: PlayerT, pos: CoordT) -> MovesList:
        """
        get all possible moves of the King

        Args:
                state: the games state
                player: the player that owns the King
                pos: the King's current position
        Return:
                a list of available moves that the King can make
        """
        result: MovesList = []
        if (
            pos[1] + 1 >= 0
            and pos[1] + 1 <= 7
            and pos[0] >= 0
            and pos[0] <= 7
            and (
                game.board[pos[1] + 1][pos[0]] * player < 0
                or game.board[pos[1] + 1][pos[0]] == 0
            )
        ):
            result.append((pos[0], pos[1] + 1))
        if (
            pos[1] - 1 >= 0
            and pos[1] - 1 <= 7
            and pos[0] >= 0
            and pos[0] <= 7
            and (
                game.board[pos[1] - 1][pos[0]] * player < 0
                or game.board[pos[1] - 1][pos[0]] == 0
            )
        ):
            result.append((pos[0], pos[1] - 1))
        if (
            pos[1] >= 0
            and pos[1] <= 7
            and pos[0] + 1 >= 0
            and pos[0] + 1 <= 7
            and (
                game.board[pos[1]][pos[0] + 1] * player < 0
                or game.board[pos[1]][pos[0] + 1] == 0
            )
        ):
            result.append((pos[0] + 1, pos[1]))
        if (
            pos[1] >= 0
            and pos[1] <= 7
            and pos[0] - 1 >= 0
            and pos[0] - 1 <= 7
            and (
                game.board[pos[1]][pos[0] - 1] * player < 0
                or game.board[pos[1]][pos[0] - 1] == 0
            )
        ):
            result.append((pos[0] - 1, pos[1]))
        if (
            pos[1] + 1 >= 0
            and pos[1] + 1 <= 7
            and pos[0] + 1 >= 0
            and pos[0] + 1 <= 7
            and (
                game.board[pos[1] + 1][pos[0] + 1] * player < 0
                or game.board[pos[1] + 1][pos[0] + 1] == 0
            )
        ):
            result.append((pos[0] + 1, pos[1] + 1))
        if (
            pos[1] + 1 >= 0
            and pos[1] + 1 <= 7
            and pos[0] - 1 >= 0
            and pos[0] - 1 <= 7
            and (
                game.board[pos[1] + 1][pos[0] - 1] * player < 0
                or game.board[pos[1] + 1][pos[0] - 1] == 0
            )
        ):
            result.append((pos[0] - 1, pos[1] + 1))
        if (
            pos[1] - 1 >= 0
            and pos[1] - 1 <= 7
            and pos[0] + 1 >= 0
            and pos[0] + 1 <= 7
            and (
                game.board[pos[1] - 1][pos[0] + 1] * player < 0
                or game.board[pos[1] - 1][pos[0] + 1] == 0
            )
        ):
            result.append((pos[0] + 1, pos[1] - 1))
        if (
            pos[1] - 1 >= 0
            and pos[1] - 1 <= 7
            and pos[0] - 1 >= 0
            and pos[0] - 1 <= 7
            and (
                game.board[pos[1] - 1][pos[0] - 1] * player < 0
                or game.board[pos[1] - 1][pos[0] - 1] == 0
            )
        ):
            result.append((pos[0] - 1, pos[1] - 1))
        if (
            (pos == (4, 7) or pos == (4, 0))
            and game.board[pos[1]][pos[0] + 1] == 0
            and game.board[pos[1]][pos[0] + 2] == 0
            and (
                (game.castling[0] == 1 and game.player == 1)
                or (game.castling[2] == 1 and game.player == -1)
            )
        ):
            result.append((pos[0] + 2, pos[1]))
        if (
            (pos == (4, 7) or pos == (4, 0))
            and game.board[pos[1]][pos[0] - 1] == 0
            and game.board[pos[1]][pos[0] - 2] == 0
            and (
                (game.castling[1] == 1 and game.player == 1)
                or (game.castling[3] == 1 and game.player == -1)
            )
        ):
            result.append((pos[0] - 2, pos[1]))
        return result


class Queen(Piece):
    """Chess King"""

    id = 5
    "the ID of the Queen"

    @classmethod
    def moves(cls, game: "Game", player: PlayerT, pos: CoordT) -> MovesList:
        """
        get all possible moves of the Queen

        Args:
                state: the games state
                player: the player that owns the Queen
                pos: the Queen's current position
        Return:
                a list of available moves that the Queen can make
        """
        result = []
        check = [True, True, True, True, True, True, True, True]
        for c in range(1, 8, 1):
            if (
                pos[1] + c >= 0
                and pos[1] + c <= 7
                and pos[0] >= 0
                and pos[0] <= 7
                and (
                    game.board[pos[1] + c][pos[0]] * player < 0
                    or game.board[pos[1] + c][pos[0]] == 0
                )
                and check[0] == True
            ):
                result.append((pos[0], pos[1] + c))
                if game.board[pos[1] + c][pos[0]] * player < 0:
                    check[0] = False
            else:
                check[0] = False
            if (
                pos[1] - c >= 0
                and pos[1] - c <= 7
                and pos[0] >= 0
                and pos[0] <= 7
                and (
                    game.board[pos[1] - c][pos[0]] * player < 0
                    or game.board[pos[1] - c][pos[0]] == 0
                )
                and check[1] == True
            ):
                result.append((pos[0], pos[1] - c))
                if game.board[pos[1] - c][pos[0]] * player < 0:
                    check[1] = False
            else:
                check[1] = False
            if (
                pos[1] >= 0
                and pos[1] <= 7
                and pos[0] + c >= 0
                and pos[0] + c <= 7
                and (
                    game.board[pos[1]][pos[0] + c] * player < 0
                    or game.board[pos[1]][pos[0] + c] == 0
                )
                and check[2] == True
            ):
                result.append((pos[0] + c, pos[1]))
                if game.board[pos[1]][pos[0] + c] * player < 0:
                    check[2] = False
            else:
                check[2] = False
            if (
                pos[1] >= 0
                and pos[1] <= 7
                and pos[0] - c >= 0
                and pos[0] - c <= 7
                and (
                    game.board[pos[1]][pos[0] - c] * player < 0
                    or game.board[pos[1]][pos[0] - c] == 0
                )
                and check[3] == True
            ):
                result.append((pos[0] - c, pos[1]))
                if game.board[pos[1]][pos[0] - c] * player < 0:
                    check[3] = False
            else:
                check[3] = False
            if (
                pos[1] + c >= 0
                and pos[1] + c <= 7
                and pos[0] + c >= 0
                and pos[0] + c <= 7
                and (
                    game.board[pos[1] + c][pos[0] + c] * player < 0
                    or game.board[pos[1] + c][pos[0] + c] == 0
                )
                and check[4] == True
            ):
                result.append((pos[0] + c, pos[1] + c))
                if game.board[pos[1] + c][pos[0] + c] * player < 0:
                    check[4] = False
            else:
                check[4] = False
            if (
                pos[1] + c >= 0
                and pos[1] + c <= 7
                and pos[0] - c >= 0
                and pos[0] - c <= 7
                and (
                    game.board[pos[1] + c][pos[0] - c] * player < 0
                    or game.board[pos[1] + c][pos[0] - c] == 0
                )
                and check[5] == True
            ):
                result.append((pos[0] - c, pos[1] + c))
                if game.board[pos[1] + c][pos[0] - c] * player < 0:
                    check[5] = False
            else:
                check[5] = False
            if (
                pos[1] - c >= 0
                and pos[1] - c <= 7
                and pos[0] + c >= 0
                and pos[0] + c <= 7
                and (
                    game.board[pos[1] - c][pos[0] + c] * player < 0
                    or game.board[pos[1] - c][pos[0] + c] == 0
                )
                and check[6] == True
            ):
                result.append((pos[0] + c, pos[1] - c))
                if game.board[pos[1] - c][pos[0] + c] * player < 0:
                    check[6] = False
            else:
                check[6] = False
            if (
                pos[1] - c >= 0
                and pos[1] - c <= 7
                and pos[0] - c >= 0
                and pos[0] - c <= 7
                and (
                    game.board[pos[1] - c][pos[0] - c] * player < 0
                    or game.board[pos[1] - c][pos[0] - c] == 0
                )
                and check[7] == True
            ):
                result.append((pos[0] - c, pos[1] - c))
                if game.board[pos[1] - c][pos[0] - c] * player < 0:
                    check[7] = False
            else:
                check[7] = False
            if True not in check:
                break
        return result


class Rook(Piece):
    """Chess Rook"""

    id = 4
    "the ID of the Rook"

    @classmethod
    def moves(cls, game: "Game", player: PlayerT, pos: CoordT) -> MovesList:
        """
        get all possible moves of the Rook

        Args:
                state: the games state
                player: the player that owns the Rook
                pos: the Rook's current position
        Return:
                a list of available moves that the Rook can make
        """
        result = []
        check = [True, True, True, True]
        for c in range(1, 8, 1):
            if (
                pos[1] + c >= 0
                and pos[1] + c <= 7
                and pos[0] >= 0
                and pos[0] <= 7
                and (
                    game.board[pos[1] + c][pos[0]] * player < 0
                    or game.board[pos[1] + c][pos[0]] == 0
                )
                and check[0] == True
            ):
                result.append((pos[0], pos[1] + c))
                if game.board[pos[1] + c][pos[0]] * player < 0:
                    check[0] = False
            else:
                check[0] = False
            if (
                pos[1] - c >= 0
                and pos[1] - c <= 7
                and pos[0] >= 0
                and pos[0] <= 7
                and (
                    game.board[pos[1] - c][pos[0]] * player < 0
                    or game.board[pos[1] - c][pos[0]] == 0
                )
                and check[1] == True
            ):
                result.append((pos[0], pos[1] - c))
                if game.board[pos[1] - c][pos[0]] * player < 0:
                    check[1] = False
            else:
                check[1] = False
            if (
                pos[1] >= 0
                and pos[1] <= 7
                and pos[0] + c >= 0
                and pos[0] + c <= 7
                and (
                    game.board[pos[1]][pos[0] + c] * player < 0
                    or game.board[pos[1]][pos[0] + c] == 0
                )
                and check[2] == True
            ):
                result.append((pos[0] + c, pos[1]))
                if game.board[pos[1]][pos[0] + c] * player < 0:
                    check[2] = False
            else:
                check[2] = False
            if (
                pos[1] >= 0
                and pos[1] <= 7
                and pos[0] - c >= 0
                and pos[0] - c <= 7
                and (
                    game.board[pos[1]][pos[0] - c] * player < 0
                    or game.board[pos[1]][pos[0] - c] == 0
                )
                and check[3] == True
            ):
                result.append((pos[0] - c, pos[1]))
                if game.board[pos[1]][pos[0] - c] * player < 0:
                    check[3] = False
            else:
                check[3] = False
            if True not in check:
                break
        return result


class Bishop(Piece):
    """Chess Bishop"""

    id = 3
    "the ID of the Bishop"

    @classmethod
    def moves(cls, game: "Game", player: PlayerT, pos: CoordT) -> MovesList:
        """
        get all possible moves of the Bishop

        Args:
                state: the games state
                player: the player that owns the Bishop
                pos: the Bishop's current position
        Return:
                a list of available moves that the Bishop can make
        """
        result = []
        check = [True, True, True, True]
        for c in range(1, 8, 1):
            if (
                pos[1] + c >= 0
                and pos[1] + c <= 7
                and pos[0] + c >= 0
                and pos[0] + c <= 7
                and (
                    game.board[pos[1] + c][pos[0] + c] * player < 0
                    or game.board[pos[1] + c][pos[0] + c] == 0
                )
                and check[0] == True
            ):
                result.append((pos[0] + c, pos[1] + c))
                if game.board[pos[1] + c][pos[0] + c] * player < 0:
                    check[0] = False
            else:
                check[0] = False
            if (
                pos[1] + c >= 0
                and pos[1] + c <= 7
                and pos[0] - c >= 0
                and pos[0] - c <= 7
                and (
                    game.board[pos[1] + c][pos[0] - c] * player < 0
                    or game.board[pos[1] + c][pos[0] - c] == 0
                )
                and check[1] == True
            ):
                result.append((pos[0] - c, pos[1] + c))
                if game.board[pos[1] + c][pos[0] - c] * player < 0:
                    check[1] = False
            else:
                check[1] = False
            if (
                pos[1] - c >= 0
                and pos[1] - c <= 7
                and pos[0] + c >= 0
                and pos[0] + c <= 7
                and (
                    game.board[pos[1] - c][pos[0] + c] * player < 0
                    or game.board[pos[1] - c][pos[0] + c] == 0
                )
                and check[2] == True
            ):
                result.append((pos[0] + c, pos[1] - c))
                if game.board[pos[1] - c][pos[0] + c] * player < 0:
                    check[2] = False
            else:
                check[2] = False
            if (
                pos[1] - c >= 0
                and pos[1] - c <= 7
                and pos[0] - c >= 0
                and pos[0] - c <= 7
                and (
                    game.board[pos[1] - c][pos[0] - c] * player < 0
                    or game.board[pos[1] - c][pos[0] - c] == 0
                )
                and check[3] == True
            ):
                result.append((pos[0] - c, pos[1] - c))
                if game.board[pos[1] - c][pos[0] - c] * player < 0:
                    check[3] = False
            else:
                check[3] = False
            if True not in check:
                break
        return result


class Knight(Piece):
    """Chess Knight"""

    id = 2
    "the ID of the Knight"

    @classmethod
    def moves(cls, game: "Game", player: PlayerT, pos: CoordT) -> MovesList:
        """
        get all possible moves of the Knight

        Args:
                state: the games state
                player: the player that owns the Knight
                pos: the Knight's current position
        Return:
                a list of available moves that the Knight can make
        """
        result = []
        for i in [-1, 1]:
            if (
                pos[0] - i >= 0
                and pos[0] - i <= 7
                and pos[1] - (2 * i) >= 0
                and pos[1] - (2 * i) <= 7
                and (
                    game.board[pos[1] - (2 * i)][pos[0] - i] * player < 0
                    or game.board[pos[1] - (2 * i)][pos[0] - i] == 0
                )
            ):
                result.append((pos[0] - i, pos[1] - (2 * i)))
            if (
                pos[0] + i >= 0
                and pos[0] + i <= 7
                and pos[1] - (2 * i) >= 0
                and pos[1] - (2 * i) <= 7
                and (
                    game.board[pos[1] - (2 * i)][pos[0] + i] * player < 0
                    or game.board[pos[1] - (2 * i)][pos[0] + i] == 0
                )
            ):
                result.append((pos[0] + i, pos[1] - (2 * i)))
            if (
                pos[0] - (2 * i) >= 0
                and pos[0] - (2 * i) <= 7
                and pos[1] - i >= 0
                and pos[1] - i <= 7
                and (
                    game.board[pos[1] - i][pos[0] - (2 * i)] * player < 0
                    or game.board[pos[1] - i][pos[0] - (2 * i)] == 0
                )
            ):
                result.append((pos[0] - (2 * i), pos[1] - i))
            if (
                pos[0] - (2 * i) >= 0
                and pos[0] - (2 * i) <= 7
                and pos[1] + i >= 0
                and pos[1] + i <= 7
                and (
                    game.board[pos[1] + i][pos[0] - (2 * i)] * player < 0
                    or game.board[pos[1] + i][pos[0] - (2 * i)] == 0
                )
            ):
                result.append((pos[0] - (2 * i), pos[1] + i))
        return result


class Pawn(Piece):
    """Chess Pawn"""

    id = 1
    "the ID of the Pawn"

    @classmethod
    def moves(cls, game: "Game", player: PlayerT, pos: CoordT) -> MovesList:
        """
        get all possible moves of the Pawn

        Args:
                state: the games state
                player: the player that owns the Pawn
                pos: the Pawn's current position
        Return:
                a list of available moves that the Pawn can make
        """
        result = []
        init = 1 if player < 0 else 6
        amt = 1 if pos[1] != init else 2
        for i in range(amt):
            if (
                pos[1] - ((i + 1) * player) >= 0
                and pos[1] - ((i + 1) * player) <= 7
                and game.board[pos[1] - ((i + 1) * player)][pos[0]] == 0
            ):
                result.append((pos[0], pos[1] - ((i + 1) * player)))
            else:
                break
        if (
            pos[1] - player <= 7
            and pos[1] - player >= 0
            and pos[0] + 1 <= 7
            and pos[0] + 1 >= 0
            and game.board[pos[1] - player][pos[0] + 1] * player < 0
        ):
            result.append((pos[0] + 1, pos[1] - player))
        if (
            pos[1] - player >= 0
            and pos[1] - player <= 7
            and pos[0] - 1 >= 0
            and pos[0] - 1 <= 7
            and game.board[pos[1] - player][pos[0] - 1] * player < 0
        ):
            result.append((pos[0] - 1, pos[1] - player))
        if (
            pos[1] - player <= 7
            and pos[1] - player >= 0
            and pos[0] + 1 <= 7
            and pos[0] + 1 >= 0
            and (pos[0] + 1, pos[1] - player) == game.en_passant
        ):
            result.append((pos[0] + 1, pos[1] - player))
        if (
            pos[1] - player >= 0
            and pos[1] - player <= 7
            and pos[0] - 1 >= 0
            and pos[0] - 1 <= 7
            and (pos[0] - 1, pos[1] - player) == game.en_passant
        ):
            result.append((pos[0] - 1, pos[1] - player))
        return result
