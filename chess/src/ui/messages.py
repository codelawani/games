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

    def __init__(self, sender: MessageTarget, promotion: int) -> None:
        super().__init__(sender)
        self.promotion = promotion


class PieceSelected(Message):
    """Message to select a piece."""

    def __init__(self, sender: MessageTarget, coords: CoordT) -> None:
        super().__init__(sender)
        self.coords = coords


class PieceDeselected(Message):
    """Message to deselect a piece."""

    def __init__(self, sender: MessageTarget, coords: CoordT) -> None:
        super().__init__(sender)
        self.coords = coords


class SwitchPlayer(Message):
    """Message to switch player."""

    pass
