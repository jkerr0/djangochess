import chessboard
import chess_piece
import itertools

from move import Move
from typing import Tuple, List


class MoveGraph:
    def __init__(self, board: chessboard.Chessboard):
        self.graph = MoveGraph.build(board)

    @staticmethod
    def build(board: chessboard.Chessboard) -> dict[chessboard.Position, List[Move]]:
        pairs = tuple(map(lambda position: (position, board.get_piece(position)),
                          chessboard.Chessboard.all_positions()))

        statics = tuple(filter(lambda pos, piece: isinstance(piece, chess_piece.StaticChessPiece), pairs))
        dynamics = tuple(filter(lambda pos, piece: isinstance(piece, chess_piece.DynamicChessPiece), pairs))
        # TODO mapping Pair(Position, Piece) -> dict(Position, List[Move]) i join
        return {}

    @staticmethod
    def get_static_moves(board: chessboard.Chessboard,
                         pair: Tuple[chessboard.Position, chess_piece.StaticChessPiece]) -> List[Move]:
        start_pos = pair[0]
        piece = pair[1]
        all_end_positions = map(lambda mapper: mapper(start_pos), piece.get_move_mappers())
        valid = filter(lambda position: position.is_valid(), all_end_positions)
        empty = filter(lambda position: board.is_empty(position), valid)
        moves = map(lambda position: Move(start_pos, position), empty)
        return list(moves)

    @staticmethod
    def get_dynamic_moves(board: chessboard.Chessboard,
                          pair: Tuple[chessboard.Position, chess_piece.DynamicChessPiece]) -> List[Move]:
        start_pos = pair[0]
        piece = pair[1]
        positions = itertools.chain(
            map(lambda mapper: [mapper(start_pos, i) for i in range(0, 8)], piece.get_move_mappers()))
        return []  # TODO

    @staticmethod
    def find_dynamic_conflict(pairs):
        pass
