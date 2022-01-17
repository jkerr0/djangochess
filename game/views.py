from django.shortcuts import render, redirect
from .models import Game
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.auth.forms import UserCreationForm

import datetime
from .util import *


def index(request):
    return render(request, 'game/index.html', None)


@login_required
def chessboard(request, game_id):
    game = get_game_or_404(int(game_id))
    if game.start_date is None:
        return redirect('/game/lobby/' + game_id)

    full_state_dict = get_game_full_state(int(game_id))
    game_move_graph = full_state_dict['move_graph']
    game_state = full_state_dict['game_state']
    game_chessboard = full_state_dict['chessboard']

    player_color = None
    if request.user == game.black_player:
        player_color = PieceColor.BLACK
    elif request.user == game.white_player:
        player_color = PieceColor.WHITE

    context = {'board_rows': game_chessboard.get_rows(perspective=player_color),
               'game_id': game_id,
               'player_color': player_color.value if player_color is not None else None,
               'move_graph': game_move_graph.as_dict(),
               'game_state': game_state.as_dict(),
               'turn': get_game_turn(int(game_id)).value}
    return render(request, 'game/chessboard.html', context)


@login_required
def lobby(request, game_id):
    game = get_game_or_404(int(game_id))
    if game.start_date is not None:
        return redirect('/game/chessboard/' + game_id)

    white_player_nick = game.white_player.username if game.white_player is not None else 'Not selected'
    black_player_nick = game.black_player.username if game.black_player is not None else 'Not selected'
    return render(request, 'game/lobby.html', {'game_id': game_id,
                                               'white_player_nick': white_player_nick,
                                               'black_player_nick': black_player_nick,
                                               'is_owner': request.user == game.created_by_player})


@login_required
def new_game(request):
    game = Game(registration_date=datetime.datetime.now(), created_by_player=request.user)
    game.save()
    return redirect('lobby/' + str(game.id))


def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/accounts/login')

    return render(request, 'game/register.html', {'form': form})


def get_game_or_404(game_id: int):
    try:
        return Game.objects.get(id=int(game_id))
    except (Game.DoesNotExist, ValueError):
        raise Http404(f"Game with id {game_id} does not exist")
