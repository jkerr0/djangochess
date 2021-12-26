from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/chessboard/([0-9]+)/$', consumers.GameConsumer.as_asgi()),
    re_path(r'ws/game/lobby/([0-9]+)/$', consumers.LobbyConsumer.as_asgi())
]