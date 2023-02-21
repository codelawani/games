from chess import Chess
import sys

WELCOME = '''
****************************
  Welcome to Console Chess
****************************
'''

HELP = '''\
White = UPPERCASE
Black = lowercase

Playing Pieces
--------------
    P,p = Pawn
    N,n = Knight
    B,b = Bishop
    R,r = Rook
    Q,q = Queen
    K,k = King

When asked where you want to moves please use the following cordinate system:

    a8 b8 c8 d8 e8 f8 g8 h8
    a7 b7 c7 d7 e7 f7 g7 h7
    a6 b6 c6 d6 e6 f6 g6 h6
    a5 b5 c5 d5 e5 f5 g5 h5
    a4 b4 c4 d4 e4 f4 g4 h4
    a3 b3 c3 d3 e3 f3 g3 h3
    a2 b2 c2 d2 e2 f2 g2 h2
    a1 b1 c1 d1 e1 f1 g1 h1
'''

if len(sys.argv) > 1 and sys.argv[1].strip() in ("--help", "-h", "help"):
    print(WELCOME)
    print(HELP)
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
        if chess_game.check_state(chess_game.EPD_hash()) == 'PP':
            print(chess_game.pawn_promotion())
    if sum(state) > 0:
        print('\n*********************\n      GAME OVER\n*********************\n')
        chess_game.display()
        print('Game Log:\n---------\n')
        print(f'INITIAL POSITION = {chess_game.init_pos}')
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
