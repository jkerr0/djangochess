import unittest
from game.core.position import Move


class MoveTest(unittest.TestCase):
    def test_something(self):
        self.assertEqual('e2e4', str(Move.from_str('e2e4')))


if __name__ == '__main__':
    unittest.main()
