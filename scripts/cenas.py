from __future__ import annotations

from pathlib import Path
from copy import deepcopy
from uuid import uuid4

import pygame

from scripts.dialogos import (
    FINAL_ROUNDS,
    INTERROGATION_ROUNDS,
    PUZZLE_ROUNDS,
    PROFILE_EVIDENCES,
    PROFILE_PAIR,
    PROFILE_CORRECT_ORDER,
    PROFILE_EVENTS,
    PROLOGUE_CHOICES,
    PROLOGUE_LINES,
    PROLOGUE_OUTRO,
    EPILOGUE_LINES,
)
from scripts.interfaces import (
    ACCENT,
    ACCENT_2,
    GOOD,
    MUTED,
    PANEL,
    TEXT,
    Button,
    FontBook,
    CLUES_PER_PAGE,
    draw_band,
    draw_scene_header,
    draw_clue_panel,
    draw_dialogue_box,
    draw_message,
    draw_panel,
    draw_text,
)
from scripts.investigacao import InvestigationState
from scripts.personagens import CHARACTERS, Player, load_portrait
from scripts.pistas import EVIDENCES, FINAL_REQUIRED
from scripts.salvamento import SaveStore, STAGES, PROGRESS_FIELDS, snapshot
from scripts.campanha import ExpandedCampaign, new_campaign
from scripts.escritorio_escape import OfficeEscape
from scripts.jogadores import PlayerScreens
from scripts.instrucoes import Instructions


