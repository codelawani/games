from copy import deepcopy
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich import print as rprint
from .epd import CoordT, get_EPD, get_coords, get_loc, get_piece, load_EPD, EPDString, set_piece
from .game import Game
from itertools import cycle
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
        self.c_escape: 'dict[CoordT, list[CoordT]]' = {}
        self.captured: 'dict[int, list[int]]' = {1: [], -1: []}
        load_EPD(self, epd)
    
    def _on_check(self) -> 'tuple[bool, dict[CoordT, list[CoordT]]]':
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
        c_escape: 'dict[CoordT, list[CoordT]]' = {}
        possible_moves = self.get_all_moves()
        king = notations.get_id('k') * (self.player)
        k_pos = tuple()  # King position
        p_moves: 'set[tuple[CoordT, CoordT]]' = set()  # Possible blocks
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
                    k_pos = ((row.index(king), y),[])
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
                rprint(f"[bold red]Bad Piece move detected![/]: {get_loc(move[0])} -> {get_loc(move[1])}")
        for move in k_pos[1]:
            x_game = self.copy()
            x_game.move(get_loc(k_pos[0]), get_loc(move))  # Move king
            x_game.switch_player()
            i_moves = x_game.get_all_moves()  # Imaginary moves
            if not any(move in m for m in i_moves.values()):  # Check if moved king still in check
                c_escape.setdefault(k_pos[0], list()).append(move)
            else:
                rprint(f"[bold red]Bad King move detected![/]: {get_loc(k_pos[0])} -> {get_loc(move)}")
        return check, c_escape

    def _is_pawn_promotion(self) -> bool:
        """
        Check if the last move was a pawn promotion. 
        """
        if (
            len(self.log) > 0
            and self.player == 1
            and (self.log[-1][0].isupper() == False or self.log[-1][0] == "P")
            and True in [True for l in self.log[-1] if l == "8"]
        ):
            return True  # Pawn promotion
        elif (
            len(self.log) > 0
            and self.player == -1
            and (self.log[-1][0].isupper() == False or self.log[-1][0] == "P")
            and True in [True for l in self.log[-1] if l == "1"]
        ):
            return True  # Pawn promotion
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
        styles = cycle((
            "{} on blue",
            "{} on red"
        ))

        # loop through rows of the board
        for index, row in enumerate(self.board):
            v_indicator = Panel(str(8 - index), box=box.SIMPLE)
            pieces = [v_indicator]
            for piece in row:
                symbol = notations.get_symbol(piece)
                style = next(styles).format(
                    "black" if piece < 0
                    else "white"
                )
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
                self.en_passant[1] -(self.player * -1)# type: ignore
                ][self.en_passant[0]] = 0 # type: ignore
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
            self.captured[self.player].append(occupant)
        set_piece(self, cp, 0)
        set_piece(self, np, part)
        hash = get_EPD(self)
        self.epd_hash.setdefault(hash, 0)
        self.epd_hash[hash] += 1
        return True

    def valid_move(self, cur_pos, next_pos):
        """
        Check if a move from current position to the next position is valid.

        Args:
            cur_pos (tuple): A tuple of two integers representing the current
                position on the board in (row, column) format.
            next_pos (tuple): A tuple of two integers representing the next
                position on the board in (row, column) format.
        Returns:
            bool: True if the move is valid, False otherwise.
        """
        piece = get_piece(self, cur_pos)
        if self.player * piece <= 0:
            return False
        is_check, is_checkmate, is_stalemate, escape = self.get_game_state()
        if is_checkmate or is_stalemate:
            return False
        if is_check:
            moves = escape
        else:
            moves = self.get_all_moves()
        if cur_pos in moves:
            if next_pos in moves[cur_pos]:
                return True
        return False

    def get_all_moves(self) -> 'dict[CoordT, list[CoordT]]':
        """
        Return a dictionary of all possible moves on the current board for each piece,
        where the key is a tuple representing the piece's position and the value is a list
        of possible next positions.

        Returns:
            dict: A dictionary of all possible moves on the current board for each piece.
        """
        moves: 'dict[CoordT, list[CoordT]]' = {}
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece * self.player <= 0:
                    continue
                p_cls = notations.get_class(piece)
                valid_moves = p_cls.moves(self, self.player, (c, r))
                moves[(c, r)] = valid_moves
        return moves

    def get_game_state(self):
        """
        """
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


