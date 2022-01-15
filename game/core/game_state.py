from typing import List

from game.core.chessboard import Chessboard, Position
from game.core.chesspiece import DynamicChessPiece
from game.core.chesspieces import King
from game.core.move_graph import MoveGraph, flatten

from game.core.position import Move


class GameState:
    def __init__(self, board: Chessboard, graph: MoveGraph):
        self.move_graph = graph
        self.board = board

    def is_check(self) -> bool:
        return any(map(self.is_attacked,
                       self.board.get_pieces_positions_by_type(King)))

    def is_attacked(self, pos: Position) -> bool:
        return bool(self.get_attacks_at_pos(pos))

    def can_piece_at_position_move(self, pos: Position) -> bool:
        return bool(self.move_graph.get_moves_by_start(pos))

    def can_attacking_piece_be_counterattacked(self, pos: Position) -> bool:
        if len(self.get_attacks_at_pos(pos)) != 1:
            return False

        return bool(self.get_counterattacks_at_pos(pos))

    def get_attacks_at_pos(self, pos: Position) -> List[Move]:
        return self.move_graph.get_moves_by_end(pos)

    def get_counterattacks_at_pos(self, pos: Position) -> List[Move]:
        return flatten(list(map(self.get_attacks_at_pos,
                                map(Move.get_start, self.get_attacks_at_pos(pos)))))

    def can_piece_be_covered(self, piece_pos: Position) -> bool:
        attacks = self.get_attacks_at_pos(piece_pos)
        dynamic_attacks = list(
            filter(lambda move: isinstance(self.board.get_piece(move.get_start()), DynamicChessPiece), attacks))

        if len(dynamic_attacks) != 1:
            return False

        return self.get_covering_moves_for_dynamic_attacker(dynamic_attacks.pop()) != []

    def get_covering_moves_for_dynamic_attacker(self, attack_move: Move) -> List[Move]:
        defended_color = self.board.get_piece(attack_move.get_end()).get_color()
        attacker_directions = self.move_graph.get_dynamic_piece_directions(attack_move.get_start())
        attacking_direction = next(filter(lambda direction: attack_move.get_end() in direction, attacker_directions))
        return list(filter(lambda move: move.get_end() in attacking_direction,
                           self.move_graph.get_moves_by_piece_color(defended_color)))

