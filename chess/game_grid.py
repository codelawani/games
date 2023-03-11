from textual.app import App, ComposeResult
from textual.widgets import Static


class Board(App):
    CSS_PATH = "grid.css"

    def compose(self) -> ComposeResult:
        for x in "87654321":
            for y in "ABCDEFGH":
                yield Static(y+x, classes="box")

if __name__ == "__main__":
    app = Board()
    app.run()

