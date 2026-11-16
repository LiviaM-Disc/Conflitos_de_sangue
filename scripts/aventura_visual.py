"""Eight-stage point-and-click campaign using only Pygame and standard Python."""
import math
import random

import pygame

from scripts.interfaces import Button, TEXT, MUTED, GOOD, ACCENT, draw_band, draw_text
from scripts.campanha_visual import CampaignVisual
from scripts.pistas import Evidence
from scripts.equipe_visual import TeamInvestigation, TEAM_TASKS


EDITION = "visual8"
STAGES = [
    ("O escritorio", "Celine sumiu. Procure os registros de sua saida.", "escritorio", 1, "Na gaveta: agenda, celular e um envelope anonimo para Cassie.", "x_envelope"),
    ("Sem sinal", "O envelope nao tem remetente. Recupere o video do escritorio.", "analise", 2, "Video: Celine sai as 20:30; o envelope chega as 21:09. A foto dentro dele indica um destino.", "x_window"),
    ("A fotografia", "O envelope trouxe uma foto rasgada. Reconstrua o destino.", "arquivo", 2, "A foto leva a equipe a Mercer House. A zeladora da casa recebe os Naturais.", "x_address"),
    ("O eco da casa", "A zeladora entregou um gravador. Abra a trava de sinais.", "masters", 3, "O audio cita Lorelai. A zeladora entrega a foto de manutencao do relogio: 03:21.", "x_target"),
    ("Fora de alcance", "A foto indica o relogio que esconde o acesso ao porao.", "masters", 3, "O relogio esconde duas sequencias. O codigo 12-16 abre a porta do porao.", "x_below"),
    ("Dois bloqueios", "O codigo abriu o porao. Destrave o arquivo protegido.", "masters", 4, "Os perfis mostram que a equipe foi estudada. O indice organiza a copia em tres lotes.", "x_team"),
    ("Sob observacao", "Copie os tres lotes enquanto a conexao estiver estavel.", "analise", 4, "Os tres lotes foram copiados. Cassie e o alvo; o rosto do mensageiro segue oculto.", "x_recording"),
    ("Antes que apaguem", "A copia esta pronta. Revise o relatorio e envie as provas.", "analise", 5, "O relatorio foi revisado e transmitido. Celine segue desaparecida; a autoria e incerta.", "x_final"),
]
LOCATIONS = ("Escritorio de Celine", "Portaria / central de cameras", "Arquivo do predio",
             "Mercer House / entrada", "Mercer House / sala do relogio",
             "Mercer House / porao", "Mercer House / servidor", "Mercer House / terminal de envio")
TRANSFERS = {7: ("Lote A / 8 registros", "Lote B / 16 registros", "Lote C / 32 registros"),
             8: ("Cronologia conferida", "Relato da zeladora", "Perfis dos Naturais", "Conclusoes revisadas")}
ITEM_NAMES = {"key417": "Chave", "fuse": "Fusivel", "magnet": "Ima", "strip": "Tira", "magnetic_tool": "Ferramenta magnetica", "hand": "Ponteiro"}
COLORS = [(226, 117, 100), (88, 182, 171), (225, 190, 91), (144, 155, 221), (209, 139, 188), (139, 189, 113)]
# kind, item/target, rectangle, prerequisite, reward
TASKS = {
    1: [("collect", "key417", (580, 205, 85, 65), "", "key417"),
        ("use", "drawer", (450, 255, 135, 85), "key417", "")],
    2: [("collect", "fuse", (355, 330, 110, 90), "", "fuse"),
        ("circuit", "socket", (700, 265, 150, 150), "fuse", "")],
    3: [("tiles", "photo", (540, 260, 205, 155), "", "")],
    4: [("memory", "recorder", (540, 300, 185, 110), "", "")],
    5: [("collect", "magnet", (340, 300, 100, 95), "", "magnet"),
        ("collect", "strip", (535, 350, 110, 70), "", "strip"),
        ("combine", "magnetic_tool", (0, 0, 0, 0), "", "magnetic_tool"),
        ("use", "grate", (770, 360, 155, 120), "magnetic_tool", "hand"),
        ("clock", "clock", (675, 185, 130, 140), "hand", "")],
    6: [("circuit", "panel", (540, 270, 190, 160), "", "")],
    7: [("timing", "terminal", (535, 255, 205, 175), "", "")],
    8: [("circuit", "terminal", (535, 255, 205, 175), "", "")],
}
TARGET_NAMES = {"drawer": "Gaveta", "socket": "Quadro eletrico", "photo": "Fotografia",
                "recorder": "Gravador", "grate": "Grelha", "clock": "Relogio",
                "panel": "Seguranca", "terminal": "Terminal", **ITEM_NAMES}
DISCOVERIES = {
    "x_envelope": ("new_envelope", "Envelope para Cassie"),
    "x_window": ("camera", "Registro das cameras"),
    "x_address": ("photo", "Mercer House"),
    "x_target": ("clock", "Lorelai e a foto da zeladora"),
    "x_below": ("lock_a", "Codigo do porao: 12-16"),
    "x_team": ("recordings", "Registros sobre os Naturais"),
    "x_recording": ("new_envelope", "Cassie era o alvo"),
    "x_final": ("transmission", "Provas transmitidas"),
}


def new_visual_campaign():
    return dict(edition=EDITION, chapter=1, view="intro", room="office", proofs=[], puzzle="",
                note_return="explore", page=0, line=0, flags=[], inventory=[], selected_items=[],
                step=0, locks=0, rotations=[], tiles=[], sequence=[], answer=[], dial=[0, 0],
                hits=0, phase_errors=0, stars=[], hints=[], tile_selected=-1,
                team_ready=False, team_round=0, team_selection=[], team_done=[])


