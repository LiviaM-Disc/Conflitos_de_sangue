import os
import sys
from pathlib import Path

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ranking_project.settings")
    (Path(__file__).resolve().parent / "saves").mkdir(exist_ok=True)
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
