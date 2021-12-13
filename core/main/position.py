class Position:
    def __init__(self, x: int, y: int):
        self._x_coord = x
        self._y_coord = y

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

    def is_valid(self):
        return self.x() in range(0, 8) and self.y() in range(0, 8)

    def __str__(self) -> str:
        return f"{chr(ord('a') + self.x())}{self.y() + 1}"
