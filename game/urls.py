from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('new-game', views.new_game, name='new_game'),
    path('start-game/<str:game_id>', views.new_game, name="start_game"),
    path('chessboard/<str:game_id>', views.chessboard, name='chessboard'),
    path('lobby/<str:game_id>', views.lobby, name='lobby')
]
