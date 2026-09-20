from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import math

import pygame

from scripts.interfaces import Button, TEXT, MUTED, ACCENT_2, GOOD, BAD, draw_band, draw_text, wrap_text
from scripts.investigacao import InvestigationState
from scripts.instrucoes import PUZZLE_INSTRUCTIONS
from scripts.campanha_visual import CampaignVisual, COMPANIONS, CONVERSATIONS
from scripts.roteiro_expandido import (PROLOGUE, EPILOGUE, CHAPTERS, ITEMS, OBJECTS,
                                      PUZZLES, ROOMS, OBJECTIVES, GRID_ROWS, EVIDENCE_DATA, HOTSPOT_POSITIONS,
                                      GUIDED_STEPS, PROOF_OPTIONS, PUZZLE_HINTS, DIALOGUES, BRIEFING)


EXPOSURE_LIMIT = 5
VIEWS = {"dialogue", "explore", "note", "inventory", "map", "puzzle", "help", "report"}


def new_campaign() -> dict:
    return dict(chapter=0, room="intro", visited=["intro"], inventory=[], flags=[], exposure=0,
                view="dialogue", dialogue="opening", line=0, puzzle="", input="", answers=[],
                choice="", proofs=[], selected_items=[], page=0, map_phase=0, note_title="",
                note_text="", note_return="explore", help_used=[], failures={}, cooldown=0.0,
                best_blocked=False, input_field=0, checkpoint=None)


def validate_campaign(data: object, nested=False) -> None:
    if not isinstance(data, dict) or set(data) != set(new_campaign()):
        raise ValueError("Campanha incompleta")
    for key, low, high in (("chapter", 0, 7), ("line", 0, max(map(len, DIALOGUES.values()))), ("exposure", 0, 4),
                           ("page", 0, 100), ("map_phase", 0, 6), ("input_field", 0, 2)):
        if type(data[key]) is not int or not low <= data[key] <= high:
            raise ValueError("Etapa da campanha invalida")
    for key, allowed in (("room", ROOMS), ("view", VIEWS), ("dialogue", DIALOGUES),
                         ("puzzle", {"", *PUZZLES}), ("note_return", VIEWS)):
        if not isinstance(data[key], str) or data[key] not in allowed:
            raise ValueError("Cena da campanha invalida")
    if data["line"] > len(DIALOGUES[data["dialogue"]]):
        raise ValueError("Fala invalida")
    if data["view"] == "dialogue" and data["line"] == len(DIALOGUES[data["dialogue"]]):
        raise ValueError("Dialogo concluido")
    known_flags = {*OBJECTS, *PUZZLES, "magnetic_tool", "panel_locked", "entered_house"}
    for key, allowed, size in (("inventory", ITEMS, len(ITEMS)), ("flags", known_flags, len(known_flags)),
                               ("visited", ROOMS, len(ROOMS)), ("selected_items", data["inventory"], 2),
                               ("proofs", {"x_" + k[2:] for k in EVIDENCE_DATA}, 3)):
        value = data[key]
        if not isinstance(value, list) or len(value) > size or any(type(x) is not str or x not in allowed for x in value) or len(set(value)) != len(value):
            raise ValueError("Inventario ou selecao invalida")
    for key, size in (("note_text", 6000), ("note_title", 150), ("input", 40), ("choice", 100)):
        if not isinstance(data[key], str) or len(data[key]) > size:
            raise ValueError("Texto de campanha invalido")
    if any(c not in "0123456789 :" for c in data["input"]):
        raise ValueError("Entrada numerica invalida")
    if not isinstance(data["answers"], list) or len(data["answers"]) > 9 or any(type(x) is not str for x in data["answers"]):
        raise ValueError("Respostas invalidas")
    if data["puzzle"]:
        options = dict(PUZZLES[data["puzzle"]]["options"])
        if any(x and x not in options for x in data["answers"]) or (data["choice"] and data["choice"] not in options):
            raise ValueError("Alternativa invalida")
        if PUZZLES[data["puzzle"]]["kind"] == "grid" and len(data["answers"]) != len(GRID_ROWS[data["puzzle"]]):
            raise ValueError("Grade incompleta")
    elif data["view"] == "puzzle":
        raise ValueError("Enigma ausente")
    if type(data["best_blocked"]) is not bool or type(data["cooldown"]) not in (int, float) or not math.isfinite(data["cooldown"]) or not 0 <= data["cooldown"] <= 8:
        raise ValueError("Indicador de campanha invalido")
    if not isinstance(data["failures"], dict) or any(k not in PUZZLES or type(v) is not int or not 0 <= v <= 100000 for k, v in data["failures"].items()):
        raise ValueError("Tentativas invalidas")
    if not isinstance(data["help_used"], list) or len(data["help_used"]) > 100 or any(type(v) is not str or len(v) > 100 for v in data["help_used"]):
        raise ValueError("Consultas invalidas")
    checkpoint = data["checkpoint"]
    if checkpoint is not None:
        if nested or not isinstance(checkpoint, dict) or set(checkpoint) != {"data", "investigation"}:
            raise ValueError("Checkpoint invalido")
        validate_campaign(checkpoint["data"], nested=True)
        inv = checkpoint["investigation"]
        if not isinstance(inv, dict) or set(inv) != set(asdict(InvestigationState())):
            raise ValueError("Investigacao do checkpoint invalida")
        for key in ("score", "mistakes", "correct_connections", "solved_puzzles", "lies_found"):
            if type(inv[key]) is not int or abs(inv[key]) > 1000000 or (key != "score" and inv[key] < 0):
                raise ValueError("Pontuacao do checkpoint invalida")
        if not isinstance(inv["evidence"], dict) or any(k not in EVIDENCE_DATA or type(v) is not bool for k, v in inv["evidence"].items()):
            raise ValueError("Provas do checkpoint invalidas")
        if not isinstance(inv["used_abilities"], list) or len(inv["used_abilities"]) > 100 or any(type(v) is not str or len(v) > 100 for v in inv["used_abilities"]):
            raise ValueError("Habilidades do checkpoint invalidas")


