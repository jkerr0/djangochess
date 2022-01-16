from typing import Callable, List, Optional
from abc import ABC, abstractmethod
from enum import Enum


class PieceColor(Enum):
    BLACK = "black_piece"
    WHITE = "white_piece"

    @classmethod
    def enemy_color(cls, color):
        return cls.WHITE if color is cls.BLACK else cls.BLACK


class ChessPiece(ABC):
    def __init__(self, color: PieceColor):
        self.color = color
        self.code = self.get_code()
        self.symbol = self.get_symbol()
        self._has_moved = False

    def get_color(self) -> PieceColor:
        return self.color

    @abstractmethod
    def get_move_mappers(self) -> List[Callable]:
        pass

    def get_attack_mappers(self) -> Optional[List[Callable]]:
        return None

    @abstractmethod
    def get_code(self) -> str:
        pass

    @abstractmethod
    def get_symbol(self) -> str:
        pass

    @abstractmethod
    def has_dynamic_possible_moves(self):
        pass

    def mark_moved(self) -> None:
        self._has_moved = True

    def has_moved(self) -> bool:
        return self._has_moved


# A piece that has constant possible moves
class StaticChessPiece(ChessPiece, ABC):
    def has_dynamic_possible_moves(self):
        return False


# A piece that has variable possible moves
class DynamicChessPiece(ChessPiece, ABC):
    def has_dynamic_possible_moves(self):
        return True
