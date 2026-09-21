"""Player identification and ranking screens in the existing Pygame loop."""
from copy import deepcopy
import pygame

from scripts.interfaces import Button, TEXT, MUTED, GOOD, ACCENT_2, draw_band, draw_text
from scripts.ranking import normalize_name


class PlayerScreens:
    def __init__(self, game, store=None):
        self.g, self.store = game, store
        self.active = ""
        self.name = ""
        self.resume = False
        self.notice = ""
        self.rows = []
        self.page = 0
        self.result_notice = ""

    def ask_name(self, resume=False):
        self.active, self.resume, self.notice = "name", resume, ""
        self.name = self.g.player_name if resume else ""

    def new_game(self):
        saved = self.g.saved_game
        if self.store and saved and saved["progress"]["state"] == "campaign":
            p = saved["progress"]
            if p["campaign_data"]["view"] in {"report", "ended"} and not p["result_saved"]:
                self.g.continue_game()
                if not self.g.player_name:
                    self.ask_name(resume=True)
                    return
                if not self.finish():
                    self.show_ranking()
                    return
        self.ask_name()

    def accept_name(self):
        try:
            name = normalize_name(self.name)
            if self.store:
                name = self.store.player(name).nickname
        except ValueError as error:
            self.notice = str(error)
            return
        except Exception:
            self.notice = "Banco indisponivel. Verifique o Django e tente novamente; a partida salva foi preservada."
            return
        self.active = ""
        if self.resume:
            self.g.player_name = name
        else:
            self.g.start_game(player_name=name)
            self.g.instructions.open(contextual=False)
        if self.g.campaign_data["view"] in {"report", "ended"}:
            self.finish()
        if self.g.save_store:
            self.g.save_progress()

    def finish(self):
        g = self.g
        if not self.store or g.state != "campaign" or g.campaign_data["view"] not in {"report", "ended"}:
            return False
        if not g.player_name:
            self.ask_name(resume=True)
            return False
        if g.result_saved:
            self.result_notice = "Resultado registrado no Django."
            return True
        try:
            self.store.record(g.run_id, g.player_name, max(0, g.investigation.score),
                              g.investigation.mistakes, g.ranking_eligible,
                              completed=g.campaign_data["view"] == "report",
                              phase=min(6, g.campaign_data["chapter"]))
        except Exception:
            self.result_notice = "Resultado pendente. Abra Ranking e tente registrar novamente."
            return False
        g.result_saved = True
        self.result_notice = "Resultado registrado no Django." if g.ranking_eligible else "Historico registrado. Partida antiga fora do ranking competitivo."
        return True

    def show_ranking(self):
        self.active, self.page, self.notice = "ranking", 0, ""
        if self.g.state == "campaign" and self.g.campaign_data["view"] in {"report", "ended"}:
            self.finish()
            if self.active == "name":
                return
        self.refresh()

    def ask_end(self):
        if self.g.state != "campaign" or self.g.campaign_data["view"] in {"report", "ended"}:
            return
        if not self.g.player_name:
            self.ask_name(resume=True)
            return
        self.active, self.notice = "end_confirm", ""

    def confirm_end(self):
        g = self.g
        if self.active != "end_confirm" or g.campaign_data["view"] in {"report", "ended"}:
            return
        before = deepcopy(g.campaign_data)
        g.campaign_data["view"] = "ended"
        # Freeze the result locally before recording it in Django, so a retry
        # cannot resume gameplay and submit a different score for the same run.
        if g.save_store and not g.save_progress():
            g.campaign_data = before
            self.notice = "Nao foi possivel salvar. A partida nao foi encerrada; tente novamente."
            return
        g.paused = False
        self.show_ranking()
        if g.save_store:
            g.save_progress()

    def refresh(self):
        self.rows = []
        if not self.store:
            self.notice = "Ranking indisponivel nesta sessao."
            return
        try:
            self.rows = self.store.standings(self.g.player_name)
            self.notice = ""
        except Exception:
            self.notice = "Nao foi possivel ler o banco. Tente atualizar novamente."

    def buttons(self):
        if self.active == "end_confirm":
            return [Button(pygame.Rect(170, 510, 300, 52), "Cancelar", "back"),
                    Button(pygame.Rect(560, 510, 390, 52), "Encerrar e registrar pontos", "end")]
        if self.active == "name":
            return [Button(pygame.Rect(260, 510, 220, 50), "Cancelar", "back"),
                    Button(pygame.Rect(640, 510, 220, 50), "Confirmar nome", "accept")]
        return [Button(pygame.Rect(60, 638, 175, 48), "Voltar", "back"),
                Button(pygame.Rect(255, 638, 240, 48), "Atualizar e registrar", "refresh"),
                Button(pygame.Rect(900, 638, 65, 48), "<", "previous", self.page > 0),
                Button(pygame.Rect(985, 638, 65, 48), ">", "next", (self.page + 1) * 7 < len(self.rows))]

    def handle_event(self, event):
        action = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                action = "back"
            elif self.active == "name":
                if event.key == pygame.K_RETURN:
                    action = "accept"
                elif event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                else:
                    char = getattr(event, "unicode", "")
                    if char and char.isprintable() and len(self.name) < 24:
                        self.name = (self.name + char)[:24]
        for button in self.buttons():
            if button.hit(event):
                action = button.value
                break
        if action == "back":
            self.active = ""
            if self.g.save_store and self.g.state != "menu":
                self.g.save_progress()
        elif action == "accept":
            self.accept_name()
        elif action == "end":
            self.confirm_end()
        elif action == "refresh":
            self.finish()
            self.refresh()
        elif action == "previous":
            self.page = max(0, self.page - 1)
        elif action == "next":
            self.page += 1

    def draw(self):
        g = self.g
        g.screen.blit(g.backgrounds["arquivo"], (0, 0))
        draw_band(g.screen, pygame.Rect(0, 0, 1120, 720), alpha=243)
        title = "Encerrar esta investigacao?" if self.active == "end_confirm" else "Identificacao do jogador" if self.active == "name" else "Ranking de investigadores"
        draw_text(g.screen, title, g.fonts.h1, TEXT, pygame.Rect(60, 55, 1000, 50))
        if self.active == "end_confirm":
            phase = self.g.campaign_data["chapter"]
            stage = "Prologo" if phase == 0 else "Epilogo" if phase == 7 else f"Fase {phase} de 6"
            draw_text(g.screen, f"{self.g.player_name} | {stage} | {self.g.investigation.score} pontos", g.fonts.h2, GOOD, pygame.Rect(170, 200, 780, 70))
            message = "Sua pontuacao atual sera registrada no ranking. Esta tentativa sera encerrada e nao podera ser continuada. As fases restantes nao serao marcadas como concluidas."
            if not self.g.ranking_eligible:
                message = "Esta partida antiga sera guardada apenas no historico, pois comecou com outras regras. Para disputar o ranking, inicie uma nova investigacao. Esta tentativa nao podera ser continuada."
            draw_text(g.screen, message, g.fonts.body, TEXT, pygame.Rect(170, 295, 780, 125))
            draw_text(g.screen, self.notice, g.fonts.small, TEXT, pygame.Rect(170, 440, 780, 60))
        elif self.active == "name":
            draw_text(g.screen, "Nome ou apelido", g.fonts.h2, TEXT, pygame.Rect(260, 220, 600, 40))
            field = pygame.Rect(260, 280, 600, 65)
            pygame.draw.rect(g.screen, (33, 50, 49), field, border_radius=4)
            pygame.draw.rect(g.screen, ACCENT_2, field, 2, border_radius=4)
            draw_text(g.screen, self.name + "|", g.fonts.h2, TEXT, field.inflate(-24, -16))
            draw_text(g.screen, "Mesmo apelido, mesmo jogador. Sem senha; use um apelido unico.", g.fonts.small, MUTED, pygame.Rect(260, 370, 600, 60))
            draw_text(g.screen, self.notice, g.fonts.small, TEXT, pygame.Rect(260, 435, 600, 65))
        else:
            draw_text(g.screen, "Melhor partida por jogador | Desempate: menos erros, depois registro mais antigo", g.fonts.small, MUTED, pygame.Rect(60, 115, 1000, 30))
            for x, label in ((60, "POSICAO"), (180, "JOGADOR"), (710, "PONTOS"), (820, "ERROS"), (930, "SITUACAO")):
                draw_text(g.screen, label, g.fonts.small, ACCENT_2, pygame.Rect(x, 177, 190, 26))
            for i, row in enumerate(self.rows[self.page * 7:self.page * 7 + 7]):
                y = 215 + i * 44
                color = GOOD if row["current"] else TEXT
                for x, width, value in ((60, 90, row["position"]), (180, 490, row["name"]), (710, 105, row["score"]), (820, 100, row["mistakes"])):
                    draw_text(g.screen, str(value), g.fonts.body, color, pygame.Rect(x, y, width, 35))
                status = "Concluida" if row.get("completed", True) else f"Encerrada F{row['phase']}" if row["phase"] else "No prologo"
                draw_text(g.screen, status, g.fonts.small, color, pygame.Rect(930, y + 3, 165, 32))
            if not self.rows and not self.notice:
                draw_text(g.screen, "Nenhuma partida registrada no ranking.", g.fonts.body, TEXT, pygame.Rect(60, 230, 1000, 45))
            current = next((r for r in self.rows if r["current"]), None)
            status = f"{current['name']}: posicao {current['position']} | Recorde: {current['score']} pontos" if current else ""
            draw_text(g.screen, status, g.fonts.body, GOOD, pygame.Rect(60, 535, 1000, 35))
            draw_text(g.screen, self.notice or self.result_notice, g.fonts.small, TEXT, pygame.Rect(60, 580, 1000, 45))
        for button in self.buttons():
            button.draw(g.screen, g.fonts, pygame.mouse.get_pos())
