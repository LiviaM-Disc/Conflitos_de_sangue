from django.db import models


class Player(models.Model):
    nickname = models.CharField(max_length=24)
    identity = models.CharField(max_length=72, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nickname


class GameResult(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="results")
    score = models.PositiveIntegerField()
    mistakes = models.PositiveIntegerField()
    ranked = models.BooleanField(default=True)
    finished_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-score", "mistakes", "finished_at", "id"]
