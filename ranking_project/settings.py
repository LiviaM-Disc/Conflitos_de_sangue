"""Local Django ORM configuration for the Pygame application."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "local-offline-game-not-a-web-deployment")
INSTALLED_APPS = ["ranking_app"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3",
                         "NAME": os.environ.get("GAME_RANKING_DB", str(BASE_DIR / "saves" / "ranking.sqlite3")),
                         "OPTIONS": {"timeout": 3}}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "America/Sao_Paulo"
