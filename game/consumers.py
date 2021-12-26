import json
from channels.generic.websocket import WebsocketConsumer
from .core.position import Move


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        move_json = text_data_json['move']
        move = Move.from_indexes(move_json['start_pos'], move_json['end_pos'])


class LobbyConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data=json.dumps({
            'white_player_nick': 'wp-nick',
            'black_player_nick': 'bp-nick'
        }))
