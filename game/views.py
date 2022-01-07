from django.shortcuts import render, redirect
from .core.chessboard import Chessboard, PieceColor
from .core.position import Move
from .models import Game, PlayerGameMove
from .forms import LobbyForm
from django.contrib.auth.decorators import login_required
from django.http import Http404

import datetime


def index(request):
    return render(request, 'game/index.html', None)


@login_required
def chessboard(request, game_id):
    try:
        game = Game.objects.get(id=int(game_id))
    except (Game.DoesNotExist, ValueError):
        raise Http404(f"Game with id {game_id} does not exist")

    moves = PlayerGameMove.objects.filter(game=game).order_by('index')

    codes_list = list(map(lambda move: move.move_code, moves))
    moves_list = list(map(lambda move_code: Move.from_str(move_code), codes_list))

    game_chessboard = Chessboard.from_moves_list(moves_list)

    player_color = PieceColor.WHITE
    if request.user == game.black_player:
        player_color = PieceColor.BLACK

    context = {'board_rows': game_chessboard.get_rows(perspective=player_color),
               'game_id': game_id,
               'player_color': player_color.value}
    return render(request, 'game/chessboard.html', context)


@login_required
def lobby(request, game_id):
    return render(request, 'game/lobby.html', {'game_id': game_id,
                                               'form': LobbyForm()})


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
        return redirect('/game/chessboard/' + game_id)
    else:
        return redirect('/game/lobby/' + game_id)


def register(request):
    return render(request, 'game/register.html', None)
