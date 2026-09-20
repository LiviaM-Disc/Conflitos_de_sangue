from django.core.management.base import BaseCommand
from scripts.ranking import DjangoRanking


class Command(BaseCommand):
    help = "Exibe o ranking local armazenado pelo Django."

    def handle(self, *args, **options):
        store = DjangoRanking()
        store.initialized = True
        rows = store.standings()
        if not rows:
            self.stdout.write("Nenhuma partida concluida no ranking.")
        for row in rows:
            self.stdout.write(f"{row['position']}. {row['name']} - {row['score']} pontos - {row['mistakes']} erros")
