from .chess import Chess
import sys
import pydoc

from .epd import get_EPD

WELCOME = '''
****************************
  Welcome to Console Chess
****************************
'''

HELP = '''\
Playing Pieces
______________

Pawn    ➜  ♟
Knight  ➜  ♞
Bishop  ➜  ♝
Rook    ➜  ♜
Queen   ➜  ♛
King    ➜  ♚
	

Moving Pieces
_____________

This is how a board looks

   a   b   c   d   e   f   g   h
   +---+---+---+---+---+---+---+---+
8  | ♜ | ♞ | ♝ | ♛ | ♚ | ♝ | ♞ | ♜ |  8
   +---+---+---+---+---+---+---+---+
7  | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ |  7
   +---+---+---+---+---+---+---+---+
6  |   |   |   |   |   |   |   |   |  6
   +---+---+---+---+---+---+---+---+
5  |   |   |   |   |   |   |   |   |  5
   +---+---+---+---+---+---+---+---+
4  |   |   |   |   |   |   |   |   |  4
   +---+---+---+---+---+---+---+---+
3  |   |   |   |   |   |   |   |   |  3
   +---+---+---+---+---+---+---+---+
2  | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ |  2
   +---+---+---+---+---+---+---+---+
1  | ♖ | ♘ | ♗ | ♕ | ♔ | ♗ | ♘ | ♖ |  1
   +---+---+---+---+---+---+---+---+
     a   b   c   d   e   f   g   h



To move pieces cross the board, use the following coordinate system


+----+----+----+----+----+----+----+----+
| a8 | b8 | c8 | d8 | e8 | f8 | g8 | h8 |
+----+----+----+----+----+----+----+----+
| a7 | b7 | c7 | d7 | e7 | f7 | g7 | h7 |
+----+----+----+----+----+----+----+----+
| a6 | b6 | c6 | d6 | e6 | f6 | g6 | h6 |
+----+----+----+----+----+----+----+----+
| a5 | b5 | c5 | d5 | e5 | f5 | g5 | h5 |
+----+----+----+----+----+----+----+----+
| a4 | b4 | c4 | d4 | e4 | f4 | g4 | h4 |
+----+----+----+----+----+----+----+----+
| a3 | b3 | c3 | d3 | e3 | f3 | g3 | h3 |
+----+----+----+----+----+----+----+----+
| a2 | b2 | c2 | d2 | e2 | f2 | g2 | h2 |
+----+----+----+----+----+----+----+----+
| a1 | b1 | c1 | d1 | e1 | f1 | g1 | h1 |
+----+----+----+----+----+----+----+----+

_____________________________________________________________________

Imagine you had a board like this...

     a   b   c   d   e   f   g   h
   +---+---+---+---+---+---+---+---+
8  | ♜ | ♞ | ♝ | ♛ | ♚ | ♝ | ♞ | ♜ |  8
   +---+---+---+---+---+---+---+---+
7  | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ | ♟ |  7
   +---+---+---+---+---+---+---+---+
6  |   |   |   |   |   |   |   |   |  6
   +---+---+---+---+---+---+---+---+
5  |   |   |   |   |   |   |   |   |  5
   +---+---+---+---+---+---+---+---+
4  |   |   |   |   |   |   |   |   |  4
   +---+---+---+---+---+---+---+---+
3  |   |   |   |   |   |   |   |   |  3
   +---+---+---+---+---+---+---+---+
2  | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ | ♙ |  2
   +---+---+---+---+---+---+---+---+
1  | ♖ | ♘ | ♗ | ♕ | ♔ | ♗ | ♘ | ♖ |  1
   +---+---+---+---+---+---+---+---+
     a   b   c   d   e   f   g   h


To move pieces on this board, you will need to use the standard chess notation for coordinates. The vertical columns are labeled from a to h, and the horizontal rows are labeled from 1 to 8.

For example, to move the pawn in front of the king two spaces forward, you would use the coordinates e2 to e4. To move the knight from b1 to c3, you would use the coordinates b1 to c3.

To capture an opposing piece, simply move your piece to the square occupied by the opposing piece. For instance, to capture the pawn on e4 with the bishop on c4, you would use the coordinates c4 to e4.

It is important to always indicate both the starting and ending squares when moving a piece. For example, if you want to move the bishop from f1 to c4, you would use the coordinates f1 to c4.
'''

if len(sys.argv) > 1 and sys.argv[1].strip() in ("--help", "-h", "help"):
    pydoc.pager(WELCOME + '\n' + HELP)
    sys.exit(0);

print(WELCOME)
chess_game = Chess()
while True:
    if chess_game.p_move == 1:
        print("\nIt's White's turn (UPPERCASE)\n")
    else:
        print("\nIt's Black's Turn (lowercase)\n")
    chess_game.display()
    if (chess_game.p_move == 1) or (chess_game.p_move == -1):
        cur = input('What piece do you want to move?\n')
        next = input('Where do you want to move the piece to?\n')
    valid = False
    if chess_game.move(cur, next) == False:
        print('Invalid move')
    else:
        valid = True
    state = chess_game.is_end()
    if state == [0, 0, 0]:
        if chess_game.check_state(get_EPD(chess_game)) == 'PP':
            print(chess_game.pawn_promotion())
    if sum(state) > 0:
        print('\n*********************\n      GAME OVER\n*********************\n')
        chess_game.display()
        print('Game Log:\n---------\n')
        print(f'INITIAL POSITION = {chess_game.initial_pos}')
        print(f'MOVES = {chess_game.log}')
        print('\nGame Result:\n------------\n')
        if state == [0, 0, 1]:
            print('BLACK WINS')
        elif state == [1, 0, 0]:
            print('WHITE WINS')
        else:
            print('TIE GAME')
        break
    if valid == True:
        chess_game.p_move = chess_game.p_move * (-1)
