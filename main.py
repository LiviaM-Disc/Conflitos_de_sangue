from pathlib import Path

import pygame

from scripts.cenas import Game


WINDOW_SIZE = (1120, 720)
FPS = 60


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Conflitos de Sangue")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()

    game = Game(screen, Path(__file__).parent)

    while game.running:
        dt = clock.tick(FPS) / 1000
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                game.running = False

        game.handle_events(events)
        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
