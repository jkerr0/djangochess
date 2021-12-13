import itertools

from chess_piece import ChessPiece, PieceColor
from position import Position, Move
from chess_pieces import King, Knight, Pawn, Rook, Bishop, Queen
from typing import List


class Chessboard:
    def __init__(self):
        self._pieces = list(itertools.chain(*Chessboard._new_bottom_line(PieceColor.WHITE),
                                            *Chessboard._new_pawn_line(PieceColor.WHITE),
                                            *([None] * 48),
                                            *Chessboard._new_pawn_line(PieceColor.BLACK),
                                            *Chessboard._new_bottom_line(PieceColor.BLACK)))

    def get_piece(self, position: Position) -> ChessPiece:
        return self._pieces[position.inx()]

    def is_empty(self, position: Position):
        return self._pieces[position.inx()] is not None

    def move(self, move: Move):
        self._pieces[move.get_end().inx()] = self._pieces[move.get_start().inx()]
        self._pieces[move.get_start().inx()] = None

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
