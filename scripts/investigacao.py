from __future__ import annotations

from dataclasses import dataclass, field

from scripts.pistas import EVIDENCES, PHASE1_REQUIRED, Evidence


@dataclass
class InvestigationState:
    score: int = 0
    evidence: dict[str, bool] = field(default_factory=dict)
    used_abilities: set[str] = field(default_factory=set)
    solved_puzzles: int = 0
    lies_found: int = 0
    correct_connections: int = 0
    mistakes: int = 0

    def add_evidence(self, evidence_id: str) -> tuple[bool, Evidence]:
        evidence = EVIDENCES[evidence_id]
        is_new = evidence_id not in self.evidence
        if is_new:
            self.evidence[evidence_id] = False
            self.score += evidence.points
        return is_new, evidence

    def mark_used(self, evidence_id: str) -> None:
        if evidence_id in self.evidence:
            self.evidence[evidence_id] = True

    def has(self, evidence_id: str) -> bool:
        return evidence_id in self.evidence

    def has_all_phase1_required(self) -> bool:
        return PHASE1_REQUIRED.issubset(self.evidence.keys())

    def use_ability(self, key: str) -> bool:
        if key in self.used_abilities:
            return False
        self.used_abilities.add(key)
        self.score += 10
        return True

    def register_lie(self, correct: bool, evidence_id: str = "lia_lie") -> None:
        if correct:
            self.lies_found += 1
            self.score += 15
            self.add_evidence(evidence_id)
        else:
            self.mistakes += 1
            self.score -= 20

    def register_emotion_read(self) -> None:
        if "michael_emotion" not in self.evidence:
            self.score += 10
            self.evidence["michael_emotion"] = False

    def register_puzzle(self, correct: bool) -> None:
        if correct:
            self.solved_puzzles += 1
            self.score += 20
        else:
            self.mistakes += 1
            self.score -= 10

    def register_connection(self, correct: bool) -> None:
        if correct:
            self.correct_connections += 1
            self.score += 20
        else:
            self.mistakes += 1
            self.score -= 20

    def discovered(self) -> list[Evidence]:
        return [EVIDENCES[key] for key in self.evidence]

    def final_rating(self) -> str:
        if self.score >= 300 and self.mistakes <= 1 and self.correct_connections >= 4 and self.lies_found == 3:
            return "Investigacao exemplar"
        if self.score >= 220:
            return "Investigacao solida"
        if self.score >= 120:
            return "Investigacao incompleta"
        return "Muitas pontas soltas"
