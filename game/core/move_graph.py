from itertools import chain

from game.core.chessboard import Chessboard, Move, Position
from game.core.chesspiece import ChessPiece, StaticChessPiece, DynamicChessPiece, PieceColor
from game.core.chesspieces import Pawn, King, Rook

from typing import List, Type


# make_move graph of possible next moves
# nodes - positions
# edges - moves
class MoveGraph:
    def __init__(self, board: Chessboard):
        self.board = board
        self.moves = self.build()
        self.add_special_moves()
        self.prevent_king_from_going_into_check()
        self.prevent_moving_pinned_pieces()
        check_attacks = self.get_check_attacks()
        if len(check_attacks) > 1:
            # king needs to move
            self.moves = [*self.get_moves_by_piece_type(King),
                          *self.get_moves_by_piece_color(self.get_check_attacker_color())]
        elif len(check_attacks) == 1:
            # king needs to move or be covered or piece counterattacked
            self.moves = [*self.get_counter_check_attacks(),
                          *self.get_covering_moves(),
                          *self.get_moves_by_piece_type(King),
                          *self.get_moves_by_piece_color(self.get_check_attacker_color())]

    def build(self) -> List[Move]:
        static_moves = flatten(list(map(self.get_static_moves,
                                        self.board.get_pieces_positions_by_type(StaticChessPiece))))
        dynamic_moves = flatten(list(map(self.get_dynamic_moves,
                                         self.board.get_pieces_positions_by_type(DynamicChessPiece))))
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

    def get_dynamic_piece_directions_no_collision(self, start_pos: Position, with_self=False) -> List[List[Position]]:
        piece = self.board.get_piece(start_pos)
        start_iter = 0 if with_self else 1
        all_directions = list(
            map(lambda mapper: [mapper(start_pos, i) for i in range(start_iter, 9)], piece.get_move_mappers()))
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
        no_collision_directions = flatten(
            list(map(lambda pos: self.get_dynamic_piece_directions_no_collision(pos, with_self=True),
                     self.board.get_pieces_positions_by_type(DynamicChessPiece))))
        for direction in no_collision_directions:
            self.find_and_restrict_pieces_to_pin_in_direction(direction)

    def find_and_restrict_pieces_to_pin_in_direction(self, direction: List[Position]) -> None:
        not_empty_pos = filter(lambda pos: not self.board.is_empty(pos), direction)
        attacker_color = self.board.get_piece(next(not_empty_pos)).get_color()

        potential_pinned_pos = next(not_empty_pos, None)
        if potential_pinned_pos is None:
            return

        potential_pinned_piece = self.board.get_piece(potential_pinned_pos)
        if isinstance(potential_pinned_piece, King) or potential_pinned_piece.get_color() == attacker_color:
            return

        next_pos = next(not_empty_pos, None)
        if next_pos is None:
            return

        next_piece = self.board.get_piece(next_pos)
        if isinstance(next_piece, King) and next_piece.get_color() == PieceColor.enemy_color(attacker_color):
            for illegal_move in filter(lambda move: move.get_end() not in direction,
                                       self.get_moves_by_start(potential_pinned_pos)):
                self.moves.remove(illegal_move)

    def is_move_going_into_enemy_attack_range(self, move: Move):
        return move.get_end() in map(Move.get_end, self.get_moves_by_piece_color(
            PieceColor.enemy_color(self.board.get_piece(move.get_start()).get_color())))

    def get_check_attacks(self) -> List[Move]:
        return flatten(list(map(self.get_moves_by_end,
                                self.board.get_pieces_positions_by_type(King))))

    def get_check_attacker_color(self) -> PieceColor:
        return self.board.get_piece(self.get_check_attacks().pop().get_start()).get_color()

    def get_counter_check_attacks(self) -> List[Move]:
        return flatten(list(map(self.get_moves_by_end,
                                map(Move.get_start, self.get_check_attacks()))))

    def get_covering_moves(self) -> List[Move]:
        attack_move = self.get_check_attacks().pop()
        if not isinstance(self.board.get_piece(attack_move.get_start()), DynamicChessPiece):
            return []
        defended_color = self.board.get_piece(attack_move.get_end()).get_color()
        attacker_directions = self.get_dynamic_piece_directions(attack_move.get_start())
        attacking_direction = next(filter(lambda direction: attack_move.get_end() in direction, attacker_directions))
        return list(filter(lambda move: move.get_end() in attacking_direction,
                           self.get_moves_by_piece_color(defended_color)))

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

    def add_special_moves(self):
        self.moves += self.board.get_possible_en_passant_moves()
        self.moves += self.castle_moves()

    def castle_moves(self):
        if self.get_check_attacks():
            # check - can't castle
            return []

        not_moved_king_pos_list = list(filter(lambda pos: not self.board.get_piece(pos).has_moved(),
                                              self.board.get_pieces_positions_by_type(King)))
        not_moved_rook_pos_list = list(filter(lambda pos: not self.board.get_piece(pos).has_moved(),
                                              self.board.get_pieces_positions_by_type(Rook)))

        castle_moves = []
        for king_pos in not_moved_king_pos_list:
            king = self.board.get_piece(king_pos)
            y = king_pos.y()

            right_direction = [Position(x, y) for x in range(5, 8)]
            right_clear = len(self.cut_after_piece_collision(king, right_direction)) == 2
            passing_through_right_check = self.is_move_going_into_enemy_attack_range(Move(king_pos, right_direction[0]))
            right_rook_not_moved = any(map(Position(7, y).__eq__, not_moved_rook_pos_list))

            left_direction = [Position(x, y) for x in range(3, -1, -1)]
            left_clear = len(self.cut_after_piece_collision(king, left_direction)) == 3
            passing_through_left_check = self.is_move_going_into_enemy_attack_range(Move(king_pos, left_direction[0]))
            left_rook_not_moved = any(map(Position(0, y).__eq__, not_moved_rook_pos_list))

            if left_clear and not passing_through_left_check and left_rook_not_moved:
                castle_moves.append(Move(king_pos, left_direction[1]))
            if right_clear and not passing_through_right_check and right_rook_not_moved:
                castle_moves.append(Move(king_pos, right_direction[1]))
        return castle_moves

    def as_dict(self) -> dict:
        return {str(start_pos.inx()): [move.get_end().inx() for move in self.get_moves_by_start(start_pos)]
                for start_pos in Chessboard.all_positions()}


def flatten(list_of_lists: List[List]) -> List:
    return list(chain.from_iterable(list_of_lists))
