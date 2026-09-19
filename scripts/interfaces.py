from __future__ import annotations

import textwrap
from dataclasses import dataclass

import pygame


BG = (24, 25, 30)
PANEL = (25, 34, 34)
PANEL_2 = (39, 49, 48)
TEXT = (239, 232, 219)
MUTED = (178, 169, 153)
ACCENT = (185, 71, 84)
ACCENT_2 = (83, 151, 139)
GOOD = (120, 190, 142)
BAD = (208, 91, 91)
LINE = (93, 110, 102)

CLUES_PER_PAGE = 4


class FontBook:
    def __init__(self) -> None:
        self.title = pygame.font.SysFont("Segoe UI", 52, bold=True)
        self.subtitle = pygame.font.SysFont("Segoe UI", 24)
        self.h1 = pygame.font.SysFont("Segoe UI", 30, bold=True)
        self.h2 = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.body = pygame.font.SysFont("Segoe UI", 19)
        self.small = pygame.font.SysFont("Segoe UI", 15)
        self.button = pygame.font.SysFont("Segoe UI", 18, bold=True)


def draw_gradient(surface: pygame.Surface, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> None:
    width, height = surface.get_size()
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (width, y))


def draw_panel(surface: pygame.Surface, rect: pygame.Rect, fill: tuple[int, int, int] = PANEL) -> None:
    pygame.draw.rect(surface, fill, rect, border_radius=8)
    pygame.draw.rect(surface, LINE, rect, width=1, border_radius=8)


def draw_band(surface: pygame.Surface, rect: pygame.Rect, alpha: int = 238) -> None:
    band = pygame.Surface(rect.size, pygame.SRCALPHA)
    band.fill((18, 26, 27, alpha))
    surface.blit(band, rect)
    pygame.draw.line(surface, LINE, rect.topleft, rect.topright)


