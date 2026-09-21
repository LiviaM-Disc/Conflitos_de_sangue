"""Django-backed local ranking; no network service is required."""
import os
import unicodedata
from pathlib import Path
from uuid import UUID


def normalize_name(value):
    name = " ".join(unicodedata.normalize("NFKC", value).split())
    if not 2 <= len(name) <= 24 or not any(c.isalnum() for c in name):
        raise ValueError("Use um apelido de 2 a 24 caracteres.")
    if any(not (c.isalnum() or c in " ._-") for c in name):
        raise ValueError("Use letras, numeros, espacos, ponto, traco ou sublinhado.")
    return name


class DjangoRanking:
    def __init__(self):
        self.initialized = False

    def setup(self):
        if self.initialized:
            return
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ranking_project.settings")
        import django
        django.setup()
        from django.conf import settings
        from django.core.management import call_command
        database = settings.DATABASES["default"]["NAME"]
        if str(database) != ":memory:":
            Path(database).parent.mkdir(parents=True, exist_ok=True)
        call_command("migrate", interactive=False, verbosity=0)
        self.initialized = True

    def player(self, name):
        self.setup()
        from ranking_app.models import Player
        name = normalize_name(name)
        player, _ = Player.objects.get_or_create(identity=name.casefold(), defaults={"nickname": name})
        return player

    def record(self, run_id, name, score, mistakes, ranked=True, completed=True, phase=6):
        self.setup()
        from django.db import transaction
        from ranking_app.models import GameResult
        run_id = UUID(str(run_id))
        if type(score) is not int or not 0 <= score <= 1000000 or type(mistakes) is not int or not 0 <= mistakes <= 1000000:
            raise ValueError("Resultado invalido.")
        if type(ranked) is not bool:
            raise ValueError("Modalidade invalida.")
        if type(completed) is not bool or type(phase) is not int or not 0 <= phase <= 6:
            raise ValueError("Etapa do resultado invalida.")
        with transaction.atomic():
            player = self.player(name)
            result, created = GameResult.objects.get_or_create(id=run_id, defaults={
                "player": player, "score": score, "mistakes": mistakes, "ranked": ranked,
                "completed": completed, "phase": phase})
            if not created and (result.player_id, result.score, result.mistakes, result.ranked, result.completed, result.phase) != (player.pk, score, mistakes, ranked, completed, phase):
                raise ValueError("Esta partida ja foi registrada com outro resultado.")
        return result

    def standings(self, name=""):
        self.setup()
        from ranking_app.models import GameResult
        rows, seen = [], set()
        # First result per player is their best; stable ties favor fewer errors,
        # then the earliest recorded result. All attempts remain in the database.
        for result in GameResult.objects.filter(ranked=True).select_related("player"):
            if result.player_id in seen:
                continue
            seen.add(result.player_id)
            rows.append({"position": len(rows) + 1, "name": result.player.nickname,
                         "score": result.score, "mistakes": result.mistakes,
                         "completed": result.completed, "phase": result.phase,
                         "current": result.player.identity == name.casefold()})
        return rows