class LegacyChess(Chess):
    """
    A class representing a chess game.
    """
    def is_check(self, possible_moves: 'dict[str, list[CoordT]]'):
        """
        Determine if the current board state is a check.

        Args:
            possible_moves:
                A dictionary containing the current possible moves for each piece on the board.
        Returns:
            bool: True if the current board state is a check, False otherwise.
        """
        k_pos = tuple()  # King position
        u_moves: 'dict[CoordT, list[CoordT]]' = {}  # User potential moves

        # Sort all possible moves
        for piece, moves in possible_moves.items():
            coord: CoordT = get_coords(piece) # type: ignore
            if (str(piece[0]).isupper() and self.player == -1) or (
                str(piece[0]).islower() and self.player == 1
            ):
                if get_piece(self, coord) == notations.get_id('k') * (
                    (self.player * -1)):
                    k_pos = (coord, moves)
            else:
                u_moves.setdefault(coord, moves)
        p_moves = [m for a in u_moves.values() for m in a]
        "possible moves"
        # Check if checkmate is in possible moves
        if k_pos and k_pos[0] not in p_moves:
            return False
        return True

    def is_checkmate(self, possible_moves: 'dict[str, list[CoordT]]'):
        """
        Determines if the current board state is a checkmate, indicating the end of the game.

        Args:
            possible_moves:
                A dictionary containing the current possible moves for each piece on the board.

        Returns:
            A list containing three elements:
                1. If the game is over (1 if True, 0 if False)
                2. The score for White (an integer)
                3. The score for Black (an integer)
        """
        self.c_escape = {}
        opponents_king = notations.get_id('k') * (self.player * -1)
        k_pos = tuple()  # King position
        p_blocks: 'set[tuple[CoordT, CoordT]]' = set()  # Possible blocks
        u_moves: 'dict[CoordT, list[CoordT]]' = {}  # User potential moves
        # Sort all possible moves
        for piece, moves in possible_moves.items():
            coord: CoordT = get_coords(piece) # type: ignore
            if (str(piece[0]).isupper() and self.player == -1) or (
                str(piece[0]).islower() and self.player == 1
            ):
                if get_piece(self, coord) == opponents_king:
                    k_pos = (coord, moves)
                else:
                    for move in moves:
                        p_blocks.add((coord, move))
            else:
                u_moves.setdefault(coord, moves)
        p_moves = [m for a in u_moves.values() for m in a]
        "possible moves"
        # Check if checkmate is in posible moves
        if k_pos and k_pos[0] not in p_moves:
            return [0, 0, 0]
        elif not k_pos:
            for y, row in enumerate(self.board):
                if opponents_king in row:
                    k_pos = ((row.index(opponents_king), y),[])
                    break
        if not (k_pos and k_pos[0] in p_moves):
            return [1, 0, 0] if self.player == 1 else [0, 0, 1]
        for move in p_blocks:
            x_game = deepcopy(self)
            x_game.switch_player()
            x_game.move(get_loc(move[0]), get_loc(move[1]))  # Move king
            x_game.switch_player()
            i_moves = x_game.possible_board_moves()  # Imaginary moves
            if not any(True for k in i_moves if k_pos[0] in i_moves[k]):
                # Check if moved king still in check
                # if len(self.log) > 0 and self.log[-1][-1] is not '+':
                # self.log[-1] += '+' #Check
                # print(m,f'{self.x[m[0][0]]}{self.y[m[0][1]]}', f'{self.x[m[1][0]]}{self.y[m[1][1]]}')
                self.c_escape.setdefault(move[0], list()).append(move[1])
                # return [0, 0, 0]
        for move in k_pos[1]:
            if move not in p_moves:
                x_game = deepcopy(self)
                x_game.switch_player()
                x_game.move(get_loc(k_pos[0]), get_loc(move))  # Move king
                x_game.switch_player()
                i_moves = x_game.possible_board_moves()  # Imaginary moves
                if not any(True for k in i_moves if move in i_moves[k]):  # Check if moved king still in check
                    # if len(self.log) > 0 and self.log[-1][-1] is not '+':
                    # self.log[-1] += '+' #Check
                    # print(m)
                    # print(k_pos[0],m,f'{self.x[k_pos[0][0]]}{self.y[k_pos[0][1]]}', f'{self.x[m[0]]}{self.y[m[1]]}')
                    self.c_escape.setdefault(k_pos[0], list()).append(move)
                    # return [0, 0, 0]
        if len(self.c_escape) > 0:
            self.log[-1] += "+"  # Check
            return [0, 0, 0]
        elif self.player == -1:
            self.log[-1] += "#"
            return [0, 0, 1]  # Black wins
        else:
            self.log[-1] += "#"
            return [1, 0, 0]  # White wins

    def pawn_promotion(self, n_part=None):
        """
        Promotes a pawn to another piece.

        Args:
            n_part (str): Optional. The notation for the piece to promote to.
            Can be one of "q", "b", "n", or "r" for queen, bishop, knight,
            or rook respectively.
            If None, the user will be prompted to enter a valid option.

        Returns:
            bool: True if the pawn was successfully promoted, False otherwise.
        """
        if n_part == None:
            while True:
                n_part = input(
                    "\nPawn Promotion - What piece would you like to switch too:\n\n*Queen[q]\n*Bishop[b]\n*Knight[n]\n*Rook[r]\n"
                )
                if str(n_part).lower() not in [
                    "q",
                    "b",
                    "n",
                    "r",
                    "queen",
                    "bishop",
                    "knight",
                    "rook",
                ]:
                    print("\nInvalid Option")
                else:
                    break
            n_part = notations.get_id(n_part)
        part = n_part * self.player
        pos = get_coords(self.log[-1].replace("+", "").split("x")[-1])
        if pos != None:
            self.board[pos[1]][pos[0]] = part
            self.log[-1] += f"={str(n_part).upper()}"
            return True
        else:
            return False

    def fifty_move_rule(self, moves, choice=None):
        """
        Applies the fifty move rule and allows a player to claim a draw.

        Args:
            moves (int): The total number of moves in the game.
            choice (str): Whether the player wants to claim a draw or not. Defaults to None.

        Returns:
            bool: True if the fifty move rule is triggered and the player chooses to claim a draw. False otherwise.


        The fifty move rule is a rule in chess that states that a player can claim a draw if no
        pawn has been moved and no piece has been captured in the last 50 moves.
        This method checks if the rule is triggered and prompts the player to choose
        whether they want to claim a draw or not.
        """
        if len(self.log) > 100:
            for m in self.log[-100:]:
                if "x" in m or m[0].islower():
                    return False
        else:
            return False
        if choice == None:
            while True:
                choice = input(
                    "Fifty move rule - do you want to claim a draw? [Y/N]"
                )
                if (
                    choice.lower() == "y"
                    or choice.lower() == "yes"
                    or choice.lower() == "1"
                ):
                    return True
                elif (
                    choice.lower() == "n"
                    or choice.lower() == "no"
                    or choice.lower() == "0"
                ):
                    return False
            print("Unsupported answer")
        if (
            choice.lower() == "y"
            or choice.lower() == "yes"
            or choice.lower() == "1"
        ):
            return True
        elif (
            choice.lower() == "n"
            or choice.lower() == "no"
            or choice.lower() == "0"
        ):
            return False

    def seventy_five_move_rule(self, moves):
        """
        Checks if the 75-move rule has been met.
        According to this rule, a player can claim a draw if the last 150 moves
        have been made without any pawn move or any capture.

        Args:
            moves (int): The number of moves made so far in the game.

        Returns:
            bool: True if the 75-move rule has been met and a draw can be claimed.
                False otherwise.
        """
        if len(self.log) > 150:
            for m in self.log[-150:]:
                if "x" in m or m[0].islower():
                    return False
        else:
            return False
        return True

    def three_fold_rule(self, hash):
        """
        Check if the current position has occurred three times, and prompt the user to claim a draw if it has.

        Args:
            hash (int): The hash value of the current board position.

        Returns:
            bool: True if the user claims a draw, False otherwise.
        """
        if hash not in self.epd_hash:
            return False
        if self.epd_hash[hash] == 3:
            while True:
                choice = input(
                    "Three fold rule - do you want to claim a draw? [Y/N]"
                )
                if (
                    choice.lower() == "y"
                    or choice.lower() == "yes"
                    or choice.lower() == "1"
                ):
                    return True
                elif (
                    choice.lower() == "n"
                    or choice.lower() == "no"
                    or choice.lower() == "0"
                ):
                    return False
                print("Unsupported answer")
        return False

    def five_fold_rule(self, hash):
        """
        Check if the game has reached a five-fold repetition,
        which is one of the conditions for a draw in chess.

        Args:
            hash: a string representing the current position of the chess game in EPD format

        Returns:
            - True if the game has reached a five-fold repetition
            - False otherwise
        """
        if hash in self.epd_hash:
            if self.epd_hash[hash] >= 5:
                return True
        return False

    def is_dead_position(self, moves):
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

    def is_stalemate(self, moves):
        """
        Determines if the current game state is a stalemate.

        A stalemate occurs when the current player is not in check but has no legal move available.

        Args:
            moves (dict): A dictionary containing all available moves for each piece on the board.
        Returns:
            bool: True if the current game state is a stalemate, False otherwise.
        """
        if False not in [
            False
            for p, a in moves.items()
            if len(a) > 0
            and (
                (self.player == 1 and str(p[0]).isupper())
                or (self.player == -1 and str(p[0]).islower())
            )
        ]:
            return True
        return False

    def is_draw(self, moves, hash):
        """
        Checks if the current game state is a draw by applying the following rules in order:

        1. Stalemate - if the current player has no legal moves, it's a draw.
        2. Dead position - if a position arises where it is impossible for either player to checkmate the other player's king, it's a draw. (e.g. king and bishop vs. king and bishop where both bishops are on the same color square)
        3. Seventy-five move rule - if the last 75 moves (by both players) have been made without any captures or pawn moves, it's a draw.
        4. Five-fold repetition rule - if the same position occurs on the board for the fifth time, it's a draw.
        5. Fifty-move rule - if the last 50 moves (by both players) have been made without any captures or pawn moves, it's a draw.
        6. Three-fold repetition rule - if the same position occurs on the board for the third time, with the same player to move and the same set of legal moves, it's a draw.

        Args:
            moves (dict): A dictionary of all legal moves for each piece on the board.
            hash (str): A string representing the current state of the board.

        Returns:
            bool: True if the current game state is a draw, False otherwise.
        """
        if self.is_stalemate(moves) == True:
            return True
        elif self.is_dead_position(moves) == True:
            return True
        elif self.seventy_five_move_rule(moves) == True:
            return True
        elif self.five_fold_rule(hash) == True:
            return True
        elif self.fifty_move_rule(moves) == True:
            return True
        elif self.three_fold_rule(hash) == True:
            return True
        return False

    def is_end(self):
        """
        Determines if the game has ended and returns a list of outcomes [white wins, draw, black wins].
        If the game is not over, returns [0, 0, 0].

        Returns:
            list: A list of integers representing the outcome of the game.
            1. If white wins, the first element is 1, else 0.
            2. If the game is a draw, the second element is 1, else 0.
            3. If black wins, the third element is 1, else 0.
        """
        w_king = False
        b_king = False
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if self.board[y][x] == notations.get_id('k') * -1:
                    b_king = True
                elif self.board[y][x] == notations.get_id('k'):
                    w_king = True
        # print("black", b_king, "white", w_king)
        if w_king == False and b_king == False:
            return [0, 1, 0]
        elif w_king == False:
            return [0, 0, 1]
        elif b_king == False:
            return [1, 0, 0]
        moves = self.possible_board_moves()
        check_mate = self.is_checkmate(moves)
        hash = get_EPD(self)
        if sum(check_mate) > 0:
            return check_mate
        elif self.is_draw(moves, hash) == True:
            return [0, 1, 0]
        return [0, 0, 0]

    def check_state(self, hash):
        """
        Check the state of the chess game based on the current board
        configuration and move history.

        Args:
            hash (str): The hash value of the current board configuration.

        Returns:
            str or None: A string indicating the current game state or None if the game is still ongoing. Possible values are:
                * "PP": Pawn promotion
                * "3F": Threefold repetition
                * "50M": Fifty-move rule
                * None: Game is still ongoing.
        """
        if (
            len(self.log) > 0
            and self.player == 1
            and (self.log[-1][0].isupper() == False or self.log[-1][0] == "P")
            and True in [True for l in self.log[-1] if l == "8"]
        ):
            return "PP"  # Pawn promotion
        elif (
            len(self.log) > 0
            and self.player == -1
            and (self.log[-1][0].isupper() == False or self.log[-1][0] == "P")
            and True in [True for l in self.log[-1] if l == "1"]
        ):
            return "PP"  # Pawn promotion
        elif hash in self.epd_hash and self.epd_hash[hash] == 3:
            return "3F"  # 3 Fold
        elif len(self.log) > 100:
            for m in self.log[-100:]:
                if "x" in m or m[0].islower():
                    return None
            return "50M"  # 50 move
        else:
            return None
    
    def possible_board_moves(self):
        """
        Returns a dictionary of all possible moves on the current board for each piece,
        where the key is a string representing the piece's position and the value is a list
        of possible next positions.

        Returns:
            dict: A dictionary of all possible moves on the current board for each piece.
        """
        moves: 'dict[str, list[CoordT]]' = {}
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece == 0:
                    continue
                p_cls = notations.get_class(piece)
                p_colour = 1 if piece > 0 else -1
                valid_moves = p_cls.moves(self, p_colour, (c, r))
                if len(self.log) > 0 and "+" in self.log[-1]:
                    valid_moves = [
                        move
                        for move in valid_moves
                        if (c, r) in self.c_escape
                        and move in self.c_escape[(c, r)]
                    ]
                piece_annotation = (str.lower if piece < 0 else str.upper)(get_loc((c, r)))
                moves[piece_annotation] = valid_moves
        return moves

    def valid_move(self, cur_pos, next_pos):
        """
        Check if a move from current position to the next position is valid.

        Args:
            cur_pos (tuple): A tuple of two integers representing the current
                position on the board in (row, column) format.
            next_pos (tuple): A tuple of two integers representing the next
                position on the board in (row, column) format.
        Returns:
            bool: True if the move is valid, False otherwise.
        """
        piece = self.board[cur_pos[1]][cur_pos[0]]
        if piece == 0 or piece * self.player < 0:
            return False
        if piece * self.player > 0 and piece != 0:
            p_cls = notations.get_class(piece)
            valid_moves = p_cls.moves(self, self.player, cur_pos)
            if len(self.log) > 0 and "+" in self.log[-1]:
                valid_moves = [
                    move
                    for move in valid_moves
                    if move in self.c_escape.get(cur_pos, [])
                ]
            if next_pos in valid_moves:
                return True
        return False