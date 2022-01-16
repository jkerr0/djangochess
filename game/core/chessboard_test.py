import unittest
import game.core.chessboard as cb


def is_position_of_type(position_str, cl):
    return isinstance(cb.Chessboard().get_piece(cb.Position.from_str(position_str)), cl)


class ChessboardTestCase(unittest.TestCase):
    def test_white_init(self):
        self.assertTrue(is_position_of_type('a1', cb.Rook))
        self.assertTrue(is_position_of_type('e1', cb.King))
        self.assertTrue(is_position_of_type('e2', cb.Pawn))

    def test_black_init(self):
        self.assertTrue(is_position_of_type('e7', cb.Pawn))
        self.assertTrue(is_position_of_type('e8', cb.King))

    def test_get_rows(self):
        board = cb.Chessboard()
        # as black, I want to get white figures in first row on init
        self.assertTrue(board.get_rows(cb.PieceColor.BLACK)[0][0].piece.get_color() == cb.PieceColor.WHITE)

        # as white, I want to get black figures in first row on init
        self.assertTrue(board.get_rows(cb.PieceColor.WHITE)[0][0].piece.get_color() == cb.PieceColor.BLACK)

        # as white, I want king from first row to be in 5th column
        self.assertTrue(isinstance(board.get_rows(cb.PieceColor.WHITE)[0][4].piece, cb.King))

        # as black, I want king from first row to be in 4th column
        self.assertTrue(isinstance(board.get_rows(cb.PieceColor.BLACK)[0][3].piece, cb.King))

    def test_moving(self):
        board = cb.Chessboard.from_moves_list([cb.Move.from_str('e2e4')])
        self.assertTrue(type(board.get_piece(cb.Position.from_str('e4'))) == cb.Pawn)
        self.assertTrue(board.get_piece(cb.Position.from_str('e2')) is None)

    def test_is_empty(self):
        board = cb.Chessboard()
        self.assertTrue(board.is_empty(cb.Position.from_str('e4')))
        self.assertFalse(board.is_empty(cb.Position.from_str('e2')))

    def test_en_passant(self):
        board = cb.Chessboard.from_moves_list(cb.Move.from_str_list(['e2e4', 'd7d5', 'e4e5', 'f7f5']))
        self.assertEqual('e5f6', str(board.get_possible_en_passant_moves().pop()))


if __name__ == '__main__':
    unittest.main()
