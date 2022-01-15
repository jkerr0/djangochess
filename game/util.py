from .core.chesspiece import PieceColor, ChessPiece
from .models import PlayerGameMove
from .core.chessboard import Chessboard, Move
from .core.move_graph import MoveGraph
from django.db.models import Max
from django.template.loader import render_to_string


def get_game_chessboard(game_id: int) -> Chessboard:
    moves = PlayerGameMove.objects.filter(game_id=game_id).order_by('index')

    codes_list = list(map(lambda move: move.move_code, moves))
    moves_list = list(map(lambda move_code: Move.from_str(move_code), codes_list))

    return Chessboard.from_moves_list(moves_list)


def get_game_move_graph(game_id: int) -> MoveGraph:
    board = get_game_chessboard(game_id)
    return MoveGraph(board)


def get_game_max_move_index(game_id: int) -> int:
    max_index = PlayerGameMove.objects.filter(game_id=game_id).aggregate(Max('index'))['index__max']
    return max_index if max_index is not None else 0


def get_game_turn(game_id: int) -> PieceColor:
    return PieceColor.WHITE if get_game_max_move_index(game_id) % 2 == 0 else PieceColor.BLACK


def render_piece(piece: ChessPiece) -> str:
    return render_to_string('game/piece.html', {'piece': piece})
