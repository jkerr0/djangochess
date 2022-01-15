import unittest

from game.core.chessboard import Chessboard, Move
from game.core.game_state import GameState
from game.core.move_graph import MoveGraph


class GameStateTestCase(unittest.TestCase):
    def test_is_check(self):
        board = Chessboard.from_moves_list([Move.from_str(code) for code in ['e2e4', 'd7d5', 'f1b5']])
        graph = MoveGraph(board)
        state = GameState(board, graph)
        self.assertTrue(state.is_check())

        board = Chessboard()
        graph = MoveGraph(board)
        state = GameState(board, graph)
        self.assertFalse(state.is_check())


if __name__ == '__main__':
    unittest.main()
