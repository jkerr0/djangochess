from typing import List, Type

from game.core.field import Field
from game.core.chesspiece import ChessPiece, PieceColor
from game.core.position import Position, Move
from game.core.chesspieces import King, Knight, Pawn, Rook, Bishop, Queen


class Chessboard:
    def __init__(self):
        self._pieces = []
        self._pieces.extend(Chessboard._new_bottom_line(PieceColor.WHITE))
        self._pieces.extend(Chessboard._new_pawn_line(PieceColor.WHITE))
        self._pieces.extend(([None] * 32))
        self._pieces.extend(Chessboard._new_pawn_line(PieceColor.BLACK))
        self._pieces.extend(Chessboard._new_bottom_line(PieceColor.BLACK))
        self._last_move_promoted = False
        self._last_move_enpassant = False
        self._last_move_castled = False
        self._last_move = None

    def did_last_move_promote(self):
        return self._last_move_promoted

    def get_piece(self, position: Position) -> ChessPiece:
        return self._pieces[position.inx()]

    def is_empty(self, position: Position):
        return self._pieces[position.inx()] is None

    def make_move(self, move: Move):
        self.reset_special_move_info()
        if self.is_castle(move):
            self.move_rook_on_castle(king_move=move)
            self._last_move_castled = True
        self._pieces[move.get_end().inx()] = self._pieces[move.get_start().inx()]
        self._pieces[move.get_end().inx()].mark_moved()
        if any(map(lambda enp_move: enp_move == move, self.get_possible_en_passant_moves())):
            self._last_move_enpassant = True
            pos_to_clear = Position(move.get_end().x(),
                                    move.get_start().y())
            self._pieces[pos_to_clear.inx()] = None

        self._pieces[move.get_start().inx()] = None
        self._last_move = move
        if self.can_promote():
            self.promote_to_queen(move.get_end())
            self._last_move_promoted = True

    def reset_special_move_info(self):
        self._last_move_promoted = False
        self._last_move_castled = False
        self._last_move_enpassant = False

    def get_special_move_info(self) -> dict:
        return {'promoted': self._last_move_promoted,
                'castled': self._last_move_castled,
                'enpassant': self._last_move_enpassant}

    def can_promote(self) -> bool:
        position = self._last_move.get_end()
        piece = self.get_piece(position)
        return isinstance(piece, Pawn) and ((piece.get_color() == PieceColor.WHITE and position.y() == 7) or
                                            (piece.get_color() == PieceColor.BLACK and position.y() == 0))

    def promote_to_queen(self, position: Position):
        current_color = self.get_piece(position).get_color()
        self._pieces[position.inx()] = Queen(current_color)

    def get_all_pieces_positions(self):
        return [*self.get_pieces_positions_by_color(PieceColor.WHITE),
                *self.get_pieces_positions_by_color(PieceColor.BLACK)]

    def get_pieces_positions_by_color(self, color: PieceColor) -> List[Position]:
        return list(filter(lambda pos: not self.is_empty(pos) and self.get_piece(pos).get_color() is color,
                           Chessboard.all_positions()))

    def get_pieces_positions_by_type(self, piece_type: Type[ChessPiece]) -> List[Position]:
        return list(filter(lambda pos: isinstance(self.get_piece(pos), piece_type),
                           self.get_all_pieces_positions()))

    def get_possible_en_passant_moves(self) -> List[Move]:
        last_move = self._last_move
        if last_move is None:
            return []
        last_piece = self.get_piece(last_move.get_end())
        if not isinstance(last_piece, Pawn):
            return []

        if not abs(last_move.get_start().y() - last_move.get_end().y()) == 2:
            return []

        move_end = last_move.get_end()
        passed_pos = Position(move_end.x(), move_end.y() + (-1 if last_piece.get_color() is PieceColor.WHITE else 1))
        attacker_positions = [Position(move_end.x() - 1, move_end.y()), Position(move_end.x() + 1, move_end.y())]
        attacker_positions = list(filter(Position.is_valid, attacker_positions))
        attacker_positions = list(
            filter(lambda pos: pos in self.get_pieces_positions_by_type(Pawn), attacker_positions))
        attacker_positions = list(
            filter(lambda pos: pos in self.get_pieces_positions_by_color(PieceColor.enemy_color(last_piece.get_color())),
                   attacker_positions))
        return [Move(attacker_pos, passed_pos) for attacker_pos in attacker_positions]

    def is_castle(self, move: Move) -> bool:

        piece = self.get_piece(move.get_start())
        x_diff = abs(move.get_start().x() - move.get_end().x())
        return not piece.has_moved() and isinstance(piece, King) and x_diff > 1

    def move_rook_on_castle(self, king_move: Move):
        x_diff = king_move.get_end().x() - king_move.get_start().x()
        y = king_move.get_start().y()
        rook_pos = None
        move_to = None
        if x_diff < 0:
            # long castle
            rook_pos = Position(0, y)
            move_to = Position(3, y)
        elif x_diff > 0:
            # short castle
            rook_pos = Position(7, y)
            move_to = Position(5, y)
        self.make_move(Move(rook_pos, move_to))

    def get_rows(self, perspective: PieceColor) -> List[List[Field]]:
        row_range = range(0, 8) if perspective == PieceColor.BLACK else range(7, -1, -1)
        rows_pieces = [self._pieces[i * 8: (i + 1) * 8] for i in row_range]
        rows_positions = [Chessboard._row_positions(i) for i in row_range]

        rows = [Chessboard._map_pieces_and_positions_to_fields(pieces_row, pos_row)
                for pieces_row, pos_row in zip(rows_pieces, rows_positions)]

        if perspective == PieceColor.BLACK:
            for row in rows:
                row.reverse()
        return rows

    @staticmethod
    def _row_positions(row_inx: int):
        return [Position.from_inx(i) for i in range(8 * row_inx, 8 * (row_inx + 1))]

    @staticmethod
    def _map_pieces_and_positions_to_fields(pieces: List[ChessPiece], positions: List[Position]) -> List[Field]:
        return [Field(pos, piece) for piece, pos in zip(pieces, positions)]

    @staticmethod
    def all_positions():
        return [Position.from_inx(i) for i in range(0, 64)]

    @staticmethod
    def _new_bottom_line(color: PieceColor) -> List[ChessPiece]:
        return [Rook(color), Knight(color), Bishop(color), Queen(color),
                King(color), Bishop(color), Knight(color), Rook(color)]

    @staticmethod
    def _new_pawn_line(color: PieceColor) -> List[Pawn]:
        return [Pawn(color)] * 8

    @staticmethod
    def from_moves_list(moves: List[Move]):
        chessboard = Chessboard()
        for move in moves:
            chessboard.make_move(move)

        return chessboard
