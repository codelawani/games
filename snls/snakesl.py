#!/usr/bin/python3
""" game_board = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]
count = 1
for row in range(9, -1, -1):
    if row % 2 == 1:  # odd row, start from the right
        for col in range(9, -1, -1):
            game_board[row][col] = count
            count += 1
    else:  # even row, start from the left
        for col in range(10):
            game_board[row][col] = count
            count += 1
for row in game_board:
    print(row) """


class Game:
    def __init__(self):
        self.board = [[0] * 10 for _ in range(10)]
        self.snakes = {16: 6, 46: 25, 49: 11, 62: 19,
                       64: 60, 74: 53, 89: 68, 92: 88, 95: 75, 99: 80}
        self.ladders = {1: 38, 4: 14, 9: 31, 21: 42,
                        28: 84, 36: 44, 51: 67, 71: 91, 80: 100}
        self.players = []
        self.current_player = None

        # Place snakes on the board
        for start, end in self.snakes.items():
            self.board[self.get_row(start)][self.get_col(start)] = end-start

        # Place ladders on the board
        for start, end in self.ladders.items():
            self.board[self.get_row(start)][self.get_col(start)] = end-start

        # Number the cells in a serpentine pattern
        counter = 1
        for i in range(9, -1, -1):
            if i % 2 == 1:
                for j in range(9, -1, -1):
                    self.board[i][j] = counter
                    counter += 1
            else:
                for j in range(10):
                    self.board[i][j] = counter
                    counter += 1

    def get_row(self, cell_num):
        row = (cell_num - 1) // 10
        if row % 2 == 0:
            col = (cell_num - 1) % 10
        else:
            col = 9 - (cell_num - 1) % 10
        return row

    def get_col(self, cell_num):
        row = (cell_num - 1) // 10
        if row % 2 == 0:
            col = (cell_num - 1) % 10
        else:
            col = 9 - (cell_num - 1) % 10
        return col