class Game:
    def __init__(self, screen: pygame.Surface, root: Path, save_path: Path | None = None, ranking_store=None) -> None:
        self.screen = screen
        self.root = root
        self.assets_dir = root / "assets"
        self.fonts = FontBook()
        self.save_store = SaveStore(save_path) if save_path is not None else None
        self.saved_game = None
        self.save_notice = ""
        self.save_status = ""
        self.save_elapsed = 0.0
        self.confirm_new = False
        if self.save_store:
            try:
                self.saved_game = self.save_store.load()
            except (OSError, ValueError, TypeError, KeyError):
                self.save_notice = "Nao foi possivel ler o progresso salvo. O arquivo foi preservado."
        self.investigation = InvestigationState()
        self.player_name = ""
        self.run_id = str(uuid4())
        self.ranking_eligible = True
        self.result_saved = False
        self.player_screens = PlayerScreens(self, ranking_store)
        self.instructions = Instructions(self)
        self.player_poses = {
            pose: load_portrait(self.assets_dir / "personagens", "cassie", (92, 142), pose)
            for pose in ("idle", "walk", "action")
        }
        self.player = Player((485, 535), self.player_poses)
        self.room_image = pygame.transform.smoothscale(
            pygame.image.load(str(self.assets_dir / "cenarios" / "escritorio.png")).convert(),
            self.screen.get_size(),
        )
        self.backgrounds = {name: pygame.transform.smoothscale(
            pygame.image.load(str(self.assets_dir / "cenarios" / f"{name}.png")).convert(),
            self.screen.get_size(),
        ) for name in ("entrevista", "analise", "arquivo", "masters")}
        self.stage_portraits = {key: load_portrait(self.assets_dir / "personagens", key, (200, 290))
                                for key in CHARACTERS}

        self.running = True
        self.campaign_data = new_campaign()
        self.campaign = ExpandedCampaign(self)
        self.office_escape = OfficeEscape(self, save_path.with_name("escritorio_escape.json") if save_path else None)
        self.state = "menu"
        self.paused = False
        self.show_clues = False
        self.clue_page = 0
        self.message = ""
        self.message_timer = 0.0

        self.dialogue_index = 0
        self.prologue_outro_index = -1
        self.epilogue_index = 0
        self.puzzle_input = ""
        self.profile_selection: list[int] = []
        self.puzzle_step = 0
        self.final_feedback = ""
        self.interrogation_feedback = ""
        self.phase5_hint_used = False
        self.interrogation_round = 0
        self.interrogation_insight = ""
        self.profile_step = "evidence"
        self.evidence_selection: list[str] = []
        self.profile_order = [2, 0, 3, 1]
        self.final_mode = "explore"
        self.final_round = 0
        self.final_round_feedback = ""
        self.proof_choice = -1
        self.proof_selection = []
        self.proof_page = 0
        self.final_interactables = [
            {"id": "lorelai_note", "label": "Retrato", "rect": pygame.Rect(515, 337, 80, 30), "marker": (557, 150)},
            {"id": "locked_exit", "label": "Porta", "rect": pygame.Rect(995, 352, 60, 30), "marker": (1025, 271)},
            {"id": "hall_pattern", "label": "Mosaico", "rect": pygame.Rect(520, 520, 80, 40), "marker": (560, 538)},
        ]

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
        before = (deepcopy(self.office_escape.data) if self.state == "escape_room" else snapshot(self)) if self.save_store and self.state != "menu" else None
        self.dispatch_events(events)
        after = self.office_escape.data if self.state == "escape_room" else snapshot(self)
        if self.running and self.save_store and self.state != "menu" and after != before:
            self.save_progress()

    def dispatch_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if self.instructions.active:
                self.instructions.handle_event(event)
                continue
            if self.instructions.available() and ((event.type == pygame.KEYDOWN and event.key == pygame.K_F1) or self.instructions.button().hit(event)):
                self.instructions.open()
                continue
            if self.player_screens.active:
                self.player_screens.handle_event(event)
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.show_clues:
                    self.show_clues = False
                    continue
                if event.key == pygame.K_ESCAPE and self.state not in {"menu", "epilogue"}:
                    self.paused = not self.paused
                    self.show_clues = False
                    continue
                if event.key == pygame.K_TAB and self.state not in {"menu", "escape_room"} and not self.paused:
                    self.show_clues = not self.show_clues
                    continue

            if self.show_clues or self.paused:
                self.handle_overlay_events(event)
                continue

            if self.state == "menu":
                self.handle_menu_event(event)
            elif self.state == "campaign":
                self.campaign.handle_event(event)
            elif self.state == "escape_room":
                self.office_escape.handle_event(event)
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
        if self.show_clues:
            last_page = max(0, (len(self.investigation.evidence) - 1) // CLUES_PER_PAGE)
            if event.type == pygame.MOUSEWHEEL:
                self.clue_page = max(0, min(last_page, self.clue_page - event.y))
            for button in self.clue_buttons():
                if button.hit(event):
                    if button.value == "close":
                        self.show_clues = False
                    else:
                        self.clue_page = max(0, min(last_page, self.clue_page + button.value))
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        if self.paused:
            for button in self.pause_buttons():
                if button.hit(event):
                    if button.value == "resume":
                        self.paused = False
                    elif button.value == "menu":
                        self.reset_to_menu()
                    elif button.value == "save":
                        self.save_progress()
                    elif button.value == "quit_without_save":
                        self.running = False
                    return

    def handle_menu_event(self, event: pygame.event.Event) -> None:
        if self.confirm_new:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.confirm_new = False
            for button in self.new_game_buttons():
                if button.hit(event):
                    self.confirm_new = False
                    if button.value == "new":
                        self.player_screens.new_game()
            return
        if event.type == pygame.KEYDOWN and event.key in {pygame.K_RETURN, pygame.K_SPACE}:
            if self.saved_game:
                self.continue_game()
            else:
                self.player_screens.new_game()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.menu_buttons():
                if button.hit(event):
                    if button.value == "continue":
                        self.continue_game()
                    elif button.value == "escape":
                        self.office_escape.start()
                    elif button.value == "ranking":
                        self.player_screens.show_ranking()
                    elif self.saved_game:
                        self.confirm_new = True
                    else:
                        self.player_screens.new_game()
                    return

    def handle_prologue_event(self, event: pygame.event.Event) -> None:
        if self.prologue_outro_index >= 0:
            if (event.type == pygame.KEYDOWN and event.key in {pygame.K_SPACE, pygame.K_RETURN}) or self.dialogue_continue_button().hit(event):
                self.prologue_outro_index += 1
                if self.prologue_outro_index == len(PROLOGUE_OUTRO):
                    self.state = "phase1"
            return
        if self.dialogue_index < len(PROLOGUE_LINES):
            if (event.type == pygame.KEYDOWN and event.key in {pygame.K_SPACE, pygame.K_RETURN}) or self.dialogue_continue_button().hit(event):
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
                    self.prologue_outro_index = 0

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
        if self.interrogation_feedback:
            if self.interrogation_continue_button().hit(event):
                self.interrogation_round += 1
                self.interrogation_feedback = ""
                self.interrogation_insight = ""
                if self.interrogation_round == len(INTERROGATION_ROUNDS):
                    self.state = "puzzle"
                self.set_message("")
            return
        topic = INTERROGATION_ROUNDS[self.interrogation_round]
        if self.proof_choice >= 0:
            self.handle_proof_event(event, topic)
            return
        for button in self.interrogation_ability_buttons():
            if button.hit(event):
                self.interrogation_insight = topic[button.value]
                self.investigation.use_ability(f"{button.value}_{self.interrogation_round}")
                if button.value == "michael" and self.interrogation_round == 2:
                    self.investigation.register_emotion_read()
                return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.interrogation_buttons():
                if button.hit(event):
                    self.proof_choice = topic["choices"].index(button.value)
                    return

    def handle_puzzle_event(self, event: pygame.event.Event) -> None:
        if self.puzzle_hint_button().hit(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            self.investigation.use_ability(f"sloane_{self.puzzle_step}")
            self.set_message(PUZZLE_ROUNDS[self.puzzle_step]["hint"], 8)
            return
        if event.type == pygame.KEYDOWN:
            character = getattr(event, "unicode", "")
            if event.key == pygame.K_BACKSPACE:
                self.puzzle_input = self.puzzle_input[:-1]
            elif character in "0123456789" and len(character) == 1 and len(self.puzzle_input) < 6:
                self.puzzle_input += character
        submit = (event.type == pygame.KEYDOWN and event.key in {pygame.K_RETURN, pygame.K_KP_ENTER}) or self.puzzle_buttons()[0].hit(event)
        if not submit or not self.puzzle_input:
            return
        correct = int(self.puzzle_input) == PUZZLE_ROUNDS[self.puzzle_step]["answer"]
        self.investigation.register_puzzle(correct)
        self.puzzle_input = ""
        if correct:
            self.puzzle_step += 1
            self.set_message("A regra confere. Ainda ha outra camada no convite.")
            if self.puzzle_step == len(PUZZLE_ROUNDS):
                self.investigation.add_evidence("fibonacci_key")
                self.investigation.mark_used("coded_invitation")
                self.state = "profile"
                self.set_message("A chave 29 abre o envelope interno. A mensagem pede que Cassie venha sozinha.", 8)
        else:
            self.set_message("A resposta nao encaixa. Revise a sequencia ou consulte Sloane.")

    def handle_profile_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.profile_buttons():
                if button.hit(event):
                    if button.value == "check":
                        correct = (set(self.evidence_selection) == PROFILE_PAIR if self.profile_step == "evidence"
                                   else self.profile_selection == PROFILE_CORRECT_ORDER)
                        self.investigation.register_connection(correct)
                        if correct:
                            if self.profile_step == "evidence":
                                for evidence_id in self.evidence_selection:
                                    self.investigation.mark_used(evidence_id)
                                self.profile_step = "timeline"
                                self.set_message("Dean: o codigo confirma que o convite foi planejado. Agora precisamos ordenar os fatos.", 8)
                            else:
                                self.investigation.add_evidence("profile_sequence")
                                self.state = "finale"
                                self.player = Player((475, 575), self.player_poses)
                                self.set_message("A pista era uma armadilha. Separada da equipe, Cassie precisa investigar o salao sozinha.", 8)
                        else:
                            self.profile_selection.clear()
                            self.evidence_selection.clear()
                            self.set_message("A hipotese deixa uma lacuna. Revise as evidencias e tente novamente.")
                    elif button.value == "clear":
                        self.profile_selection.clear()
                        self.evidence_selection.clear()
                    elif self.profile_step == "evidence":
                        if button.value in self.evidence_selection:
                            self.evidence_selection.remove(button.value)
                        elif len(self.evidence_selection) < 2:
                            self.evidence_selection.append(button.value)
                    elif button.value not in self.profile_selection:
                        self.profile_selection.append(button.value)
                    return

    def handle_finale_event(self, event: pygame.event.Event) -> None:
        if self.final_mode == "explore":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.try_interact()
                elif event.key == pygame.K_q:
                    self.set_message("Cassie: o retrato, a porta e o mosaico contam versoes diferentes deste lugar.", 8)
                    self.player.investigate()
                elif event.key == pygame.K_RETURN and FINAL_REQUIRED.issubset(self.investigation.evidence):
                    self.final_mode = "deduce"
                    self.set_message("")
            return
        if self.final_round_feedback:
            if self.final_continue_button().hit(event):
                self.final_round += 1
                self.final_round_feedback = ""
                self.set_message("")
                if self.final_round == len(FINAL_ROUNDS):
                    self.state = "epilogue"
                    self.final_feedback = FINAL_ROUNDS[-1]["feedback"]
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            if not self.phase5_hint_used and self.investigation.use_ability("cassie_finale"):
                self.phase5_hint_used = True
                self.set_message(FINAL_ROUNDS[self.final_round]["hint"], 10)
            else:
                self.set_message("Agora Cassie precisa concluir sem novas ajudas.")

        if self.proof_choice >= 0:
            self.handle_proof_event(event, FINAL_ROUNDS[self.final_round])
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.final_buttons():
                if button.hit(event):
                    self.proof_choice = FINAL_ROUNDS[self.final_round]["choices"].index(button.value)
                    return

    def handle_proof_event(self, event, topic) -> None:
        for button in self.proof_buttons(topic):
            if not button.hit(event):
                continue
            value = button.value
            if value == "back":
                self.proof_choice = -1
                self.proof_selection.clear()
                self.proof_page = 0
            elif value in ("previous", "next"):
                self.proof_page += -1 if value == "previous" else 1
            elif value == "submit":
                hypothesis = topic["choices"][self.proof_choice][1]
                supported = set(self.proof_selection) == set(topic["uses"])
                correct = hypothesis and supported
                if self.state == "interrogation":
                    self.investigation.register_lie(correct, topic["evidence"])
                else:
                    self.investigation.register_connection(correct)
                    if correct and self.final_round == len(FINAL_ROUNDS) - 1:
                        self.investigation.add_evidence("final_deduction")
                if correct:
                    for evidence_id in self.proof_selection:
                        self.investigation.mark_used(evidence_id)
                prefix = ("Argumento sustentado pelas provas. " if correct else
                          "Hipotese correta, mas as provas apresentadas nao a sustentam. " if hypothesis else
                          "A hipotese nao resiste ao confronto com os registros. ")
                if self.state == "finale" and not correct:
                    self.proof_choice = -1
                    self.proof_selection.clear()
                    self.proof_page = 0
                    self.set_message("O argumento tem uma lacuna. Reavalie a hipotese e a relevancia de cada prova antes de concluir.", 10)
                    return
                feedback = prefix + topic["feedback"]
                if self.state == "interrogation":
                    self.interrogation_feedback = feedback
                else:
                    self.final_round_feedback = feedback
                self.proof_choice = -1
                self.proof_selection.clear()
                self.proof_page = 0
                self.set_message("")
            elif value in self.proof_selection:
                self.proof_selection.remove(value)
            else:
                self.proof_selection.append(value)
            return

    def proof_buttons(self, topic) -> list[Button]:
        evidence = list(self.investigation.evidence)
        buttons = []
        for index, key in enumerate(evidence[self.proof_page * 6:self.proof_page * 6 + 6]):
            selected = key in self.proof_selection
            buttons.append(Button(pygame.Rect(70 + index % 2 * 500, 248 + index // 2 * 60, 480, 50),
                                  EVIDENCES[key].name, key, selected=selected,
                                  enabled=selected or len(self.proof_selection) < 3))
        buttons.extend([
            Button(pygame.Rect(70, 628, 170, 48), "Rever hipotese", "back"),
            Button(pygame.Rect(460, 628, 52, 48), "<", "previous", enabled=self.proof_page > 0),
            Button(pygame.Rect(524, 628, 52, 48), ">", "next", enabled=(self.proof_page + 1) * 6 < len(evidence)),
            Button(pygame.Rect(800, 628, 250, 48), "Apresentar provas", "submit",
                   enabled=bool(self.proof_selection)),
        ])
        return buttons

    def draw_proofs(self, topic) -> None:
        draw_band(self.screen, pygame.Rect(0, 90, 1120, 630))
        draw_text(self.screen, topic["choices"][self.proof_choice][0], self.fonts.h2, TEXT,
                  pygame.Rect(70, 114, 980, 74))
        count = f"PROVAS DO ARGUMENTO: {len(self.proof_selection)} / 3 ESPACOS"
        draw_text(self.screen, count, self.fonts.small, ACCENT_2, pygame.Rect(70, 207, 750, 30))
        draw_text(self.screen, f"Pagina {self.proof_page + 1}", self.fonts.small, MUTED, pygame.Rect(900, 207, 150, 30))
        for index, key in enumerate(self.proof_selection):
            detail = f"{EVIDENCES[key].name}: {EVIDENCES[key].description}"
            draw_text(self.screen, detail, self.fonts.small, TEXT,
                      pygame.Rect(70, 440 + index * 58, 980, 54))
        for button in self.proof_buttons(topic):
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def handle_epilogue_event(self, event: pygame.event.Event) -> None:
        if self.epilogue_index < len(EPILOGUE_LINES):
            if (event.type == pygame.KEYDOWN and event.key in {pygame.K_RETURN, pygame.K_SPACE}) or self.dialogue_continue_button().hit(event):
                self.epilogue_index += 1
            return
        if event.type == pygame.KEYDOWN and event.key in {pygame.K_RETURN, pygame.K_SPACE}:
            self.reset_to_menu()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.epilogue_buttons():
                if button.hit(event):
                    self.reset_to_menu()

    def update(self, dt: float) -> None:
        self.save_elapsed += dt
        if self.save_elapsed >= 5 and self.state != "menu":
            self.save_progress()
            self.save_elapsed = 0.0
        if self.paused or self.show_clues or self.player_screens.active or self.instructions.active:
            return
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

        if self.state == "phase1" or (self.state == "finale" and self.final_mode == "explore"):
            obstacles = self.obstacles if self.state == "phase1" else ()
            self.player.update(dt, pygame.key.get_pressed(), self.room_bounds, obstacles)
        elif self.state == "campaign":
            self.campaign.update(dt)

    def draw(self) -> None:
        if self.instructions.active:
            self.instructions.draw()
            return
        if self.player_screens.active:
            self.player_screens.draw()
            return
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "campaign":
            self.campaign.draw()
        elif self.state == "escape_room":
            self.office_escape.draw()
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
            used = {key for key, was_used in self.investigation.evidence.items() if was_used}
            draw_clue_panel(self.screen, self.fonts, self.investigation.discovered(), self.investigation.score, self.clue_page, used)
            for button in self.clue_buttons():
                button.draw(self.screen, self.fonts, pygame.mouse.get_pos())
        if self.paused:
            self.draw_pause()
        if self.save_notice:
            draw_band(self.screen, pygame.Rect(0, 76, 1120, 40))
            draw_text(self.screen, self.save_notice, self.fonts.small, TEXT, pygame.Rect(28, 84, 1064, 28))
        if self.instructions.available():
            self.instructions.button().draw(self.screen, self.fonts, pygame.mouse.get_pos())

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
        if self.saved_game:
            saved = self.saved_game
            label = f"{STAGES[saved['progress']['state']]}  /  {saved['investigation']['score']} pontos"
            if saved["progress"]["state"] == "campaign":
                chapter = saved["progress"]["campaign_data"]["chapter"]
                stage = "Prologo" if chapter == 0 else "Epilogo" if chapter == 7 else f"Fase {chapter} de 6"
                label = f"Roteiro expandido / {stage} / {saved['investigation']['score']} pontos"
            else:
                label = "Roteiro anterior / " + label
            draw_text(self.screen, label, self.fonts.small, TEXT, pygame.Rect(180, 644, 760, 30), align="center")
        if self.confirm_new:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            self.screen.blit(overlay, (0, 0))
            draw_panel(self.screen, pygame.Rect(280, 225, 560, 270))
            draw_text(self.screen, "Nova investigacao?", self.fonts.h1, TEXT, pygame.Rect(310, 255, 500, 44))
            draw_text(self.screen, "O progresso salvo desta partida sera substituido.", self.fonts.body, MUTED,
                      pygame.Rect(310, 315, 500, 70))
            for button in self.new_game_buttons():
                button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_prologue(self) -> None:
        if self.prologue_outro_index >= 0:
            speaker, text = PROLOGUE_OUTRO[self.prologue_outro_index]
            self.draw_story_scene("arquivo", "PROLOGO / O CHAMADO", "O desaparecimento de Celine", speaker, text)
            return
        self.draw_stage("entrevista", "PROLOGO / DANIEL REDDING", "Uma conversa sob suspeita")
        self.draw_stage_character("daniel", 255, 414)
        self.draw_stage_character("cassie", 865, 414)

        if self.dialogue_index < len(PROLOGUE_LINES):
            speaker, text = PROLOGUE_LINES[self.dialogue_index]
            draw_dialogue_box(self.screen, self.fonts, speaker, text)
            self.dialogue_continue_button().draw(self.screen, self.fonts, pygame.mouse.get_pos())
        else:
            draw_dialogue_box(
                self.screen,
                self.fonts,
                "Cassie",
                "Redding deixou uma abertura. Como voce conduz a conversa?",
                "",
            )
            for button in self.prologue_choice_buttons():
                button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_phase1(self) -> None:
        final_area = self.state == "finale"
        self.draw_room()
        self.player.draw(self.screen)
        bar = pygame.Surface((1120, 72), pygame.SRCALPHA)
        bar.fill((18, 24, 25, 235))
        self.screen.blit(bar, (0, 0))
        chapter = "FASE 05 / SEM O APOIO DA EQUIPE" if final_area else "CASO 01 / O DESAPARECIMENTO"
        title = "O salao dos Masters" if final_area else "O escritorio de Celine"
        self.screen.blit(self.fonts.small.render(chapter, True, ACCENT_2), (28, 12))
        self.screen.blit(self.fonts.h2.render(title, True, TEXT), (28, 33))
        required = FINAL_REQUIRED if final_area else ("celine_bracelet", "broken_phone", "coded_invitation")
        count = sum(self.investigation.has(key) for key in required)
        status = self.fonts.body.render(f"Evidencias {count}/3     Pontos {self.investigation.score}", True, TEXT)
        self.screen.blit(status, status.get_rect(midright=(1090, 36)))
        self.screen.blit(bar, (0, 664))
        nearest = self.nearest_interactable()
        if nearest:
            prompt = self.fonts.body.render(f"Investigar: {nearest['label']}", True, TEXT)
            self.screen.blit(prompt, (28, 682))
        else:
            objective = "Investigue o retrato, a porta e o mosaico." if final_area else "Encontre os rastros deixados por Celine."
            self.screen.blit(self.fonts.body.render(objective, True, MUTED), (28, 682))
        if count == 3:
            label = "ENTER - Construir a deducao" if final_area else "ENTER - Seguir para o interrogatorio"
            ready = self.fonts.body.render(label, True, GOOD)
            self.screen.blit(ready, ready.get_rect(midright=(1090, 694)))
        draw_message(self.screen, self.fonts, self.message)

    def draw_room(self) -> None:
        final_area = self.state == "finale"
        self.screen.blit(self.backgrounds["masters"] if final_area else self.room_image, (0, 0))
        nearest = self.nearest_interactable()
        for item in self.active_interactables():
            if final_area and item is not nearest:
                continue
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
        topic = INTERROGATION_ROUNDS[self.interrogation_round]
        self.draw_stage("entrevista", f"FASE 02 / DEPOIMENTO {self.interrogation_round + 1} DE 3", topic["title"])
        if self.proof_choice >= 0:
            self.draw_proofs(topic)
            return
        self.draw_stage_character("lia", 150, 414)
        self.draw_stage_character("michael", 970, 414)
        rect = pygame.Rect(300, 120, 520, 296)
        draw_panel(self.screen, rect)
        self.screen.blit(self.fonts.small.render("REGISTRO DA ENTREVISTA", True, ACCENT_2), (324, 140))
        draw_text(self.screen, topic["statement"], self.fonts.body, TEXT, pygame.Rect(324, 176, 472, 90))
        draw_text(self.screen, self.interrogation_insight or "Lia e Michael aguardam a proxima pergunta.",
                  self.fonts.small, MUTED, pygame.Rect(324, 272, 472, 72))
        for button in self.interrogation_ability_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())
        draw_band(self.screen, pygame.Rect(0, 458, 1120, 262))
        if self.interrogation_feedback:
            self.screen.blit(self.fonts.h2.render("Conclusao registrada", True, ACCENT_2), (100, 482))
            draw_text(self.screen, self.interrogation_feedback, self.fonts.body, TEXT, pygame.Rect(100, 516, 920, 92))
            buttons = [self.interrogation_continue_button()]
        else:
            buttons = self.interrogation_buttons()
        for button in buttons:
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_puzzle(self) -> None:
        puzzle = PUZZLE_ROUNDS[self.puzzle_step]
        self.draw_stage("analise", "FASE 03 / O PADRAO DOS MASTERS", "O convite cifrado")
        self.draw_stage_character("sloane", 170, 445)
        rect = pygame.Rect(340, 142, 724, 294)
        draw_panel(self.screen, rect)
        self.screen.blit(self.fonts.small.render(f"ANALISE {self.puzzle_step + 1} / {len(PUZZLE_ROUNDS)}", True, ACCENT_2), (368, 164))
        heading = puzzle["title"]
        self.screen.blit(self.fonts.h1.render(heading, True, TEXT), (368, 195))
        values = puzzle["values"]
        for index, value in enumerate(values):
            tile = pygame.Rect(368 + index * 111, 254, 96, 74)
            pygame.draw.rect(self.screen, (36, 54, 52), tile, border_radius=4)
            pygame.draw.line(self.screen, ACCENT_2, tile.bottomleft, tile.bottomright, 2)
            number = self.fonts.h1.render(value, True, TEXT)
            self.screen.blit(number, number.get_rect(center=tile.center))
        draw_text(self.screen, puzzle["prompt"], self.fonts.body, MUTED, pygame.Rect(368, 355, 650, 64))
        draw_band(self.screen, pygame.Rect(0, 480, 1120, 240))
        self.screen.blit(self.fonts.h2.render("Sloane", True, ACCENT_2), (40, 506))
        self.puzzle_hint_button().draw(self.screen, self.fonts, pygame.mouse.get_pos())
        pygame.draw.rect(self.screen, (36, 54, 52), pygame.Rect(610, 528, 210, 62), border_radius=4)
        draw_text(self.screen, self.puzzle_input or "_", self.fonts.h1, TEXT, pygame.Rect(630, 540, 170, 44))
        for button in self.puzzle_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())
        self.draw_status()

    def draw_profile(self) -> None:
        self.draw_stage("arquivo", "FASE 04 / CACADORES E CACADOS", "A linha do tempo")
        self.draw_stage_character("cassie", 135, 460)
        self.draw_stage_character("dean", 985, 460)
        board = pygame.Rect(276, 110, 568, 488)
        draw_panel(self.screen, board)
        heading = "Cruzar evidencias" if self.profile_step == "evidence" else "Reconstrucao"
        title = self.fonts.h1.render(heading, True, TEXT)
        self.screen.blit(title, (board.x + 26, board.y + 24))
        if self.profile_step == "evidence":
            draw_text(self.screen, "Quais duas pistas mostram que o convite tem um codigo planejado?", self.fonts.body,
                      TEXT, pygame.Rect(302, 182, 512, 68))
        for index in range(4 if self.profile_step == "timeline" else 0):
            slot = pygame.Rect(302 + index * 131, 193, 116, 46)
            pygame.draw.rect(self.screen, (35, 53, 50), slot, border_radius=4)
            label = str(self.profile_order.index(self.profile_selection[index]) + 1) if index < len(self.profile_selection) else "-"
            number = self.fonts.h2.render(label, True, TEXT)
            self.screen.blit(number, number.get_rect(center=slot.center))
        for button in self.profile_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())
        self.draw_status("Dean: o que aconteceu primeiro muda toda a leitura do caso.")

    def draw_finale(self) -> None:
        if self.final_mode == "explore":
            self.draw_phase1()
            return
        conclusion = FINAL_ROUNDS[self.final_round]
        self.draw_stage("masters", "FASE 05 / CASSIE E OS MASTERS", "O outro lado da armadilha")
        if self.proof_choice >= 0:
            self.draw_proofs(conclusion)
            return
        self.draw_stage_character("cassie", 150, 414)
        self.draw_stage_character("lorelai", 970, 414, "Lorelai / lembranca")
        rect = pygame.Rect(300, 146, 520, 242)
        draw_panel(self.screen, rect)
        title = self.fonts.h1.render(conclusion["title"], True, TEXT)
        self.screen.blit(title, (rect.x + 24, rect.y + 22))
        draw_text(
            self.screen,
            self.message or conclusion["prompt"],
            self.fonts.body,
            TEXT,
            pygame.Rect(rect.x + 24, rect.y + 72, rect.width - 48, 140),
        )
        draw_band(self.screen, pygame.Rect(0, 458, 1120, 262))
        if self.final_round_feedback:
            draw_text(self.screen, self.final_round_feedback, self.fonts.body, TEXT, pygame.Rect(100, 490, 920, 116))
            buttons = [self.final_continue_button()]
        else:
            buttons = self.final_buttons()
        for button in buttons:
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_epilogue(self) -> None:
        if self.epilogue_index < len(EPILOGUE_LINES):
            speaker, text = EPILOGUE_LINES[self.epilogue_index]
            if self.epilogue_index == len(EPILOGUE_LINES) - 1:
                text += (" Ha lacunas que precisamos reconhecer antes de seguir." if self.investigation.mistakes
                         else "Os registros sustentam cada passo desta conclusao.")
            self.draw_story_scene("masters" if self.epilogue_index < 2 else "arquivo",
                                  "EPILOGO / O QUE FICA", "Depois da armadilha", speaker, text)
            return
        self.draw_stage("arquivo", "EPILOGO / BALANCO DO CASO", "Relatorio da investigacao")
        self.draw_stage_character("cassie", 150, 475)
        rect = pygame.Rect(310, 132, 748, 458)
        draw_panel(self.screen, rect)
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
            draw_text(self.screen, self.final_feedback, self.fonts.body, MUTED, pygame.Rect(rect.x + 34, rect.bottom - 102, rect.width - 68, 78))

        for button in self.epilogue_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_stage(self, background: str, chapter: str, title: str) -> None:
        self.screen.blit(self.backgrounds[background], (0, 0))
        draw_scene_header(self.screen, self.fonts, chapter, title, self.investigation.score)

    def draw_story_scene(self, background, chapter, title, speaker, text) -> None:
        self.draw_stage(background, chapter, title)
        key = {"Cassie": "cassie", "Dean": "dean", "Lia": "lia", "Sloane": "sloane"}[speaker]
        self.draw_stage_character(key, 560, 414)
        draw_dialogue_box(self.screen, self.fonts, speaker, text)
        self.dialogue_continue_button().draw(self.screen, self.fonts, pygame.mouse.get_pos())

    def draw_stage_character(self, key: str, center_x: int, feet_y: int, caption: str | None = None) -> None:
        image = self.stage_portraits[key]
        shadow = pygame.Surface((120, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (12, 19, 19, 90), shadow.get_rect())
        self.screen.blit(shadow, shadow.get_rect(center=(center_x, feet_y - 3)))
        self.screen.blit(image, image.get_rect(midbottom=(center_x, feet_y)))
        name = self.fonts.small.render(caption or CHARACTERS[key]["name"], True, TEXT)
        label_rect = name.get_rect(midtop=(center_x, feet_y + 9)).inflate(24, 12)
        pygame.draw.rect(self.screen, PANEL, label_rect, border_radius=4)
        self.screen.blit(name, name.get_rect(center=label_rect.center))

    def draw_status(self, default: str = "") -> None:
        if self.message or default:
            draw_band(self.screen, pygame.Rect(0, 620, 1120, 100))
            draw_text(self.screen, self.message or default, self.fonts.body, TEXT, pygame.Rect(40, 638, 1040, 66))

    def draw_pause(self) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        rect = pygame.Rect(390, 180, 340, 380)
        draw_panel(self.screen, rect, PANEL)
        title = self.fonts.h1.render("Pausa", True, TEXT)
        self.screen.blit(title, title.get_rect(center=(rect.centerx, rect.y + 46)))
        for button in self.pause_buttons():
            button.draw(self.screen, self.fonts, pygame.mouse.get_pos())
        if self.save_status and not self.save_notice:
            draw_text(self.screen, self.save_status, self.fonts.small, GOOD, pygame.Rect(420, 492, 280, 34), align="center")

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
        for item in self.active_interactables():
            if self.player.rect.colliderect(item["rect"].inflate(44, 44)):
                return item
        return None

    def active_interactables(self) -> list[dict]:
        return self.final_interactables if self.state == "finale" else self.interactables

    def set_message(self, message: str, seconds: float = 4.5) -> None:
        self.message = message
        self.message_timer = seconds

    def start_game(self, expanded: bool = True, player_name: str = "") -> None:
        self.instructions.active = False
        self.player_screens.active = ""
        self.player_name = player_name
        self.run_id = str(uuid4())
        self.ranking_eligible = expanded
        self.result_saved = False
        self.player_screens.result_notice = ""
        self.campaign_data = new_campaign()
        self.prologue_outro_index = -1
        self.epilogue_index = 0
        self.puzzle_input = ""
        self.proof_choice = -1
        self.proof_selection = []
        self.proof_page = 0
        self.investigation = InvestigationState()
        self.player = Player((485, 535), self.player_poses)
        self.state = "campaign" if expanded else "prologue"
        self.dialogue_index = 0
        self.puzzle_step = 0
        self.profile_selection = []
        self.final_feedback = ""
        self.interrogation_feedback = ""
        self.phase5_hint_used = False
        self.interrogation_round = 0
        self.interrogation_insight = ""
        self.profile_step = "evidence"
        self.evidence_selection = []
        self.final_mode = "explore"
        self.final_round = 0
        self.final_round_feedback = ""
        self.show_clues = False
        self.clue_page = 0
        self.paused = False
        self.set_message("")

    def reset_to_menu(self) -> None:
        if self.save_store and self.state != "menu" and not self.save_progress():
            return
        self.state = "menu"
        self.player_screens.active = ""
        self.paused = False
        self.show_clues = False
        self.set_message("")

    def menu_buttons(self) -> list[Button]:
        if self.saved_game:
            return [Button(pygame.Rect(370, 436, 380, 50), "Continuar investigacao", "continue", selected=True),
                    Button(pygame.Rect(370, 505, 380, 50), "Nova investigacao", "new"),
                    Button(pygame.Rect(370, 573, 185, 50), "Ranking", "ranking"),
                    Button(pygame.Rect(565, 573, 185, 50), "Teste escritorio", "escape")]
        return [Button(pygame.Rect(370, 470, 380, 54), "Iniciar investigacao", "start", selected=True),
                Button(pygame.Rect(370, 548, 185, 54), "Ranking", "ranking"),
                Button(pygame.Rect(565, 548, 185, 54), "Teste escritorio", "escape")]

    def new_game_buttons(self) -> list[Button]:
        return [Button(pygame.Rect(310, 412, 220, 52), "Cancelar", "cancel"),
                Button(pygame.Rect(558, 412, 250, 52), "Iniciar nova", "new")]

    def save_progress(self) -> bool:
        if self.state == "escape_room":
            return self.office_escape.save()
        if not self.save_store or self.state == "menu":
            return False
        data = snapshot(self)
        if data == self.saved_game and self.save_store.path.exists():
            self.save_status = "Progresso salvo."
            self.save_notice = ""
            return True
        try:
            self.save_store.write(data)
        except (OSError, ValueError, TypeError):
            self.save_notice = "Nao foi possivel salvar. Sua partida continua aberta; tente novamente antes de fechar."
            return False
        self.saved_game = data
        self.save_notice = ""
        self.save_status = "Progresso salvo."
        return True

    def request_quit(self) -> None:
        if self.save_store and self.state != "menu" and not self.save_progress():
            self.paused = True
            self.show_clues = False
            return
        self.running = False

    def continue_game(self) -> None:
        if self.saved_game is None:
            return
        self.instructions.active = False
        saved = self.saved_game
        for key in PROGRESS_FIELDS:
            value = saved["progress"][key]
            setattr(self, key, deepcopy(value))
        inv = dict(saved["investigation"])
        inv["evidence"] = dict(inv["evidence"])
        inv["used_abilities"] = set(inv["used_abilities"])
        self.investigation = InvestigationState(**inv)
        self.player = Player(tuple(saved["position"]), self.player_poses)
        self.player.facing_left = saved["facing_left"]
        self.paused = False
        self.show_clues = False
        self.clue_page = 0
        self.confirm_new = False
        self.message_timer = 8.0 if self.message else 0.0
        self.save_elapsed = 0.0
        if self.state == "campaign" and not self.player_name and self.player_screens.store:
            self.player_screens.ask_name(resume=True)

    def prologue_choice_buttons(self) -> list[Button]:
        return [
            Button(pygame.Rect(48, 624, 496, 56), PROLOGUE_CHOICES[0][0], PROLOGUE_CHOICES[0]),
            Button(pygame.Rect(576, 624, 496, 56), PROLOGUE_CHOICES[1][0], PROLOGUE_CHOICES[1]),
        ]

    def dialogue_continue_button(self) -> Button:
        return Button(pygame.Rect(862, 624, 210, 56), "Continuar", "next")

    def interrogation_continue_button(self) -> Button:
        label = "Proximo assunto" if self.interrogation_round < len(INTERROGATION_ROUNDS) - 1 else "Analisar o convite"
        return Button(pygame.Rect(760, 614, 260, 56), label, "next")

    def interrogation_ability_buttons(self) -> list[Button]:
        return [Button(pygame.Rect(324, 358, 220, 40), "Lia: analisar fala", "lia", enabled=not self.interrogation_feedback),
                Button(pygame.Rect(572, 358, 220, 40), "Michael: observar", "michael", enabled=not self.interrogation_feedback)]

    def puzzle_hint_button(self) -> Button:
        return Button(pygame.Rect(40, 548, 340, 42), "Consultar Sloane", "hint")

    def final_continue_button(self) -> Button:
        label = "Proxima deducao" if self.final_round == 0 else "Concluir investigacao"
        return Button(pygame.Rect(760, 614, 260, 56), label, "next")

    def clue_buttons(self) -> list[Button]:
        pages = max(1, (len(self.investigation.evidence) + CLUES_PER_PAGE - 1) // CLUES_PER_PAGE)
        return [
            Button(pygame.Rect(896, 78, 110, 40), "Fechar", "close"),
            Button(pygame.Rect(886, 602, 52, 44), "<", -1, enabled=self.clue_page > 0),
            Button(pygame.Rect(954, 602, 52, 44), ">", 1, enabled=self.clue_page < pages - 1),
        ]

    def interrogation_buttons(self) -> list[Button]:
        buttons = []
        y = 486
        for text, correct in INTERROGATION_ROUNDS[self.interrogation_round]["choices"]:
            buttons.append(Button(pygame.Rect(100, y, 920, 56), text, (text, correct)))
            y += 64
        return buttons

    def puzzle_buttons(self) -> list[Button]:
        return [Button(pygame.Rect(842, 528, 218, 62), "Validar codigo", "submit", enabled=bool(self.puzzle_input))]

    def profile_buttons(self) -> list[Button]:
        buttons = []
        y = 260
        options = PROFILE_EVIDENCES if self.profile_step == "evidence" else self.profile_order
        for row, value in enumerate(options):
            if self.profile_step == "evidence":
                label = EVIDENCES[value].name
                selected = value in self.evidence_selection
                enabled = self.investigation.has(value) and (selected or len(self.evidence_selection) < 2)
            else:
                label = f"{row + 1}. {PROFILE_EVENTS[value]}"
                selected = value in self.profile_selection
                enabled = not selected
            buttons.append(Button(pygame.Rect(300, y, 520, 50), label, value, enabled=enabled, selected=selected))
            y += 58
        buttons.append(Button(pygame.Rect(300, 530, 150, 44), "Limpar", "clear"))
        ready = len(self.evidence_selection) == 2 if self.profile_step == "evidence" else len(self.profile_selection) == 4
        buttons.append(Button(pygame.Rect(670, 530, 150, 44), "Conferir", "check", enabled=ready))
        return buttons

    def final_buttons(self) -> list[Button]:
        buttons = []
        y = 486
        for text, correct in FINAL_ROUNDS[self.final_round]["choices"]:
            buttons.append(Button(pygame.Rect(100, y, 920, 56), text, (text, correct)))
            y += 64
        return buttons

    def epilogue_buttons(self) -> list[Button]:
        return [Button(pygame.Rect(558, 620, 250, 56), "Voltar ao menu", "menu")]

    def pause_buttons(self) -> list[Button]:
        buttons = [
            Button(pygame.Rect(430, 270, 260, 52), "Continuar", "resume"),
            Button(pygame.Rect(430, 340, 260, 52), "Salvar partida", "save", enabled=self.save_store is not None),
            Button(pygame.Rect(430, 410, 260, 52), "Salvar e voltar ao menu", "menu"),
        ]
        if self.save_notice:
            buttons.append(Button(pygame.Rect(430, 480, 260, 52), "Sair sem salvar", "quit_without_save"))
        return buttons
