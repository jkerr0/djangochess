from django.shortcuts import render
from game.core.chessboard import Chessboard, PieceColor


def index(request):
    return render(request, 'game/index.html', None)


def chessboard(request):
    context = {'board_rows': Chessboard().get_rows(perspective=PieceColor.WHITE)}
    return render(request, 'game/chessboard.html', context)


def lobby(request):
    return render(request, 'game/lobby.html', None)


def login(request):
    return render(request, 'game/login.html', None)


def register(request):
    return render(request, 'game/register.html', None)
