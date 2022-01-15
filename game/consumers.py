import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from .core.chesspieces import Queen
from .models import Game
from django.contrib.auth.models import User
from .util import *

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
        game_current_turn = get_game_turn(int(self.game_id))

        if self.player_move_authorized():
            self.store_move(move)
            move_graph = get_game_move_graph(int(self.game_id))
            game_next_turn = get_game_turn(int(self.game_id)).value
            promoted_to_piece = None

            if get_game_chessboard(int(self.game_id)).did_last_move_promote():
                promoted_to_piece = render_piece(Queen(game_current_turn))

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'move_message',
                    'move': move.as_dict(),
                    'move_graph': move_graph.as_dict(),
                    'turn': game_next_turn,
                    'promoted_to_piece': promoted_to_piece
                }
            )

    def player_move_authorized(self) -> bool:
        game = self.get_game()
        player = self.scope['user']
        game_current_turn = get_game_turn(int(self.game_id))
        return game_current_turn == PieceColor.WHITE and game.white_player == player \
            or game_current_turn == PieceColor.BLACK and game.black_player == player

    # Receive message from room group
    def move_message(self, event):
        self.send(text_data=json.dumps({
            'move': event['move'],
            'move_graph': event['move_graph'],
            'turn': event['turn'],
            'promoted_to_piece': event['promoted_to_piece']
        }))

    def store_move(self, move: Move):
        max_game_index = get_game_max_move_index(int(self.game_id))
        if max_game_index is None:
            max_game_index = 0

        db_move = PlayerGameMove(game_id=int(self.game_id),
                                 player=self.scope['user'],
                                 index=max_game_index + 1,
                                 move_code=str(move),
                                 registered_date=datetime.datetime.now())
        db_move.save()

    def get_game(self):
        return Game.objects.get(id=int(self.game_id))


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
            if game.black_player is not None and game.white_player is not None:
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
