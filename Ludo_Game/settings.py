"""
This module contains the settings of the game.

Colors:
    GREEN: Color of the green player.
    RED: Color of the red player.
    YELLOW: Color of the yellow player.
    BLUE: Color of the blue player.

Board:
    SQUARE_SIZE: Size of the square.
    PANEL_WIDTH: Width of the panel.
    PANEL_HEIGHT: Height of the panel.
    BOARD_WIDTH: Width of the board.
    BOARD_HEIGHT: Height of the board.
    POINTS: List of the points.
    POSITIVE_V: List of the positive vertical squares.
    POSITIVE_H: List of the positive horizontal squares.

Player:
    PLAYER_WIDTH: Width of the player.
    PLAYER_HEIGHT: Height of the player.
    PLAYER_RADIUS: Radius of the player.
    PLAYER_COLOR: Color of the player.
    PLAYER_OUTLINE: Outline of the player.
    PLAYER_OUTLINE_WIDTH: Width of the outline of the player.
    PLAYER_OUTLINE_COLOR: Color of the outline of the player.
    PLAYER_TEXT_COLOR: Color of the text of the player.
    PLAYER_TEXT_SIZE: Size of the text of the player.
    PLAYER_TEXT_FONT: Font of the text of the player.
    PLAYER_TEXT_OFFSET: Offset of the text of the player.

Text
"""
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
)

logger = logging.getLogger("ludo")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    "ludo.log",
    mode='a'
)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class Color:
    """This class contains the colors used in the game."""

    GREEN = '#0CED2C'
    RED = '#F71313'
    YELLOW = '#FFFF00'
    BLUE = '#3575EC'
    DEFAULT = '#E9E9E9'
    CYAN = '#4EB1BA'
    GRAY = '#A9A9A9'


class Board:
    """This class contains the board settings."""

    SQUARE_SIZE = 40
    PANEL_WIDTH = 600
    PANEL_HEIGHT = 640
    BOARD_WIDTH = 640
    BOARD_HEIGHT = 640
    POINTS = [(0, 0), (0, 1), (1, 0), (1, 1)]
    POSITIVE_V = [(6, 2), (8, 1), (6, 13), (8, 12)]
    POSITIVE_H = [(1, 6), (2, 8), (13, 8), (12, 6)]


class Text:
    """This class contains the text used in the game."""

    MADE_BY = 'Made By: Mansi Agrawal & Shivam Gupta'
    HEADER = 'LUDO - THE GAME'


class Path:
    """This class contains the path of the game."""

    gx = None
    gy = None
    ry = None
    by = None
    count = None

    def __init__(self):
        """This method initializes the path of the game."""
        self.green_path = []
        self.red_path = []
        self.blue_path = []
        self.yellow_path = []

    def update_coordinates(self, gx, gy, ry, by, count):
        """
        This method updates the coordinates of the path.
        """
        self.gx = gx
        self.gy = gy
        self.ry = ry
        self.by = by
        self.count = count

    def start_populating(self):
        """This method populates the path of the game."""
        # 1
        self.update_coordinates(60, 260, 540, 340, 5)
        self.direct(pow_index=0, direction='right')
        # 2
        self.update_coordinates(260, 220, 340, 380, 5)
        self.direct(pow_index=3, direction='up')
        # 3
        self.update_coordinates(260, 20, 340, 580, 3)
        self.direct(direction='right')
        # 4
        self.update_coordinates(340, 60, 260, 540, 5)
        self.direct(pow_index=0, direction='down')
        # 5
        self.update_coordinates(380, 260, 220, 340, 5)
        self.direct(pow_index=3, direction='right')
        # 6
        self.update_coordinates(580, 260, 20, 340, 3)
        self.direct(direction='down')
        # 7
        self.update_coordinates(540, 340, 60, 260, 5)
        self.direct(pow_index=0, direction='left')
        # 8
        self.update_coordinates(340, 380, 260, 220, 5)
        self.direct(pow_index=3, direction='down')
        # 9
        self.update_coordinates(340, 580, 260, 20, 3)
        self.direct(direction='left')
        # 10
        self.update_coordinates(260, 540, 340, 60, 5)
        self.direct(pow_index=0, direction='up')
        # 11
        self.update_coordinates(220, 340, 380, 260, 6)
        self.direct(pow_index=3, direction='left')
        # 12
        self.update_coordinates(20, 300, 580, 300, 7)
        self.direct(direction='right')

    def direct_horizontal(self, k, pow_index=-1):
        """This method populates the path of the game in horizontal direction."""
        for i in range(self.count):
            if i == pow_index:
                p = 1
            else:
                p = 0
            self.green_path.append(
                (self.gx + k*i*Board.SQUARE_SIZE, self.gy, p))
            self.red_path.append((self.gy, self.ry - k*i*Board.SQUARE_SIZE, p))
            self.blue_path.append(
                (self.ry - k*i*Board.SQUARE_SIZE, self.by, p))
            self.yellow_path.append(
                (self.by, self.gx + k*i*Board.SQUARE_SIZE, p))

    def direct_vertical(self, k, pow_index=-1):
        """This method populates the path of the game in vertical direction."""
        for i in range(self.count):
            if i == pow_index:
                p = 1
            else:
                p = 0
            self.green_path.append(
                (self.gx, self.gy - k*i*Board.SQUARE_SIZE, p))
            self.red_path.append((self.gy - k*i*Board.SQUARE_SIZE, self.ry, p))
            self.blue_path.append(
                (self.ry, self.by + k*i*Board.SQUARE_SIZE, p))
            self.yellow_path.append(
                (self.by + k*i*Board.SQUARE_SIZE, self.gx, p))

    def direct(self, direction, pow_index=-1):
        """This method populates the path of the game in any direction."""
        if direction == 'right':
            self.direct_horizontal(1, pow_index=pow_index)
        elif direction == 'up':
            self.direct_vertical(1, pow_index=pow_index)
        elif direction == 'left':
            self.direct_horizontal(-1, pow_index=pow_index)
        elif direction == 'down':
            self.direct_vertical(-1, pow_index=pow_index)


path = Path()
path.start_populating()