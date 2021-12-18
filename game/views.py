from django.shortcuts import render
from game.core.chessboard import Chessboard, PieceColor


def index(request):
    context = {'board_rows': Chessboard().get_rows(PieceColor.BLACK)}
    return render(request, 'game/index.html', context)
