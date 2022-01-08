import unittest
from game.core.position import Position


class PositionTestCase(unittest.TestCase):
    def test_position_str(self):
        self.assertEqual('a1', str(Position.from_str('a1')))
        self.assertEqual('d2', str(Position.from_str('d2')))
        self.assertEqual('e4', str(Position.from_str('e4')))

    def test_position_from_inx(self):
        self.assertEqual(9, Position.from_inx(9).inx())

    def test_is_valid(self):
        self.assertFalse(Position(-1, 1).is_valid())
        self.assertFalse(Position(1, -1).is_valid())
        self.assertTrue(Position(1, 1).is_valid())
        self.assertFalse(Position(8, 8).is_valid())

    def test_eq(self):
        self.assertEqual(Position.from_str('e2'),
                         Position.from_str('e2'))


if __name__ == '__main__':
    unittest.main()
