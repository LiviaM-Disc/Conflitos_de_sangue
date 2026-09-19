from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path

from scripts.dialogos import FINAL_ROUNDS, INTERROGATION_ROUNDS, PUZZLE_ROUNDS, PROLOGUE_LINES, PROFILE_EVIDENCES, PROLOGUE_OUTRO, EPILOGUE_LINES
from scripts.pistas import EVIDENCES


STAGES = {
    "prologue": "Prologo", "phase1": "O escritorio de Celine",
    "interrogation": "Interrogatorio", "puzzle": "O convite cifrado",
    "profile": "Reconstrucao", "finale": "O salao dos Masters", "epilogue": "Resultado do caso",
}
PROGRESS_FIELDS = (
    "state", "dialogue_index", "puzzle_step", "profile_selection", "profile_order",
    "final_feedback", "interrogation_feedback", "phase5_hint_used", "interrogation_round",
    "interrogation_insight", "profile_step", "evidence_selection", "final_mode",
    "final_round", "final_round_feedback", "message", "proof_choice", "proof_selection", "proof_page",
    "prologue_outro_index", "epilogue_index", "puzzle_input",
)


def snapshot(game) -> dict:
    investigation = asdict(game.investigation)
    investigation["used_abilities"] = sorted(game.investigation.used_abilities)
    # Copy the selection lists: later clicks must not change the last saved snapshot.
    progress = {key: list(value) if isinstance(value := getattr(game, key), list) else value
                for key in PROGRESS_FIELDS}
    return {"version": 3, "progress": progress, "investigation": investigation,
            "position": list(game.player.rect.topleft), "facing_left": game.player.facing_left}


