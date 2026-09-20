"""Point-and-click investigation; the legacy filename preserves save integration."""

import json
import os

import pygame

from scripts.interfaces import Button, TEXT, MUTED, ACCENT_2, GOOD, draw_band, draw_text


POINTS = {"note": 10, "books": 30, "key": 10, "drawer": 20, "photo": 10,
          "badge": 10, "phone": 10, "records": 20, "envelope": 20, "case_closed": 20}
ITEMS = {"note": "Bilhete", "key": "Chave", "photo": "Fotografia", "badge": "Cracha"}
SCENES = {"room", "desk", "shelf", "drawer", "phone", "team", "records", "finished"}
HINTS = {
    "note": ("Cassie: Celine deixou algo sobre a mesa.", "Observe o papel ao lado da luminaria.", "Examine a mesa e recolha o bilhete."),
    "books": ("Cassie: O bilhete parece falar das lombadas da estante.", "A sequencia comeca com 3 e 5. Some os dois para encontrar o terceiro livro.", "Puxe os livros 3, 5 e 8, nessa ordem."),
    "key": ("Cassie: A estante se moveu.", "Ha um objeto metalico no compartimento aberto.", "Recolha a chave no compartimento da estante."),
    "drawer": ("Cassie: A chave pequena deve abrir um movel, nao a porta.", "A gaveta fica do lado esquerdo da mesa.", "Selecione a chave no inventario e clique na gaveta."),
    "photo": ("Cassie: A gaveta guarda uma imagem do escritorio.", "A fotografia pode mostrar o que estava aqui antes da investigacao.", "Recolha a fotografia na gaveta e confira a legenda."),
    "badge": ("Cassie: A gaveta guarda os documentos de Celine.", "O cartao identifica Celine nos registros do edificio.", "Recolha o cracha na gaveta e leve-o ao computador da equipe."),
    "phone": ("Cassie: Precisamos de horarios comprovados, nao de suposicoes.", "O aparelho esta na mesa redonda, a direita.", "Examine o celular: o ultimo registro e 20h42."),
    "records": ("Dean esta na sala ao lado, conferindo os registros do edificio.", "O computador da equipe consulta os acessos pelo cracha.", "Va pela porta, selecione o cracha e examine o computador."),
    "envelope": ("Cassie: Vale conferir se algo mudou enquanto estivemos com a equipe.", "Compare a mesa atual com a fotografia recolhida.", "Volte ao escritorio, examine a mesa e recolha o envelope com o nome CASSIE."),
    "case_closed": ("Cassie: O envelope nao estava aqui. Alguem interferiu na investigacao.", "A foto, o celular e os registros ajudam a separar a saida de Celine da chegada do envelope.", "Volte a sala da equipe e converse com Dean sobre as descobertas."),
}


def new_escape():
    return dict(version=2, scene="room", flags=[], selected="", books=[], hints={},
                message="Dean: Vou conferir os acessos na sala ao lado. Cassie, veja o que Celine deixou no escritorio.")


def migrate_escape(data):
    if not isinstance(data, dict) or "version" in data:
        return data
    old_keys = {"scene", "flags", "selected", "books", "code", "hints", "message"}
    old_flags = {"note", "books", "key", "drawer", "photo", "badge", "phone", "door", "escaped"}
    if set(data) != old_keys or not isinstance(data["flags"], list) or any(type(k) is not str or k not in old_flags for k in data["flags"]):
        raise ValueError("Progresso anterior invalido")
    if not isinstance(data["scene"], str) or data["scene"] not in {"room", "desk", "shelf", "drawer", "phone", "code", "finished"}:
        raise ValueError("Cena anterior invalida")
    if not isinstance(data["hints"], dict):
        raise ValueError("Dicas anteriores invalidas")
    migrated = {**data, "version": 2, "flags": [k for k in data["flags"] if k in POINTS],
                "hints": {k: v for k, v in data["hints"].items() if k in HINTS},
                "message": "Cassie: Os objetos estao comigo. Vou conferir os registros com a equipe."}
    migrated.pop("code")
    if migrated["scene"] in {"code", "finished"}:
        migrated["scene"] = "team"
    return migrated