def validate_visual(data):
    if not isinstance(data, dict) or set(data) != set(new_visual_campaign()) or data["edition"] != EDITION:
        raise ValueError("Aventura incompleta")
    for key, low, high in (("chapter", 1, 8), ("step", 0, 5), ("locks", 0, 3), ("hits", 0, 4),
                           ("phase_errors", 0, 100000), ("tile_selected", -1, 5)):
        if type(data[key]) is not int or not low <= data[key] <= high:
            raise ValueError("Etapa da aventura invalida")
    if data["view"] not in {"intro", "explore", "circuit", "tiles", "memory", "clock", "timing", "team_task", "complete", "epilogue", "report", "ended"}:
        raise ValueError("Tela invalida")
    for key, allowed, maximum in (("inventory", ITEM_NAMES, 6), ("selected_items", data["inventory"], 2),
                                  ("flags", range(1, 9), 8), ("hints", range(1, 9), 8), ("team_done", range(1, 9), 8)):
        values = data[key]
        if not isinstance(values, list) or len(values) > maximum or len(set(values)) != len(values) or any(v not in allowed for v in values):
            raise ValueError("Inventario invalido")
    for key, limit, count in (("rotations", 3, 16), ("tiles", 5, 6), ("sequence", 5, 7), ("answer", 5, 7), ("stars", 3, 8), ("dial", 59, 2)):
        values = data[key]
        if not isinstance(values, list) or len(values) > count or any(type(v) is not int or not 0 <= v <= limit for v in values):
            raise ValueError("Mecanismo invalido")
    if len(data["dial"]) != 2 or data["dial"][0] > 11:
        raise ValueError("Relogio invalido")
    if data["tiles"] and sorted(data["tiles"]) != list(range(6)):
        raise ValueError("Fotografia invalida")
    if data["rotations"] and len(data["rotations"]) != len(circuit_solution(data["chapter"])):
        raise ValueError("Circuito invalido")
    if data["view"] == "circuit" and not data["rotations"] or data["view"] == "tiles" and not data["tiles"] or data["view"] == "memory" and not data["sequence"]:
        raise ValueError("Mecanismo ausente")
    if data["view"] in {"circuit", "memory", "timing", "tiles", "clock"}:
        allowed = {"circuit": {2, 6, 8}, "memory": {4, 6, 8}, "timing": {7, 8}, "tiles": {3}, "clock": {5}}
        if data["chapter"] not in allowed[data["view"]]:
            raise ValueError("Mecanismo fora da fase")
    if data["answer"] != data["sequence"][:len(data["answer"])]:
        raise ValueError("Sequencia invalida")
    if data["view"] == "memory" and (len(data["answer"]) >= len(data["sequence"]) or any(v >= (4 if data["chapter"] == 4 else 6) for v in data["sequence"])):
        raise ValueError("Memoria invalida")
    if len(data["stars"]) != len(data["flags"]) or data["flags"] != list(range(1, len(data["flags"]) + 1)):
        raise ValueError("Progresso invalido")
    rounds = TEAM_TASKS[data["chapter"]]
    if type(data["team_ready"]) is not bool or type(data["team_round"]) is not int or not 0 <= data["team_round"] <= len(rounds):
        raise ValueError("Analise da equipe invalida")
    task = rounds[min(data["team_round"], len(rounds) - 1)]
    chosen = data["team_selection"]
    if (not isinstance(chosen, list) or len(chosen) > len(task["answer"])
            or any(type(i) is not int or not 0 <= i < len(task["cards"]) for i in chosen)
            or len(set(chosen)) != len(chosen)):
        raise ValueError("Selecao da equipe invalida")
    if data["team_ready"] and (data["team_round"] == len(rounds) or data["chapter"] in data["team_done"] or data["chapter"] in data["flags"]):
        raise ValueError("Analise ja encerrada")
    if data["view"] == "team_task" and not data["team_ready"]:
        raise ValueError("Analise ainda bloqueada")
    if data["proofs"] or data["puzzle"] or data["room"] != "office" or data["note_return"] != "explore" or any(data[k] != 0 for k in ("page", "line")):
        raise ValueError("Estado auxiliar invalido")


def circuit_dimensions(chapter):
    return (3, 2) if chapter == 2 else (4, 3) if chapter == 6 else (4, 4)


def circuit_solution(chapter):
    cols, rows = circuit_dimensions(chapter)
    path = [(x, y) for y in range(rows) for x in (range(cols) if y % 2 == 0 else range(cols - 1, -1, -1))]
    result = [0] * (cols * rows)
    directions = {(0, -1): 0, (1, 0): 1, (0, 1): 2, (-1, 0): 3}
    for i, (x, y) in enumerate(path):
        before = path[i - 1] if i else (-1, 0)
        after = path[i + 1] if i + 1 < len(path) else (x + (-1 if rows % 2 == 0 else 1), y)
        result[y * cols + x] = sum(1 << directions[(nx - x, ny - y)] for nx, ny in (before, after))
    return result


def rotated_mask(mask, rotation):
    return ((mask << rotation) | (mask >> (4 - rotation))) & 15


def powered_cells(chapter, rotations):
    cols, rows = circuit_dimensions(chapter)
    masks = [rotated_mask(m, r) for m, r in zip(circuit_solution(chapter), rotations)]
    if not masks or not masks[0] & 8:
        return set(), False
    seen, pending = {0}, [0]
    for i in pending:
        x, y = i % cols, i // cols
        for direction, (dx, dy) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))):
            nx, ny = x + dx, y + dy
            other = ny * cols + nx
            if 0 <= nx < cols and 0 <= ny < rows and masks[i] & (1 << direction) and masks[other] & (1 << ((direction + 2) % 4)) and other not in seen:
                seen.add(other)
                pending.append(other)
    end = (rows - 1) * cols + (0 if rows % 2 == 0 else cols - 1)
    return seen, end in seen and bool(masks[end] & (8 if rows % 2 == 0 else 2))


