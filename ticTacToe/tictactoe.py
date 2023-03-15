#!/usr/bin/python3
import random


def display_board(board):
    print(" {} | {} | {} ".format(*board[:3]))
    print("---+---+---")
    print(" {} | {} | {} ".format(*board[3:6]))
    print("---+---+---")
    print(" {} | {} | {} ".format(*board[6:9]))
    print()


def player_move(board, player, position):
    board[position] = player
    return board


def get_player_move(board, player):
    while True:
        try:
            position = int(
                input(f"Player {player}, make your move (1-9): ")) - 1
            if position < 0 or position > 8:
                raise ValueError
            if board[position] != " ":
                print("Position is already occupied.")
                continue
            return position
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 9.")


def get_computer_move(board, computer):
    print(f"Computer ({computer}), is making its move...")
    possible_moves = [i for i in range(9) if board[i] == " "]
    move = random.choice(possible_moves)
    return move


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


def get_game_mode():
    while True:
        mode = input("Select game mode (PvP, PvC, CvC): ")
        if mode.lower() not in ["pvp", "pvc", "cvc"]:
            print("Invalid input. Please select a valid game mode.")
            continue
        return mode.lower()


def get_player_symbols():
    while True:
        player1 = input("Player 1, select your symbol (X or O): ")
        if player1.lower() not in ["x", "o"]:
            print("Invalid input. Please select either X or O.")
            continue
        player2 = "X" if player1.lower() == "o" else "O"
        return player1.upper(), player2


def run_game():
    mode = get_game_mode()
    player1_symbol, player2_symbol = get_player_symbols()
    board = [" " for i in range(9)]
    current_player = player1_symbol
    while True:
        display_board(board)
        if mode == "pvp":
            position = get_player_move(board, current_player)
        elif mode == "pvc" and current_player == player1_symbol:
            position = get_player_move(board, current_player)
        else:
            position = get_computer_move(board, current_player)
        board = player_move(board, current_player, position)
        if check_win(board, current_player):
            display_board(board)
            print(f"Player {current_player} wins!")
            break
        elif check_draw(board):
            display_board(board)
            print("It's a draw!")
            break
        current_player = player2_symbol if current_player == player1_symbol else player1_symbol


if __name__ == '__main__':
    run_game()