def draw_scene_header(surface: pygame.Surface, fonts: FontBook, chapter: str, title: str, score: int) -> None:
    draw_band(surface, pygame.Rect(0, 0, surface.get_width(), 76))
    surface.blit(fonts.small.render(chapter, True, ACCENT_2), (28, 11))
    surface.blit(fonts.h2.render(title, True, TEXT), (28, 33))
    points = fonts.body.render(f"Pontos {score}", True, TEXT)
    surface.blit(points, points.get_rect(midright=(surface.get_width() - 30, 38)))


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        test = word if not current else f"{current} {word}"
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            if font.size(word)[0] <= max_width:
                current = word
            else:
                # Rare fallback for very long words.
                chunks = textwrap.wrap(word, width=12)
                lines.extend(chunks[:-1])
                current = chunks[-1] if chunks else ""

    if current:
        lines.append(current)
    return lines


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    rect: pygame.Rect,
    line_spacing: int = 5,
    align: str = "left",
) -> int:
    y = rect.y
    for line in wrap_text(text, font, rect.width):
        image = font.render(line, True, color)
        if y + image.get_height() > rect.bottom:
            break
        image_rect = image.get_rect()
        if align == "center":
            image_rect.centerx = rect.centerx
        elif align == "right":
            image_rect.right = rect.right
        else:
            image_rect.x = rect.x
        image_rect.y = y
        surface.blit(image, image_rect)
        y += image_rect.height + line_spacing
        if y > rect.bottom:
            break
    return y


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    value: object = None
    enabled: bool = True
    selected: bool = False

    def draw(self, surface: pygame.Surface, fonts: FontBook, mouse_pos: tuple[int, int]) -> None:
        hovered = self.enabled and self.rect.collidepoint(mouse_pos)
        fill = ACCENT if hovered else PANEL_2
        border = (232, 217, 190) if hovered else LINE
        if not self.enabled:
            fill = (45, 45, 50)
            border = (70, 70, 76)
        if self.selected:
            fill = (36, 70, 62)
            border = ACCENT_2

        pygame.draw.rect(surface, fill, self.rect, border_radius=7)
        pygame.draw.rect(surface, border, self.rect, width=1, border_radius=7)

        text_color = TEXT if self.enabled or self.selected else (126, 122, 118)
        lines = wrap_text(self.text, fonts.button, self.rect.width - 24)
        total_height = len(lines) * fonts.button.get_height() + max(0, len(lines) - 1) * 3
        y = self.rect.centery - total_height // 2
        for line in lines[:3]:
            image = fonts.button.render(line, True, text_color)
            surface.blit(image, image.get_rect(center=(self.rect.centerx, y + image.get_height() // 2)))
            y += image.get_height() + 3

    def hit(self, event: pygame.event.Event) -> bool:
        return (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


def draw_hud(surface: pygame.Surface, fonts: FontBook, score: int, objective: str) -> None:
    hud = pygame.Rect(18, 14, surface.get_width() - 36, 50)
    draw_panel(surface, hud, (30, 31, 37))
    score_img = fonts.h2.render(f"Pontos: {score}", True, TEXT)
    surface.blit(score_img, (hud.x + 18, hud.y + 12))
    draw_text(surface, objective, fonts.small, MUTED, pygame.Rect(hud.x + 175, hud.y + 15, hud.width - 200, 24))


def draw_message(surface: pygame.Surface, fonts: FontBook, message: str) -> None:
    if not message:
        return
    width = surface.get_width() - 200
    lines = wrap_text(message, fonts.body, width - 32)
    height = len(lines) * (fonts.body.get_height() + 5) + 24
    rect = pygame.Rect(100, surface.get_height() - 72 - height, width, height)
    draw_panel(surface, rect, (31, 32, 38))
    draw_text(surface, message, fonts.body, TEXT, rect.inflate(-32, -24))


def draw_clue_panel(surface: pygame.Surface, fonts: FontBook, evidences: list, score: int, page: int = 0, used: set[str] | None = None) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    rect = pygame.Rect(90, 54, surface.get_width() - 180, 612)
    draw_panel(surface, rect)

    title = fonts.h1.render("Dossie da investigacao", True, TEXT)
    surface.blit(title, (rect.x + 28, rect.y + 24))
    meta = fonts.small.render(f"{len(evidences)} registros  /  {score} pontos", True, MUTED)
    surface.blit(meta, (rect.x + 28, rect.y + 66))

    y = rect.y + 106
    if not evidences:
        draw_text(surface, "Nenhuma evidencia encontrada ainda.", fonts.body, MUTED, pygame.Rect(rect.x + 28, y, rect.width - 56, 60))
        return

    for evidence in evidences[page * CLUES_PER_PAGE:(page + 1) * CLUES_PER_PAGE]:
        item = pygame.Rect(rect.x + 28, y, rect.width - 56, 104)
        pygame.draw.line(surface, LINE, item.topleft, item.topright)
        label = fonts.h2.render(evidence.name, True, TEXT)
        surface.blit(label, (item.x + 16, item.y + 10))
        tag = fonts.small.render("Usada na deducao" if evidence.id in (used or set()) else "Registro", True, ACCENT_2)
        surface.blit(tag, (item.right - tag.get_width() - 16, item.y + 13))
        draw_text(surface, evidence.description, fonts.small, MUTED, pygame.Rect(item.x + 16, item.y + 40, item.width - 32, 56))
        y += 104
    pages = max(1, (len(evidences) + CLUES_PER_PAGE - 1) // CLUES_PER_PAGE)
    surface.blit(fonts.small.render(f"Pagina {page + 1} de {pages}", True, MUTED), (rect.x + 28, 619))


def draw_dialogue_box(
    surface: pygame.Surface,
    fonts: FontBook,
    speaker: str,
    text: str,
    hint: str = "",
) -> None:
    rect = pygame.Rect(0, 458, surface.get_width(), surface.get_height() - 458)
    draw_band(surface, rect)
    name_img = fonts.h2.render(speaker, True, ACCENT_2)
    surface.blit(name_img, (rect.x + 48, rect.y + 24))
    draw_text(surface, text, fonts.body, TEXT, pygame.Rect(rect.x + 48, rect.y + 68, rect.width - 96, 84))
    hint_img = fonts.small.render(hint, True, MUTED)
    surface.blit(hint_img, (rect.right - hint_img.get_width() - 22, rect.bottom - 28))
