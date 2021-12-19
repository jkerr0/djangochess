from django.db import models


class Player(models.Model):
    nickname = models.CharField(max_length=50)

    def __str__(self):
        return self.nickname


class Game(models.Model):
    white_player_id = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="white_player")
    black_player_id = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="black_player")
    start_date = models.DateTimeField()

    def __str__(self):
        return self.id


class PlayerGameMove(models.Model):
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    index = models.SmallIntegerField()
    move_code = models.CharField(max_length=4)
    registered_date = models.DateTimeField()

    def __str__(self):
        return str(self.index) + self.move_code
