import os
from pathlib import Path
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from scripts.cenas import Game
from scripts.dialogos import FINAL_ROUNDS, PROLOGUE_LINES, PROLOGUE_OUTRO, EPILOGUE_LINES, PROFILE_PAIR, INTERROGATION_ROUNDS, PUZZLE_ROUNDS
from scripts.pistas import EVIDENCES
from scripts.interfaces import wrap_text


class GameFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1120, 720))
        cls.game = Game(cls.screen, Path(__file__).resolve().parents[1])

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.game.start_game()

    def click(self, button):
        self.game.handle_events([pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=button.rect.center)])

    def key(self, key):
        self.game.handle_events([pygame.event.Event(pygame.KEYDOWN, key=key)])

    def enter_code(self, answer):
        for char in str(answer):
            self.game.handle_events([pygame.event.Event(pygame.KEYDOWN, key=ord(char), unicode=char)])
        self.key(pygame.K_RETURN)

    def present_proofs(self, topic, proofs=None):
        for key in topic["uses"] if proofs is None else proofs:
            self.game.proof_page = list(self.game.investigation.evidence).index(key) // 6
            self.click(next(b for b in self.game.proof_buttons(topic) if b.value == key))
        self.game.draw()
        self.click(self.game.proof_buttons(topic)[-1])

    def test_complete_investigation_with_real_controls(self):
        game = self.game
        for _ in PROLOGUE_LINES:
            self.click(game.dialogue_continue_button())
        self.click(game.prologue_choice_buttons()[0])
        self.assertEqual(game.state, "prologue")
        for _ in PROLOGUE_OUTRO:
            self.click(game.dialogue_continue_button())
        self.assertEqual(game.state, "phase1")
        for pos in [(95, 540), (995, 420), (535, 390), (163, 350), (860, 350)]:
            game.player.rect.topleft = pos
            self.assertFalse(any(game.player.rect.colliderect(rect) for rect in game.obstacles))
            self.key(pygame.K_e)
        self.assertEqual(len(game.investigation.evidence), 6)
        self.key(pygame.K_RETURN)
        self.assertEqual(game.state, "interrogation")
        for _ in INTERROGATION_ROUNDS:
            self.click(game.interrogation_ability_buttons()[0])
            self.click(game.interrogation_ability_buttons()[1])
            self.click(next(b for b in game.interrogation_buttons() if b.value[1]))
            self.present_proofs(INTERROGATION_ROUNDS[game.interrogation_round])
            self.assertEqual(game.state, "interrogation")
            self.assertTrue(game.interrogation_feedback)
            score = game.investigation.score
            self.click(game.interrogation_buttons()[0])
            self.assertEqual(game.investigation.score, score)
            self.click(game.interrogation_continue_button())
        self.assertEqual(game.state, "puzzle")
        for puzzle in PUZZLE_ROUNDS:
            self.enter_code(puzzle["answer"])
        self.assertEqual(game.state, "profile")
        for evidence_id in PROFILE_PAIR:
            self.click(next(b for b in game.profile_buttons() if b.value == evidence_id))
        self.click(game.profile_buttons()[-1])
        self.assertEqual(game.profile_step, "timeline")
        for index in range(4):
            self.click(next(b for b in game.profile_buttons() if b.value == index))
        self.click(game.profile_buttons()[-1])
        self.assertEqual(game.state, "finale")
        self.assertEqual(game.final_mode, "explore")
        self.key(pygame.K_RETURN)
        self.assertEqual(game.final_mode, "explore")
        for pos in [(530, 350), (1010, 365), (540, 540)]:
            game.player.rect.topleft = pos
            self.key(pygame.K_e)
        self.key(pygame.K_RETURN)
        self.assertEqual(game.final_mode, "deduce")
        self.key(pygame.K_q)
        for _ in range(2):
            self.click(next(b for b in game.final_buttons() if b.value[1]))
            self.present_proofs(FINAL_ROUNDS[game.final_round])
            self.assertTrue(game.final_round_feedback)
            self.click(game.final_continue_button())
        self.assertEqual(game.state, "epilogue")
        self.assertTrue(game.investigation.has("final_deduction"))
        self.assertEqual(game.investigation.mistakes, 0)
        self.assertEqual(game.investigation.solved_puzzles, 3)
        self.assertEqual(game.investigation.lies_found, 3)
        self.assertEqual(game.investigation.correct_connections, 4)
        self.assertTrue(game.investigation.evidence["coded_invitation"])
        self.assertEqual(game.investigation.final_rating(), "Investigacao exemplar")
        game.draw()
        for _ in EPILOGUE_LINES:
            self.click(game.dialogue_continue_button())
        self.click(game.epilogue_buttons()[0])
        self.click(game.menu_buttons()[0])
        self.assertEqual(game.state, "prologue")
        self.assertEqual(game.investigation.score, 0)
        self.assertEqual(game.interrogation_round, 0)
        self.assertEqual(game.final_round, 0)
        self.assertEqual(game.profile_step, "evidence")

    def test_failed_answers_can_be_recovered(self):
        game = self.game
        game.state = "interrogation"
        game.investigation.add_evidence("broken_phone")
        self.click(game.interrogation_buttons()[1])
        self.present_proofs(INTERROGATION_ROUNDS[0])
        self.assertEqual(game.investigation.mistakes, 1)
        self.click(game.interrogation_continue_button())
        self.assertEqual(game.interrogation_round, 1)
        game.state = "puzzle"
        self.enter_code(18)
        self.assertEqual(game.puzzle_step, 0)
        self.assertEqual(game.investigation.mistakes, 2)
        for puzzle in PUZZLE_ROUNDS:
            self.enter_code(puzzle["answer"])
        self.assertEqual(game.state, "profile")
        for evidence_id in ("broken_phone", "coded_invitation", "celine_bracelet"):
            game.investigation.add_evidence(evidence_id)
        self.click(game.profile_buttons()[0])
        self.click(game.profile_buttons()[2])
        self.click(game.profile_buttons()[-1])
        self.assertEqual(game.evidence_selection, [])
        self.assertEqual(game.profile_step, "evidence")
        for evidence_id in PROFILE_PAIR:
            self.click(next(b for b in game.profile_buttons() if b.value == evidence_id))
        self.click(game.profile_buttons()[-1])
        for index in (3, 2, 1, 0):
            self.click(next(b for b in game.profile_buttons() if b.value == index))
        self.click(game.profile_buttons()[-1])
        self.assertEqual(game.profile_selection, [])
        self.assertEqual(game.state, "profile")
        self.assertEqual(game.investigation.mistakes, 4)

    def test_all_evidence_pages_and_close_in_epilogue(self):
        game = self.game
        for evidence_id in EVIDENCES:
            game.investigation.add_evidence(evidence_id)
        game.state = "epilogue"
        self.key(pygame.K_TAB)
        last_page = (len(EVIDENCES) - 1) // 4
        for _ in range(last_page):
            self.click(game.clue_buttons()[-1])
        self.assertEqual(game.clue_page, last_page)
        self.assertFalse(game.clue_buttons()[-1].enabled)
        self.assertIn("hall_pattern", [e.id for e in game.investigation.discovered()[last_page * 4:]])
        game.draw()
        self.game.handle_events([pygame.event.Event(pygame.MOUSEWHEEL, y=1)])
        self.assertEqual(game.clue_page, last_page - 1)
        self.key(pygame.K_ESCAPE)
        self.assertFalse(game.show_clues)
        self.assertFalse(game.paused)

    def test_overlay_preserves_message_time_and_blocks_choices(self):
        game = self.game
        game.state = "puzzle"
        game.set_message("Registro encontrado", 4.5)
        self.key(pygame.K_TAB)
        self.enter_code(21)
        game.update(10)
        self.assertEqual(game.puzzle_step, 0)
        self.assertEqual(game.message_timer, 4.5)
        self.key(pygame.K_ESCAPE)
        self.key(pygame.K_ESCAPE)
        game.update(10)
        self.assertEqual(game.message_timer, 4.5)
        self.key(pygame.K_ESCAPE)
        game.update(1)
        self.assertEqual(game.message_timer, 3.5)

    def test_repeated_abilities_do_not_farm_points(self):
        game = self.game
        game.state = "interrogation"
        for button in game.interrogation_ability_buttons():
            self.click(button)
            score = game.investigation.score
            self.click(button)
            self.assertEqual(game.investigation.score, score)
        game.state = "puzzle"
        self.click(game.puzzle_hint_button())
        score = game.investigation.score
        self.key(pygame.K_q)
        self.assertEqual(game.investigation.score, score)

    def test_final_errors_keep_narrative_but_reduce_performance(self):
        game = self.game
        game.state = "finale"
        game.final_mode = "deduce"
        for key in EVIDENCES:
            game.investigation.add_evidence(key)
        del game.investigation.evidence["final_deduction"]
        for _ in range(2):
            self.click(next(b for b in game.final_buttons() if not b.value[1]))
            self.present_proofs(FINAL_ROUNDS[game.final_round])
            self.assertFalse(game.final_round_feedback)
            self.assertEqual(game.state, "finale")
            self.assertFalse(game.investigation.has("final_deduction"))
            self.click(next(b for b in game.final_buttons() if b.value[1]))
            self.present_proofs(FINAL_ROUNDS[game.final_round])
            self.click(game.final_continue_button())
        self.assertEqual(game.state, "epilogue")
        self.assertEqual(game.investigation.mistakes, 2)
        self.assertTrue(game.investigation.has("final_deduction"))
        self.assertIn("Celine foi usada como isca", game.final_feedback)

    def test_correct_hypothesis_with_wrong_proof_is_not_rewarded(self):
        game = self.game
        game.state = "interrogation"
        for key in ("broken_phone", "celine_bracelet"):
            game.investigation.add_evidence(key)
        self.click(game.interrogation_buttons()[0])
        self.assertFalse(game.proof_buttons(INTERROGATION_ROUNDS[0])[-1].enabled)
        self.click(game.proof_buttons(INTERROGATION_ROUNDS[0])[-1])
        self.assertFalse(game.interrogation_feedback)
        self.present_proofs(INTERROGATION_ROUNDS[0], ["celine_bracelet"])
        self.assertEqual(game.investigation.mistakes, 1)
        self.assertEqual(game.investigation.lies_found, 0)
        self.assertFalse(game.investigation.has("lia_lie"))
        self.assertIn("Hipotese correta", game.interrogation_feedback)

    def test_proof_pagination_revision_and_selection_limit(self):
        game = self.game
        game.state = "finale"
        game.final_mode = "deduce"
        for key in EVIDENCES:
            game.investigation.add_evidence(key)
        topic = FINAL_ROUNDS[0]
        self.click(game.final_buttons()[1])
        self.click(game.proof_buttons(topic)[0])
        self.click(game.proof_buttons(topic)[1])
        self.assertTrue(game.proof_buttons(topic)[2].enabled)
        self.click(game.proof_buttons(topic)[2])
        self.assertFalse(game.proof_buttons(topic)[3].enabled)
        self.click(game.proof_buttons(topic)[-2])
        self.assertEqual(game.proof_page, 1)
        self.assertEqual(len(game.proof_selection), 3)
        self.key(pygame.K_TAB)
        self.click(game.proof_buttons(topic)[-4])
        self.assertEqual(game.proof_choice, 1)
        self.key(pygame.K_ESCAPE)
        self.click(game.proof_buttons(topic)[-4])
        self.assertEqual(game.proof_choice, -1)
        self.assertEqual(game.proof_selection, [])
        self.assertEqual(game.proof_page, 0)
        self.assertEqual(game.investigation.mistakes, 0)

    def test_final_correct_hypothesis_requires_complete_relevant_proofs(self):
        game = self.game
        game.state = "finale"
        game.final_mode = "deduce"
        game.final_round = 1
        for key in ("hall_pattern", "lorelai_note", "fibonacci_key", "celine_bracelet"):
            game.investigation.add_evidence(key)
        self.click(game.final_buttons()[0])
        self.present_proofs(FINAL_ROUNDS[1], ["hall_pattern", "lorelai_note", "celine_bracelet"])
        self.assertEqual(game.investigation.correct_connections, 0)
        self.assertFalse(game.investigation.has("final_deduction"))
        self.assertEqual(game.investigation.mistakes, 1)
        self.assertFalse(game.investigation.evidence["hall_pattern"])

    def test_narrative_scenes_fit_and_cannot_skip_to_report(self):
        game = self.game
        for speaker, text in PROLOGUE_LINES + PROLOGUE_OUTRO + EPILOGUE_LINES:
            lines = wrap_text(text, game.fonts.body, 1024)
            self.assertLessEqual(len(lines) * (game.fonts.body.get_height() + 5) - 5, 84)
        game.dialogue_index = len(PROLOGUE_LINES)
        self.click(game.prologue_choice_buttons()[1])
        self.assertEqual(game.prologue_outro_index, 0)
        score = game.investigation.score
        self.click(game.prologue_choice_buttons()[1])
        self.assertEqual(game.investigation.score, score)
        for index in range(len(PROLOGUE_OUTRO)):
            self.assertEqual(game.prologue_outro_index, index)
            game.draw()
            self.key(pygame.K_RETURN)
        self.assertEqual(game.state, "phase1")
        game.state = "epilogue"
        self.click(game.epilogue_buttons()[0])
        self.assertEqual(game.epilogue_index, 0)
        for index in range(len(EPILOGUE_LINES)):
            game.draw()
            self.assertEqual(game.epilogue_index, index)
            self.key(pygame.K_SPACE)
        self.assertEqual(game.state, "epilogue")
        game.draw()
        self.key(pygame.K_RETURN)
        self.assertEqual(game.state, "menu")

    def test_numeric_input_edit_limit_and_empty_submission(self):
        game = self.game
        game.state = "puzzle"
        self.key(pygame.K_RETURN)
        self.assertEqual(game.investigation.mistakes, 0)
        for char in "a1234567":
            game.handle_events([pygame.event.Event(pygame.KEYDOWN, key=ord(char), unicode=char)])
        self.assertEqual(game.puzzle_input, "123456")
        self.key(pygame.K_BACKSPACE)
        self.assertEqual(game.puzzle_input, "12345")
        self.key(pygame.K_RETURN)
        self.assertEqual(game.investigation.mistakes, 1)
        self.assertEqual(game.puzzle_input, "")
        self.enter_code(21)
        self.assertEqual(game.puzzle_step, 1)


if __name__ == "__main__":
    unittest.main()
