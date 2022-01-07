import itertools

from game.core.chessboard import Chessboard, Move, Position
from game.core.chesspiece import ChessPiece, StaticChessPiece, DynamicChessPiece

from typing import List


# make_move graph of possible next moves
# nodes - positions
# edges - moves
class MoveGraph:
    def __init__(self, board: Chessboard):
        self.board = board
        self.moves = self.build()

    def build(self) -> List[Move]:
        static_pos = list(
            filter(lambda pos: isinstance(self.board.get_piece(pos), StaticChessPiece), Chessboard.all_positions()))
        dynamic_pos = list(
            filter(lambda pos: isinstance(self.board.get_piece(pos), DynamicChessPiece), Chessboard.all_positions()))
        static_moves = itertools.chain(*[self.get_static_moves(pos) for pos in static_pos])
        dynamic_moves = itertools.chain(*[self.get_dynamic_moves(pos) for pos in dynamic_pos])

        return list(static_moves) + list(dynamic_moves)

    def get_static_moves(self, start_pos: Position) -> List[Move]:
        piece = self.board.get_piece(start_pos)
        all_end_positions = map(lambda mapper: mapper(start_pos), piece.get_move_mappers())
        valid = filter(lambda position: position.is_valid, all_end_positions)
        empty = filter(lambda position: self.board.is_empty(position), valid)
        moves = map(lambda position: Move(start_pos, position), empty)
        return list(moves)

    def get_dynamic_moves(self, start_pos: Position) -> List[Move]:
        piece = self.board.get_piece(start_pos)
        all_directions = map(lambda mapper: [mapper(start_pos, i) for i in range(1, 9)], piece.get_move_mappers())
        valid_directions = map(lambda pos_list: list(filter(lambda pos: pos.is_valid(), pos_list)), all_directions)
        positions = itertools.chain(
            *list(map(lambda pos_list: self.cut_after_piece_collision(piece, pos_list), list(valid_directions))))
        moves = map(lambda position: Move(start_pos, position), positions)
        return list(moves)

    def find_first_piece_inx(self, direction_position_list: List[Position]):
        for inx, position in enumerate(direction_position_list):
            if not self.board.is_empty(position):
                return inx
        return None

    def cut_after_piece_collision(self, start_piece: ChessPiece,
                                  direction_position_list: List[Position]):
        conflict_inx = self.find_first_piece_inx(direction_position_list)
        if conflict_inx is None:
            return direction_position_list

        conflict_piece = self.board.get_piece(direction_position_list[conflict_inx])
        if conflict_piece.get_color() == start_piece.get_color():
            return direction_position_list[:conflict_inx]
        else:
            return direction_position_list[:conflict_inx + 1]

    def get_moves_by_start(self, position: Position):
        return list(filter(lambda move: move.get_start() == position, self.moves))

    def get_moves_by_end(self, position: Position):
        return list(filter(lambda move: move.get_end() == position, self.moves))
