from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="white_player", null=True)
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="black_player", null=True)
    created_by_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_player")
    start_date = models.DateTimeField(null=True)
    registration_date = models.DateTimeField()

    def __str__(self):
        return str(self.id)


class PlayerGameMove(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    index = models.SmallIntegerField()
    move_code = models.CharField(max_length=4)
    registered_date = models.DateTimeField()

    def __str__(self):
        return str(self.index) + self.move_code
