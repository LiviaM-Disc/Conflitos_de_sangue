from __future__ import annotations

from pathlib import Path

import pygame

from scripts.dialogos import (
    FINAL_CHOICES,
    INTERROGATION_CHOICES,
    INTERROGATION_STATEMENTS,
    PROFILE_CORRECT_ORDER,
    PROFILE_EVENTS,
    PROLOGUE_CHOICES,
    PROLOGUE_LINES,
)
from scripts.interfaces import (
    ACCENT,
    ACCENT_2,
    BAD,
    BG,
    GOOD,
    MUTED,
    PANEL,
    TEXT,
    Button,
    FontBook,
    draw_clue_panel,
    draw_dialogue_box,
    draw_gradient,
    draw_hud,
    draw_message,
    draw_panel,
    draw_text,
)
from scripts.investigacao import InvestigationState
from scripts.personagens import CHARACTERS, Player, load_portrait, load_portraits
from scripts.pistas import EVIDENCES


class Game:
    def __init__(self, screen: pygame.Surface, root: Path) -> None:
        self.screen = screen
        self.root = root
        self.assets_dir = root / "assets"
        self.fonts = FontBook()
        self.investigation = InvestigationState()
        self.player_poses = {
            pose: load_portrait(self.assets_dir / "personagens", "cassie", (92, 142), pose)
            for pose in ("idle", "walk", "action")
        }
        self.player = Player((485, 535), self.player_poses)
        self.portraits = load_portraits(self.assets_dir)
        self.action_portraits = load_portraits(self.assets_dir, "action")
        self.room_image = pygame.transform.smoothscale(
            pygame.image.load(str(self.assets_dir / "cenarios" / "escritorio.png")).convert(),
            self.screen.get_size(),
        )

        self.running = True
        self.state = "menu"
        self.paused = False
        self.show_clues = False
        self.message = ""
        self.message_timer = 0.0

        self.dialogue_index = 0
        self.profile_selection: list[int] = []
        self.puzzle_step = 0
        self.final_feedback = ""
        self.interrogation_feedback = ""
        self.phase5_hint_used = False

        self.room_bounds = pygame.Rect(48, 337, 1034, 313)
        self.obstacles = (pygame.Rect(426, 300, 280, 82), pygame.Rect(1030, 340, 90, 127))
        self.interactables = [
            {
                "id": "celine_bracelet",
                "label": "Pulseira",
                "rect": pygame.Rect(82, 516, 42, 26),
                "marker": (102, 523),
                "color": (155, 116, 76),
            },
            {
                "id": "broken_phone",
                "label": "Celular",
                "rect": pygame.Rect(992, 370, 35, 50),
                "marker": (1078, 347),
                "color": (73, 81, 88),
            },
            {
                "id": "coded_invitation",
                "label": "Convite",
                "rect": pygame.Rect(522, 377, 65, 22),
                "marker": (568, 224),
                "color": (169, 161, 134),
            },
            {
                "id": "dusty_book",
                "label": "Livro",
                "rect": pygame.Rect(142, 334, 64, 28),
                "marker": (169, 246),
                "color": (96, 73, 62),
            },
            {
                "id": "window_mark",
                "label": "Janela",
                "rect": pygame.Rect(846, 337, 64, 28),
                "marker": (883, 212),
                "color": (72, 102, 112),
            },
        ]

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.state not in {"menu", "epilogue"}:
                    self.paused = not self.paused
                    self.show_clues = False
                    continue
                if event.key == pygame.K_TAB and self.state != "menu":
                    self.show_clues = not self.show_clues
                    continue

            if self.show_clues or self.paused:
                self.handle_overlay_events(event)
                continue

            if self.state == "menu":
                self.handle_menu_event(event)
            elif self.state == "prologue":
                self.handle_prologue_event(event)
            elif self.state == "phase1":
                self.handle_phase1_event(event)
            elif self.state == "interrogation":
                self.handle_interrogation_event(event)
            elif self.state == "puzzle":
                self.handle_puzzle_event(event)
            elif self.state == "profile":
                self.handle_profile_event(event)
            elif self.state == "finale":
                self.handle_finale_event(event)
            elif self.state == "epilogue":
                self.handle_epilogue_event(event)

    def handle_overlay_events(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        if self.paused:
            for button in self.pause_buttons():
                if button.hit(event):
                    if button.value == "resume":
                        self.paused = False
                    elif button.value == "menu":
                        self.reset_to_menu()

    def handle_menu_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in {pygame.K_RETURN, pygame.K_SPACE}:
            self.start_game()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.menu_buttons():
                if button.hit(event):
                    self.start_game()

    def handle_prologue_event(self, event: pygame.event.Event) -> None:
        if self.dialogue_index < len(PROLOGUE_LINES):
            if event.type == pygame.KEYDOWN and event.key in {pygame.K_SPACE, pygame.K_RETURN}:
                self.dialogue_index += 1
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.prologue_choice_buttons():
                if button.hit(event):
                    _, evidence_id, feedback = button.value
                    if evidence_id:
                        self.investigation.add_evidence(evidence_id)
                        self.investigation.use_ability("cassie_prologue")
                    else:
                        self.investigation.mistakes += 1
                        self.investigation.score -= 10
                    self.set_message(feedback)
                    self.state = "phase1"

    def handle_phase1_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.try_interact()
            elif event.key == pygame.K_q:
                self.player.investigate()
                if self.investigation.use_ability("cassie_observation"):
                    self.set_message("Cassie reconstruiu a cena: nada aqui parece aleatorio.")
                else:
                    self.set_message("Cassie ja registrou o padrao principal desta sala.")
            elif event.key == pygame.K_RETURN and self.investigation.has_all_phase1_required():
                self.state = "interrogation"
                self.set_message("")

    def handle_interrogation_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.interrogation_buttons():
                if button.hit(event):
                    text, correct = button.value
                    self.investigation.register_lie(correct)
                    self.investigation.register_emotion_read()
                    if correct:
                        self.interrogation_feedback = "Correto: a mentira indica protecao e medo, nao culpa automatica."
                    else:
                        self.interrogation_feedback = "Essa conclusao força as evidencias. A investigacao perde pontos."
                    self.state = "puzzle"

    def handle_puzzle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.puzzle_buttons():
                if button.hit(event):
                    if self.puzzle_step == 0:
                        correct = button.value == 21
                        self.investigation.register_puzzle(correct)
                        if correct:
                            self.puzzle_step = 1
                            self.set_message("Sloane: agora encontre o numero que nao pertence ao padrao.")
                        else:
                            self.set_message("Nao fecha. A regra soma os dois numeros anteriores.")
                    else:
                        correct = button.value == 30
                        self.investigation.register_puzzle(correct)
                        if correct:
                            self.investigation.add_evidence("fibonacci_key")
                            self.state = "profile"
                            self.set_message("Padrao resolvido. A chave aponta para uma armadilha em progresso.")
                        else:
                            self.set_message("Esse numero ainda obedece ao padrao. Procure a quebra.")

    def handle_profile_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.profile_buttons():
                if button.hit(event):
                    if button.value == "check":
                        correct = self.profile_selection == PROFILE_CORRECT_ORDER
                        self.investigation.register_connection(correct)
                        if correct:
                            self.investigation.add_evidence("profile_sequence")
                            self.state = "finale"
                            self.set_message("A sequencia fecha. A equipe percebe tarde demais: tambem era alvo.")
                        else:
                            self.profile_selection.clear()
                            self.set_message("Ha uma inconsistencia na ordem. Revise a linha do tempo.")
                    elif button.value == "clear":
                        self.profile_selection.clear()
                    elif button.value not in self.profile_selection:
                        self.profile_selection.append(button.value)

    def handle_finale_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            if not self.phase5_hint_used and self.investigation.use_ability("cassie_finale"):
                self.phase5_hint_used = True
                self.set_message("Cassie: a isca nao era so Celine. Era a nossa necessidade de entender.")
            else:
                self.set_message("Agora Cassie precisa concluir sem novas ajudas.")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.final_buttons():
                if button.hit(event):
                    _, correct = button.value
                    self.investigation.register_connection(correct)
                    if correct:
                        self.investigation.add_evidence("final_deduction")
                        self.final_feedback = "A deducao conecta Celine, Masters, Cassie e Lorelai."
                    else:
                        self.final_feedback = "A hipotese nao sustenta todos os rastros. O final continua, mas a pontuacao cai."
                    self.state = "epilogue"

    def handle_epilogue_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in {pygame.K_RETURN, pygame.K_SPACE}:
            self.reset_to_menu()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.epilogue_buttons():
                if button.hit(event):
                    self.reset_to_menu()

    def update(self, dt: float) -> None:
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

        if self.state == "phase1" and not self.paused and not self.show_clues:
            self.player.update(dt, pygame.key.get_pressed(), self.room_bounds, self.obstacles)

    def draw(self) -> None:
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "prologue":
            self.draw_prologue()
        elif self.state == "phase1":
            self.draw_phase1()
        elif self.state == "interrogation":
            self.draw_interrogation()
        elif self.state == "puzzle":
            self.draw_puzzle()
        elif self.state == "profile":
            self.draw_profile()
        elif self.state == "finale":
            self.draw_finale()
        elif self.state == "epilogue":
            self.draw_epilogue()

        if self.show_clues:
            draw_clue_panel(self.screen, self.fonts, self.investigation.discovered(), self.investigation.score)
        if self.paused:
            self.draw_pause()

    def draw_menu(self) -> None:
        self.screen.blit(self.room_image, (0, 0))
        shade = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        shade.fill((10, 17, 17, 155))
        self.screen.blit(shade, (0, 0))
        width, height = self.screen.get_size()

        title = self.fonts.title.render("Conflitos de Sangue", True, TEXT)
        self.screen.blit(title, title.get_rect(center=(width // 2, 145)))
        subtitle = self.fonts.subtitle.render("Aventura narrativa 2D de misterio e investigacao", True, MUTED)
        self.screen.blit(subtitle, subtitle.get_rect(center=(width // 2, 200)))

        case_rect = pygame.Rect(230, 272, width - 460, 190)
        draw_text(
            self.screen,
            (
                "Investigue o desaparecimento de Celine, conecte pistas, use as habilidades "
                "dos Naturais e descubra o padrao por tras dos Masters."
            ),
            self.fonts.body,
            TEXT,
            pygame.Rect(case_rect.x + 34, case_rect.y + 32, case_rect.width - 68, 70),
            align="center",
        )
        draw_text(
            self.screen,
            "Um desaparecimento. Uma mensagem. Uma armadilha.",
            self.fonts.small,
            MUTED,
            pygame.Rect(case_rect.x + 34, case_rect.y + 118, case_rect.width - 68, 32),
            align="center",
        )

        for button in self.menu_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_prologue(self) -> None:
        draw_gradient(self.screen, (20, 21, 27), (45, 39, 45))
        self.draw_portrait("daniel", (140, 146))
        self.draw_portrait("cassie", (820, 146))
        draw_hud(self.screen, self.fonts, self.investigation.score, "Prologo: observe as falas de Daniel Redding.")

        if self.dialogue_index < len(PROLOGUE_LINES):
            speaker, text = PROLOGUE_LINES[self.dialogue_index]
            draw_dialogue_box(self.screen, self.fonts, speaker, text)
        else:
            draw_dialogue_box(
                self.screen,
                self.fonts,
                "Cassie",
                "Redding deixou uma abertura. Como voce conduz a conversa?",
                "Escolha uma resposta",
            )
            for button in self.prologue_choice_buttons():
                button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_phase1(self) -> None:
        self.draw_room()
        self.player.draw(self.screen)
        bar = pygame.Surface((1120, 72), pygame.SRCALPHA)
        bar.fill((18, 24, 25, 235))
        self.screen.blit(bar, (0, 0))
        self.screen.blit(self.fonts.small.render("CASO 01 / O DESAPARECIMENTO", True, ACCENT_2), (28, 12))
        self.screen.blit(self.fonts.h2.render("O escritorio de Celine", True, TEXT), (28, 33))
        count = sum(self.investigation.has(key) for key in ("celine_bracelet", "broken_phone", "coded_invitation"))
        status = self.fonts.body.render(f"Evidencias {count}/3     Pontos {self.investigation.score}", True, TEXT)
        self.screen.blit(status, status.get_rect(midright=(1090, 36)))
        self.screen.blit(bar, (0, 664))
        nearest = self.nearest_interactable()
        if nearest:
            prompt = self.fonts.body.render(f"Investigar: {nearest['label']}", True, TEXT)
            self.screen.blit(prompt, (28, 682))
        else:
            self.screen.blit(self.fonts.body.render("Encontre os rastros deixados por Celine.", True, MUTED), (28, 682))
        if self.investigation.has_all_phase1_required():
            ready = self.fonts.body.render("ENTER - Seguir para o interrogatorio", True, GOOD)
            self.screen.blit(ready, ready.get_rect(midright=(1090, 694)))
        draw_message(self.screen, self.fonts, self.message)

    def draw_room(self) -> None:
        self.screen.blit(self.room_image, (0, 0))
        nearest = self.nearest_interactable()
        for item in self.interactables:
            if self.investigation.has(item["id"]) and item is not nearest:
                continue
            x, y = item["marker"]
            color = TEXT if item is nearest else (221, 197, 127)
            pygame.draw.circle(self.screen, (24, 29, 28), (x, y - 20), 10)
            pygame.draw.circle(self.screen, color, (x, y - 20), 9, 1)
            pygame.draw.circle(self.screen, color, (x, y - 20), 2)
            if item is nearest:
                label = self.fonts.small.render(item["label"], True, TEXT)
                rect = label.get_rect(midbottom=(x, y - 36)).inflate(20, 12)
                rect.clamp_ip(self.screen.get_rect())
                pygame.draw.rect(self.screen, (24, 29, 28), rect, border_radius=4)
                self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_interrogation(self) -> None:
        draw_gradient(self.screen, (21, 22, 28), (39, 33, 38))
        draw_hud(
            self.screen,
            self.fonts,
            self.investigation.score,
            "Fase 2: Lia indica mentira, Michael le emocoes. Interprete sem concluir cedo demais.",
        )
        self.draw_portrait("lia", (88, 130))
        self.draw_portrait("michael", (870, 130))

        rect = pygame.Rect(285, 118, 550, 222)
        draw_panel(self.screen, rect, (35, 37, 44))
        y = rect.y + 24
        for line in INTERROGATION_STATEMENTS:
            y = draw_text(self.screen, line, self.fonts.body, TEXT, pygame.Rect(rect.x + 24, y, rect.width - 48, 52)) + 8

        for button in self.interrogation_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_puzzle(self) -> None:
        draw_gradient(self.screen, (20, 24, 29), (31, 52, 54))
        draw_hud(self.screen, self.fonts, self.investigation.score, "Fase 3: encontre o padrao dos Masters.")
        self.draw_portrait("sloane", (80, 154))

        rect = pygame.Rect(290, 130, 720, 250)
        draw_panel(self.screen, rect, (34, 38, 44))
        title = self.fonts.h1.render("Analise de padroes", True, TEXT)
        self.screen.blit(title, (rect.x + 28, rect.y + 24))
        if self.puzzle_step == 0:
            prompt = "Complete a sequencia: 3, 5, 8, 13, ?, 34"
        else:
            prompt = "Qual numero quebra o padrao: 8, 13, 21, 30, 34, 55?"
        draw_text(self.screen, prompt, self.fonts.subtitle, TEXT, pygame.Rect(rect.x + 28, rect.y + 82, rect.width - 56, 70))
        draw_text(
            self.screen,
            "Sloane entrega a estrutura, mas a conclusao ainda precisa ser sua.",
            self.fonts.body,
            MUTED,
            pygame.Rect(rect.x + 28, rect.y + 162, rect.width - 56, 48),
        )

        for button in self.puzzle_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())
        draw_message(self.screen, self.fonts, self.message)

    def draw_profile(self) -> None:
        draw_gradient(self.screen, (22, 22, 27), (48, 41, 48))
        draw_hud(self.screen, self.fonts, self.investigation.score, "Fase 4: organize os acontecimentos para reconstruir a armadilha.")
        self.draw_portrait("cassie", (70, 132))
        self.draw_portrait("dean", (890, 132))

        board = pygame.Rect(276, 105, 570, 445)
        draw_panel(self.screen, board, (35, 37, 44))
        title = self.fonts.h1.render("Reconstrucao", True, TEXT)
        self.screen.blit(title, (board.x + 26, board.y + 24))
        draw_text(
            self.screen,
            "Clique nos eventos na ordem mais coerente. Uma ordem fraca revela inconsistencia.",
            self.fonts.body,
            MUTED,
            pygame.Rect(board.x + 26, board.y + 70, board.width - 52, 52),
        )

        for button in self.profile_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

        selected = " -> ".join(str(i + 1) for i in self.profile_selection) or "nenhum evento selecionado"
        draw_text(
            self.screen,
            f"Ordem atual: {selected}",
            self.fonts.body,
            ACCENT_2,
            pygame.Rect(board.x + 26, board.bottom - 62, board.width - 52, 34),
        )
        draw_message(self.screen, self.fonts, self.message)

    def draw_finale(self) -> None:
        draw_gradient(self.screen, (18, 19, 24), (58, 31, 39))
        draw_hud(
            self.screen,
            self.fonts,
            self.investigation.score,
            "Fase 5: Cassie esta sem apoio direto. Q usa a ultima reconstrucao mental.",
        )
        self.draw_portrait("cassie", (86, 132))
        self.draw_portrait("lorelai", (872, 132))

        rect = pygame.Rect(282, 104, 560, 214)
        draw_panel(self.screen, rect, (35, 35, 42))
        title = self.fonts.h1.render("Deducao final", True, TEXT)
        self.screen.blit(title, (rect.x + 24, rect.y + 22))
        draw_text(
            self.screen,
            (
                "As pistas nao apontam para uma fuga simples. Elas formam uma provocacao "
                "dirigida a Cassie e ao passado que os Masters querem reabrir."
            ),
            self.fonts.body,
            TEXT,
            pygame.Rect(rect.x + 24, rect.y + 72, rect.width - 48, 100),
        )

        for button in self.final_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())
        draw_message(self.screen, self.fonts, self.message)

    def draw_epilogue(self) -> None:
        draw_gradient(self.screen, (24, 25, 30), (35, 45, 43))
        width = self.screen.get_width()
        title = self.fonts.title.render("Epilogo", True, TEXT)
        self.screen.blit(title, title.get_rect(center=(width // 2, 90)))

        rect = pygame.Rect(220, 150, width - 440, 390)
        draw_panel(self.screen, rect, (34, 36, 43))
        rating = self.fonts.h1.render(self.investigation.final_rating(), True, GOOD if self.investigation.score >= 100 else TEXT)
        self.screen.blit(rating, (rect.x + 30, rect.y + 30))

        lines = [
            f"Pontuacao total: {self.investigation.score}",
            f"Pistas encontradas: {len(self.investigation.evidence)}",
            f"Enigmas resolvidos: {self.investigation.solved_puzzles}",
            f"Mentiras identificadas: {self.investigation.lies_found}",
            f"Conexoes corretas: {self.investigation.correct_connections}",
            f"Erros investigativos: {self.investigation.mistakes}",
        ]
        y = rect.y + 92
        for line in lines:
            image = self.fonts.body.render(line, True, TEXT)
            self.screen.blit(image, (rect.x + 34, y))
            y += 36

        if self.final_feedback:
            draw_text(self.screen, self.final_feedback, self.fonts.body, MUTED, pygame.Rect(rect.x + 34, rect.bottom - 78, rect.width - 68, 48))

        for button in self.epilogue_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_pause(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        rect = pygame.Rect(390, 210, 340, 250)
        draw_panel(self.screen, rect, PANEL)
        title = self.fonts.h1.render("Pausa", True, TEXT)
        self.screen.blit(title, title.get_rect(center=(rect.centerx, rect.y + 46)))
        for button in self.pause_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_portrait(self, key: str, pos: tuple[int, int]) -> None:
        portraits = self.action_portraits if self.state in {"interrogation", "puzzle", "profile", "finale"} else self.portraits
        self.screen.blit(portraits[key], pos)
        info = CHARACTERS[key]
        name = self.fonts.h2.render(info["name"], True, TEXT)
        ability = self.fonts.small.render(info["ability"], True, MUTED)
        self.screen.blit(name, (pos[0], pos[1] + 230))
        self.screen.blit(ability, (pos[0], pos[1] + 258))

    def try_interact(self) -> None:
        item = self.nearest_interactable()
        if not item:
            self.set_message("Nada relevante ao alcance.")
            return

        is_new, evidence = self.investigation.add_evidence(item["id"])
        self.player.investigate()
        if is_new:
            self.set_message(f"Pista registrada: {evidence.name}. {evidence.description}")
        else:
            self.set_message(evidence.description)

    def nearest_interactable(self) -> dict | None:
        for item in self.interactables:
            if self.player.rect.colliderect(item["rect"].inflate(44, 44)):
                return item
        return None

    def set_message(self, message: str, seconds: float = 4.5) -> None:
        self.message = message
        self.message_timer = seconds

    def start_game(self) -> None:
        self.investigation = InvestigationState()
        self.player = Player((485, 535), self.player_poses)
        self.state = "prologue"
        self.dialogue_index = 0
        self.puzzle_step = 0
        self.profile_selection = []
        self.final_feedback = ""
        self.interrogation_feedback = ""
        self.phase5_hint_used = False
        self.show_clues = False
        self.paused = False
        self.set_message("")

    def reset_to_menu(self) -> None:
        self.state = "menu"
        self.paused = False
        self.show_clues = False
        self.set_message("")

    def menu_buttons(self) -> list[Button]:
        return [Button(pygame.Rect(435, 505, 250, 58), "Iniciar investigacao", "start")]

    def prologue_choice_buttons(self) -> list[Button]:
        return [
            Button(pygame.Rect(220, 462, 320, 62), PROLOGUE_CHOICES[0][0], PROLOGUE_CHOICES[0]),
            Button(pygame.Rect(580, 462, 320, 62), PROLOGUE_CHOICES[1][0], PROLOGUE_CHOICES[1]),
        ]

    def interrogation_buttons(self) -> list[Button]:
        buttons = []
        y = 392
        for text, correct in INTERROGATION_CHOICES:
            buttons.append(Button(pygame.Rect(250, y, 620, 58), text, (text, correct)))
            y += 74
        return buttons

    def puzzle_buttons(self) -> list[Button]:
        values = [18, 21, 26] if self.puzzle_step == 0 else [21, 30, 55]
        buttons = []
        start_x = 385
        for index, value in enumerate(values):
            buttons.append(Button(pygame.Rect(start_x + index * 150, 438, 120, 62), str(value), value))
        return buttons

    def profile_buttons(self) -> list[Button]:
        buttons = []
        y = 238
        for index, event_text in enumerate(PROFILE_EVENTS):
            label = f"{index + 1}. {event_text}"
            enabled = index not in self.profile_selection
            buttons.append(Button(pygame.Rect(318, y, 486, 48), label, index, enabled=enabled))
            y += 58
        buttons.append(Button(pygame.Rect(318, 494, 150, 44), "Limpar", "clear"))
        buttons.append(Button(pygame.Rect(654, 494, 150, 44), "Conferir", "check", enabled=len(self.profile_selection) == 4))
        return buttons

    def final_buttons(self) -> list[Button]:
        buttons = []
        y = 358
        for text, correct in FINAL_CHOICES:
            buttons.append(Button(pygame.Rect(250, y, 620, 58), text, (text, correct)))
            y += 74
        return buttons

    def epilogue_buttons(self) -> list[Button]:
        return [Button(pygame.Rect(435, 585, 250, 56), "Voltar ao menu", "menu")]

    def pause_buttons(self) -> list[Button]:
        return [
            Button(pygame.Rect(460, 300, 200, 52), "Continuar", "resume"),
            Button(pygame.Rect(460, 370, 200, 52), "Menu inicial", "menu"),
        ]