def validate(data: object) -> dict:
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] not in (1, 2, 3):
        raise ValueError("Versao de salvamento nao suportada")
    if data["version"] == 1 and isinstance(data.get("progress"), dict):
        data = {**data, "version": 2, "progress": {**data["progress"],
                "proof_choice": -1, "proof_selection": [], "proof_page": 0}}
    if data["version"] == 2 and isinstance(data.get("progress"), dict):
        progress = {**data["progress"], "prologue_outro_index": -1, "epilogue_index": 0, "puzzle_input": ""}
        # Preserve old completed Redding dialogue, without replaying its rewards.
        if progress.get("dialogue_index") == 3:
            progress["dialogue_index"] = len(PROLOGUE_LINES)
        elif type(progress.get("dialogue_index")) is int and progress.get("state") == "prologue":
            progress["dialogue_index"] += 2
        data = {**data, "version": 3, "progress": progress}
    p, inv = data.get("progress"), data.get("investigation")
    if not isinstance(p, dict) or not isinstance(inv, dict) or set(p) != set(PROGRESS_FIELDS):
        raise ValueError("Progresso incompleto")
    if not isinstance(p["state"], str) or p["state"] not in STAGES:
        raise ValueError("Fase desconhecida")
    if type(p["prologue_outro_index"]) is not int or not -1 <= p["prologue_outro_index"] <= len(PROLOGUE_OUTRO):
        raise ValueError("Abertura invalida")
    if p["state"] == "prologue" and p["prologue_outro_index"] == len(PROLOGUE_OUTRO):
        raise ValueError("Abertura concluida")
    if type(p["epilogue_index"]) is not int or not 0 <= p["epilogue_index"] <= len(EPILOGUE_LINES):
        raise ValueError("Epilogo invalido")
    if not isinstance(p["puzzle_input"], str) or len(p["puzzle_input"]) > 6 or any(c not in "0123456789" for c in p["puzzle_input"]):
        raise ValueError("Codigo invalido")
    limits = {"dialogue_index": len(PROLOGUE_LINES), "puzzle_step": len(PUZZLE_ROUNDS),
              "interrogation_round": len(INTERROGATION_ROUNDS), "final_round": len(FINAL_ROUNDS)}
    for key, maximum in limits.items():
        if type(p[key]) is not int or not 0 <= p[key] <= maximum:
            raise ValueError("Etapa invalida")
    for stage, key in (("interrogation", "interrogation_round"), ("puzzle", "puzzle_step"), ("finale", "final_round")):
        if p["state"] == stage and p[key] >= limits[key]:
            raise ValueError("Etapa fora da fase")
    for key, allowed, maximum in (("profile_selection", range(4), 4), ("profile_order", range(4), 4),
                                   ("evidence_selection", PROFILE_EVIDENCES, 2)):
        value = p[key]
        if not isinstance(value, list) or len(value) > maximum:
            raise ValueError("Selecao invalida")
        expected_type = str if key == "evidence_selection" else int
        if any(type(item) is not expected_type or item not in allowed for item in value) or len(set(value)) != len(value):
            raise ValueError("Selecao invalida")
    if len(p["profile_order"]) != 4 or p["profile_step"] not in ("evidence", "timeline") or p["final_mode"] not in ("explore", "deduce"):
        raise ValueError("Modo invalido")
    if type(p["phase5_hint_used"]) is not bool or type(data.get("facing_left")) is not bool:
        raise ValueError("Indicador invalido")
    for key in ("final_feedback", "interrogation_feedback", "interrogation_insight", "final_round_feedback", "message"):
        if not isinstance(p[key], str) or len(p[key]) > 4000:
            raise ValueError("Texto invalido")
    counters = ("score", "solved_puzzles", "lies_found", "correct_connections", "mistakes")
    if set(inv) != {*counters, "evidence", "used_abilities"}:
        raise ValueError("Investigacao incompleta")
    for key in counters:
        if type(inv[key]) is not int or not -1000000 <= inv[key] <= 1000000 or (key != "score" and inv[key] < 0):
            raise ValueError("Pontuacao invalida")
    if not isinstance(inv["evidence"], dict) or any(key not in EVIDENCES or type(value) is not bool for key, value in inv["evidence"].items()):
        raise ValueError("Evidencia invalida")
    if type(p["proof_choice"]) is not int or not -1 <= p["proof_choice"] < 3:
        raise ValueError("Hipotese invalida")
    if type(p["proof_page"]) is not int or not 0 <= p["proof_page"] <= max(0, (len(inv["evidence"]) - 1) // 6):
        raise ValueError("Pagina de provas invalida")
    proofs = p["proof_selection"]
    if (not isinstance(proofs, list) or len(proofs) > 3
            or any(type(key) is not str or key not in inv["evidence"] for key in proofs)
            or len(set(proofs)) != len(proofs)):
        raise ValueError("Provas invalidas")
    if p["proof_choice"] >= 0:
        if p["state"] == "interrogation" and not p["interrogation_feedback"]:
            topic = INTERROGATION_ROUNDS[p["interrogation_round"]]
        elif p["state"] == "finale" and p["final_mode"] == "deduce" and not p["final_round_feedback"]:
            topic = FINAL_ROUNDS[p["final_round"]]
        else:
            raise ValueError("Confronto fora da fase")
    elif proofs or p["proof_page"]:
        raise ValueError("Confronto inativo")
    abilities = inv["used_abilities"]
    if not isinstance(abilities, list) or len(abilities) > 100 or any(not isinstance(key, str) or len(key) > 100 for key in abilities):
        raise ValueError("Habilidade invalida")
    pos = data.get("position")
    if not isinstance(pos, list) or len(pos) != 2 or any(type(n) is not int for n in pos) or not (48 <= pos[0] <= 1048 and 337 <= pos[1] <= 630):
        raise ValueError("Posicao invalida")
    return data


class SaveStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> dict | None:
        if not self.path.exists():
            return None
        if self.path.stat().st_size > 1000000:
            raise ValueError("Arquivo de salvamento muito grande")
        return validate(json.loads(self.path.read_text(encoding="utf-8")))

    def write(self, data: dict) -> None:
        validate(data)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            with temporary.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=True, indent=2, allow_nan=False)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()
