import unittest

from game.core.move_graph import MoveGraph
from game.core.chessboard import Chessboard, Move, Position


class MoveGraphTestCase(unittest.TestCase):
    def test_knight_at_start(self):
        chessboard = Chessboard()
        graph = MoveGraph(chessboard)
        self.assertEqual({'b1a3', 'b1c3'},
                         {str(move) for move in graph.get_moves_by_start(Position.from_str('b1'))})

    def test_pawn_at_start(self):
        chessboard = Chessboard()
        graph = MoveGraph(chessboard)
        self.assertEqual({'e2e3', 'e2e4'},
                         {str(move) for move in graph.get_moves_by_start(Position.from_str('e2'))})

    def test_dynamic_moves(self):
        chessboard = Chessboard.from_moves_list([Move.from_str('e2e4')])
        graph = MoveGraph(chessboard)
        self.assertEqual({'f1' + end_code for end_code in ['e2', 'd3', 'c4', 'b5', 'a6']},
                         {str(move) for move in graph.get_moves_by_start(Position.from_str('f1'))})

    def test_can_pinned_move(self):
        chessboard = Chessboard.from_moves_list([Move.from_str(code) for code in ['e2e3', 'd7d6', 'd1h5']])
        graph = MoveGraph(chessboard)
        self.assertEqual([], [str(move) for move in graph.get_moves_by_start(Position.from_str('f7'))])


if __name__ == '__main__':
    unittest.main()
