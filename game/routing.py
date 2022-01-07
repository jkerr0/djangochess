from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/game/chessboard/(?P<game_id>[0-9]+)/$', consumers.GameConsumer.as_asgi()),
    re_path(r'ws/game/lobby/(?P<game_id>[0-9]+)/$', consumers.LobbyConsumer.as_asgi())
]