"""Pygame drawing and mouse controls for the complete investigation."""

import pygame

from scripts.interfaces import TEXT, MUTED, GOOD, ACCENT_2, draw_band, draw_text
from scripts.roteiro_expandido import ROOMS, OBJECTS, ITEMS, OBJECTIVES, PUZZLES, TEAM_PROFILES


# Neighbouring locations, not an automatic route through the answers.
CONNECTIONS = [
    ("reception", "office"), ("reception", "pantry"), ("office", "archive"),
    ("office", "service"), ("reception", "hall"), ("hall", "interview"),
    ("hall", "security"), ("security", "technical"), ("hall", "lab"),
    ("lab", "digital"), ("lab", "evidence"), ("evidence", "connections"),
    ("evidence", "archive"), ("garden", "vestibule"), ("vestibule", "library"),
    ("vestibule", "kitchen"), ("vestibule", "upper"), ("library", "gallery"),
    ("upper", "bedroom"), ("upper", "house_office"), ("house_office", "basement"),
    ("basement", "hidden"), ("hidden", "observation"), ("observation", "recording"),
    ("recording", "final_chamber"), ("final_chamber", "photo_archive"),
    ("final_chamber", "exit"), ("exit", "transmission"),
]
ROOM_LINKS = {key: [] for key in ROOMS}
for left, right in CONNECTIONS:
    ROOM_LINKS[left].append(right)
    ROOM_LINKS[right].append(left)

COMPANIONS = {"reception": "Dean", "interview": "Lia", "hall": "Michael",
              "lab": "Sloane", "connections": "Dean", "garden": "Dean",
              "recording": "Lia", "final_chamber": "Dean"}
CONVERSATIONS = {
    "reception": "Celine desapareceu. Vamos observar os registros antes de supor um sequestro. Eu acompanho a investigacao.",
    "interview": "O que ele diz pode ser comparado ao celular. Uma mentira nao prova, sozinha, que ele participa dos Masters.",
    "hall": "Medo de ser desmentido nao e a mesma coisa que medo de Celine. A portaria pode nos dar horarios confiaveis.",
    "lab": "O envelope tem tres camadas. Vamos conferir cada resultado antes de abrir o compartimento seguinte.",
    "connections": "O endereco indica um caminho, nao o paradeiro comprovado de Celine. A quem a mensagem se dirige?",
    "garden": "Chegamos ao endereco. Vamos descobrir por que escolheram esta casa e o que querem mostrar a Cassie.",
    "recording": "Uma gravacao pode misturar uma frase verdadeira com outra falsa. Compare as duas com os registros.",
    "final_chamber": "Falta separar os documentos autenticos das adulteracoes. Um nome conhecido nao e prova de autoria.",
}
ACTORS = {"leave_intro": "dean", "target_board": "dean", "continue_final": "dean"}
OBJECT_RECTS = {
    "desk": (548, 185, 95, 56), "phone": (1035, 310, 60, 87),
    "chair": (532, 303, 85, 100), "glass": (659, 190, 36, 54),
    "bin": (368, 275, 65, 65), "lamp": (442, 173, 66, 75),
    "new_envelope": (602, 263, 100, 57),
    "redding_notes": (485, 269, 108, 65), "reflection": (725, 176, 105, 85),
    "stopped_watch": (929, 176, 80, 80), "leave_intro": (120, 356, 105, 160),
}


def prop_kind(key):
    if key in ACTORS or key in {"witness", "guard"}:
        return "person"
    if "key" in key:
        return "key"
    if key in {"phone"}:
        return "phone"
    if key in {"clock", "stopped_watch", "hand"}:
        return "clock"
    if key in {"shelves", "false_index", "guest_book"}:
        return "books"
    if key in {"drawer", "drawer_cover", "box", "positional"}:
        return "box"
    if key in {"camera", "digital", "router", "terminals", "transmission", "final_panel"}:
        return "terminal"
    if key in {"badge", "punched", "maintenance_door"}:
        return "badge"
    if "photo" in key or key in {"altered", "portraits", "portrait_notes", "reflection"}:
        return "photo"
    if key in {"new_envelope", "sequence", "intruder", "hidden_symbol"}:
        return "envelope"
    if key in {"magnet", "magnetic_tool", "strip", "clip"}:
        return "tool"
    if key in {"grate", "lock_a", "lock_b", "lock_c", "recordings", "logic_grid"}:
        return "panel"
    if key in {"lamp", "office_light"}:
        return "lamp"
    return "paper"