def validate_escape(data):
    data = migrate_escape(data)
    if not isinstance(data, dict) or set(data) != set(new_escape()):
        raise ValueError("Sala incompleta")
    if type(data["version"]) is not int or data["version"] != 2:
        raise ValueError("Versao desconhecida")
    if not isinstance(data["scene"], str) or data["scene"] not in SCENES:
        raise ValueError("Cena invalida")
    if not isinstance(data["flags"], list) or any(type(k) is not str or k not in POINTS for k in data["flags"]) or len(set(data["flags"])) != len(data["flags"]):
        raise ValueError("Descobertas invalidas")
    if not isinstance(data["selected"], str) or (data["selected"] and (data["selected"] not in ITEMS or data["selected"] not in data["flags"])):
        raise ValueError("Objeto invalido")
    if not isinstance(data["books"], list) or len(data["books"]) > 3 or any(type(n) is not int or not 1 <= n <= 8 for n in data["books"]) or len(set(data["books"])) != len(data["books"]):
        raise ValueError("Livros invalidos")
    if not isinstance(data["hints"], dict) or any(k not in HINTS or type(v) is not int or not 1 <= v <= 3 for k, v in data["hints"].items()):
        raise ValueError("Dicas invalidas")
    if not isinstance(data["message"], str) or len(data["message"]) > 500:
        raise ValueError("Mensagem invalida")
    for flag, required in {"books": "note", "key": "books", "drawer": "key", "photo": "drawer", "badge": "drawer", "records": "badge", "envelope": "records", "case_closed": "envelope"}.items():
        if flag in data["flags"] and required not in data["flags"]:
            raise ValueError("Descobertas fora de ordem")
    if data["scene"] == "drawer" and "drawer" not in data["flags"]:
        raise ValueError("Gaveta fechada")
    if data["scene"] == "records" and "records" not in data["flags"]:
        raise ValueError("Registros ausentes")
    if "case_closed" in data["flags"] and not {"photo", "phone"}.issubset(data["flags"]):
        raise ValueError("Conclusao sem provas")
    if data["scene"] == "finished" and "case_closed" not in data["flags"]:
        raise ValueError("Investigacao incompleta")
    return data


