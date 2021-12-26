import unittest
from game.core.position import Move


class MoveTest(unittest.TestCase):
    def test_move(self):
        self.assertEqual('e2e4', str(Move.from_str('e2e4')))
        self.assertEqual('a1b1', str(Move.from_indexes(0, 1)))


if __name__ == '__main__':
    unittest.main()
