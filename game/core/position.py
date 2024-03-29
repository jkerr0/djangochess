from typing import List


class Position:
    def __init__(self, x: int, y: int):
        self._x_coord = x
        self._y_coord = y
        self.id = self.inx()

    @staticmethod
    def from_inx(inx: int):
        return Position(inx % 8, inx // 8)

    @staticmethod
    def from_str(code: str):
        x = ord(code[0]) - ord('a')
        y = int(code[1]) - 1

        return Position(x, y)

    def x(self) -> int:
        return self._x_coord

    def y(self) -> int:
        return self._y_coord

    def inx(self) -> int:
        return self._x_coord + 8 * self._y_coord

    def is_valid(self) -> bool:
        return self.x() in range(0, 8) and self.y() in range(0, 8)

    def __str__(self) -> str:
        return f"{chr(ord('a') + self.x())}{self.y() + 1}"

    def __eq__(self, other):
        return self.inx() == other.inx()


class Move:
    def __init__(self, start_pos: Position, end_pos: Position):
        self._start_pos = start_pos
        self._end_pos = end_pos

    @staticmethod
    def from_str(code: str):
        start_pos = Position.from_str(code[0:2])
        end_pos = Position.from_str(code[2:4])
        return Move(start_pos, end_pos)

    @staticmethod
    def from_str_list(code_list: List[str]):
        return list(map(Move.from_str, code_list))

    @staticmethod
    def from_indexes(start_inx: int, end_inx: int):
        return Move(Position.from_inx(start_inx), Position.from_inx(end_inx))

    def as_dict(self):
        return {'start_pos': self._start_pos.inx(),
                'end_pos': self._end_pos.inx()}

    def get_start(self) -> Position:
        return self._start_pos

    def get_end(self) -> Position:
        return self._end_pos

    def __str__(self):
        return str(self._start_pos) + str(self._end_pos)

    def __eq__(self, other):
        return str(self) == str(other)
