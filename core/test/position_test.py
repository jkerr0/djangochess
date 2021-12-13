import unittest
from core.main.position import Position


class PositionTest(unittest.TestCase):
    def test_position_str(self):
        self.assertEqual('a1', str(Position.from_str('a1')))
        self.assertEqual('d2', str(Position.from_str('d2')))
        self.assertEqual('e4', str(Position.from_str('e4')))

    def test_position_from_inx(self):
        self.assertEqual(9, Position.from_inx(9).inx())


if __name__ == '__main__':
    unittest.main()
