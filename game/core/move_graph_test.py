import unittest

from game.core import move_graph as mg, chessboard as cb


class MyTestCase(unittest.TestCase):
    def test_knight_at_start(self):
        chessboard = cb.Chessboard()
        graph = mg.MoveGraph(chessboard)
        self.assertTrue(set(graph.get_moves_by_start(cb.Position.from_str('b1'))
                            == set(*cb.Move.from_str('b1a3'), *cb.Move.from_str('b1c3'))))


if __name__ == '__main__':
    unittest.main()