class ExpandedCampaign:
    def __init__(self, game):
        self.game = game
        self.visual = CampaignVisual(self)

    @property
    def data(self):
        return self.game.campaign_data

    def has(self, key):
        return key in self.data["flags"] or key in self.data["inventory"] or self.game.investigation.has(key)

    def flag(self, key):
        if key not in self.data["flags"]:
            self.data["flags"].append(key)

    def next_step(self):
        if self.data["chapter"] >= len(GUIDED_STEPS):
            return None
        for room, key in GUIDED_STEPS[self.data["chapter"]]:
            done = (OBJECTS[key]["puzzle"] or key) if key in OBJECTS else key
            if done in self.data["flags"]:
                continue
            return room, key
        return None

    def step_label(self):
        step = self.next_step()
        if step is None:
            return "Investigacao concluida"
        room, key = step
        action = "Montar ferramenta magnetica" if key == "magnetic_tool" else OBJECTS[key]["label"]
        return action + " / " + ROOMS[room]["title"]

    def note(self, title, text, back="explore"):
        self.data.update(view="note", note_title=title, note_text=text, note_return=back, page=0)

    def reward(self, content):
        for key in content.get("items", []):
            if key not in self.data["inventory"]:
                self.data["inventory"].append(key)
        for key in content.get("evidence", []):
            self.game.investigation.add_evidence(key)

    def checkpoint(self):
        saved = deepcopy({k: v for k, v in self.data.items() if k != "checkpoint"})
        saved.update(checkpoint=None, view="explore", puzzle="", input="", answers=[], choice="", proofs=[],
                     selected_items=[], page=0, exposure=0, cooldown=0.0)
        inv = asdict(self.game.investigation)
        inv["used_abilities"] = sorted(inv["used_abilities"])
        self.data["checkpoint"] = dict(data=saved, investigation=inv)

    def penalize(self, reason, exposure=1):
        self.game.investigation.mistakes += 1
        previous_score = self.game.investigation.score
        self.game.investigation.score = max(0, previous_score - 5)
        self.data.update(exposure=0, cooldown=0.0)
        self.game.set_message(reason + f" (-{previous_score - self.game.investigation.score} pontos)", 8)

    def hint_level(self):
        key = self.data["puzzle"]
        for level in (3, 2, 1):
            if f"hint:{key}:{level}" in self.data["help_used"]:
                return level
        return 0

    def show_hint(self):
        key = self.data["puzzle"]
        if not key:
            return
        level = min(3, self.hint_level() + 1)
        used = self.data["help_used"]
        used[:] = [value for value in used if not value.startswith(f"hint:{key}:")]
        used.append(f"hint:{key}:{level}")
        content = PUZZLES[key]
        if level < 3:
            text = PUZZLE_HINTS[key][level - 1]
            title = f"Dica {level} de 2: " + content["title"]
        else:
            answer = content["answer"]
            labels = dict(content["options"])
            if content["kind"] == "grid":
                text = "\n".join(row + ": " + labels[value] for row, value in zip(GRID_ROWS[key], answer))
            elif isinstance(answer, list):
                text = "\n".join(f"{i + 1}. {labels[value]}" for i, value in enumerate(answer))
            else:
                text = labels.get(answer, answer)
            if content["proofs"]:
                text += "\n\nProvas: " + "; ".join(EVIDENCE_DATA[proof][0] for proof in content["proofs"])
            text += "\n\n" + PUZZLE_HINTS[key][1]
            title = "Resposta: " + content["title"]
        self.note(title, text, "puzzle")

    def advance(self, phase, room):
        self.data.update(chapter=phase, room=room, map_phase=min(phase, 6), page=0)
        if room not in self.data["visited"]:
            self.data["visited"].append(room)
        self.game.player.rect.topleft = (1010, 510)
        self.checkpoint()
        if phase == 7:
            self.data.update(view="dialogue", dialogue="epilogue", line=0)
        else:
            self.note(CHAPTERS[phase], OBJECTIVES[phase])

    def available_rooms(self):
        phase = self.data["map_phase"]
        return [key for key, room in ROOMS.items() if room["phase"] == phase or (phase == 5 and key == "hidden")]

    def travel(self, key):
        room = ROOMS[key]
        chapter = self.data["chapter"]
        if room["phase"] > chapter or (chapter >= 4 and room["phase"] < 4):
            self.note("Outro momento da investigacao", "A equipe agora investiga Mercer House." if chapter >= 4 else "Ainda precisamos concluir os registros desta etapa.")
            return
        if any(not self.has(k) for k in room["needs"]):
            names = [ITEMS[k][0] if k in ITEMS else "a mensagem que revela o acesso" for k in room["needs"] if not self.has(k)]
            self.note("Acesso fechado", "Falta: " + ", ".join(names) + ".")
            return
        self.data.update(room=key, view="explore", page=0)
        if key not in self.data["visited"]:
            self.data["visited"].append(key)
        self.game.player.rect.topleft = (1010, 510)
        if key == "vestibule" and not self.has("entered_house"):
            self.flag("entered_house")
            self.note("Mercer House", "Dean: Vamos observar a casa e seus registros. Descobrir por que escolheram este lugar pode explicar a mensagem para Cassie.")

    def interact(self, key):
        if key not in ROOMS[self.data["room"]]["objects"]:
            return
        content = OBJECTS[key]
        if (key in self.data["flags"] and not content["puzzle"]) or (content["puzzle"] and content["puzzle"] in self.data["flags"]):
            self.note(content["label"], content["text"])
            return
        if any(not self.has(k) for k in content["needs"]):
            if key in {"lock_b", "lock_c"}:
                self.penalize("A placa exige a ordem A, B, C. O mecanismo reagiu ao acionamento prematuro.")
            else:
                self.note(content["label"], "Ainda falta uma descoberta anterior. " + content["text"])
            return
        if content["use"] and not set(content["use"]).issubset(self.data["selected_items"]):
            if key == "drawer" and any(k in self.data["selected_items"] for k in ("key471", "key714")):
                self.penalize("Esta chave nao abre a gaveta. Confira a etiqueta e tente outra.")
                return
            if key == "drawer":
                self.note("Escolher chave", "A etiqueta da tampa lateral indica o patrimonio 417. Qual copia abre esta gaveta?")
                return
            self.note(content["label"], "Objeto necessario: " + ", ".join(ITEMS[item][0] for item in content["use"]) + ".")
            return
        if key == "terminals":
            self.data.update(view="help", page=0)
            return
        self.reward(content)
        self.data["selected_items"] = []
        if content["puzzle"]:
            self.open_puzzle(content["puzzle"])
        else:
            self.flag(key)
            if content["phase"]:
                self.advance(*content["phase"])
            else:
                text = content["text"]
                for evidence in content["evidence"]:
                    text += "\n\n" + EVIDENCE_DATA[evidence][1]
                self.note(content["label"], text)

    def open_puzzle(self, key):
        content = PUZZLES[key]
        if any(not self.has(k) for k in content["needs"]):
            self.note(content["title"], "O argumento ainda precisa dos registros da sala e do arquivo. Revise os ambientes antes de concluir.")
            return
        self.data.update(view="puzzle", puzzle=key, input="", answers=[""] * len(GRID_ROWS[key]) if key in GRID_ROWS else [],
                         choice="", proofs=[], page=0, input_field=0)
        self.game.set_message("")

    def solve(self):
        key = self.data["puzzle"]
        if not key or key in self.data["flags"]:
            return
        content = PUZZLES[key]
        kind = content["kind"]
        if kind == "code":
            value = " ".join(self.data["input"].strip().split()).replace(":", "")
            if not value:
                return
            correct = value == content["answer"]
        elif kind in {"order", "grid", "set"}:
            if not self.data["answers"] or "" in self.data["answers"]:
                return
            correct = (set(self.data["answers"]) == set(content["answer"]) if kind == "set" else self.data["answers"] == content["answer"])
        else:
            if not self.data["choice"] or (kind == "proof" and not self.data["proofs"]):
                return
            correct = self.data["choice"] == content["answer"]
            if kind == "proof":
                correct = correct and set(self.data["proofs"]) == set(content["proofs"])
        if not correct:
            failures = self.data["failures"].get(key, 0) + 1
            self.data["failures"][key] = failures
            self.penalize("Ainda nao. Seu progresso foi mantido; voce pode tentar novamente.", exposure=0)
            return
        self.flag(key)
        self.reward(content)
        if kind == "proof":
            self.game.investigation.register_connection(True)
            for proof in self.data["proofs"]:
                self.game.investigation.mark_used(proof)
            if key == "witness":
                self.game.investigation.lies_found += 1
        else:
            self.game.investigation.register_puzzle(True)
        if key == "recovery_two":
            self.flag("final_code")
        message = "Os registros sustentam a resposta."
        if content["items"]:
            message += " Objetos obtidos: " + ", ".join(ITEMS[k][0] for k in content["items"]) + "."
        for proof in content["evidence"]:
            message += "\n\n" + EVIDENCE_DATA[proof][1]
        if key == "witness":
            message = "Depoente: Eu inventei a ligacao. Celine pediu que eu nao revelasse sua saida.\n\n" + message
        if key == "positional":
            message += "\n\nFragmento: ...ER HOUSE / 23. Uma transparencia precisa da fotografia dobrada do arquivo de Celine."
        if key == "gallery":
            message += "\n\nToda equipe tem um ponto que pode ser puxado."
        if key == "recovery_two":
            message += " O circuito alternativo recuperou o acesso aos registros. O terminal de transmissao esta acessivel."
        self.data.update(puzzle="", input="", answers=[], choice="", proofs=[], cooldown=0.0)
        if content["phase"]:
            self.advance(*content["phase"])
            if self.data["chapter"] != 7:
                self.data["note_text"] = message + "\n\n" + self.data["note_text"]
        else:
            self.checkpoint()
            self.note(content["title"], message)

    def combine(self):
        selected = set(self.data["selected_items"])
        if selected == {"magnet", "strip"}:
            for key in selected:
                self.data["inventory"].remove(key)
            self.reward({"items": ["magnetic_tool"]})
            self.flag("magnetic_tool")
            self.data["selected_items"] = []
            self.note("Ferramenta magnetica", "O ima preso a tira alcanca objetos na grelha da cozinha.", "inventory")
        elif selected == {"folded_photo", "overlay"}:
            if self.has("overlay"):
                self.note("Transparencia alinhada", "As janelas deixam visiveis as letras de MERCER HOUSE. A mesa de luz na sala de evidencias permite conferir o endereco.", "inventory")
        else:
            self.note("Objetos separados", "Os encaixes destes objetos nao combinam.", "inventory")

    def help(self, person):
        chapter = self.data["chapter"]
        key = f"{chapter}:{person}" if chapter == 5 else f"{chapter}:{self.data['puzzle']}:{person}"
        used = self.data["help_used"]
        budget = 2 if chapter == 5 else 3
        if chapter in (0, 4, 6, 7):
            self.note("Sem apoio direto", "Cassie precisa comparar os registros do dossie e os objetos que trouxe.", "puzzle" if self.data["puzzle"] else "explore")
            return
        if key not in used:
            if sum(v.startswith(f"{chapter}:") for v in used) >= budget:
                self.note("Consultas esgotadas", "As pistas continuam no dossie. Nao ha novas consultas disponiveis nesta fase.", "puzzle" if self.data["puzzle"] else "explore")
                return
            used.append(key)
        texts = {
            "Lia": "Ele construiu o horario antes de construir a frase." if chapter == 2 else "Compare a frase inteira. Uma afirmacao verdadeira nao torna a segunda verdadeira.",
            "Michael": "A mencao ao celular produz medo de ser desmentido, nao medo de Celine." if chapter == 2 else "Medo, culpa e antecipacao nao sao equivalentes. A reacao nao identifica o rosto do mensageiro.",
            "Sloane": "Cada numero conversa com os dois anteriores." if chapter == 3 else "Retire o separador do horario; conserve o termo; use dois digitos para o minuto. O manual permite fazer a mesma transformacao sem mim.",
        }
        self.note(person, texts[person], "puzzle" if self.data["puzzle"] else "explore")

    def button(self, rect, text, value, enabled=True, selected=False):
        return Button(pygame.Rect(rect), text, value, enabled=enabled, selected=selected)

    def buttons(self):
        d = self.data
        view = d["view"]
        buttons = []
        if view == "explore":
            return self.visual.explore_buttons()
        elif view == "dialogue":
            buttons = [self.button((830, 630, 240, 50), "Continuar", "dialogue_next")]
        elif view == "note":
            return self.visual.note_buttons()
        elif view == "inventory":
            for i, key in enumerate(d["inventory"][d["page"] * 8:d["page"] * 8 + 8]):
                selected = key in d["selected_items"]
                buttons.append(self.button((50 + i % 2 * 520, 172 + i // 2 * 62, 500, 50), ITEMS[key][0], ("item", key), selected or len(d["selected_items"]) < 2, selected))
            buttons += [self.button((50, 630, 160, 48), "Voltar", "back"), self.button((230, 630, 160, 48), "Usar", "back", bool(d["selected_items"])),
                        self.button((410, 630, 160, 48), "Combinar", "combine", len(d["selected_items"]) == 2)]
            buttons += self.page_buttons(len(d["inventory"]), 8)
        elif view == "map":
            for i in range(min(d["chapter"], 6) + 1):
                if d["chapter"] >= 4 and i < 4:
                    continue
                buttons.append(self.button((50 + i * 140, 158, 126, 42), "Prologo" if i == 0 else f"Fase {i}", ("phase", i), selected=d["map_phase"] == i))
            rooms = self.available_rooms()
            for i, key in enumerate(rooms[d["page"] * 8:d["page"] * 8 + 8]):
                buttons.append(self.button((50 + i % 2 * 520, 230 + i // 2 * 70, 500, 54), ROOMS[key]["title"], ("room", key), selected=d["room"] == key))
            buttons += [self.button((50, 630, 170, 48), "Voltar", "back")] + self.page_buttons(len(rooms), 8)
        elif view == "help":
            people = ("Lia", "Michael") if d["chapter"] == 2 else ("Sloane",) if d["chapter"] == 3 else ("Lia", "Michael", "Sloane")
            for i, person in enumerate(people):
                buttons.append(self.button((370, 240 + i * 90, 380, 60), person, ("consult", person)))
            buttons.append(self.button((50, 630, 170, 48), "Voltar", "help_back"))
        elif view == "puzzle":
            content = PUZZLES[d["puzzle"]]
            kind = content["kind"]
            if kind in {"choice", "order", "set"} or (kind == "proof" and not d["choice"]):
                options = content["options"]
                columns = 3 if len(options) > 6 else 2 if len(options) > 3 else 1
                width = 1020 // columns
                height = 82 if columns == 2 else 66
                for i, (key, label) in enumerate(options):
                    selected = key in d["answers"] or key == d["choice"]
                    if kind == "order" and selected:
                        label = f"{d['answers'].index(key) + 1}. " + label
                    buttons.append(self.button((50 + i % columns * width, 280 + i // columns * (height + 10), width - 12, height), label, ("answer", key), selected=selected))
            elif kind == "proof":
                keys = [k for k in PROOF_OPTIONS[d["puzzle"]] if self.has(k)]
                for i, key in enumerate(keys[d["page"] * 6:d["page"] * 6 + 6]):
                    selected = key in d["proofs"]
                    buttons.append(self.button((50 + i % 2 * 520, 285 + i // 2 * 72, 500, 58), EVIDENCE_DATA[key][0], ("proof", key), selected or len(d["proofs"]) < 3, selected))
                buttons += self.page_buttons(len(keys), 6)
            elif kind == "grid":
                options = dict(content["options"])
                for i, row in enumerate(GRID_ROWS[d["puzzle"]]):
                    buttons.append(self.button((470, 270 + i * 56, 560, 48), options.get(d["answers"][i], "-"), ("grid", i)))
                if d["puzzle"] == "grid":
                    buttons.append(self.button((50, 530, 610, 42), "Atribuir o rosto do mensageiro a Lorelai", "unsupported"))
            elif kind == "code" and d["puzzle"] == "final_code":
                fields = (d["input"].split(" ") + ["", "", ""])[:3]
                for i, value in enumerate(fields):
                    buttons.append(self.button((180 + i * 260, 318, 240, 76), value or "_", ("field", i), selected=d["input_field"] == i))
            if kind == "code":
                for i, digit in enumerate("1234567890"):
                    buttons.append(self.button((50 + i * 88, 466, 78, 52), digit, ("digit", digit)))
                buttons.append(self.button((936, 466, 125, 52), "Apagar", ("digit", "backspace")))
            buttons += [self.button((50, 630, 150, 48), "Voltar", "puzzle_back"),
                        self.button((220, 630, 145, 48), "Limpar", "clear"),
                        self.button((390, 630, 145, 48), "Dossie", "dossier"),
                        self.button((550, 630, 155, 48), "Ver resposta" if self.hint_level() >= 2 else "Dica", "hint"),
                        self.button((715, 630, 165, 48), "Confirmar", "submit")]
        elif view == "report":
            buttons = [self.button((510, 630, 250, 48), "Ranking", "ranking"),
                       self.button((790, 630, 270, 48), "Voltar ao menu", "menu")]
        return buttons

    def page_buttons(self, length, size):
        return [self.button((900, 630, 60, 48), "<", "previous", self.data["page"] > 0),
                self.button((980, 630, 60, 48), ">", "next", (self.data["page"] + 1) * size < length)]

    def activate(self, value):
        d = self.data
        if isinstance(value, tuple):
            action, key = value
            if action == "object":
                self.interact(key)
            elif action == "walk":
                if key in self.visual.neighbours():
                    self.travel(key)
            elif action == "talk":
                if key == d["room"] and key in COMPANIONS:
                    self.note(COMPANIONS[key], CONVERSATIONS[key])
            elif action == "digit":
                if d["view"] == "puzzle" and PUZZLES[d["puzzle"]]["kind"] == "code":
                    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE if key == "backspace" else ord(key), unicode="" if key == "backspace" else key)
                    self.handle_event(event)
            elif action == "use_key":
                if key in d["inventory"] and d["room"] == "archive":
                    d["selected_items"] = [key]
                    self.interact("drawer")
                    if key != "key417":
                        self.data["selected_items"] = []
                        if self.data["note_title"] == "Escolher chave":
                            self.data["note_text"] = "Esta chave nao serve. Tente outra, sem perder progresso. A etiqueta da tampa indica 417."
            elif action == "room":
                self.travel(key)
            elif action == "phase":
                d.update(map_phase=key, page=0)
            elif action == "item":
                if key in d["selected_items"]:
                    d["selected_items"].remove(key)
                elif len(d["selected_items"]) < 2:
                    d["selected_items"].append(key)
                if d["view"] == "explore":
                    self.game.set_message(ITEMS[key][1], 10)
            elif action == "consult":
                self.help(key)
            elif action == "answer":
                kind = PUZZLES[d["puzzle"]]["kind"]
                if kind in {"order", "set"}:
                    if key in d["answers"]:
                        d["answers"].remove(key)
                    else:
                        d["answers"].append(key)
                else:
                    d.update(choice=key, page=0)
            elif action == "proof":
                if key in d["proofs"]:
                    d["proofs"].remove(key)
                elif len(d["proofs"]) < 3:
                    d["proofs"].append(key)
            elif action == "grid":
                options = [k for k, _ in PUZZLES[d["puzzle"]]["options"]]
                current = d["answers"][key]
                d["answers"][key] = options[(options.index(current) + 1) % len(options)] if current else options[0]
            elif action == "field":
                d["input_field"] = key
            return
        if value == "world_hint":
            self.note("Pista para continuar", self.step_label())
        elif value in {"inventory", "map", "help"}:
            d.update(view=value, page=0)
            if value == "map":
                d["map_phase"] = min(d["chapter"], 6)
        elif value == "back":
            d.update(view="explore", page=0)
        elif value == "puzzle_back":
            d.update(view="explore", puzzle="", answers=[], choice="", proofs=[], input="", page=0)
        elif value == "help_back":
            d["view"] = "puzzle" if d["puzzle"] else "explore"
        elif value == "note_back":
            d.update(view=d["note_return"], page=0)
        elif value == "previous":
            d["page"] = max(0, d["page"] - 1)
        elif value == "next":
            d["page"] += 1
        elif value == "dossier":
            self.game.show_clues = True
            self.game.clue_page = 0
        elif value == "objective":
            self.note("Objetivo", OBJECTIVES[d["chapter"]])
        elif value == "combine":
            previous_view = d["view"]
            self.combine()
            if previous_view == "explore":
                self.data["note_return"] = "explore"
        elif value == "clear":
            d.update(input="", input_field=0, choice="", proofs=[], page=0, answers=[""] * len(GRID_ROWS[d["puzzle"]]) if d["puzzle"] in GRID_ROWS else [])
        elif value == "submit":
            self.solve()
        elif value == "hint":
            self.show_hint()
        elif value == "unsupported":
            d["best_blocked"] = True
            self.penalize("O video nao identifica Lorelai. A atribuicao sem prova comprometeu a melhor avaliacao.")
        elif value == "dialogue_next":
            lines = DIALOGUES[d["dialogue"]]
            d["line"] += 1
            if d["line"] == len(lines):
                d["view"] = "report" if d["dialogue"] == "epilogue" else "explore"
                if d["dialogue"] != "epilogue":
                    self.game.player.rect.topleft = (1010, 510)
                    self.checkpoint()
                else:
                    self.game.player_screens.finish()
        elif value == "menu":
            self.game.reset_to_menu()
        elif value == "ranking":
            self.game.player_screens.show_ranking()

    def handle_event(self, event):
        d = self.data
        if event.type == pygame.KEYDOWN:
            if d["view"] == "dialogue" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.activate("dialogue_next")
                return
            if d["view"] == "puzzle":
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.solve()
                elif d["puzzle"] == "final_code":
                    fields = (d["input"].split(" ") + ["", "", ""])[:3]
                    index = d["input_field"]
                    char = getattr(event, "unicode", "")
                    if event.key == pygame.K_BACKSPACE:
                        if not fields[index] and index > 0:
                            index -= 1
                        fields[index] = fields[index][:-1]
                    elif char == " " and fields[index]:
                        index = min(2, index + 1)
                    elif len(char) == 1 and char in "0123456789":
                        limit = 4 if index == 0 else 2
                        if len(fields[index]) < limit:
                            fields[index] += char
                            if len(fields[index]) == limit:
                                index = min(2, index + 1)
                    d.update(input=" ".join(fields), input_field=index)
                elif event.key == pygame.K_BACKSPACE:
                    d["input"] = d["input"][:-1]
                elif PUZZLES[d["puzzle"]]["kind"] == "code":
                    char = getattr(event, "unicode", "")
                    if len(char) == 1 and char in "0123456789 :" and len(d["input"]) < 40:
                        d["input"] += char
            elif d["view"] == "explore":
                if event.key in (pygame.K_i, pygame.K_m, pygame.K_q):
                    self.activate({pygame.K_i: "inventory", pygame.K_m: "map", pygame.K_q: "help"}[event.key])
                elif event.key == pygame.K_e:
                    nearby = sorted([b for b in self.buttons() if isinstance(b.value, tuple) and b.value[0] == "object"], key=lambda b: pygame.Vector2(b.rect.midbottom).distance_to(self.game.player.rect.center))
                    if nearby and pygame.Vector2(nearby[0].rect.midbottom).distance_to(self.game.player.rect.center) < 180:
                        self.activate(nearby[0].value)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and d["view"] == "note":
                if (d["page"] + 1) * 10 < len(self.note_lines()):
                    self.activate("next")
                else:
                    self.activate("note_back")
        for button in self.buttons():
            if button.hit(event):
                self.activate(button.value)
                return

    def update(self, dt):
        self.data["cooldown"] = max(0.0, self.data["cooldown"] - dt)
        if self.data["view"] == "explore":
            self.game.player.update(dt, pygame.key.get_pressed(), pygame.Rect(48, 337, 1034, 204), ())

    def note_lines(self):
        lines = []
        for paragraph in self.data["note_text"].split("\n"):
            lines.extend(wrap_text(paragraph, self.game.fonts.body, 730) or [""])
        return lines

    def draw(self):
        d, g = self.data, self.game
        room = ROOMS[d["room"]]
        background = g.room_image if room["background"] == "escritorio" else g.backgrounds[room["background"]]
        g.screen.blit(background, (0, 0))
        if d["view"] == "dialogue":
            if d["dialogue"] == "opening" and d["line"] < len(BRIEFING):
                self.visual.draw_briefing(*BRIEFING[d["line"]], team=d["line"] == 2)
                return
            if d["dialogue"] == "epilogue" and DIALOGUES["epilogue"][d["line"]][0] == "Continua":
                self.visual.draw_briefing("A investigacao continua", EPILOGUE[-1][1], ending=True)
                return
        draw_band(g.screen, pygame.Rect(0, 0, 1120, 112))
        title = "EPILOGO" if d["chapter"] == 7 else "PROLOGO" if d["chapter"] == 0 else f"FASE {d['chapter']} / 6"
        draw_text(g.screen, title, g.fonts.small, ACCENT_2, pygame.Rect(28, 12, 200, 22))
        draw_text(g.screen, room["title"] if d["view"] == "explore" else CHAPTERS[min(d["chapter"], 6)], g.fonts.h2, TEXT, pygame.Rect(28, 39, 780, 38))
        draw_text(g.screen, f"Pontos {g.investigation.score}", g.fonts.small, TEXT, pygame.Rect(775, 18, 330, 28))
        if d["chapter"] < 7:
            objective = OBJECTIVES[d["chapter"]]
            draw_text(g.screen, objective, g.fonts.small, MUTED, pygame.Rect(28, 80, 1050, 26))
        view = d["view"]
        if view == "explore":
            self.visual.draw_explore()
            return
        elif view == "note":
            self.visual.draw_note()
            return
        elif view == "dialogue":
            speaker, text = DIALOGUES[d["dialogue"]][d["line"]]
            character = {"Daniel Redding": "daniel", "Cassie": "cassie", "Dean": "dean", "Lia": "lia", "Michael": "michael", "Sloane": "sloane"}[speaker]
            g.draw_stage_character(character, 560, 430)
            draw_band(g.screen, pygame.Rect(0, 470, 1120, 250))
            draw_text(g.screen, speaker, g.fonts.h2, ACCENT_2, pygame.Rect(48, 490, 900, 40))
            draw_text(g.screen, text, g.fonts.body, TEXT, pygame.Rect(48, 540, 1020, 84))
        else:
            draw_band(g.screen, pygame.Rect(0, 112, 1120, 608))
            if view == "inventory":
                draw_text(g.screen, "Inventario", g.fonts.h2, TEXT, pygame.Rect(50, 127, 900, 35))
                for i, key in enumerate(d["selected_items"]):
                    draw_text(g.screen, ITEMS[key][0] + ": " + ITEMS[key][1], g.fonts.body, TEXT, pygame.Rect(50, 445 + i * 72, 1000, 66))
            elif view == "map":
                draw_text(g.screen, "Ambientes", g.fonts.h2, TEXT, pygame.Rect(50, 119, 800, 35))
            elif view == "help":
                spent = sum(k.startswith(f"{d['chapter']}:") for k in d["help_used"])
                limit = 0 if d["chapter"] in (0, 4, 6, 7) else 2 if d["chapter"] == 5 else 3
                draw_text(g.screen, f"Consultas da equipe / {max(0, limit - spent)} disponiveis", g.fonts.h2, TEXT, pygame.Rect(50, 150, 1000, 60))
            elif view == "puzzle":
                content = PUZZLES[d["puzzle"]]
                draw_text(g.screen, content["title"], g.fonts.h2, TEXT, pygame.Rect(50, 127, 1000, 35))
                prompt = dict(content["options"])[d["choice"]] if content["kind"] == "proof" and d["choice"] else content["prompt"]
                draw_text(g.screen, prompt, g.fonts.body, TEXT, pygame.Rect(50, 172, 1010, 97))
                if content["kind"] == "code" and d["puzzle"] != "final_code":
                    pygame.draw.rect(g.screen, (36, 54, 52), pygame.Rect(180, 318, 760, 76), border_radius=4)
                    draw_text(g.screen, d["input"] or "_", g.fonts.h1, TEXT, pygame.Rect(205, 334, 710, 52))
                if content["kind"] == "grid":
                    for i, label in enumerate(GRID_ROWS[d["puzzle"]]):
                        draw_text(g.screen, label, g.fonts.body, TEXT, pygame.Rect(60, 280 + i * 56, 390, 42))
                        if d["puzzle"] == "gallery":
                            portrait = g.stage_portraits[label.lower()]
                            g.screen.blit(pygame.transform.smoothscale(portrait, (32, 46)), (415, 270 + i * 56))
                status = g.message
                if content["kind"] == "proof" and d["choice"]:
                    status = status or f"Provas anexadas: {len(d['proofs'])} / {len(content['proofs'])}. Marque as provas e clique em Confirmar."
                status = status or PUZZLE_INSTRUCTIONS[content["kind"]]
                draw_text(g.screen, status, g.fonts.small, MUTED, pygame.Rect(50, 590, 1020, 34))
            elif view == "report":
                rating = "Conclusao sustentada"
                if d["best_blocked"]:
                    rating = "Conclusao com atribuicao indevida"
                elif g.investigation.mistakes <= 2 and {"guest_book", "router", "portrait_notes"}.issubset(d["flags"]):
                    rating = "Investigacao exemplar"
                draw_text(g.screen, rating, g.fonts.h1, GOOD, pygame.Rect(60, 160, 1000, 70))
                draw_text(g.screen, g.player_name or "Partida sem identificacao", g.fonts.small, MUTED, pygame.Rect(60, 220, 1000, 24))
                lines = [f"Pontos: {g.investigation.score}", f"Provas: {len(g.investigation.evidence)}",
                         f"Enigmas: {g.investigation.solved_puzzles}", f"Deducoes: {g.investigation.correct_connections}",
                         f"Erros: {g.investigation.mistakes}", "Cassie saiu da propriedade e reencontrou a equipe.", EVIDENCE_DATA["x_final"][1]]
                for i, line in enumerate(lines[:5]):
                    draw_text(g.screen, line, g.fonts.body, TEXT, pygame.Rect(60, 245 + i * 38, 1000, 32))
                draw_text(g.screen, " ".join(lines[5:]), g.fonts.body, TEXT, pygame.Rect(60, 470, 1000, 138))
                draw_text(g.screen, g.player_screens.result_notice, g.fonts.small, MUTED, pygame.Rect(60, 596, 1000, 28))
        for button in self.buttons():
            if not self.visual.draw_puzzle_button(button):
                button.draw(g.screen, g.fonts, pygame.mouse.get_pos())
