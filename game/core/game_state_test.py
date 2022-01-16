import unittest

from game.core.chessboard import Chessboard, Move
from game.core.chesspiece import PieceColor
from game.core.game_state import GameState
from game.core.move_graph import MoveGraph


class GameStateTestCase(unittest.TestCase):
    def test_is_check(self):
        board = Chessboard.from_moves_list(moves_from_codes(['e2e4', 'd7d5', 'f1b5']))
        graph = MoveGraph(board)
        state = GameState(graph, PieceColor.WHITE)
        self.assertTrue(state.is_check())

    def test_is_checkmate(self):
        # fools mate
        board = Chessboard.from_moves_list(moves_from_codes(['f2f3', 'e7e5', 'g2g4', 'd8h4']))
        graph = MoveGraph(board)
        state = GameState(graph, PieceColor.WHITE)
        self.assertTrue(state.is_checkmate())

    def test_at_start(self):
        board = Chessboard()
        graph = MoveGraph(board)
        state = GameState(graph, PieceColor.WHITE)
        self.assertFalse(state.is_checkmate())
        self.assertFalse(state.is_draw())
        self.assertFalse(state.is_check())


def moves_from_codes(codes):
    return [Move.from_str(code) for code in codes]


if __name__ == '__main__':
    unittest.main()
