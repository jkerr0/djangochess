from typing import List

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

    def get_piece(self, position: Position) -> ChessPiece:
        return self._pieces[position.inx()]

    def is_empty(self, position: Position):
        return self._pieces[position.inx()] is not None

    def move(self, move: Move):
        self._pieces[move.get_end().inx()] = self._pieces[move.get_start().inx()]
        self._pieces[move.get_start().inx()] = None

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