class VisualCampaign:
    def __init__(self, game):
        self.game = game
        self.visual = CampaignVisual(self)
        self.elapsed = 0.0
        self.replay_time = 0.0
        self.demo_offset = 0
        self.feedback = ""
        self.feedback_time = 0.0
        self.hint_time = 0.0
        self.flash = 0.0
        self.pad_pressed = -1
        self.pad_timer = 0.0
        self.pickups = []
        self.team = TeamInvestigation(self)
        self.photo = pygame.transform.smoothscale(game.backgrounds["masters"], (600, 340))
        if self.data["view"] == "memory":
            self.replay_remaining()
        elif self.data["view"] == "timing" and self.needs_final_review():
            # Old saves may have reached transmission before the team review.
            self.open_puzzle("timing")

    @property
    def data(self):
        return self.game.campaign_data

    def button(self, rect, text, value, enabled=True, selected=False):
        return Button(pygame.Rect(rect), text, value, enabled, selected)

    def stage(self):
        return STAGES[self.data["chapter"] - 1]

    def needs_final_review(self):
        d = self.data
        return d["chapter"] == 8 and 8 not in d["team_done"] and 8 not in d["flags"] and d["hits"] < 4

    def notice(self, text, error=False):
        self.feedback, self.feedback_time = text, 2.2
        if error:
            self.flash = .3

    def mistake(self, reason):
        inv = self.game.investigation
        lost = min(5, inv.score)
        inv.mistakes += 1
        inv.score = max(0, inv.score - 5)
        self.data["phase_errors"] += 1
        self.notice(f"{reason}  |  -{lost} pontos" if lost else reason, True)

    def discovered(self):
        return [Evidence(stage[5], DISCOVERIES[stage[5]][1], stage[4], "pista", f"fase{i}")
                for i, stage in enumerate(STAGES, 1) if stage[5] in self.game.investigation.evidence]

    def next_action(self):
        d = self.data
        if d["view"] == "explore":
            if d["team_ready"]:
                return f"Continue a investigacao com {self.team.actor().capitalize()}."
            kind, target, _, required, _ = self.task()
            if kind == "collect":
                items = [ITEM_NAMES[t[4]] for i, t in enumerate(TASKS[d["chapter"]])
                         if t[0] == "collect" and self.task_ready(i)]
                return "Clique para recolher: " + " + ".join(items) + "."
            if kind == "combine":
                return "Clique em Combinar + para unir o ima e a tira."
            if required:
                return f"Use {ITEM_NAMES[required]} em {TARGET_NAMES[target]}: basta clicar no objeto."
            return f"Clique em {TARGET_NAMES[target]} para continuar."
        if d["view"] == "team_task":
            return self.team.current()["prompt"]
        if d["view"] == "memory":
            if self.replay_time > 0:
                return "Observe os sinais restantes. Seus acertos foram mantidos." if self.demo_offset else "Observe os simbolos que acendem."
            return "Continue a sequencia. Os acertos estao em verde." if d["answer"] else "Clique nos simbolos na mesma ordem."
        return {
            "circuit": "Gire as pecas e leve energia ate o circulo vazio.",
            "tiles": "Clique em outra parte para trocar as duas." if d["tile_selected"] >= 0 else "Escolha duas partes da foto para trocar de lugar.",
            "clock": "Use + e - para copiar o horario da foto.",
            "timing": "Clique em Copiar na faixa verde: conexao estavel." if d["chapter"] == 7 else "Clique em Enviar na faixa verde: conexao estavel.",
        }.get(d["view"], "")

    def animate_pickup(self, item, origin):
        slot = self.data["inventory"].index(item)
        self.pickups.append({"item": item, "origin": pygame.Vector2(origin),
                             "target": pygame.Vector2(332 + slot * 116, 647), "age": 0.0})

    def task(self):
        tasks = TASKS[self.data["chapter"]]
        return tasks[min(self.data["step"], len(tasks) - 1)]

    def task_ready(self, index):
        tasks = TASKS[self.data["chapter"]]
        step = self.data["step"]
        if not 0 <= index < len(tasks) or index < step:
            return False
        kind, _, _, _, reward = tasks[index]
        if kind == "collect":
            return reward not in self.data["inventory"] and all(task[0] == "collect" for task in tasks[step:index + 1])
        return index == step

    def complete(self):
        d = self.data
        if d["chapter"] in d["flags"]:
            return
        if d["chapter"] not in d["team_done"]:
            d["team_ready"] = True
            if d["chapter"] in (6, 8):
                d["locks"] = 2 if d["chapter"] == 6 else 3
            self.pickups.clear()
            self.team.open()
            return
        stars = 3 if d["phase_errors"] == 0 and d["chapter"] not in d["hints"] else 2 if d["phase_errors"] < 4 else 1
        d["flags"].append(d["chapter"])
        d["stars"].append(stars)
        d["view"] = "complete"
        self.game.investigation.score += 50 + stars * 10
        self.game.investigation.solved_puzzles += 1
        self.game.investigation.evidence[self.stage()[5]] = False
        self.notice("+" + str(50 + stars * 10))

    def next_stage(self):
        d = self.data
        if d["view"] != "complete":
            return
        if d["chapter"] == 8:
            d["view"] = "epilogue"
            return
        d.update(chapter=d["chapter"] + 1, view="explore", step=0, locks=0, rotations=[], tiles=[],
                 sequence=[], answer=[], dial=[0, 0], hits=0, phase_errors=0, tile_selected=-1,
                 inventory=[], selected_items=[])
        d.update(team_ready=False, team_round=0, team_selection=[])
        self.elapsed = 0
        self.feedback = ""
        self.feedback_time = 0
        self.pickups.clear()

    def open_puzzle(self, kind):
        d = self.data
        if kind == "timing" and self.needs_final_review():
            d["team_ready"] = True
            self.team.open()
            return
        rng = random.Random(self.game.run_id + str(d["chapter"]) + kind)
        d["view"] = kind
        if kind == "circuit" and not d["rotations"]:
            d["rotations"] = [rng.randrange(1, 4) for _ in circuit_solution(d["chapter"])]
            if powered_cells(d["chapter"], d["rotations"])[1]:
                d["rotations"][0] = 1
        elif kind == "tiles" and not d["tiles"]:
            d["tiles"] = list(range(6))
            rng.shuffle(d["tiles"])
            if d["tiles"] == list(range(6)):
                d["tiles"][0], d["tiles"][1] = 1, 0
        elif kind == "memory":
            if not d["sequence"]:
                count = {4: 4, 6: 5, 8: 7}[d["chapter"]]
                d["sequence"] = [rng.randrange(4 if d["chapter"] == 4 else 6) for _ in range(count)]
            self.replay_remaining()
        self.elapsed = 0

    def puzzle_done(self):
        d = self.data
        if d["team_ready"] or d["chapter"] in d["flags"]:
            return
        self.game.investigation.score += 25
        self.notice("+25")
        if d["chapter"] in (6, 8) and d["view"] == "circuit":
            d["locks"] = 1
            self.open_puzzle("memory")
        elif d["chapter"] == 8 and d["view"] == "memory":
            d["locks"] = 2
            self.open_puzzle("timing")
        else:
            self.complete()

    def demo_interval(self):
        return {4: .9, 6: .7, 8: .55}.get(self.data["chapter"], .9)

    def demo_duration(self):
        return (len(self.data["sequence"]) - self.demo_offset + 1) * self.demo_interval()

    def replay_remaining(self):
        self.demo_offset = len(self.data["answer"])
        self.replay_time = self.demo_duration()
        self.pad_timer = 0

    def lit_pad(self):
        if self.replay_time <= 0:
            return -1
        t = self.demo_duration() - self.replay_time
        index = self.demo_offset + int(t / self.demo_interval()) - 1
        if self.demo_offset <= index < len(self.data["sequence"]) and t % self.demo_interval() < self.demo_interval() * .72:
            return self.data["sequence"][index]
        return -1

    def timing_position(self):
        return (self.elapsed * (0.39 if self.data["chapter"] == 7 else .55)) % 1

    def timing_window(self):
        center = (.28, .68, .44, .73)[self.data["hits"] % 4]
        half = .12 if self.data["chapter"] == 7 else .075
        return center - half, center + half

    def act(self, action):
        d = self.data
        if action == "begin" and d["view"] == "intro":
            d["view"] = "explore"
        elif action == "next":
            self.next_stage()
        elif action == "report" and d["view"] == "epilogue":
            d["view"] = "report"
            self.game.player_screens.show_ranking()
        elif action == "ranking":
            self.game.player_screens.show_ranking()
        elif action == "menu":
            self.game.reset_to_menu()
        elif action == "back":
            d["view"] = "explore"
            self.feedback_time = 0
        elif action == "dossier":
            self.game.show_clues = True
        elif action == "team":
            self.team.roster_open = True
        elif action == "team_continue" and d["team_ready"]:
            self.team.open()
        elif action == "team_confirm":
            self.team.confirm()
        elif action == "team_clear" and d["view"] == "team_task":
            d["team_selection"] = []
        elif action == "hint":
            if d["chapter"] not in d["hints"]:
                d["hints"].append(d["chapter"])
            self.hint_time = 6
            if d["view"] == "memory":
                self.replay_remaining()
            elif d["view"] == "team_task":
                self.notice(self.team.current()["hint"])
                self.feedback_time = 5
        elif action == "replay" and d["view"] == "memory":
            self.replay_remaining()
            self.feedback_time = 0
        elif action == "combine" and d["view"] == "explore" and self.task()[0] == "combine":
            if {"magnet", "strip"}.issubset(d["inventory"]):
                d["inventory"] = ["magnetic_tool"]
                d["selected_items"] = ["magnetic_tool"]
                d["step"] += 1
                self.notice("Ferramenta montada")
                self.animate_pickup("magnetic_tool", (695, 655))
        elif action == "pulse" and d["view"] == "timing":
            if self.needs_final_review():
                self.open_puzzle("timing")
                return
            low, high = self.timing_window()
            if low <= self.timing_position() <= high:
                d["hits"] += 1
                self.notice("Lote copiado" if d["chapter"] == 7 else "Parte do relatorio enviada")
                if d["hits"] == (3 if d["chapter"] == 7 else 4):
                    self.puzzle_done()
            else:
                self.mistake("Conexao perdida. Reinicie a transferencia.")
                d["hits"] = 0
        elif isinstance(action, tuple):
            kind, index = action
            if kind == "team_card":
                self.team.select(index)
            elif kind == "item":
                if index in d["inventory"]:
                    d["selected_items"] = [] if index in d["selected_items"] else [index]
            elif kind == "task" and d["view"] == "explore":
                if d["team_ready"]:
                    self.team.open()
                    return
                if not self.task_ready(index):
                    self.hint_time = 2
                    self.notice(self.next_action())
                    return
                task, target, rect, required, reward = TASKS[d["chapter"]][index]
                if required and required not in d["inventory"]:
                    self.hint_time = 3
                    self.notice("Falta: " + ITEM_NAMES[required])
                    return
                if task == "collect":
                    if reward not in d["inventory"]:
                        d["inventory"].append(reward)
                        self.game.investigation.score += 10
                        self.animate_pickup(reward, pygame.Rect(rect).center)
                    tasks = TASKS[d["chapter"]]
                    while d["step"] < len(tasks) and tasks[d["step"]][0] == "collect" and tasks[d["step"]][4] in d["inventory"]:
                        d["step"] += 1
                    self.notice(ITEM_NAMES[reward] + " no inventario  |  +10 pontos")
                elif task == "use":
                    d["inventory"].remove(required)
                    d["selected_items"] = []
                    if reward:
                        d["inventory"].append(reward)
                        self.animate_pickup(reward, pygame.Rect(rect).center)
                        self.notice(ITEM_NAMES[reward] + " recuperado")
                    d["step"] += 1
                    if d["step"] == len(TASKS[d["chapter"]]):
                        self.complete()
                else:
                    if d["chapter"] in (6, 8) and d["locks"]:
                        self.open_puzzle("memory" if d["locks"] == 1 else "timing")
                    else:
                        self.open_puzzle(task)
            elif kind == "rotate" and d["view"] == "circuit":
                d["rotations"][index] = (d["rotations"][index] + 1) % 4
                if powered_cells(d["chapter"], d["rotations"])[1]:
                    self.puzzle_done()
            elif kind == "tile" and d["view"] == "tiles":
                before = d["tile_selected"]
                if before < 0:
                    d["tile_selected"] = index
                else:
                    d["tiles"][before], d["tiles"][index] = d["tiles"][index], d["tiles"][before]
                    d["tile_selected"] = -1
                    if d["tiles"] == list(range(6)):
                        self.puzzle_done()
            elif kind == "pad" and d["view"] == "memory" and self.replay_time <= 0:
                self.pad_pressed, self.pad_timer = index, .2
                if index != d["sequence"][len(d["answer"])]:
                    self.mistake("Sequencia diferente. Observe de novo.")
                    d["answer"] = []
                    self.replay_remaining()
                else:
                    d["answer"].append(index)
                    self.notice(str(len(d["answer"])) + " / " + str(len(d["sequence"])))
                    if len(d["answer"]) == len(d["sequence"]):
                        self.puzzle_done()
            elif kind in {"dial", "dial_back"} and d["view"] == "clock":
                delta = (1 if index == 0 else 3) * (-1 if kind == "dial_back" else 1)
                d["dial"][index] = (d["dial"][index] + delta) % (12 if index == 0 else 60)
                if d["dial"] == [3, 21]:
                    self.puzzle_done()

    def buttons(self):
        d = self.data
        view = d["view"]
        team_button = self.button((755, 14, 150, 42), "Equipe", "team")
        if view in {"intro", "complete", "epilogue"}:
            buttons = [self.button((845, 622, 220, 55), "Investigar" if view == "intro" else "Ranking" if view == "epilogue" else "Avancar >", "begin" if view == "intro" else "report" if view == "epilogue" else "next")]
            if view != "intro":
                buttons.append(self.button((30, 633, 175, 48), "Rever pistas", "dossier"))
            return buttons + [team_button]
        if view in {"report", "ended"}:
            return [self.button((350, 470, 420, 60), "Ranking", "ranking"), self.button((350, 550, 420, 50), "Menu", "menu"), team_button]
        buttons = [self.button((1042, 633, 52, 52), "?", "hint"),
                   self.button((110, 633, 150, 48), f"Pistas {len(d['flags'])}/8", "dossier"), team_button]
        if view != "explore":
            buttons.append(self.button((26, 633, 64, 52), "<", "back"))
        if view == "explore":
            if d["team_ready"]:
                return buttons + [self.button((435, 485, 370, 60), "Investigar com " + self.team.actor().capitalize(), "team_continue")]
            for i, (kind, key, rect, required, reward) in enumerate(TASKS[d["chapter"]]):
                if i >= d["step"] and kind != "combine" and not (kind == "collect" and reward in d["inventory"]):
                    buttons.append(self.button(rect, TARGET_NAMES[key], ("task", i)))
            for i, item in enumerate(d["inventory"]):
                buttons.append(self.button((282 + i * 116, 624, 100, 80), ITEM_NAMES[item], ("item", item), selected=item in d["selected_items"]))
            if self.task()[0] == "combine":
                buttons.append(self.button((780, 636, 170, 48), "Combinar +", "combine"))
        elif view == "circuit":
            cols, rows = circuit_dimensions(d["chapter"])
            size = min(100, 380 // rows)
            x0, y0 = 560 - cols * size // 2, 170
            for i in range(cols * rows):
                buttons.append(self.button((x0 + i % cols * size, y0 + i // cols * size, size - 5, size - 5), "Girar", ("rotate", i)))
        elif view == "tiles":
            for i in range(6):
                buttons.append(self.button((260 + i % 3 * 200, 210 + i // 3 * 170, 200, 170), "Fotografia", ("tile", i)))
        elif view == "memory":
            count = 4 if d["chapter"] == 4 else 6
            for i in range(count):
                cols = 2 if count == 4 else 3
                x0 = 425 if count == 4 else 350
                buttons.append(self.button((x0 + i % cols * 145, 230 + i // cols * 140, 125, 120), "Sinal " + str(i + 1), ("pad", i), self.replay_time <= 0))
            buttons.append(self.button((920, 635, 90, 48), "Rever", "replay"))
        elif view == "clock":
            for index, x in enumerate((385, 585)):
                buttons += [self.button((x, 538, 50, 48), "-", ("dial_back", index)),
                            self.button((x + 110, 538, 50, 48), "+", ("dial", index))]
        elif view == "timing":
            low, high = self.timing_window()
            buttons.append(self.button((430, 460, 260, 80), "Copiar lote" if d["chapter"] == 7 else "Enviar provas", "pulse",
                                       selected=low <= self.timing_position() <= high))
        elif view == "team_task":
            buttons += self.team.buttons()
        return buttons

    def handle_event(self, event):
        if self.team.roster_open:
            self.team.handle_roster_event(event)
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                command = {"intro": "begin", "complete": "next", "epilogue": "report", "timing": "pulse", "team_task": "team_confirm"}.get(self.data["view"])
                if command:
                    self.act(command)
                    return
        for button in self.buttons():
            if button.hit(event):
                self.act(button.value)
                return

    def update(self, dt):
        if self.team.roster_open:
            return
        self.elapsed += min(dt, .1) * (.5 if self.data["view"] == "timing" and self.hint_time else 1)
        self.feedback_time = max(0, self.feedback_time - dt)
        self.flash = max(0, self.flash - dt)
        self.pad_timer = max(0, self.pad_timer - dt)
        self.hint_time = max(0, self.hint_time - dt)
        for pickup in self.pickups:
            pickup["age"] += dt
        self.pickups = [p for p in self.pickups if p["age"] < .55 and p["item"] in self.data["inventory"]]
        if self.data["view"] == "memory":
            self.replay_time = max(0, self.replay_time - dt)

    def text(self, text, rect, font=None, color=TEXT, align="left", line_spacing=5):
        draw_text(self.game.screen, text, font or self.game.fonts.body, color, pygame.Rect(rect), align=align, line_spacing=line_spacing)

    def symbol(self, center, index, radius=22, color=None):
        screen = self.game.screen
        color = color or COLORS[index % len(COLORS)]
        x, y = center
        if index % 3 == 0:
            pygame.draw.circle(screen, color, center, radius, 4)
        elif index % 3 == 1:
            pygame.draw.polygon(screen, color, [(x, y - radius), (x + radius, y + radius), (x - radius, y + radius)], 4)
        else:
            pygame.draw.rect(screen, color, (x - radius, y - radius, radius * 2, radius * 2), 4)
        if index >= 3:
            pygame.draw.circle(screen, color, center, 4)

    def draw_item(self, key, rect):
        if key == "photo":
            pygame.draw.rect(self.game.screen, TEXT, rect)
            inner = self.photo.get_rect().fit(rect.inflate(-8, -8))
            self.game.screen.blit(pygame.transform.smoothscale(self.photo, inner.size), inner)
            return
        if key not in {"magnet", "strip", "magnetic_tool", "fuse", "hand", "grate", "dust", "witness", "recorder"}:
            key = {"panel": "lock_a", "socket": "lock_a", "terminal": "terminals"}.get(key, key)
            self.visual.draw_prop(key, rect)
            return
        icon = pygame.Surface((120, 100), pygame.SRCALPHA)
        if key == "strip":
            pygame.draw.polygon(icon, (215, 206, 177), [(10, 60), (98, 18), (110, 39), (22, 80)])
            pygame.draw.line(icon, (151, 139, 111), (20, 65), (98, 29), 2)
        elif key in {"magnet", "magnetic_tool"}:
            if key == "magnetic_tool":
                pygame.draw.line(icon, (215, 206, 177), (25, 90), (60, 53), 9)
            pygame.draw.arc(icon, (212, 91, 88), (35, 8, 55, 65), 0, math.pi, 13)
            pygame.draw.rect(icon, (212, 91, 88), (35, 39, 13, 24))
            pygame.draw.rect(icon, (212, 91, 88), (77, 39, 13, 24))
            for x in (35, 77):
                pygame.draw.rect(icon, (216, 227, 223), (x, 58, 13, 14))
        elif key == "hand":
            pygame.draw.line(icon, (221, 185, 94), (60, 87), (60, 15), 7)
            pygame.draw.polygon(icon, (221, 185, 94), [(60, 5), (50, 28), (70, 28)])
            pygame.draw.circle(icon, (221, 185, 94), (60, 84), 11, 4)
        elif key == "recorder":
            pygame.draw.rect(icon, (78, 94, 97), (12, 8, 96, 85), border_radius=8)
            pygame.draw.rect(icon, (29, 41, 43), (22, 18, 76, 40), border_radius=3)
            for x in (40, 80):
                pygame.draw.circle(icon, (211, 213, 198), (x, 38), 11, 3)
            pygame.draw.line(icon, (211, 213, 198), (40, 46), (80, 46), 2)
            for x, color in ((31, COLORS[0]), (58, COLORS[1]), (85, COLORS[2])):
                pygame.draw.rect(icon, color, (x - 8, 70, 17, 12), border_radius=2)
        elif key == "witness":
            pygame.draw.circle(icon, (193, 180, 160), (60, 30), 22)
            pygame.draw.rect(icon, (77, 106, 109), (34, 56, 52, 42), border_radius=8)
        elif key == "dust":
            color = (164, 150, 124)
            pygame.draw.ellipse(icon, color, (12, 65, 98, 22))
            for x, y, radius in ((30, 64, 12), (58, 54, 20), (88, 64, 13), (17, 43, 3), (92, 32, 4)):
                pygame.draw.circle(icon, color, (x, y), radius)
        elif key == "fuse":
            pygame.draw.rect(icon, (94, 168, 176), (22, 30, 77, 35), border_radius=5)
            pygame.draw.lines(icon, (237, 222, 123), False, [(28, 48), (44, 39), (55, 55), (70, 39), (89, 48)], 3)
            for x in (12, 94):
                pygame.draw.rect(icon, (214, 219, 213), (x, 26, 15, 43), border_radius=3)
        else:
            pygame.draw.rect(icon, (36, 42, 44), (5, 4, 110, 92), border_radius=3)
            for x in range(15, 110, 19):
                pygame.draw.line(icon, (170, 178, 176), (x, 12), (x, 88), 6)
            for y in (18, 80):
                pygame.draw.line(icon, (170, 178, 176), (10, y), (110, y), 5)
        self.game.screen.blit(pygame.transform.smoothscale(icon, rect.size), rect)

    def draw_star(self, center, color):
        points = [(center[0] + math.cos(i * math.pi / 5 - math.pi / 2) * (26 if i % 2 == 0 else 12),
                   center[1] + math.sin(i * math.pi / 5 - math.pi / 2) * (26 if i % 2 == 0 else 12)) for i in range(10)]
        pygame.draw.polygon(self.game.screen, color, points)

    def draw_pickups(self):
        if self.data["view"] != "explore":
            return
        for pickup in self.pickups:
            if pickup["item"] not in self.data["inventory"]:
                continue
            t = min(1, pickup["age"] / .55)
            center = pickup["origin"].lerp(pickup["target"], 1 - (1 - t) ** 3)
            center.y -= math.sin(t * math.pi) * 48
            size = int(64 - 24 * t)
            rect = pygame.Rect(0, 0, size, size)
            rect.center = (round(center.x), round(center.y))
            pygame.draw.circle(self.game.screen, COLORS[2], rect.center, size // 2 + 7, 2)
            self.draw_item(pickup["item"], rect)

    def draw_discovery(self):
        d, g = self.data, self.game
        icon, title = DISCOVERIES[self.stage()[5]]
        rect = pygame.Rect(115, 250, 220, 185)
        if icon == "photo":
            rect = self.photo.get_rect().fit(rect)
            pygame.draw.rect(g.screen, TEXT, rect.inflate(12, 12), 4)
            g.screen.blit(pygame.transform.smoothscale(self.photo, rect.size), rect)
        elif icon == "clock":
            pygame.draw.rect(g.screen, TEXT, rect, 3)
            self.draw_clock(rect.center, 73, 3, 21)
            self.text("03:21", (115, 438, 220, 28), g.fonts.small, align="center")
        else:
            self.draw_item(icon, rect)
        self.text("Fase concluida", (375, 205, 670, 50), g.fonts.h1)
        self.text("PISTA RECUPERADA", (375, 270, 650, 26), g.fonts.small, GOOD)
        self.text(title, (375, 303, 650, 38), g.fonts.h2)
        self.text(self.stage()[4], (375, 354, 650, 85))
        for i in range(3):
            self.draw_star((405 + i * 70, 475), COLORS[2] if i < d["stars"][-1] else MUTED)
        self.text(f"Bonus da fase: +{50 + 10 * d['stars'][-1]}", (620, 460, 390, 36), g.fonts.h2, COLORS[2])
        following = "Proximo: " + STAGES[d["chapter"]][1] if d["chapter"] < 8 else "As provas chegaram a equipe. O caso continua."
        self.text(following, (375, 544, 670, 58), g.fonts.body, MUTED)

    def draw_locks(self):
        d = self.data
        if d["chapter"] not in (6, 8) or d["view"] not in {"explore", "circuit", "memory", "timing"}:
            return
        final_step = "Revisao" if d["chapter"] == 8 and 8 not in d["team_done"] else "Transmissao"
        labels = ("Circuito", "Sinais", final_step) if d["chapter"] == 8 else ("Circuito", "Sinais")
        if d["view"] == "explore":
            shade = pygame.Surface((235, 58 * len(labels) + 52), pygame.SRCALPHA)
            shade.fill((18, 26, 27, 225))
            self.game.screen.blit(shade, (16, 154))
        self.text("ETAPAS", (30, 170, 180, 26), self.game.fonts.small, MUTED)
        for i, label in enumerate(labels):
            y = 224 + i * 58
            done, active = i < d["locks"], i == d["locks"]
            color = GOOD if done else COLORS[2] if active else MUTED
            pygame.draw.circle(self.game.screen, color, (46, y), 12, 0 if done else 2)
            if done:
                pygame.draw.lines(self.game.screen, (28, 32, 33), False, [(40, y), (45, y + 5), (52, y - 5)], 3)
            elif active:
                pygame.draw.circle(self.game.screen, color, (46, y), 4)
            self.text(label, (68, y - 15, 175, 30), color=color)
            self.text("Concluido" if done else "Agora" if active else "A seguir",
                      (68, y + 15, 175, 24), self.game.fonts.small, color)

    def draw_clock(self, center, radius, hour, minute):
        screen = self.game.screen
        pygame.draw.circle(screen, (232, 225, 201), center, radius)
        pygame.draw.circle(screen, (192, 155, 81), center, radius, 6)
        for i in range(12):
            angle = i * math.pi / 6 - math.pi / 2
            end = (center[0] + math.cos(angle) * (radius - 10), center[1] + math.sin(angle) * (radius - 10))
            start = (center[0] + math.cos(angle) * (radius - 18), center[1] + math.sin(angle) * (radius - 18))
            pygame.draw.line(screen, (42, 46, 47), start, end, 3)
        for value, length, width in ((hour / 12 + minute / 720, radius * .5, 7), (minute / 60, radius * .76, 4)):
            angle = value * math.tau - math.pi / 2
            pygame.draw.line(screen, (42, 46, 47), center, (center[0] + math.cos(angle) * length, center[1] + math.sin(angle) * length), width)
        pygame.draw.circle(screen, ACCENT, center, 7)

    def draw(self):
        g, d = self.game, self.data
        if self.team.roster_open:
            self.team.draw_roster()
            return
        screen = g.screen
        title, objective, background, difficulty, story, evidence = self.stage()
        screen.blit(g.room_image if background == "escritorio" else g.backgrounds[background], (0, 0))
        view = d["view"]
        if view != "explore":
            draw_band(screen, pygame.Rect(0, 108, 1120, 505), alpha=222)
        draw_band(screen, pygame.Rect(0, 0, 1120, 108), alpha=238)
        self.text(f"FASE {d['chapter']} / 8  |  {title}", (28, 13, 680, 34), g.fonts.h2)
        self.text(objective, (28, 55, 760, 30), g.fonts.body)
        self.text("LOCAL: " + LOCATIONS[d["chapter"] - 1], (225, 87, 530, 21), self.visual.item_font, MUTED)
        self.text(f"{g.investigation.score} pontos", (780, 64, 190, 25), g.fonts.small)
        for i in range(5):
            pygame.draw.rect(screen, COLORS[0] if i < difficulty else (62, 71, 69), (982 + i * 22, 69, 15, 12), border_radius=2)
        draw_band(screen, pygame.Rect(0, 612, 1120, 108), alpha=240)
        for i in range(8):
            pygame.draw.circle(screen, GOOD if i + 1 in d["flags"] else COLORS[2] if i + 1 == d["chapter"] else (76, 85, 82), (34 + i * 20, 96), 5)
        buttons = self.buttons()
        if view == "intro":
            self.team.draw_intro()
        elif view == "complete":
            self.draw_discovery()
        elif view in {"epilogue", "report", "ended"}:
            screen.blit(g.stage_portraits["celine" if view == "epilogue" else "cassie"], (115, 230))
            heading = "A investigacao continua" if view == "epilogue" else "Investigacao encerrada"
            self.text(heading, (375, 220, 670, 50), g.fonts.h1)
            self.text("A equipe tem as provas. Ainda falta encontrar Celine." if view == "epilogue" else f"{g.player_name} / {g.investigation.score} pontos", (375, 305, 650, 110))
            if view == "epilogue":
                self.team.draw_ending()
        elif view == "explore":
            if d["team_ready"]:
                screen.blit(self.team.faces[self.team.actor()], (555, 250))
            else:
                screen.blit(self.team.faces["cassie"], (120, 380))
                if self.team.actor() != "cassie":
                    screen.blit(self.team.faces[self.team.actor()], (945, 380))
                    self.text(self.team.actor().capitalize(), (935, 575, 150, 28), g.fonts.small, align="center")
            for button in buttons:
                if isinstance(button.value, tuple) and button.value[0] == "task":
                    index = button.value[1]
                    kind, key, rect, required, reward = TASKS[d["chapter"]][index]
                    prop = {"socket": "panel"}.get(key, key)
                    self.draw_item(prop, button.rect)
                    pygame.draw.rect(screen, COLORS[2] if self.task_ready(index) else MUTED, button.rect.inflate(10, 10), 2, border_radius=4)
                    if self.task_ready(index):
                        pygame.draw.circle(screen, COLORS[2], (button.rect.centerx, button.rect.y - 22), 7 + int(math.sin(self.elapsed * 4) * 2))
                        if self.hint_time:
                            pygame.draw.rect(screen, COLORS[2], button.rect.inflate(26, 26), 4, border_radius=5)
                    if required:
                        self.draw_item(required, pygame.Rect(button.rect.right - 32, button.rect.bottom - 28, 30, 26))
                elif isinstance(button.value, tuple) and button.value[0] == "item":
                    pygame.draw.rect(screen, (48, 78, 71), button.rect, border_radius=4)
                    pygame.draw.rect(screen, COLORS[2] if button.selected else MUTED, button.rect, 2, border_radius=4)
                    self.draw_item(button.value[1], pygame.Rect(button.rect.x + 30, button.rect.y + 5, 40, 35))
                    draw_text(screen, button.text, self.visual.item_font, TEXT,
                              pygame.Rect(button.rect.x + 4, 666, 92, 38), line_spacing=0, align="center")
            if self.task()[0] == "combine":
                pygame.draw.line(screen, COLORS[2], (524, 653), (754, 653), 3)
                self.draw_item("magnetic_tool", pygame.Rect(665, 630, 60, 50))
        elif view == "circuit":
            solution = circuit_solution(d["chapter"])
            powered, done = powered_cells(d["chapter"], d["rotations"])
            cells = [b for b in buttons if isinstance(b.value, tuple) and b.value[0] == "rotate"]
            hint_index = next((i for i, r in enumerate(d["rotations"]) if r % (2 if solution[i] in (5, 10) else 4)), -1)
            for button in cells:
                i = button.value[1]
                mask = rotated_mask(solution[i], d["rotations"][i])
                pygame.draw.rect(screen, (41, 54, 54), button.rect, border_radius=4)
                pygame.draw.rect(screen, (109, 127, 119), button.rect, 1, border_radius=4)
                color = COLORS[1] if i in powered else (157, 164, 159)
                for direction, point in enumerate((button.rect.midtop, button.rect.midright, button.rect.midbottom, button.rect.midleft)):
                    if mask & (1 << direction):
                        pygame.draw.line(screen, color, button.rect.center, point, 11)
                pygame.draw.circle(screen, color, button.rect.center, 10)
                if self.hint_time and i == hint_index:
                    pygame.draw.rect(screen, COLORS[2], button.rect, 3, border_radius=4)
                    for direction, point in enumerate((button.rect.midtop, button.rect.midright, button.rect.midbottom, button.rect.midleft)):
                        if solution[i] & (1 << direction):
                            pygame.draw.line(screen, COLORS[2], button.rect.center, point, 3)
            # Source and destination stay fixed, independent of rotations.
            first, last = cells[0].rect, cells[-1 if circuit_dimensions(d["chapter"])[1] % 2 else -circuit_dimensions(d["chapter"])[0]].rect
            pygame.draw.circle(screen, COLORS[1], (first.left - 34, first.centery), 18)
            endx = last.right + 34 if circuit_dimensions(d["chapter"])[1] % 2 else last.left - 34
            pygame.draw.circle(screen, GOOD if done else COLORS[0], (endx, last.centery), 18, 4)
        elif view == "tiles":
            for button in buttons:
                if isinstance(button.value, tuple) and button.value[0] == "tile":
                    i = button.value[1]
                    tile = d["tiles"][i]
                    screen.blit(self.photo, button.rect, pygame.Rect(tile % 3 * 200, tile // 3 * 170, 200, 170))
                    pygame.draw.rect(screen, COLORS[2] if d["tile_selected"] == i else (220, 216, 199), button.rect, 3)
                    if self.hint_time and tile != i:
                        self.text(str(tile + 1), (button.rect.x + 8, button.rect.y + 8, 40, 30), g.fonts.h2)
            screen.blit(pygame.transform.smoothscale(self.photo, (150, 85)), (930, 220))
            self.text("FOTO RASGADA DO ENVELOPE", (365, 565, 400, 30), g.fonts.small, align="center")
        elif view == "memory":
            lit = self.lit_pad()
            if self.pad_timer and self.replay_time <= 0:
                lit = self.pad_pressed
            for button in buttons:
                if isinstance(button.value, tuple) and button.value[0] == "pad":
                    i = button.value[1]
                    pygame.draw.rect(screen, COLORS[i] if lit == i else (41, 51, 53), button.rect, border_radius=6)
                    pygame.draw.rect(screen, COLORS[i], button.rect, 3, border_radius=6)
                    self.symbol(button.rect.center, i, 25, (28, 32, 33) if lit == i else None)
            for i in range(len(d["sequence"])):
                pygame.draw.circle(screen, GOOD if i < len(d["answer"]) else MUTED, (430 + i * 35, 570), 8, 0 if i < len(d["answer"]) else 2)
            device = {4: "Gravador", 6: "Arquivo", 8: "Terminal"}[d["chapter"]]
            self.text(device + (": observe" if self.replay_time > 0 else ": sua vez"), (390, 158, 400, 35), g.fonts.h2,
                      COLORS[1] if self.replay_time > 0 else COLORS[2])
        elif view == "clock":
            self.draw_clock((550, 335), 145, *d["dial"])
            self.draw_clock((910, 270), 65, 3, 21)
            self.text("FOTO DA ZELADORA", (815, 365, 210, 25), g.fonts.small, align="center")
            self.text("03:21", (855, 400, 120, 35), g.fonts.h2, COLORS[2], align="center")
            for i, x in enumerate((385, 585)):
                self.text("Hora" if i == 0 else "Minutos", (x, 497, 160, 28), g.fonts.small, align="center")
                self.text(f"{d['dial'][i]:02d}", (x + 52, 548, 56, 32), g.fonts.h2, align="center")
        elif view == "timing":
            transfer = TRANSFERS[d["chapter"]][min(d["hits"], len(TRANSFERS[d["chapter"]]) - 1)]
            self.text(transfer, (300, 185, 550, 40), g.fonts.h2, align="center")
            bar = pygame.Rect(300, 325, 550, 65)
            pygame.draw.rect(screen, (48, 53, 56), bar, border_radius=4)
            low, high = self.timing_window()
            pygame.draw.rect(screen, COLORS[1], (bar.x + low * bar.w, bar.y, (high - low) * bar.w, bar.h))
            x = bar.x + self.timing_position() * bar.w
            pygame.draw.line(screen, TEXT, (x, bar.y - 15), (x, bar.bottom + 15), 5)
            self.text("FAIXA VERDE = CONEXAO ESTAVEL", (300, 415, 550, 30), g.fonts.small, MUTED, "center")
            count = 3 if d["chapter"] == 7 else 4
            for i in range(count):
                pygame.draw.circle(screen, GOOD if i < d["hits"] else MUTED, (475 + i * 55, 250), 14, 0 if i < d["hits"] else 3)
        elif view == "team_task":
            self.team.draw_task()
        for button in buttons:
            if not isinstance(button.value, tuple) or button.value[0] in {"dial", "dial_back"}:
                button.draw(screen, g.fonts, pygame.mouse.get_pos())
        self.draw_locks()
        self.draw_pickups()
        instruction = self.next_action()
        if instruction or self.feedback_time > 0:
            draw_band(screen, pygame.Rect(0, 108, 1120, 44), alpha=238)
            message = self.feedback if self.feedback_time > 0 else "AGORA  |  " + instruction
            self.text(message, (28, 115, 1064, 32), g.fonts.body,
                      COLORS[0] if self.flash else COLORS[2] if self.feedback_time > 0 else TEXT, align="center")
        hover = next((b for b in buttons if b.rect.collidepoint(pygame.mouse.get_pos())), None)
        if hover and (isinstance(hover.value, tuple) or hover.value in {"hint", "replay", "back"}) and not (isinstance(hover.value, tuple) and hover.value[0] == "team_card"):
            label = {"hint": "Ajuda visual", "replay": "Rever sinais restantes", "back": "Voltar"}.get(hover.value if isinstance(hover.value, str) else "", hover.text)
            if isinstance(hover.value, tuple) and hover.value[0] in {"dial", "dial_back"}:
                label = ("Diminuir " if hover.value[0] == "dial_back" else "Aumentar ") + ("hora" if hover.value[1] == 0 else "minutos")
            self.visual.draw_tooltip(label, hover.rect, 245)
        if self.flash:
            pygame.draw.rect(screen, COLORS[0], (3, 3, 1114, 714), 5)
