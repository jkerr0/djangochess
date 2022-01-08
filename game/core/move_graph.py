import itertools

from game.core.chessboard import Chessboard, Move, Position
from game.core.chesspiece import ChessPiece, StaticChessPiece, DynamicChessPiece
from game.core.chesspieces import Pawn

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

        pawns_pos = list(filter(lambda pos: isinstance(self.board.get_piece(pos), Pawn), Chessboard.all_positions()))

        static_moves = list(itertools.chain(*[self.get_static_moves(pos) for pos in static_pos]))
        dynamic_moves = list(itertools.chain(*[self.get_dynamic_moves(pos) for pos in dynamic_pos]))
        pawn_moves = list(itertools.chain(*[self.get_pawn_moves(pos) for pos in pawns_pos],
                                          *[self.get_pawn_attack_moves(pos) for pos in pawns_pos]))

        return static_moves + dynamic_moves + pawn_moves

    def get_static_moves(self, start_pos: Position) -> List[Move]:
        piece = self.board.get_piece(start_pos)
        all_end_positions = list(map(lambda mapper: mapper(start_pos), piece.get_move_mappers()))
        valid = list(filter(lambda position: position is not None and position.is_valid(), all_end_positions))
        possible = list(filter(lambda position: self.can_move_to(piece, position), valid))
        moves = list(map(lambda position: Move(start_pos, position), possible))
        return moves

    def get_dynamic_moves(self, start_pos: Position) -> List[Move]:
        piece = self.board.get_piece(start_pos)
        all_directions = list(map(lambda mapper: [mapper(start_pos, i) for i in range(1, 9)], piece.get_move_mappers()))
        valid_directions = list(
            map(lambda pos_list: list(filter(lambda pos: pos.is_valid(), pos_list)), all_directions))
        positions = itertools.chain(
            *list(map(lambda pos_list: self.cut_after_piece_collision(piece, pos_list), list(valid_directions))))
        moves = list(map(lambda position: Move(start_pos, position), positions))
        return moves

    def get_pawn_moves(self, start_pos: Position) -> List[Move]:
        piece = self.board.get_piece(start_pos)
        attack_end_positions = list(map(lambda mapper: mapper(start_pos), piece.get_move_mappers()))
        valid = list(filter(lambda position: position is not None and position.is_valid(), attack_end_positions))
        possible = list(filter(lambda position: self.board.is_empty(position), valid))
        moves = list(map(lambda position: Move(start_pos, position), possible))
        return moves

    def get_pawn_attack_moves(self, start_pos: Position) -> List[Move]:
        piece = self.board.get_piece(start_pos)
        attack_end_positions = list(map(lambda mapper: mapper(start_pos), piece.get_attack_mappers()))
        valid = list(filter(lambda position: position is not None and position.is_valid(), attack_end_positions))
        possible = list(filter(lambda position: self.is_enemy(piece, position), valid))
        moves = list(map(lambda position: Move(start_pos, position), possible))
        return moves

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

    def can_move_to(self, piece: ChessPiece, end_pos: Position):
        if self.board.is_empty(end_pos):
            return True

        return self.is_enemy(piece, end_pos)

    def is_enemy(self, piece: ChessPiece, end_pos: Position):
        if self.board.is_empty(end_pos):
            return False

        return self.board.get_piece(end_pos).get_color() != piece.get_color()

    def get_moves_by_start(self, position: Position) -> List[Move]:
        return list(filter(lambda move: move.get_start() == position, self.moves))

    def get_moves_by_end(self, position: Position) -> List[Move]:
        return list(filter(lambda move: move.get_end() == position, self.moves))

    def as_dict(self):
        return {str(start_pos.inx()): [move.get_end().inx() for move in self.get_moves_by_start(start_pos)]
                for start_pos in Chessboard.all_positions()}
