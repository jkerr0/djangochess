from enum import Enum

from game.core.position import Position
from game.core.chesspiece import ChessPiece


class FieldColor(Enum):
    WHITE = "white_field"
    BLACK = "black_field"


class Field:
    def __init__(self, position: Position, piece: ChessPiece):
        self.position = position
        self.piece = piece
        self.color = self.find_color()

    def find_color(self) -> FieldColor:
        return FieldColor.BLACK if (self.position.y() + self.position.x()) % 2 == 0\
            else FieldColor.WHITE
