from itertools import chain

from game.core.chessboard import Chessboard, Move, Position
from game.core.chesspiece import ChessPiece, StaticChessPiece, DynamicChessPiece, PieceColor
from game.core.chesspieces import Pawn, King

from typing import List, Type


# make_move graph of possible next moves
# nodes - positions
# edges - moves
class MoveGraph:
    def __init__(self, board: Chessboard):
        self.board = board
        self.moves = self.build()
        self.prevent_king_from_going_into_check()
        self.prevent_moving_pinned_pieces()

    def build(self) -> List[Move]:
        static_moves = flatten([self.get_static_moves(pos) for pos in
                                self.board.get_pieces_positions_by_type(StaticChessPiece)])
        dynamic_moves = flatten([self.get_dynamic_moves(pos) for pos in
                                 self.board.get_pieces_positions_by_type(DynamicChessPiece)])
        pawn_moves = flatten([*[self.get_pawn_moves(pos) for pos in
                                self.board.get_pieces_positions_by_type(Pawn)],
                              *[self.get_pawn_attack_moves(pos) for pos in
                                self.board.get_pieces_positions_by_type(Pawn)]])

        return static_moves + dynamic_moves + pawn_moves

    def get_static_moves(self, start_pos: Position) -> List[Move]:
        piece = self.board.get_piece(start_pos)
        all_end_positions = list(map(lambda mapper: mapper(start_pos), piece.get_move_mappers()))
        valid = list(filter(lambda position: position is not None and position.is_valid(), all_end_positions))
        possible = list(filter(lambda position: self.can_move_to(piece, position), valid))
        moves = list(map(lambda position: Move(start_pos, position), possible))
        return moves

    def get_dynamic_moves(self, start_pos: Position) -> List[Move]:
        positions = flatten(self.get_dynamic_piece_directions(start_pos))
        moves = list(map(lambda position: Move(start_pos, position), positions))
        return moves

    def get_dynamic_piece_directions_no_collision(self, start_pos: Position) -> List[List[Position]]:
        piece = self.board.get_piece(start_pos)
        all_directions = list(map(lambda mapper: [mapper(start_pos, i) for i in range(1, 9)], piece.get_move_mappers()))
        valid_directions = list(map(lambda pos_list: list(filter(Position.is_valid, pos_list)), all_directions))
        return valid_directions

    def get_dynamic_piece_directions(self, start_pos: Position):
        piece = self.board.get_piece(start_pos)
        return list(map(lambda pos_list: self.cut_after_piece_collision(piece, pos_list),
                        self.get_dynamic_piece_directions_no_collision(start_pos)))

    def get_pawn_moves(self, start_pos: Position) -> List[Move]:
        moves = self.get_static_moves(start_pos)
        if len(moves) == 1:
            move = moves[0]
            # disable jumping over
            if abs(move.get_start().y() - move.get_end().y()) == 2:
                return []
        return moves

    def get_pawn_attack_moves(self, start_pos: Position) -> List[Move]:
        piece = self.board.get_piece(start_pos)
        attack_end_positions = list(map(lambda mapper: mapper(start_pos), piece.get_attack_mappers()))
        valid = list(filter(Position.is_valid, attack_end_positions))
        possible = list(filter(lambda position: self.is_enemy_at_pos(piece, position), valid))
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
        elif isinstance(piece, Pawn):
            return False

        return self.is_enemy_at_pos(piece, end_pos)

    def is_enemy_at_pos(self, piece: ChessPiece, pos: Position):
        if self.board.is_empty(pos):
            return False

        return self.board.get_piece(pos).get_color() != piece.get_color()

    def prevent_king_from_going_into_check(self) -> None:
        for invalid_move in filter(self.is_move_going_into_enemy_attack_range, self.get_moves_by_piece_type(King)):
            self.moves.remove(invalid_move)

    def prevent_moving_pinned_pieces(self) -> None:
        pass

    def is_move_going_into_enemy_attack_range(self, move: Move):
        return move.get_end() in map(Move.get_end, self.get_moves_by_piece_color(
            PieceColor.enemy_color(self.board.get_piece(move.get_start()))))

    def get_moves_by_start(self, position: Position) -> List[Move]:
        return list(filter(lambda move: move.get_start() == position, self.moves))

    def get_moves_by_end(self, position: Position) -> List[Move]:
        return list(filter(lambda move: move.get_end() == position, self.moves))

    def get_moves_by_piece_color(self, color: PieceColor) -> List[Move]:
        return flatten((list(map(self.get_moves_by_start,
                                 self.board.get_pieces_positions_by_color(color)))))

    def get_moves_by_piece_type(self, piece_type: Type[ChessPiece]) -> List[Move]:
        return flatten((list(map(self.get_moves_by_start,
                                 self.board.get_pieces_positions_by_type(piece_type)))))

    def as_dict(self) -> dict:
        return {str(start_pos.inx()): [move.get_end().inx() for move in self.get_moves_by_start(start_pos)]
                for start_pos in Chessboard.all_positions()}


def flatten(list_of_lists: List[List]) -> List:
    return list(chain.from_iterable(list_of_lists))
