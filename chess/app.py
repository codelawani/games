from typing import Literal
from textual.containers import Vertical, Horizontal, Container
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.widget import Widget
from textual.reactive import reactive
from rich.table import Table
from rich import box
from rich.panel import Panel
from itertools import cycle
from rich.segment import Segment

symbols = {
	'P': "♟",
	'N': "♞",
	'B': "♝",
	'R': "♜",
	'Q': "♛",
	'K': "♚",
	'p': "♙",
	'n': "♘",
	'b': "♗",
	'r': "♖",
	'q': "♕",
	'k': "♔",
}

names = {
	'p': "Pawn",
	'n': "Knight",
	'b': "Bishop",
	'r': "Rook",
	'q': "Queen",
	'k': "King",
}

"""
black_symbols = {
	'p': "♙",
	'n': "♘",
	'b': "♗",
	'r': "♖",
	'q': "♕",
	'k': "♔",
}  # black symbols
"""

board = [
	['R', 'N', 'B', 'Q', 'K', 'R', 'N', 'R'],
	['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
	['.', '.', '.', '.', '.', '.', '.', '.'],
	['.', '.', '.', '.', '.', '.', '.', '.'],
	['.', '.', '.', '.', '.', '.', '.', '.'],
	['.', '.', '.', '.', '.', '.', '.', '.'],
	['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
	['r', 'n', 'b', 'q', 'k', 'r', 'n', 'r']
]

alphas = "abcdefgh"
digits = "12345678"

def get_piece(symbol: str) -> 'Piece':
	"""
	return a chess piece from a symbol
	"""
	char = symbols.get(symbol.upper(), ' ')
	color = "black" if symbol.isupper() else "white"
	name = names.get(symbol.lower(), '')
	return Piece(char, color=color, name=name)


def humanize_coords(coords: tuple[int, int]) -> str:
	"""
	translate a board coordinate into a friendly form
	"""
	return f"{'abcdefgh'[coords[0]]}{coords[1]}"



class Cell(Container):
	"""a cell on a chessboard"""

	def __init__(self, coords: tuple[int, int],
				color: Literal['light', 'dark']):
		self.cell_coords = coords
		cell_id = "cell-" + humanize_coords(coords)
		piece = get_piece(board[coords[0]][coords[1]])
		super().__init__(piece, classes=color, id=cell_id)

	def on_click(self):
		if self.has_class("selected"):
			self.remove_class("selected")
		else:
			for cell in self.app.query(Cell):
				cell.remove_class("selected")
			self.add_class("selected")

class Piece(Static):
	"""a chess piece"""

	def __init__(self, symbol, color, name):
		self.piece_name = name
		self.piece_color = color
		super().__init__(symbol, classes=color)


class PieceInfo(Static):
	"""shows you the selected piece"""
	default = "Select A Piece To Move"


class LeftIndicators(Vertical):
	def __init__(self):
		indicators = []
		for i in range(8):
			indicators.append(Static(alphas[i], classes="indicator"))
		super().__init__(*indicators, id="left-indicators")


class BottomIndicators(Horizontal):
	def __init__(self):
		indicators = []
		for i in range(8):
			indicators.append(Static(digits[i], classes="indicator"))
		super().__init__(*indicators, id="bottom-indicators")




class ChessApp(App):
	CSS_PATH = "app.css"

	def compose(self) -> ComposeResult:
		style = cycle(("light", "dark"))
		rows: list[Horizontal] = []
		for r in range(8):
			cells: list[Cell] = []
			for c in range(8):
				cell = Cell((r,c), next(style))
				cells.append(cell)
			rows.append(Horizontal(
				*cells, id=f"board-row{r}",
				classes="board-row"
			))
			next(style)
		board = Vertical(*rows, id="board")
		
		yield Header()
		yield Vertical(*rows)
		yield board

if __name__ == "__main__":
	app = ChessApp()
	app.run()

