from typing import Callable, List
from abc import ABC, abstractmethod
from enum import Enum


class PieceColor(Enum):
    BLACK = "black_piece"
    WHITE = "white_piece"


class ChessPiece(ABC):
    def __init__(self, color: PieceColor):
        self.color = color
        self.code = self.get_code()
        self.symbol = self.get_symbol()

    def get_color(self) -> PieceColor:
        return self.color

    @abstractmethod
    def get_move_mappers(self) -> List[Callable]:
        pass

    @abstractmethod
    def get_code(self) -> str:
        pass

    @abstractmethod
    def get_symbol(self) -> str:
        pass

    @abstractmethod
    def has_dynamic_possible_moves(self):
        pass


# A piece that has constant possible moves
class StaticChessPiece(ChessPiece, ABC):
    def has_dynamic_possible_moves(self):
        return False


# A piece that has variable possible moves
class DynamicChessPiece(ChessPiece, ABC):
    def has_dynamic_possible_moves(self):
        return True
