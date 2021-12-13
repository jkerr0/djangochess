import unittest
from core.main.move import Move


class MoveTest(unittest.TestCase):
    def test_something(self):
        self.assertEqual('e2e4', Move.from_str('e2e4'))


if __name__ == '__main__':
    unittest.main()
