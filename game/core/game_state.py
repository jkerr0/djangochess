from game.core.chesspiece import PieceColor
from game.core.move_graph import MoveGraph


class GameState:
    def __init__(self, move_graph: MoveGraph, turn: PieceColor):
        self.move_graph = move_graph
        self.turn = turn

    def is_check(self) -> bool:
        return bool(self.move_graph.get_check_attacks())

    def is_checkmate(self) -> bool:
        return self.is_check() and not self.can_player_move()

    def is_draw(self):
        return not self.is_check() and not self.can_player_move()

    def can_player_move(self) -> bool:
        return bool(self.move_graph.get_moves_by_piece_color(self.turn))

    def get_turn(self) -> PieceColor:
        return self.turn

    def as_dict(self) -> dict:
        return {
            'turn': self.turn.value,
            'is_check': self.is_check(),
            'is_checkmate': self.is_checkmate(),
            'is_draw': self.is_draw()
        }
