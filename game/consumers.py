import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .core.position import Move
from .models import PlayerGameMove, Game
from django.contrib.auth.models import User
from django.db.models import Max

import datetime


class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = 'game_%s' % self.game_id

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

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'move_message',
                'move': {'start_pos': move.get_start().inx(),
                         'end_pos': move.get_end().inx()}
            }
        )

        self.store_move(move)

    # Receive message from room group
    def move_message(self, event):
        move = event['move']

        self.send(text_data=json.dumps({
            'move': move
        }))

    def store_move(self, move: Move):
        max_game_index = PlayerGameMove.objects.filter(game_id=int(self.game_id)).aggregate(Max('index'))['index__max']
        if max_game_index is None:
            max_game_index = 0

        db_move = PlayerGameMove(game_id=int(self.game_id),
                                 player=self.scope['user'],
                                 index=max_game_index + 1,
                                 move_code=str(move),
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
        play_as = text_data_json['play_as']
        player = self.scope['user']
        start_game = text_data_json['start_game']

        if start_game is True:
            game = self.get_game()
            game.start_date = datetime.datetime.now()
            game.save()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'start_game',
                    'start_game_url': '/game/chessboard/' + self.game_id
                }
            )
        else:
            game = self.update_game_after_request(play_as, player)
            new_setup = {
                'type': 'new_setup',
                'setup': {
                    'white_player_nick': game.white_player.username if game.white_player is not None else '-',
                    'black_player_nick': game.black_player.username if game.black_player is not None else '-'
                }
            }

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                new_setup
            )

    def new_setup(self, event):
        new_setup = event['setup']

        self.send(text_data=json.dumps({
            'setup': new_setup,
            'start_game_url': None,
        }))

    def update_game_after_request(self, play_as: str, requesting_player: User) -> Game:
        game = self.get_game()
        current_white_player = game.white_player
        current_black_player = game.black_player

        if play_as == 'black' and current_black_player != requesting_player:
            if current_black_player is not None or current_white_player == requesting_player:
                game.white_player = current_black_player
            game.black_player = requesting_player
        elif play_as == 'white' and current_white_player != requesting_player:
            if current_white_player is not None or current_black_player == requesting_player:
                game.black_player = current_white_player
            game.white_player = requesting_player

        game.save()
        return game

    def start_game(self, event):
        start_game_url = event['start_game_url']

        self.send(text_data=json.dumps({
            'setup': None,
            'start_game_url': start_game_url
        }))

    def get_game(self):
        return Game.objects.get(id=int(self.game_id))

