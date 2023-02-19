#!/usr/bin/python3


""" def display_board(board):
    print(" {} | {} | {} ".format(board[0], board[1], board[2]))
    print("---+---+---")
    print(" {} | {} | {} ".format(board[3], board[4], board[5]))
    print("---+---+---")
    print(" {} | {} | {} ".format(board[6], board[7], board[8]))
 """


def display_board(board):

    print(" {} | {} | {} ".format(*board[:3]))
    print("---+---+---")
    print(" {} | {} | {} ".format(*board[3:6]))
    print("---+---+---")
    print(" {} | {} | {} ".format(*board[6:9]))


def player_move(board, player, position):
    board[position] = player
    return board


""" def check_win(board, player):
    # Horizontal wins
    if board[0] == board[1] == board[2] == player or \
       board[3] == board[4] == board[5] == player or \
       board[6] == board[7] == board[8] == player:
        return True
    # Vertical wins
    elif board[0] == board[3] == board[6] == player or \
            board[1] == board[4] == board[7] == player or \
            board[2] == board[5] == board[8] == player:
        return True
    # Diagonal wins
    elif board[0] == board[4] == board[8] == player or \
            board[2] == board[4] == board[6] == player:
        return True
    else:
        return False """


def check_win(board, player):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Horizontal wins
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Vertical wins
        [0, 4, 8], [2, 4, 6]  # Diagonal wins
    ]
    for condition in win_conditions:
        if all(board[i] == player for i in condition):
            return True
    return False


def check_draw(board):
    return all(cell != " " for cell in board)


def run_game():
    board = [" " for i in range(9)]
    players = ["X", "O"]
    current_player = 0

    while True:
        display_board(board)
        print(f"Player {players[current_player]}, make your move (0-8):")
        position = int(input())
        board = player_move(board, players[current_player], position)
        if check_win(board, players[current_player]):
            display_board(board)
            print(f"Player {players[current_player]} wins!")
            break
        elif check_draw(board):
            display_board(board)
            print("It's a draw!")
            break
        current_player = (current_player + 1) % 2


if __name__ == '__main__':
    run_game()
