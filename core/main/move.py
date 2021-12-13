from position import Position


class Move:
    def __init__(self, start_pos: Position, end_pos: Position):
        self._start_pos = start_pos
        self._end_pos = end_pos

    @staticmethod
    def from_str(code: str):
        start_pos = Position.from_str(code[0:2])
        end_pos = Position.from_str(code[2:4])
        return Move(start_pos, end_pos)

    def get_start(self) -> Position:
        return self._start_pos

    def get_end(self) -> Position:
        return self._end_pos

    def __str__(self):
        return str(self._start_pos) + str(self._end_pos)
