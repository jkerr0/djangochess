import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .core.position import Move
from .models import PlayerGameMove
from django.db.models import Max

import datetime


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = 'game_%s' % self.game_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        move_json = text_data_json['move']
        move = Move.from_indexes(move_json['start_pos'], move_json['end_pos'])

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'move_message',
                'move': {'start_pos': move.get_start().inx(),
                         'end_pos': move.get_end().inx()}
            }
        )

    # Receive message from room group
    def move_message(self, event):
        move = event['move']

        self.store_move(move)
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'move': move
        }))

    def store_move(self, move):
        max_game_index = PlayerGameMove.objects.filter(game_id=int(self.game_id)).aggregate(Max('index'))['index__max']
        if max_game_index is None:
            max_game_index = 0

        db_move = PlayerGameMove(game_id=int(self.game_id), player=self.scope['user'], index=max_game_index + 1,
                                 move_code=str(Move.from_indexes(move['start_pos'], move['end_pos'])),
                                 registered_date=datetime.datetime.now())
        db_move.save()


class LobbyConsumer(WebsocketConsumer):
    def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = 'lobby_%s' % self.game_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        play_as = text_data_json['play-as']
        player_nick = self.scope["user"].username

        white_player_nick = 'wp-nick'
        black_player_nick = 'bp-nick'

        if play_as == 'black':
            black_player_nick = player_nick
        elif play_as == 'white':
            white_player_nick = player_nick

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'players_setup',
                'setup': {'white_player_nick': white_player_nick,
                          'black_player_nick': black_player_nick}
            }
        )

    def players_setup(self, event):
        setup = event['setup']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'setup': setup
        }))
