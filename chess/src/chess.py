from copy import deepcopy
import sys
from typing import cast
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich import print as rprint
from textual.reactive import reactive
from .epd import CoordT, get_EPD, get_coords, load_EPD, EPDString
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
        load_EPD(self, epd)

    def reset(self, epd: EPDString):
        """
        Resets the Chess game to its initial state.

        Args:
            epd (str): The EPD string representing the starting position
            of the game. Defaults to the standard starting position.
        Returns:
            None
        The method resets the game state by resetting the
        - game log
        - EPD hashtable
        - current player's move
        - castling control,
        - en passant control
        - previous move
        - and board
        The method then loads in the EPD string to set the game to its
        starting position.
        """
        self.__init__(epd)


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
        if self.valid_move(cp, np) == False:
            return False
        part = self.board[cp[1]][cp[0]]
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
        self.board[cp[1]][cp[0]] = 0
        self.board[np[1]][np[0]] = part
        hash = get_EPD(self)
        if hash in self.epd_hash:
            self.epd_hash[hash] += 1
        else:
            self.epd_hash[hash] = 1
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
        piece = self.board[cur_pos[1]][cur_pos[0]]
        if piece == 0 or piece * self.player < 0:
            return False
        if piece * self.player > 0 and piece != 0:
            p_cls = notations.get_class(piece)
            v_moves = p_cls.moves(self, self.player, cur_pos)
            if len(self.log) > 0 and "+" in self.log[-1]:
                v_moves = [
                    m
                    for m in v_moves
                    if cur_pos in self.c_escape
                    and m in self.c_escape[cur_pos]
                ]
            if next_pos in v_moves:
                return True
        return False

    def possible_board_moves(self):
        """
        Returns a dictionary of all possible moves on the current board for each piece,
        where the key is a string representing the piece's position and the value is a list
        of possible next positions.

        Returns:
            dict: A dictionary of all possible moves on the current board for each piece.
        """
        moves = {}
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece == 0:
                    continue
                p_cls = notations.get_class(piece)
                p_colour = 1 if piece > 0 else -1
                v_moves = p_cls.moves(self, p_colour, (c, r))
                if len(self.log) > 0 and "+" in self.log[-1]:
                    v_moves = [
                        m
                        for m in v_moves
                        if (c, r) in self.c_escape
                        and m in self.c_escape[(c, r)]
                    ]
                moves[
                    f"{str(self.x[c]).upper() if p_colour > 0 else str(self.x[c]).lower()}{self.y[r]}"
                ] = v_moves
        return moves

    def is_checkmate(self, moves):
        """
        Determines if the current board state is a checkmate, indicating the end of the game.

        Args:
            moves (dict): A dictionary containing the current possible moves for each piece on the board.

        Returns:
            A list containing three elements:
                1. If the game is over (1 if True, 0 if False)
                2. The score for White (an integer)
                3. The score for Black (an integer)
        """
        self.c_escape = {}
        k_pos: tuple = ()  # King position
        p_blocks = []  # Possible blocks
        u_moves = {}  # User potential moves
        # Sort all possible moves
        for p, a in moves.items():
            pos: CoordT = get_coords(p) # type: ignore
            if (str(p[0]).isupper() and self.player == -1) or (
                str(p[0]).islower() and self.player == 1
            ):
                if self.board[pos[1]][pos[0]] == notations.get_id('k') * (
                    (self.player * -1)):
                    k_pos = (pos, a)
                else:
                    for m in a:
                        if (pos, m) not in p_blocks:
                            p_blocks.append((pos, m))
            else:
                if pos not in u_moves:
                    u_moves[pos] = a
        k_pos = cast(tuple, k_pos)
        p_moves = [m for a in u_moves.values() for m in a]
        # Check if checkmate is in posible moves
        if len(k_pos) > 0 and k_pos[0] not in p_moves:
            return [0, 0, 0]
        elif len(k_pos) == 0:
            for y, row in enumerate(self.board):
                if notations.get_id('k') * (self.player * -1) in row:
                    k_pos = ((
                        row.index(
                            notations.get_id('k') * (self.player * -1)),
                        y),[])
                    break
        k_pos = cast(tuple, k_pos)
        if len(k_pos) > 0 and k_pos[0] in p_moves:
            for m in p_blocks:
                i_game = deepcopy(self)
                i_game.p_move = i_game.p_move * (-1) # type: ignore
                i_game.move(
                    f"{self.x[m[0][0]]}{self.y[m[0][1]]}",
                    f"{self.x[m[1][0]]}{self.y[m[1][1]]}",
                )  # Move king
                i_game.p_move = i_game.p_move * (-1) # type: ignore
                i_moves = i_game.possible_board_moves()  # Imaginary moves
                if True not in [
                    True for k in i_moves if k_pos[0] in i_moves[k]
                ]:  # Check if moved king still in check
                    # if len(self.log) > 0 and self.log[-1][-1] is not '+':
                    # self.log[-1] += '+' #Check
                    # print(m,f'{self.x[m[0][0]]}{self.y[m[0][1]]}', f'{self.x[m[1][0]]}{self.y[m[1][1]]}')
                    if m[0] in self.c_escape:
                        self.c_escape[m[0]].append(m[1])
                    else:
                        self.c_escape[m[0]] = [m[1]]
                    # return [0, 0, 0]
            for m in k_pos[1]:
                if m not in p_moves:
                    i_game = deepcopy(self)
                    i_game.p_move = i_game.p_move * (-1) # type: ignore
                    i_game.move(
                        f"{self.x[k_pos[0][0]]}{self.y[k_pos[0][1]]}",
                        f"{self.x[m[0]]}{self.y[m[1]]}",
                    )  # Move king
                    i_game.p_move = i_game.p_move * (-1) # type: ignore
                    i_moves = i_game.possible_board_moves()  # Imaginary moves
                    if True not in [
                        True for k in i_moves if m in i_moves[k]
                    ]:  # Check if moved king still in check
                        # if len(self.log) > 0 and self.log[-1][-1] is not '+':
                        # self.log[-1] += '+' #Check
                        # print(m)
                        # print(k_pos[0],m,f'{self.x[k_pos[0][0]]}{self.y[k_pos[0][1]]}', f'{self.x[m[0]]}{self.y[m[1]]}')
                        if k_pos[0] in self.c_escape:
                            self.c_escape[k_pos[0]].append(m)
                        else:
                            self.c_escape[k_pos[0]] = [m]
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
        else:
            return [1, 0, 0] if self.player == 1 else [0, 0, 1]

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

        * King and bishop against king and bishop with both bishops on squares of the same color
        * King and knight against king
        * King against king with no other pieces on the board

        Args:
            moves (int): The current move number.

        Returns:
            bool: True if the current position is a dead position, False otherwise.
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
