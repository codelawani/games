from itertools import cycle

from rich import box
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table

from .epd import (CoordT, EPDString, get_coords, get_EPD, get_loc, get_piece,
                  load_EPD, set_piece)
from .game import Game
from .piece import notations

EPD = EPDString("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")


class Chess(Game):
    """
    Chess Implementation
    """

    x = "abcdefgh"
    y = "87654321"

    def __init__(self, epd: EPDString = EPD):
        super().__init__(epd)
        self.c_escape: "dict[CoordT, list[CoordT]]" = {}
        load_EPD(self, epd)

    def _on_check(self) -> "tuple[bool, dict[CoordT, list[CoordT]]]":
        """
        Check if the king is in check.

        Args:
            king: The king's coordinates and possible moves
            p_moves: The possible moves of the other pieces
        Returns:
            bool: True if the king is in check, False otherwise
            dict: The possible moves of the pieces that can escape check
        """
        check = False
        c_escape: "dict[CoordT, list[CoordT]]" = {}
        possible_moves = self.get_all_moves()
        king = notations.get_id("k") * (self.player)
        k_pos = tuple()  # King position
        p_moves: "set[tuple[CoordT, CoordT]]" = set()  # Possible blocks
        # Sort all possible moves
        for piece, moves in possible_moves.items():
            if not moves:
                continue
            if get_piece(self, piece) == king:
                k_pos = (piece, moves)
            else:
                for move in moves:
                    p_moves.add((piece, move))
        # Check if checkmate is in posible moves
        if not k_pos:
            for y, row in enumerate(self.board):
                if king in row:
                    k_pos = ((row.index(king), y), [])
                    break
        # Check if king is in check
        for move in p_moves:
            x_game = self.copy()
            x_game.switch_player()
            i_moves = x_game.get_all_moves()  # Imaginary moves
            if any(k_pos[0] in moves for moves in i_moves.values()):
                check = True

        for move in p_moves:
            x_game = self.copy()
            x_game.move(get_loc(move[0]), get_loc(move[1]))  # Move piece
            x_game.switch_player()
            i_moves = x_game.get_all_moves()  # Imaginary moves
            if not any(k_pos[0] in moves for moves in i_moves.values()):
                c_escape.setdefault(move[0], list()).append(move[1])
            else:
                rprint(
                    f"[bold red]Bad Piece move detected![/]: {get_loc(move[0])} -> {get_loc(move[1])}"
                )
        for move in k_pos[1]:
            x_game = self.copy()
            x_game.move(get_loc(k_pos[0]), get_loc(move))  # Move king
            x_game.switch_player()
            i_moves = x_game.get_all_moves()  # Imaginary moves
            if not any(
                move in m for m in i_moves.values()
            ):  # Check if moved king still in check
                c_escape.setdefault(k_pos[0], list()).append(move)
            else:
                rprint(
                    f"[bold red]Bad King move detected![/]: {get_loc(k_pos[0])} -> {get_loc(move)}"
                )
        if check:
            if len(c_escape) == 0:
                self.log[-1] += "#"
            else:
                self.log[-1] += "+"
        return check, c_escape

    def promote_pawn(self, to: int) -> bool:
        """
        Promotes a pawn to another piece.

        Args:
            to: The piece to promote the pawn to.

        Returns:
            bool: True if the pawn was successfully promoted, False otherwise.
        """
        rprint(f"Current player: {self.player}")
        part = to * self.player
        if self.last_move == None:
            return False
        pos = self.last_move.to_loc
        rprint(
            f"Change: {get_piece(self, pos)}({get_loc(pos)}) -> {part} {notations.get_char(part, True)}"
        )
        if pos != None:
            set_piece(self, pos, part)
            self.log[-1] += f"={notations.get_char(to).upper()}"
            return True
        else:
            return False

    def _is_pawn_promotion(self) -> bool:
        """
        Check if the last move was a pawn promotion.
        """
        if self.last_move == None:
            return False
        last_piece = get_piece(self, self.last_move.to_loc)
        prev_loc = get_loc(self.last_move.from_loc)
        new_loc = get_loc(self.last_move.to_loc)
        if last_piece != notations.get_id("p") * self.player:
            return False
        if self.player == 1:
            opponents_home = "8"
        else:
            opponents_home = "1"
        if prev_loc[1] != opponents_home and new_loc[1] == opponents_home:
            return True
        return False

    def _is_fifty_move_rule(self) -> bool:
        """
        Check if the 50 move rule has been reached.
        """
        if len(self.log) > 100:
            for m in self.log[-100:]:
                if "x" in m or m[0].islower():
                    return False
            return True
        else:
            return False

    def _is_seventy_five_move_rule(self) -> bool:
        """
        Check if the 75 move rule has been reached.
        """
        if len(self.log) > 150:
            for m in self.log[-150:]:
                if "x" in m or m[0].islower():
                    return False
            return True
        else:
            return False

    def _is_threefold_repetition(self) -> bool:
        """
        Check if the threefold repetition rule has been reached.
        """
        hash = get_EPD(self)
        if hash not in self.epd_hash:
            return False
        if self.epd_hash[hash] >= 3:
            return True
        return False

    def _is_fivefold_repetition(self) -> bool:
        """
        Check if the fivefold repetition rule has been reached.
        """
        hash = get_EPD(self)
        if hash not in self.epd_hash:
            return False
        if self.epd_hash[hash] >= 5:
            return True
        return False

    def _is_dead_position(self):
        """
        Determine whether the current position is a "dead position" (i.e., a position where neither player can win). A position is a dead position if it is one of the following:

        * King and bishop against king and bishop with both bishops on squares
            of the same color
        * King and knight against king
        * King against king with no other pieces on the board

        Args:
            moves (int): The current move number.

        Returns:
            bool: True if the current position is a dead position,
                False otherwise.
        """
        a_pieces = []
        for y in self.board:
            for x in y:
                if x != 0:
                    a_pieces.append(x)
                if len(a_pieces) > 4:
                    return False
        if len(a_pieces) == 2 and -6 in a_pieces and 6 in a_pieces:
            return True
        elif len(a_pieces) == 3 and (
            (-6 in a_pieces and 3 in a_pieces and 6 in a_pieces)
            or (-6 in a_pieces and -3 in a_pieces and 6 in a_pieces)
        ):
            return True
        elif len(a_pieces) == 3 and (
            (-6 in a_pieces and 2 in a_pieces and 6 in a_pieces)
            or (-6 in a_pieces and -2 in a_pieces and 6 in a_pieces)
        ):
            return True
        return False

    def display(self):
        """
        Display the current state of the chess board using chess characters.
        """

        board = Table.grid()
        for i in range(8):
            board.add_column()

        h_indicators = [Panel(c, box=box.SIMPLE) for c in " abcdefgh "]

        board.add_row(*h_indicators)
        flag = True
        styles = cycle(("{} on blue", "{} on red"))

        # loop through rows of the board
        for index, row in enumerate(self.board):
            v_indicator = Panel(str(8 - index), box=box.SIMPLE)
            pieces = [v_indicator]
            for piece in row:
                symbol = notations.get_symbol(piece)
                style = next(styles).format("black" if piece < 0 else "white")
                pieces.append(Panel(symbol, style=style, box=box.SIMPLE))
            pieces.append(v_indicator)
            board.add_row(*pieces)
            next(styles)
        board.add_row(*h_indicators)
        rprint(Panel.fit(board))

    def move(self, curr_loc: str, next_loc: str):
        """
        Move a piece on the board.

        Args:
            curr_loc (str): The current coordinates of the piece in algebraic
                notation (e.g. "a1", "h8").
            next_loc (str): The coordinates of the square that the piece is
                moving to in algebraic notation.
        """
        cp: CoordT = get_coords(curr_loc)
        np: CoordT = get_coords(next_loc)
        # if self.valid_move(cp, np) == False:
        #     return False
        part = get_piece(self, cp)
        self.add_move_history(cp, np, part)
        if np == self.en_passant and (part == 1 or part == -1):
            self.board[
                self.en_passant[1] - (self.player * -1)  # type: ignore
            ][
                self.en_passant[0] # type: ignore
            ] = 0  # type: ignore
        self.log_move(part, curr_loc, next_loc, cp, np)
        if (part == 1 and np[1] == 4) or (part == -1 and np[1] == 3):
            self.en_passant = (
                (np[0], np[1] + 1) if part == 1 else (np[0], np[1] - 1)
            )
        elif part == 6 * self.player and np[0] - cp[0] == 2:
            self.board[np[1]][np[0] - 1] = 4 * self.player
            self.board[np[1]][np[0] + 1] = 0
        elif part == 6 * self.player and np[0] - cp[0] == -2:
            self.board[np[1]][np[0] + 1] = 4 * self.player
            self.board[np[1]][np[0] - 2] = 0
        else:
            self.en_passant = None
        if part == 6 * self.player:
            if self.player == 1:
                self.castling[0] = 0
                self.castling[1] = 0
            else:
                self.castling[2] = 0
                self.castling[3] = 0
        elif part == 4 * self.player:
            if self.player == 1:
                if cp == (0, 7):
                    self.castling[1] = 0
                else:
                    self.castling[0] = 0
            else:
                if cp == (0, 0):
                    self.castling[3] = 0
                else:
                    self.castling[2] = 0
        occupant = get_piece(self, np)
        if occupant != 0:
            print("Captured: " + notations.get_name(occupant))
            self.captured[self.player].append(occupant)
        set_piece(self, cp, 0)
        set_piece(self, np, part)
        hash = get_EPD(self)
        self.epd_hash.setdefault(hash, 0)
        self.epd_hash[hash] += 1
        return True

    def get_all_moves(self) -> "dict[CoordT, list[CoordT]]":
        """
        Return a dictionary of all possible moves on the current board for each piece,
        where the key is a tuple representing the piece's position and the value is a list
        of possible next positions.

        Returns:
            dict: A dictionary of all possible moves on the current board for each piece.
        """
        moves: "dict[CoordT, list[CoordT]]" = {}
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece * self.player <= 0:
                    continue
                p_cls = notations.get_class(piece)
                valid_moves = p_cls.moves(self, self.player, (c, r))
                moves[(c, r)] = valid_moves
        return moves

    def get_game_state(self):
        """ """
        is_check, c_escape = self._on_check()
        if not len(c_escape) and is_check:
            is_checkmate = True
            self.log += "#"
        else:
            is_checkmate = False
            self.log += "+" if is_check else ""
        if not len(c_escape) and not is_check:
            is_stalemate = True
        else:
            is_stalemate = False
        return (is_check, is_checkmate, is_stalemate, c_escape)