class CampaignVisual:
    def __init__(self, campaign):
        self.c = campaign
        self.g = campaign.game
        self.item_font = pygame.font.SysFont("Segoe UI", 13)

    def neighbours(self):
        d = self.c.data
        return [key for key in ROOM_LINKS[d["room"]]
                if ROOMS[key]["phase"] <= d["chapter"]
                and not (d["chapter"] >= 4 and ROOMS[key]["phase"] < 4)]

    def draw_briefing(self, title, text, team=False, ending=False):
        g = self.g
        draw_band(g.screen, pygame.Rect(0, 0, 1120, 720), alpha=242)
        draw_text(g.screen, "CONFLITOS DE SANGUE / " + ("FIM DO CAPITULO" if ending else "ABERTURA"), g.fonts.small, MUTED, pygame.Rect(60, 54, 1000, 30))
        draw_text(g.screen, title, g.fonts.h1, TEXT, pygame.Rect(60, 115, 1000, 50))
        draw_text(g.screen, text, g.fonts.body, TEXT, pygame.Rect(60, 183, 1000, 145), line_spacing=8)
        if team:
            for i, (key, name, role, description) in enumerate(TEAM_PROFILES):
                x = 60 + i * 204
                portrait = g.stage_portraits[key].subsurface(pygame.Rect(25, 0, 150, 140))
                g.screen.blit(pygame.transform.smoothscale(portrait, (96, 90)), (x + 42, 300))
                draw_text(g.screen, name, g.fonts.h2, TEXT, pygame.Rect(x, 410, 185, 35), align="center")
                draw_text(g.screen, role, g.fonts.small, ACCENT_2, pygame.Rect(x, 450, 185, 28), align="center")
                draw_text(g.screen, description, g.fonts.small, MUTED, pygame.Rect(x + 5, 486, 175, 85), align="center")
        for button in self.c.buttons():
            button.draw(g.screen, g.fonts, pygame.mouse.get_pos())

    def object_rect(self, key, index):
        if key in OBJECT_RECTS:
            return pygame.Rect(OBJECT_RECTS[key])
        if prop_kind(key) == "person":
            return pygame.Rect(265 + index * 135, 345, 105, 160)
        return pygame.Rect(265 + index % 4 * 177, 210 + index // 4 * 140, 110, 88)

    def inventory_buttons(self):
        c, d = self.c, self.c.data
        buttons = []
        page = d["page"] if d["view"] == "explore" else 0
        for i, key in enumerate(d["inventory"][page * 6:page * 6 + 6]):
            chosen = key in d["selected_items"]
            buttons.append(c.button((25 + i * 128, 637, 118, 72), ITEMS[key][0], ("item", key), chosen or len(d["selected_items"]) < 2, chosen))
        if d["view"] == "explore":
            buttons += [c.button((806, 653, 48, 42), "<", "previous", page > 0),
                        c.button((864, 653, 48, 42), ">", "next", (page + 1) * 6 < len(d["inventory"]))]
        return buttons

    def explore_buttons(self):
        c, d = self.c, self.c.data
        buttons = []
        for i, key in enumerate(ROOMS[d["room"]]["objects"]):
            if key == "new_envelope" and not c.has("supply"):
                continue
            buttons.append(c.button(self.object_rect(key, i), OBJECTS[key]["label"], ("object", key)))
        for i, key in enumerate(self.neighbours()):
            buttons.append(c.button((24 + i * 216, 116, 204, 36), ROOMS[key]["title"], ("walk", key)))
        if d["room"] in COMPANIONS:
            buttons.append(c.button((106, 349, 100, 155), COMPANIONS[d["room"]], ("talk", d["room"])))
        buttons += self.inventory_buttons()
        buttons += [c.button((590, 594, 100, 34), "Combinar", "combine", len(d["selected_items"]) == 2),
                    c.button((702, 594, 80, 34), "Itens", "inventory"),
                    c.button((794, 594, 80, 34), "Locais", "map"),
                    c.button((886, 594, 80, 34), "Pistas", "dossier"),
                    c.button((978, 594, 115, 34), "Dica", "world_hint")]
        return buttons

    def note_buttons(self):
        c, d = self.c, self.c.data
        buttons = [c.button((25, 590, 180, 36), "Continuar", "note_back"),
                   c.button((918, 590, 60, 36), "<", "previous", d["page"] > 0),
                   c.button((994, 590, 60, 36), ">", "next", (d["page"] + 1) * 10 < len(c.note_lines()))]
        if d["note_title"] == "Escolher chave":
            for i, key in enumerate(("key417", "key471", "key714")):
                buttons.append(c.button((350 + i * 240, 525, 225, 40), ITEMS[key][0], ("use_key", key), key in d["inventory"]))
        return buttons + self.inventory_buttons()

    def draw_prop(self, key, rect, opened=False):
        kind = prop_kind(key)
        g = self.g
        if kind == "person":
            actor = ACTORS.get(key)
            if actor:
                g.screen.blit(pygame.transform.smoothscale(g.stage_portraits[actor], rect.size), rect)
            else:
                # Unidentified witnesses use a neutral figure, never another character's portrait.
                pygame.draw.circle(g.screen, (193, 180, 160), (rect.centerx, rect.y + 25), 23)
                pygame.draw.rect(g.screen, (77, 89, 94), (rect.x + 16, rect.y + 53, rect.w - 32, rect.h - 53), border_radius=6)
            return
        icon = pygame.Surface((120, 100), pygame.SRCALPHA)
        ink, paper, gold = (39, 50, 55), (221, 223, 208), (213, 181, 96)
        if kind == "key":
            pygame.draw.circle(icon, gold, (30, 38), 17, 6)
            pygame.draw.line(icon, gold, (46, 38), (104, 38), 7)
            pygame.draw.line(icon, gold, (90, 39), (90, 56), 6)
        elif kind in {"terminal", "phone"}:
            r = pygame.Rect(8, 8, 104, 70) if kind == "terminal" else pygame.Rect(32, 2, 56, 93)
            pygame.draw.rect(icon, ink, r, border_radius=5)
            pygame.draw.rect(icon, (79, 132, 138), r.inflate(-12, -12), border_radius=2)
            for y in (28, 40, 52):
                pygame.draw.line(icon, paper, (r.x + 14, y), (r.right - 14, y), 2)
            if kind == "terminal":
                pygame.draw.rect(icon, ink, (47, 78, 26, 10))
                pygame.draw.rect(icon, ink, (23, 88, 74, 6))
        elif kind == "books":
            for i, color in enumerate(((102, 54, 60), (63, 105, 104), (94, 86, 111), (130, 117, 69))):
                pygame.draw.rect(icon, color, (8 + i * 26, 8 + i % 2 * 8, 22, 80 - i % 2 * 8), border_radius=2)
                pygame.draw.line(icon, gold, (11 + i * 26, 27), (27 + i * 26, 27), 2)
        elif kind == "box":
            pygame.draw.rect(icon, (115, 82, 64), (7, 21, 106, 65), border_radius=3)
            pygame.draw.rect(icon, (30, 34, 35) if opened else (150, 112, 76), (15, 28, 90, 36))
            pygame.draw.rect(icon, gold, (49, 68, 24, 6), border_radius=2)
        elif kind == "clock":
            pygame.draw.circle(icon, gold, (60, 48), 43)
            pygame.draw.circle(icon, paper, (60, 48), 36)
            pygame.draw.line(icon, ink, (60, 48), (60, 20), 4)
            pygame.draw.line(icon, ink, (60, 48), (84, 55), 4)
        elif kind == "photo":
            pygame.draw.rect(icon, paper, (4, 4, 112, 92), border_radius=2)
            icon.blit(pygame.transform.smoothscale(g.room_image, (100, 67)), (10, 10))
        elif kind == "badge":
            pygame.draw.rect(icon, paper, (5, 12, 110, 72), border_radius=4)
            pygame.draw.rect(icon, (49, 104, 111), (11, 18, 98, 14))
            pygame.draw.circle(icon, (105, 132, 137), (33, 55), 15)
            pygame.draw.line(icon, ink, (59, 47), (99, 47), 3)
        elif kind == "tool":
            pygame.draw.line(icon, (147, 170, 174), (22, 77), (95, 19), 9)
            pygame.draw.arc(icon, (178, 68, 78), (3, 5, 55, 55), 0, 3.14, 12)
        elif kind == "panel":
            pygame.draw.rect(icon, (52, 73, 76), (5, 8, 110, 80), border_radius=4)
            for i in range(6):
                pygame.draw.circle(icon, GOOD if opened else gold, (27 + i % 3 * 33, 32 + i // 3 * 31), 9)
        elif kind == "lamp":
            pygame.draw.line(icon, gold, (63, 20), (63, 83), 6)
            pygame.draw.polygon(icon, (235, 211, 136), [(35, 10), (87, 10), (108, 47), (14, 47)])
            pygame.draw.ellipse(icon, gold, (37, 80, 53, 12))
        else:
            pygame.draw.rect(icon, paper, (10, 12, 100, 72), border_radius=3)
            if kind == "envelope":
                pygame.draw.lines(icon, ink, False, [(10, 12), (60, 51), (110, 12)], 2)
            else:
                for y in (29, 41, 53, 65):
                    pygame.draw.line(icon, ink, (25, y), (94, y), 2)
        g.screen.blit(pygame.transform.smoothscale(icon, rect.size), rect)

    def draw_inventory(self):
        g, c = self.g, self.c
        for i in range(6):
            pygame.draw.rect(g.screen, (65, 85, 84), (25 + i * 128, 637, 118, 72), 1, border_radius=4)
        for button in self.inventory_buttons():
            if not isinstance(button.value, tuple):
                button.draw(g.screen, g.fonts, pygame.mouse.get_pos())
                continue
            key = button.value[1]
            pygame.draw.rect(g.screen, (39, 70, 68) if button.selected else (28, 41, 43), button.rect, border_radius=4)
            pygame.draw.rect(g.screen, GOOD if button.selected else MUTED, button.rect, 2 if button.selected else 1, border_radius=4)
            self.draw_prop(key, pygame.Rect(button.rect.x + 40, 640, 40, 31))
            draw_text(g.screen, ITEMS[key][0], self.item_font, TEXT, pygame.Rect(button.rect.x + 3, 672, 112, 37), line_spacing=0, align="center")

    def draw_control(self, button):
        g = self.g
        hovered = button.enabled and button.rect.collidepoint(pygame.mouse.get_pos())
        fill = (51, 90, 87) if hovered or button.selected else (39, 49, 48)
        color = TEXT if button.enabled else MUTED
        pygame.draw.rect(g.screen, fill, button.rect, border_radius=4)
        pygame.draw.rect(g.screen, GOOD if hovered else MUTED, button.rect, 1, border_radius=4)
        label = g.fonts.small.render(button.text, True, color)
        scale = min(1, (button.rect.w - 16) / label.get_width(), (button.rect.h - 8) / label.get_height())
        if scale < 1:
            label = pygame.transform.smoothscale(label, (max(1, int(label.get_width() * scale)), max(1, int(label.get_height() * scale))))
        g.screen.blit(label, label.get_rect(center=button.rect.center))

    def draw_explore(self):
        c, g, d = self.c, self.g, self.c.data
        buttons = self.explore_buttons()
        for button in buttons:
            if isinstance(button.value, tuple) and button.value[0] == "object":
                key = button.value[1]
                done = (OBJECTS[key]["puzzle"] or key) in d["flags"]
                # Existing furniture stays visible; new evidence is drawn over the scenery.
                if key not in {"chair", "bin", "glass", "lamp", "desk"}:
                    self.draw_prop(key, button.rect, done)
                if done:
                    pygame.draw.circle(g.screen, GOOD, (button.rect.right - 4, button.rect.y + 4), 4)
            elif isinstance(button.value, tuple) and button.value[0] == "talk":
                actor = COMPANIONS[button.value[1]].lower()
                g.screen.blit(pygame.transform.smoothscale(g.stage_portraits[actor], button.rect.size), button.rect)
        if d["room"] == "intro":
            g.screen.blit(pygame.transform.smoothscale(g.stage_portraits["daniel"], (100, 155)), (850, 350))
        g.player.rect.clamp_ip(pygame.Rect(48, 340, 1034, 201))
        g.player.draw(g.screen)
        draw_band(g.screen, pygame.Rect(0, 550, 1120, 170))
        selected = ", ".join(ITEMS[k][0] for k in d["selected_items"])
        draw_text(g.screen, g.message or ("Em maos: " + selected if selected else OBJECTIVES[d["chapter"]]), g.fonts.small, TEXT, pygame.Rect(25, 560, 1070, 31))
        if d["selected_items"]:
            draw_text(g.screen, selected, g.fonts.small, ACCENT_2, pygame.Rect(25, 599, 545, 28))
        self.draw_inventory()
        for button in buttons:
            if isinstance(button.value, tuple) and button.value[0] in {"object", "talk"}:
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(g.screen, GOOD, button.rect, 2, border_radius=3)
                    label = g.fonts.small.render(button.text, True, TEXT)
                    r = label.get_rect(midbottom=(button.rect.centerx, button.rect.y - 4)).inflate(14, 8)
                    r.clamp_ip(pygame.Rect(6, 159, 1108, 383))
                    pygame.draw.rect(g.screen, (20, 29, 30), r, border_radius=3)
                    g.screen.blit(label, label.get_rect(center=r.center))
            elif not (isinstance(button.value, tuple) and button.value[0] == "item") and button.value not in {"previous", "next"}:
                self.draw_control(button)

    def draw_note(self):
        c, g, d = self.c, self.g, self.c.data
        draw_band(g.screen, pygame.Rect(0, 112, 1120, 608))
        draw_text(g.screen, d["note_title"], g.fonts.h2, TEXT, pygame.Rect(30, 137, 1050, 70))
        actor = d["note_title"].lower()
        key = next((key for key, obj in OBJECTS.items() if obj["label"] == d["note_title"]), "record")
        if actor in g.stage_portraits:
            g.screen.blit(pygame.transform.smoothscale(g.stage_portraits[actor], (185, 268)), (95, 230))
        else:
            self.draw_prop(key, pygame.Rect(55, 250, 245, 204), key in d["flags"])
        for i, line in enumerate(c.note_lines()[d["page"] * 10:d["page"] * 10 + 10]):
            draw_text(g.screen, line, g.fonts.body, TEXT, pygame.Rect(345, 224 + i * 28, 730, 28))
        self.draw_inventory()
        for button in self.note_buttons():
            if not (isinstance(button.value, tuple) and button.value[0] == "item"):
                self.draw_control(button)

    def draw_puzzle_button(self, button):
        d, g = self.c.data, self.g
        if d["view"] != "puzzle" or not isinstance(button.value, tuple) or button.value[0] != "answer":
            return False
        if d["puzzle"] not in {"books", "photos", "altered", "recordings"}:
            return False
        rect = button.rect
        fill = (51, 90, 87) if button.selected else (49, 57, 59)
        pygame.draw.rect(g.screen, fill, rect, border_radius=4)
        pygame.draw.rect(g.screen, GOOD if button.selected else MUTED, rect, 2, border_radius=4)
        kind = "shelves" if d["puzzle"] == "books" else "recordings" if d["puzzle"] == "recordings" else "photo"
        self.draw_prop(kind, pygame.Rect(rect.x + 7, rect.y + 12, 42, 42), button.selected)
        draw_text(g.screen, button.text, g.fonts.small, TEXT, pygame.Rect(rect.x + 58, rect.y + 8, rect.w - 65, rect.h - 12), line_spacing=2)
        return True
