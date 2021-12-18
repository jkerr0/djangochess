import unittest
from game.core import chessboard as cb


def is_position_of_type(position_str, cl):
    return isinstance(cb.Chessboard().get_piece(cb.Position.from_str(position_str)), cl)


class ChessboardCase(unittest.TestCase):
    def test_white_init(self):
        self.assertTrue(is_position_of_type('a1', cb.Rook))
        self.assertTrue(is_position_of_type('e1', cb.King))
        self.assertTrue(is_position_of_type('e2', cb.Pawn))

    def test_black_init(self):
        self.assertTrue(is_position_of_type('e7', cb.Pawn))
        self.assertTrue(is_position_of_type('e8', cb.King))

    def test_get_rows(self):
        board = cb.Chessboard()
        # as black i want to get white figures in first row on init
        self.assertTrue(board.get_rows(cb.PieceColor.BLACK)[0][0].piece.get_color() == cb.PieceColor.WHITE)

        # as white i want to get black figures in first row on init
        self.assertTrue(board.get_rows(cb.PieceColor.WHITE)[0][0].piece.get_color() == cb.PieceColor.BLACK)

        # as white i want king from first row to be in 5th column
        self.assertTrue(isinstance(board.get_rows(cb.PieceColor.WHITE)[0][4].piece, cb.King))

        # as black i want king from first row to be in 4th column
        self.assertTrue(isinstance(board.get_rows(cb.PieceColor.BLACK)[0][3].piece, cb.King))


if __name__ == '__main__':
    unittest.main()
