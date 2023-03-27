from textual.message import Message, MessageTarget

from src.epd import CoordT


class NewGame(Message):
    """Message to start a new game."""

    pass


class PieceMoved(Message):
    """Message to move a piece."""

    pass


class PiecePromotion(Message):
    """Message to promote a piece."""

    def __init__(self, promotion: int) -> None:
        super().__init__()
        self.promotion = promotion


class PieceSelected(Message):
    """Message to select a piece."""

    def __init__(self, coords: CoordT) -> None:
        super().__init__()
        self.coords = coords


class PieceDeselected(Message):
    """Message to deselect a piece."""

    def __init__(self, coords: CoordT) -> None:
        super().__init__()
        self.coords = coords


class SwitchPlayer(Message):
    """Message to switch player."""
    pass

class Refresh(Message):
    """Message to refresh the board."""
    pass