class OfficeEscape:
    def __init__(self, game, path=None):
        self.game = game
        self.path = path
        self.data = new_escape()
        self.dean_image = pygame.transform.smoothscale(game.stage_portraits["dean"], (110, 160))

    def start(self):
        self.data = new_escape()
        if self.path and self.path.exists():
            try:
                self.data = validate_escape(json.loads(self.path.read_text(encoding="utf-8")))
            except (OSError, ValueError, TypeError):
                self.game.save_notice = "O teste salvo nao pode ser lido. O arquivo foi preservado."
                return False
        self.game.state = "escape_room"
        self.game.paused = False
        self.game.show_clues = False
        self.game.save_notice = ""
        return True

    def save(self):
        if self.path is None:
            return True
        try:
            validate_escape(self.data)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.data, ensure_ascii=True, indent=2), encoding="utf-8")
            os.replace(temporary, self.path)
        except (OSError, ValueError, TypeError):
            self.game.save_notice = "Nao foi possivel salvar o escritorio. Tente novamente antes de sair."
            return False
        self.game.save_notice = ""
        self.game.save_status = "Escritorio salvo."
        return True

    def has(self, flag):
        return flag in self.data["flags"]

    @property
    def score(self):
        return sum(POINTS[key] for key in self.data["flags"])

    def discover(self, key, text):
        if not self.has(key):
            self.data["flags"].append(key)
        self.data["message"] = text

    def stage(self):
        return next((key for key in HINTS if not self.has(key)), "case_closed")

    def buttons(self):
        d = self.data
        buttons = []
        def add(rect, label, value, selected=False):
            buttons.append(Button(pygame.Rect(rect), label, value, selected=selected))
        scene = d["scene"]
        if scene == "room":
            for rect, label, value in [((0, 140, 80, 340), "Sala da equipe", "door"),
                                       ((145, 140, 166, 190), "Estante", "shelf"),
                                       ((434, 177, 270, 62), "Mesa de Celine", "desk"),
                                       ((439, 244, 78, 46), "Gaveta", "drawer"),
                                       ((1024, 305, 96, 91), "Celular", "phone")]:
                add(rect, label, ("hotspot", value))
        elif scene == "desk":
            if not self.has("note"):
                add((440, 242, 245, 152), "Bilhete dobrado", ("take", "note"))
            if self.has("records") and not self.has("envelope"):
                add((630, 200, 195, 90), "Envelope CASSIE", ("take", "envelope"))
        elif scene == "shelf":
            if not self.has("books"):
                for n in range(1, 9):
                    add((198 + (n - 1) * 90, 177, 72, 235), f"Livro {n}", ("book", n), n in d["books"])
                add((800, 442, 150, 44), "Recolocar", "reset_books")
            elif not self.has("key"):
                add((465, 252, 185, 100), "Chave pequena", ("take", "key"))
        elif scene == "drawer":
            if not self.has("photo"):
                add((340, 227, 185, 175), "Fotografia", ("take", "photo"))
            if not self.has("badge"):
                add((623, 260, 160, 110), "Cracha de Celine", ("take", "badge"))
        elif scene == "team":
            add((715, 139, 191, 91), "Computador de acessos", ("hotspot", "terminal"))
            add((330, 350, 110, 160), "Dean", ("hotspot", "dean"))
            add((30, 465, 160, 42), "Escritorio", "back")
        elif scene == "finished":
            add((295, 440, 240, 52), "Jogar novamente", "restart")
            add((565, 440, 240, 52), "Voltar ao menu", "menu")
        if scene != "finished":
            if scene not in {"room", "team"}:
                add((30, 465, 160, 42), "Voltar a equipe" if scene == "records" else "Voltar a sala", "back")
            add((858, 645, 105, 48), "Dica", "hint")
            add((978, 645, 112, 48), "Menu", "menu")
        for i, (key, label) in enumerate(ITEMS.items()):
            if self.has(key):
                add((30 + i * 195, 633, 180, 70), label, ("item", key), d["selected"] == key)
        return buttons

    def activate(self, value):
        d = self.data
        if isinstance(value, tuple):
            action, key = value
            if action == "hotspot":
                if key == "drawer":
                    if self.has("drawer"):
                        d["scene"] = "drawer"
                    elif d["selected"] == "key":
                        self.discover("drawer", "Cassie: Abriu. Celine guardou uma fotografia e seu cracha.")
                        d.update(scene="drawer", selected="")
                    else:
                        d["message"] = "Cassie: A gaveta esta trancada. Preciso de uma chave pequena."
                elif key == "door":
                    d.update(scene="team", message="Dean: Pode entrar. Estou conferindo os acessos; o que voce encontrou?")
                elif key == "terminal":
                    if self.has("records"):
                        d["scene"] = "records"
                    elif d["selected"] == "badge":
                        self.discover("records", "Dean: Celine saiu as 20h30. Mais tarde houve outro acesso ao corredor do escritorio.")
                        d.update(scene="records", selected="")
                    else:
                        d["message"] = "Dean: Preciso do cracha de Celine para localizar os registros dela no computador."
                elif key == "dean":
                    if all(self.has(flag) for flag in ("photo", "phone", "records", "envelope")):
                        self.discover("case_closed", "Dean: A foto confirma. O envelope apareceu durante nossa investigacao; alguem quer falar com voce, Cassie.")
                        d["scene"] = "finished"
                    elif self.has("envelope"):
                        d["message"] = "Dean: Antes de concluir, confira a fotografia da gaveta e o horario no celular. Precisamos de registros."
                    elif self.has("records"):
                        d["message"] = "Dean: Alguem acessou o corredor enquanto estavamos aqui. Confira se algo mudou na mesa de Celine."
                    else:
                        d["message"] = "Dean: Procure documentos e o cracha no escritorio. Eu fico aqui; pode ir e voltar quando precisar."
                else:
                    d["scene"] = key
                    if key == "phone":
                        self.discover("phone", "Cassie: O ultimo registro foi as 20h42. Vou guardar esse horario.")
                    elif key == "shelf":
                        d["message"] = "Cassie: Algumas lombadas estao gastas. Esses livros parecem acionar um mecanismo."
                    else:
                        d["message"] = "Cassie: Esse envelope com meu nome nao estava aqui..." if self.has("records") and not self.has("envelope") else "Cassie: Vou conferir o que Celine deixou na mesa."
            elif action == "take":
                messages = {"note": "Bilhete: '3, 5, ... O proximo e a soma dos dois anteriores. As lombadas guardam a chave.'",
                            "key": "Cassie: Uma chave pequena. Deve servir na gaveta da mesa.",
                            "photo": "Fotografia de inspecao, 21h03: a mesa de Celine aparece sem nenhum envelope enderecado a Cassie.",
                            "badge": "Cassie: O cracha de Celine. Dean pode usar isso para consultar os acessos.",
                            "envelope": "Envelope CASSIE: 'Voce reconhece padroes. Reconhece a propria historia?' Preciso mostrar isso a Dean."}
                self.discover(key, messages[key])
            elif action == "item":
                d["selected"] = "" if d["selected"] == key else key
                if key == "note":
                    d["message"] = "Bilhete: '3, 5, ... O proximo e a soma dos dois anteriores. As lombadas guardam a chave.'"
                elif key == "photo":
                    d["message"] = "Fotografia de inspecao, 21h03: a mesa de Celine aparece sem nenhum envelope enderecado a Cassie."
                else:
                    d["message"] = ITEMS[key] + " em maos."
            elif action == "book":
                if not self.has("note"):
                    d["message"] = "Cassie: Sem uma pista, eu so estaria puxando livros ao acaso."
                elif key in d["books"]:
                    d["books"].remove(key)
                elif len(d["books"]) < 3:
                    d["books"].append(key)
                    if d["books"] == [3, 5, 8]:
                        self.discover("books", "Cassie: Ouvi um estalo. Ha uma chave atras da estante!")
                    elif len(d["books"]) == 3:
                        d["message"] = "Cassie: Nada aconteceu. A ordem precisa seguir o bilhete."
            return
        if value == "back":
            d["scene"] = "team" if d["scene"] == "records" else "room"
            if d["scene"] == "room" and self.has("records") and not self.has("envelope"):
                d["message"] = "Cassie: Espere... ha alguma coisa nova sobre a mesa."
        elif value == "reset_books":
            d["books"] = []
        elif value == "hint":
            stage = self.stage()
            level = min(3, d["hints"].get(stage, 0) + 1)
            d["hints"][stage] = level
            d["message"] = HINTS[stage][level - 1]
        elif value == "menu":
            self.game.reset_to_menu()
        elif value == "restart":
            self.data = new_escape()

    def handle_event(self, event):
        for button in self.buttons():
            if button.hit(event):
                self.activate(button.value)
                return

    def draw_item(self, key, rect):
        s = pygame.Surface((96, 72), pygame.SRCALPHA)
        x, y = 48, 36
        if key == "key":
            pygame.draw.circle(s, (231, 190, 77), (x - 19, y), 12, 5)
            pygame.draw.line(s, (231, 190, 77), (x - 6, y), (x + 35, y), 6)
            pygame.draw.line(s, (231, 190, 77), (x + 25, y), (x + 25, y + 12), 5)
        else:
            paper = pygame.Rect(x - 38, y - 25, 76, 50)
            pygame.draw.rect(s, (215, 222, 213), paper, border_radius=3)
            if key == "badge":
                pygame.draw.rect(s, (43, 88, 91), (x - 34, y - 20, 68, 12))
                pygame.draw.circle(s, (93, 116, 118), (x - 18, y + 3), 10)
            elif key == "photo":
                s.blit(pygame.transform.smoothscale(self.game.room_image, (64, 36)), (x - 32, y - 19))
            else:
                for offset in (-10, 0, 10):
                    pygame.draw.line(s, (73, 79, 82), (x - 26, y + offset), (x + 26, y + offset), 2)
                if key == "envelope":
                    pygame.draw.rect(s, (215, 222, 213), paper)
                    pygame.draw.lines(s, (73, 79, 82), False, [(x - 38, y - 25), (x, y), (x + 38, y - 25)], 2)
                    name = self.game.fonts.small.render("CASSIE", True, (40, 50, 52))
                    s.blit(name, name.get_rect(center=(x, y + 13)))
        scale = min(rect.width / 96, rect.height / 72, 1.8)
        icon = pygame.transform.smoothscale(s, (int(96 * scale), int(72 * scale)))
        self.game.screen.blit(icon, icon.get_rect(center=rect.center))

    def draw(self):
        g, d = self.game, self.data
        s, f = g.screen, g.fonts
        scene = d["scene"]
        s.blit(g.backgrounds["analise"] if scene in {"team", "records", "finished"} else g.room_image, (0, 0))
        if scene == "room":
            s.blit(g.player_poses["idle"], (800, 375))
            if self.has("drawer"):
                pygame.draw.rect(s, (22, 21, 18), (440, 246, 77, 36))
                pygame.draw.rect(s, (112, 82, 52), (432, 277, 88, 14))
            if self.has("books"):
                pygame.draw.rect(s, (24, 29, 27), (169, 196, 105, 72))
                if not self.has("key"):
                    self.draw_item("key", pygame.Rect(177, 213, 90, 30))
            if self.has("records") and not self.has("envelope"):
                self.draw_item("envelope", pygame.Rect(596, 202, 68, 44))
        elif scene == "team":
            s.blit(self.dean_image, (330, 350))
            s.blit(g.player_poses["idle"], (520, 375))
        else:
            draw_band(s, pygame.Rect(0, 82, 1120, 448), 245)
            if scene in ("desk", "drawer", "shelf"):
                crop = pygame.Rect(429, 170, 283, 167) if scene != "shelf" else pygame.Rect(140, 140, 172, 195)
                s.blit(pygame.transform.smoothscale(g.room_image.subsurface(crop), (760, 370)), (180, 118))
            if scene == "desk" and self.has("note") and not self.has("records"):
                draw_text(s, "O bilhete esta com Cassie.", f.body, TEXT, pygame.Rect(345, 230, 470, 70), align="center")
            elif scene == "drawer":
                pygame.draw.rect(s, (58, 43, 35), (245, 177, 630, 280), border_radius=4)
                pygame.draw.rect(s, (142, 106, 68), (232, 439, 656, 30), border_radius=3)
            elif scene == "shelf" and self.has("books"):
                pygame.draw.rect(s, (22, 27, 27), (350, 193, 420, 211))
                draw_text(s, "Compartimento aberto", f.body, TEXT, pygame.Rect(370, 365, 380, 30), align="center")
            elif scene == "phone":
                pygame.draw.rect(s, (53, 62, 65), (411, 109, 298, 393), border_radius=8)
                pygame.draw.rect(s, (16, 24, 26), (429, 128, 262, 350), border_radius=4)
                draw_text(s, "REGISTRO DO APARELHO", f.small, MUTED, pygame.Rect(445, 169, 230, 48), align="center")
                draw_text(s, "20:42", f.title, TEXT, pygame.Rect(445, 247, 230, 80), align="center")
                draw_text(s, "Desligamento", f.body, ACCENT_2, pygame.Rect(445, 340, 230, 35), align="center")
            elif scene == "records":
                draw_text(s, "REGISTROS DO EDIFICIO", f.h1, TEXT, pygame.Rect(220, 120, 800, 60))
                for i, line in enumerate(("20h30  /  Saida de Celine registrada na portaria.",
                                           "21h09  /  Entrada no corredor do escritorio.",
                                           "21h14  /  Saida da pessoa que acessou o corredor.",
                                           "A imagem nao permite identificar essa pessoa.")):
                    draw_text(s, line, f.body, TEXT, pygame.Rect(220, 215 + i * 52, 820, 48))
            elif scene == "finished":
                draw_text(s, "Uma mensagem para Cassie", f.h1, TEXT, pygame.Rect(170, 150, 780, 80), align="center")
                draw_text(s, f"{self.score} pontos", f.h1, GOOD, pygame.Rect(200, 250, 720, 55), align="center")
                draw_text(s, "O envelope apareceu depois da saida de Celine, durante a investigacao. Cassie e Dean decidem analisar a mensagem. Nada disso, sozinho, comprova um sequestro.", f.body, TEXT, pygame.Rect(240, 327, 640, 100), align="center")
        draw_band(s, pygame.Rect(0, 0, 1120, 82))
        location = "SALA DA EQUIPE" if scene in {"team", "records", "finished"} else "ESCRITORIO DE CELINE"
        draw_text(s, "CONFLITOS DE SANGUE / " + location, f.small, ACCENT_2, pygame.Rect(28, 8, 830, 24))
        draw_text(s, "Investigue o desaparecimento de Celine", f.h2, TEXT, pygame.Rect(28, 34, 860, 40))
        draw_text(s, f"{self.score} pontos", f.body, TEXT, pygame.Rect(940, 27, 170, 34))
        draw_band(s, pygame.Rect(0, 530, 1120, 190))
        draw_text(s, d["message"], f.body, TEXT, pygame.Rect(30, 543, 1050, 67))
        draw_text(s, "COM CASSIE", f.small, MUTED, pygame.Rect(30, 609, 500, 24))
        for i in range(4):
            pygame.draw.rect(s, (42, 53, 54), (30 + i * 195, 633, 180, 70), 1, border_radius=4)
        mouse = pygame.mouse.get_pos()
        for button in self.buttons():
            value = button.value
            if isinstance(value, tuple) and value[0] in ("hotspot", "take", "book"):
                kind, key = value
                if kind == "take":
                    self.draw_item(key, button.rect)
                elif kind == "book":
                    rect = button.rect.copy()
                    rect.y += 15 if button.selected else 0
                    color = [(122, 58, 61), (56, 91, 91), (105, 105, 62)][key % 3]
                    pygame.draw.rect(s, color, rect, border_radius=3)
                    pygame.draw.rect(s, (199, 178, 119), rect, 2, border_radius=3)
                    draw_text(s, str(key), f.h1, TEXT, pygame.Rect(rect.x, rect.y + 90, rect.w, 55), align="center")
                    if button.selected:
                        draw_text(s, str(d["books"].index(key) + 1), f.small, GOOD, pygame.Rect(rect.x, rect.y + 12, rect.w, 30), align="center")
                if button.rect.collidepoint(mouse):
                    pygame.draw.rect(s, GOOD, button.rect, 2, border_radius=4)
                    text = f.small.render(button.text, True, TEXT)
                    label = text.get_rect(midbottom=(button.rect.centerx, button.rect.y - 4)).inflate(16, 8)
                    label.clamp_ip(pygame.Rect(8, 85, 1104, 435))
                    pygame.draw.rect(s, (20, 29, 29), label, border_radius=3)
                    s.blit(text, text.get_rect(center=label.center))
            else:
                if isinstance(value, tuple) and value[0] == "item":
                    fill = (40, 73, 68) if button.selected else (35, 47, 48)
                    pygame.draw.rect(s, fill, button.rect, border_radius=4)
                    color = GOOD if button.selected or button.rect.collidepoint(mouse) else MUTED
                    pygame.draw.rect(s, color, button.rect, 2 if button.selected else 1, border_radius=4)
                    self.draw_item(value[1], pygame.Rect(button.rect.x + 48, button.rect.y + 3, 84, 39))
                    draw_text(s, button.text, f.small, TEXT, pygame.Rect(button.rect.x, button.rect.y + 44, button.rect.w, 25), align="center")
                else:
                    button.draw(s, f, mouse)
