from typing import Callable, List

from position import Position
from chess_piece import StaticChessPiece, DynamicChessPiece, PieceColor


class Knight(StaticChessPiece):
    def get_move_mappers(self) -> List[Callable]:
        x_offsets = [1, 2, 2, 1]
        y_offsets = [2, 1, -1, -2]

        positive_mappers = [lambda pos: Position(pos.x() + x, pos.y() + y)
                            for x, y in zip(x_offsets, y_offsets)]
        x_offsets = list(map(lambda n: -n, x_offsets))
        y_offsets = list(map(lambda n: -n, y_offsets))
        negative_mappers = [lambda pos: Position(pos.x() + x, pos.y() + y)
                            for x, y in zip(x_offsets, y_offsets)]

        return positive_mappers + negative_mappers

    def get_code(self) -> str:
        return 'N'


class King(StaticChessPiece):
    def get_move_mappers(self) -> List[Callable]:
        x_offsets = [0, 1, 1, 1, 0, -1, -1, -1]
        y_offsets = [1, 1, 0, -1, -1, -1, 0, 1]

        return [lambda pos: Position(pos.x() + x, pos.y() + y)
                for x, y in zip(x_offsets, y_offsets)]

    def get_code(self) -> str:
        return 'K'


class Pawn(StaticChessPiece):
    def get_move_mappers(self) -> List[Callable]:
        return [lambda pos: Position(pos.x(), pos.y() + self._get_direction()),
                lambda pos: self._start_double_move(pos)]

    def get_attack_mappers(self) -> List[Callable]:
        return [lambda pos, iteration: Position(pos.x() + i, pos.y() + self._get_direction())
                for i in (1, -1)]

    def _get_direction(self):
        return 1 if self.color == PieceColor.WHITE else -1 if self.color == PieceColor.BLACK else None

    def _get_starting_y(self):
        return 1 if self.color == PieceColor.WHITE else 6 if self.color == PieceColor.BLACK else None

    def _start_double_move(self, pos):
        return Position(pos.x(), pos.y() + 2 * self._get_direction()) if pos.y() == self._get_starting_y() else None

    def get_code(self) -> str:
        return ''


class Bishop(DynamicChessPiece):
    _slopes = [(1, 1), (1, -1), (-1, -1), (-1, 1)]

    def get_move_mappers(self) -> List[Callable]:
        return [lambda pos, iteration: Position(pos.x() + iteration * x, pos.y() + iteration * y)
                for x, y in Bishop._slopes]

    def get_code(self) -> str:
        return 'B'

    @classmethod
    def get_slopes(cls):
        return cls._slopes


class Rook(DynamicChessPiece):
    _slopes = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def get_move_mappers(self) -> List[Callable]:
        return [lambda pos, iteration: Position(pos.x() + iteration * x, pos.y() + iteration * y)
                for x, y in Rook._slopes]

    def get_code(self) -> str:
        return 'R'

    @classmethod
    def get_slopes(cls):
        return cls._slopes


class Queen(DynamicChessPiece):
    def get_move_mappers(self) -> List[Callable]:
        return [lambda pos, iteration: Position(pos.x() + iteration * x, pos.y() + iteration * y)
                for x, y in Rook.get_slopes() + Bishop.get_slopes()]

    def get_code(self) -> str:
        return 'Q'
