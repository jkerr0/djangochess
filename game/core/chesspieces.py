from typing import Callable, List, Optional

from game.core.position import Position
from game.core.chesspiece import StaticChessPiece, DynamicChessPiece, PieceColor, ChessPiece


def static_mapper(x_diff: int, y_diff: int) -> Callable:
    return lambda start_pos: Position(start_pos.x() + x_diff, start_pos.y() + y_diff)


def dynamic_mapper(x_diff_per_iter: int, y_diff_per_iter: int) -> Callable:
    return lambda start_pos, iter_num: Position(start_pos.x() + iter_num * x_diff_per_iter,
                                                start_pos.y() + iter_num * y_diff_per_iter)


class Knight(StaticChessPiece):
    def get_move_mappers(self) -> List[Callable]:
        x_offsets = [1, 2, 2, 1]
        y_offsets = [2, 1, -1, -2]

        positive_mappers = [static_mapper(x, y)
                            for x, y in zip(x_offsets, y_offsets)]
        x_offsets = list(map(lambda n: -n, x_offsets))
        y_offsets = list(map(lambda n: -n, y_offsets))
        negative_mappers = [static_mapper(x, y)
                            for x, y in zip(x_offsets, y_offsets)]

        return positive_mappers + negative_mappers

    def get_code(self) -> str:
        return 'N'

    def get_symbol(self) -> str:
        return "\u2658"


class King(StaticChessPiece):
    def get_move_mappers(self) -> List[Callable]:
        x_offsets = [0, 1, 1, 1, 0, -1, -1, -1]
        y_offsets = [1, 1, 0, -1, -1, -1, 0, 1]

        return [static_mapper(x, y)
                for x, y in zip(x_offsets, y_offsets)]

    def get_code(self) -> str:
        return 'K'

    def get_symbol(self) -> str:
        return "\u2654"


class Pawn(ChessPiece):
    def has_dynamic_possible_moves(self):
        return True

    def get_move_mappers(self) -> List[Callable]:
        return [static_mapper(0, self._get_direction()),
                lambda pos: self._start_double_move(pos)]

    def get_attack_mappers(self) -> List[Callable]:
        return [static_mapper(i, self._get_direction()) for i in (1, -1)]

    def _get_direction(self):
        return 1 if self.color == PieceColor.WHITE else -1 if self.color == PieceColor.BLACK else None

    def _get_starting_y(self):
        return 1 if self.color == PieceColor.WHITE else 6 if self.color == PieceColor.BLACK else None

    def _start_double_move(self, pos) -> Optional[Position]:
        return Position(pos.x(), pos.y() + 2 * self._get_direction()) if pos.y() == self._get_starting_y() else None

    def get_code(self) -> str:
        return 'p'

    def get_symbol(self) -> str:
        return "\u2659"


class Bishop(DynamicChessPiece):
    _slopes = [(1, 1), (1, -1), (-1, -1), (-1, 1)]

    def get_move_mappers(self) -> List[Callable]:
        return [dynamic_mapper(x, y)
                for x, y in Bishop._slopes]

    def get_code(self) -> str:
        return 'B'

    def get_symbol(self) -> str:
        return "\u2657"

    @classmethod
    def get_slopes(cls):
        return cls._slopes


class Rook(DynamicChessPiece):
    _slopes = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def get_move_mappers(self) -> List[Callable]:
        return [dynamic_mapper(x, y)
                for x, y in Rook._slopes]

    def get_code(self) -> str:
        return 'R'

    def get_symbol(self) -> str:
        return "\u2656"

    @classmethod
    def get_slopes(cls):
        return cls._slopes


class Queen(DynamicChessPiece):
    def get_move_mappers(self) -> List[Callable]:
        return [dynamic_mapper(x, y)
                for x, y in Rook.get_slopes() + Bishop.get_slopes()]

    def get_code(self) -> str:
        return 'Q'

    def get_symbol(self) -> str:
        return "\u2655"
