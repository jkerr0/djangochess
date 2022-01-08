from .models import PlayerGameMove
from .core.chessboard import Chessboard, Move


def get_game_chessboard(game_id: int) -> Chessboard:
    moves = PlayerGameMove.objects.filter(game_id=game_id).order_by('index')

    codes_list = list(map(lambda move: move.move_code, moves))
    moves_list = list(map(lambda move_code: Move.from_str(move_code), codes_list))

    return Chessboard.from_moves_list(moves_list)
