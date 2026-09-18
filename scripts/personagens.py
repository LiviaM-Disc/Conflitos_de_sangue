from __future__ import annotations

from pathlib import Path
from functools import lru_cache
import math

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
    "masters": {
        "name": "Masters",
        "ability": "Antagonistas do caso",
        "color": (82, 65, 70),
    },
}

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")

ATLAS_CELLS = {
    "dean": ("equipe.png", 0), "michael": ("equipe.png", 1),
    "lia": ("equipe.png", 2), "sloane": ("equipe.png", 3),
    "celine": ("caso.png", 0), "daniel": ("caso.png", 1),
    "lorelai": ("caso.png", 2), "masters": ("caso.png", 3),
}


@lru_cache(maxsize=4)
def load_atlas(path: Path) -> pygame.Surface:
    return pygame.image.load(str(path)).convert_alpha()


def prepared_portrait(folder: Path, key: str, pose: str) -> pygame.Surface | None:
    prepared = folder / "preparados"
    if key == "cassie":
        path = prepared / "cassie.png"
        if not path.exists():
            return None
        atlas = load_atlas(path)
        index = {"idle": 0, "walk": 1, "action": 2}.get(pose, 0)
        width = atlas.get_width() // 3
        # Shared vertical framing keeps the crouching pose at the same scale.
        return atlas.subsurface((index * width + 40, 160, width - 80, 740))
    if key not in ATLAS_CELLS:
        return None
    filename, index = ATLAS_CELLS[key]
    path = prepared / filename
    if not path.exists():
        return None
    atlas = load_atlas(path)
    width, height = atlas.get_width() // 2, atlas.get_height() // 2
    cell = atlas.subsurface((index % 2 * width, index // 2 * height, width, height))
    return cell.subsurface(cell.get_bounding_rect(min_alpha=128))


def find_character_file(folder: Path, key: str, pose: str = "idle") -> Path | None:
    if not folder.exists():
        return None

    character_folder = folder / key
    if character_folder.is_dir():
        files = sorted(character_folder.iterdir())
        for candidate_pose in dict.fromkeys((pose, "idle")):
            for path in files:
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS and path.stem.lower() == candidate_pose:
                    return path

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


def load_portrait(folder: Path, key: str, size: tuple[int, int] = (160, 220), pose: str = "idle") -> pygame.Surface:
    try:
        image = prepared_portrait(folder, key, pose)
        if image is None:
            image_path = find_character_file(folder, key, pose)
            if image_path is None:
                return make_placeholder(key, size)
            image = pygame.image.load(str(image_path)).convert_alpha()
    except (pygame.error, OSError):
        return make_placeholder(key, size)

    image_rect = image.get_rect()
    scale = min(size[0] / image_rect.width, size[1] / image_rect.height)
    new_size = (max(1, int(image_rect.width * scale)), max(1, int(image_rect.height * scale)))
    image = pygame.transform.smoothscale(image, new_size)

    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.blit(image, image.get_rect(center=surface.get_rect().center))
    return surface


def load_portraits(assets_dir: Path, pose: str = "idle") -> dict[str, pygame.Surface]:
    folder = assets_dir / "personagens"
    return {key: load_portrait(folder, key, pose=pose) for key in CHARACTERS}


class Player:
    def __init__(self, position: tuple[int, int], poses: dict[str, pygame.Surface] | None = None) -> None:
        self.rect = pygame.Rect(position[0], position[1], 34, 20)
        self.speed = 190
        self.poses = poses or {}
        self.moving = False
        self.action_timer = 0.0
        self.walk_time = 0.0
        self.facing_left = False

    def investigate(self) -> None:
        self.action_timer = 0.8

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper, bounds: pygame.Rect, obstacles: tuple = ()) -> None:
        self.action_timer = max(0.0, self.action_timer - dt)
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

        previous_position = self.rect.topleft
        self.rect.x += int(dx * self.speed * dt)
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                self.rect.x = previous_position[0]
        self.rect.y += int(dy * self.speed * dt)
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                self.rect.y = previous_position[1]
        self.rect.clamp_ip(bounds)
        self.moving = self.rect.topleft != previous_position
        if dx:
            self.facing_left = dx < 0
        self.walk_time = self.walk_time + dt if self.moving else 0.0
        if self.moving:
            self.action_timer = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        pose = "action" if self.action_timer > 0 else "walk" if self.moving else "idle"
        image = self.poses.get(pose, self.poses.get("idle"))
        if image is not None:
            shadow = pygame.Surface((58, 18), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (12, 15, 18, 70), shadow.get_rect())
            surface.blit(shadow, shadow.get_rect(center=self.rect.midbottom))
            if self.facing_left:
                image = pygame.transform.flip(image, True, False)
            bob = int(abs(math.sin(self.walk_time * 12)) * 2) if self.moving else 0
            surface.blit(image, image.get_rect(midbottom=(self.rect.centerx, self.rect.bottom - bob)))
            return
        shadow = self.rect.copy()
        shadow.y += 6
        pygame.draw.ellipse(surface, (20, 18, 22), shadow.inflate(18, -18))
        pygame.draw.rect(surface, (170, 94, 112), self.rect, border_radius=8)
        pygame.draw.rect(surface, (244, 235, 219), self.rect, width=2, border_radius=8)
        head = pygame.Rect(0, 0, 24, 24)
        head.center = (self.rect.centerx, self.rect.top - 6)
        pygame.draw.ellipse(surface, (226, 201, 180), head)
