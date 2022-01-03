from django.shortcuts import render, redirect
from game.core.chessboard import Chessboard, PieceColor
from .models import Game
from django.contrib.auth.decorators import login_required

import datetime


def index(request):
    return render(request, 'game/index.html', None)


@login_required
def chessboard(request, game_id):
    player_color = PieceColor.WHITE
    context = {'board_rows': Chessboard().get_rows(perspective=player_color),
               'game_id': game_id,
               'player_color': player_color.value}
    return render(request, 'game/chessboard.html', context)


@login_required
def lobby(request, game_id):
    return render(request, 'game/lobby.html', {'game_id': game_id})


@login_required
def new_game(request):
    game = Game(registration_date=datetime.datetime.now(), created_by_player=request.user)
    game.save()
    return redirect('lobby/' + str(game.id))


@login_required
def start_game(request, game_id):
    # TODO get players from lobby and assign them to game
    game = Game.objects.get(id=int(game_id))
    game.start_date = datetime.datetime.now()

    if game.created_by_player == request.user:
        return redirect('chessboard/' + game_id)
    else:
        return redirect('lobby/' + game_id)


def register(request):
    return render(request, 'game/register.html', None)
