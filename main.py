from pathlib import Path

import pygame

from scripts.cenas import Game
from scripts.ranking import DjangoRanking


WINDOW_SIZE = (1120, 720)
FPS = 60


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Conflitos de Sangue")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    root = Path(__file__).parent
    game = Game(screen, root, root / "saves" / "progresso.json", ranking_store=DjangoRanking())

    while game.running:
        dt = clock.tick(FPS) / 1000
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                game.request_quit()

        if not game.running:
            break

        game.handle_events(events)
        if not game.running:
            break
        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
