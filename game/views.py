from django.shortcuts import render
from game.core.chessboard import Chessboard, PieceColor


def index(request):
    return render(request, 'game/index.html', None)


def chessboard(request, game_id):
    player_color = PieceColor.WHITE
    context = {'board_rows': Chessboard().get_rows(perspective=player_color),
               'game_id': game_id,
               'player_color': player_color.value}
    return render(request, 'game/chessboard.html', context)


def lobby(request, game_id):
    return render(request, 'game/lobby.html', {'game_id': game_id})


def login(request):
    return render(request, 'game/login.html', None)


def register(request):
    return render(request, 'game/register.html', None)
