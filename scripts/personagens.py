from __future__ import annotations

from pathlib import Path

import pygame


CHARACTERS = {
    "cassie": {
        "name": "Cassie",
        "ability": "Perfilacao e reconstrucao mental",
        "color": (122, 74, 90),
    },
    "dean": {
        "name": "Dean",
        "ability": "Perfilacao criminal",
        "color": (70, 87, 110),
    },
    "michael": {
        "name": "Michael",
        "ability": "Leitura de emocoes",
        "color": (134, 95, 55),
    },
    "lia": {
        "name": "Lia",
        "ability": "Deteccao de mentiras",
        "color": (102, 93, 134),
    },
    "sloane": {
        "name": "Sloane",
        "ability": "Analise de padroes",
        "color": (62, 111, 106),
    },
    "celine": {
        "name": "Celine",
        "ability": "Elemento central do caso",
        "color": (145, 79, 74),
    },
    "daniel": {
        "name": "Daniel Redding",
        "ability": "Figura do prologo",
        "color": (84, 84, 84),
    },
    "lorelai": {
        "name": "Lorelai",
        "ability": "Ligacao pessoal com Cassie",
        "color": (120, 75, 120),
    },
}

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


def find_character_file(folder: Path, key: str) -> Path | None:
    if not folder.exists():
        return None

    wanted = {key, CHARACTERS[key]["name"].lower().replace(" ", "_")}
    for path in folder.iterdir():
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        stem = path.stem.lower().replace(" ", "_")
        if stem in wanted:
            return path
    return None


def make_placeholder(key: str, size: tuple[int, int]) -> pygame.Surface:
    info = CHARACTERS[key]
    surface = pygame.Surface(size, pygame.SRCALPHA)
    rect = surface.get_rect()
    color = info["color"]

    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, (230, 224, 212), rect, width=2, border_radius=10)
    pygame.draw.circle(surface, (224, 213, 196), (rect.centerx, 54), 34)
    pygame.draw.rect(surface, (38, 34, 38), (30, 92, size[0] - 60, size[1] - 116), border_radius=24)

    font = pygame.font.SysFont("Segoe UI", 22, bold=True)
    small = pygame.font.SysFont("Segoe UI", 14)
    initial = info["name"][0]
    initial_img = font.render(initial, True, (32, 27, 31))
    surface.blit(initial_img, initial_img.get_rect(center=(rect.centerx, 54)))

    name_img = small.render(info["name"], True, (248, 242, 232))
    surface.blit(name_img, name_img.get_rect(center=(rect.centerx, size[1] - 20)))
    return surface


def load_portrait(folder: Path, key: str, size: tuple[int, int] = (160, 220)) -> pygame.Surface:
    image_path = find_character_file(folder, key)
    if image_path is None:
        return make_placeholder(key, size)

    try:
        image = pygame.image.load(str(image_path)).convert_alpha()
    except pygame.error:
        return make_placeholder(key, size)

    image_rect = image.get_rect()
    scale = min(size[0] / image_rect.width, size[1] / image_rect.height)
    new_size = (max(1, int(image_rect.width * scale)), max(1, int(image_rect.height * scale)))
    image = pygame.transform.smoothscale(image, new_size)

    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.blit(image, image.get_rect(center=surface.get_rect().center))
    return surface


def load_portraits(assets_dir: Path) -> dict[str, pygame.Surface]:
    folder = assets_dir / "personagens"
    return {key: load_portrait(folder, key) for key in CHARACTERS}


class Player:
    def __init__(self, position: tuple[int, int]) -> None:
        self.rect = pygame.Rect(position[0], position[1], 34, 46)
        self.speed = 230

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper, bounds: pygame.Rect) -> None:
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071

        self.rect.x += int(dx * self.speed * dt)
        self.rect.y += int(dy * self.speed * dt)
        self.rect.clamp_ip(bounds)

    def draw(self, surface: pygame.Surface) -> None:
        shadow = self.rect.copy()
        shadow.y += 6
        pygame.draw.ellipse(surface, (20, 18, 22), shadow.inflate(18, -18))
        pygame.draw.rect(surface, (170, 94, 112), self.rect, border_radius=8)
        pygame.draw.rect(surface, (244, 235, 219), self.rect, width=2, border_radius=8)
        head = pygame.Rect(0, 0, 24, 24)
        head.center = (self.rect.centerx, self.rect.top - 6)
        pygame.draw.ellipse(surface, (226, 201, 180), head)
