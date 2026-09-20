import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from scripts.cenas import Game
from scripts.dialogos import INTERROGATION_ROUNDS, PROLOGUE_LINES
from scripts.salvamento import SaveStore, snapshot, validate


class SavingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1120, 720))
        cls.root = Path(__file__).resolve().parents[1]

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "saves" / "progresso.json"
        self.game = Game(self.screen, self.root, self.path)
        self.game.start_game(expanded=False)

    def click(self, button):
        self.game.handle_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=button.rect.center, button=1)])

    def test_restart_restores_partial_reconstruction_and_inventory(self):
        game = self.game
        game.state = "profile"
        game.profile_step = "timeline"
        game.profile_selection = [0, 1]
        game.investigation.add_evidence("coded_invitation")
        game.investigation.mark_used("coded_invitation")
        game.investigation.use_ability("lia_0")
        game.investigation.mistakes = 2
        game.player.rect.topleft = (530, 350)
        game.player.facing_left = True
        expected = snapshot(game)
        self.assertTrue(game.save_progress())
        restarted = Game(self.screen, self.root, self.path)
        self.assertEqual(restarted.state, "menu")
        restarted.continue_game()
        self.assertEqual(snapshot(restarted), expected)
        restarted.draw()
        restarted.profile_selection.append(2)
        self.assertEqual(restarted.saved_game["progress"]["profile_selection"], [0, 1])

    def test_feedback_restores_without_rewarding_twice(self):
        game = self.game
        game.state = "interrogation"
        game.investigation.add_evidence("broken_phone")
        self.click(game.interrogation_buttons()[0])
        self.click(game.proof_buttons(INTERROGATION_ROUNDS[0])[0])
        self.click(game.proof_buttons(INTERROGATION_ROUNDS[0])[-1])
        self.assertTrue(self.path.exists())
        score = game.investigation.score
        restarted = Game(self.screen, self.root, self.path)
        restarted.continue_game()
        self.assertTrue(restarted.interrogation_feedback)
        button = restarted.interrogation_buttons()[0]
        restarted.handle_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=button.rect.center, button=1)])
        self.assertEqual(restarted.investigation.score, score)

    def test_partial_proofs_restore_and_old_saves_migrate(self):
        game = self.game
        game.state = "interrogation"
        game.investigation.add_evidence("broken_phone")
        self.click(game.interrogation_buttons()[0])
        self.click(game.proof_buttons(INTERROGATION_ROUNDS[0])[0])
        restarted = Game(self.screen, self.root, self.path)
        restarted.continue_game()
        self.assertEqual(restarted.proof_choice, 0)
        self.assertEqual(restarted.proof_selection, ["broken_phone"])
        restarted.draw()
        old = snapshot(game)
        old["version"] = 1
        for key in ("proof_choice", "proof_selection", "proof_page", "prologue_outro_index", "epilogue_index", "puzzle_input"):
            del old["progress"][key]
        migrated = validate(old)
        self.assertEqual(migrated["version"], 5)
        self.assertEqual(migrated["progress"]["proof_choice"], -1)
        self.assertEqual(migrated["investigation"], old["investigation"])

    def test_uncollected_proof_is_rejected(self):
        data = snapshot(self.game)
        data["progress"].update(state="interrogation", proof_choice=0, proof_selection=["broken_phone"])
        with self.assertRaises(ValueError):
            validate(data)

    def test_narrative_and_code_progress_round_trip(self):
        for state, field, value in (("prologue", "prologue_outro_index", 2),
                                    ("epilogue", "epilogue_index", 3),
                                    ("puzzle", "puzzle_input", "29")):
            with self.subTest(state=state):
                self.game.start_game(expanded=False)
                self.game.state = state
                setattr(self.game, field, value)
                self.assertTrue(self.game.save_progress())
                restarted = Game(self.screen, self.root, self.path)
                restarted.continue_game()
                self.assertEqual(getattr(restarted, field), value)
                restarted.draw()

    def test_version_two_at_old_prologue_choice_migrates(self):
        old = snapshot(self.game)
        old["version"] = 2
        old["progress"]["dialogue_index"] = 3
        for key in ("prologue_outro_index", "epilogue_index", "puzzle_input"):
            del old["progress"][key]
        migrated = validate(old)
        self.assertEqual(migrated["progress"]["dialogue_index"], len(PROLOGUE_LINES))
        self.assertEqual(migrated["progress"]["prologue_outro_index"], -1)

    def test_exploration_and_quit_flush_position(self):
        game = self.game
        game.state = "finale"
        game.player.rect.topleft = (600, 550)
        game.update(5)
        self.assertEqual(SaveStore(self.path).load()["position"], [600, 550])
        game.player.rect.topleft = (640, 565)
        game.request_quit()
        self.assertFalse(game.running)
        self.assertEqual(SaveStore(self.path).load()["position"], [640, 565])

    def test_new_game_requires_confirmation_and_cancel_keeps_progress(self):
        game = self.game
        game.state = "phase1"
        game.investigation.add_evidence("broken_phone")
        game.reset_to_menu()
        previous = self.path.read_bytes()
        self.click(next(button for button in game.menu_buttons() if button.value == "new"))
        self.assertTrue(game.confirm_new)
        self.click(game.new_game_buttons()[0])
        self.assertEqual(self.path.read_bytes(), previous)
        self.click(next(button for button in game.menu_buttons() if button.value == "new"))
        self.click(game.new_game_buttons()[1])
        self.assertEqual(game.player_screens.active, "name")
        self.assertEqual(self.path.read_bytes(), previous)
        game.player_screens.name = "Teste"
        game.player_screens.accept_name()
        self.assertEqual(game.state, "campaign")
        self.assertEqual(SaveStore(self.path).load()["investigation"]["evidence"], {})

    def test_bad_file_is_not_modified_when_opening_menu(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{broken", encoding="utf-8")
        game = Game(self.screen, self.root, self.path)
        self.assertIsNone(game.saved_game)
        self.assertTrue(game.save_notice)
        game.draw()
        game.request_quit()
        self.assertEqual(self.path.read_text(encoding="utf-8"), "{broken")

    def test_invalid_active_round_is_rejected(self):
        data = snapshot(self.game)
        data["progress"]["state"] = "puzzle"
        data["progress"]["puzzle_step"] = 3
        with self.assertRaises(ValueError):
            validate(data)
        data = snapshot(self.game)
        data["investigation"]["evidence"] = {"unknown": True}
        with self.assertRaises(ValueError):
            validate(data)

    def test_failed_atomic_replace_preserves_last_save_and_keeps_game_open(self):
        game = self.game
        game.save_progress()
        previous = self.path.read_bytes()
        game.dialogue_index = 1
        with patch("scripts.salvamento.os.replace", side_effect=PermissionError("locked")):
            game.request_quit()
            self.assertTrue(game.running)
            self.assertTrue(game.paused)
            self.assertTrue(game.save_notice)
            game.reset_to_menu()
            self.assertEqual(game.state, "prologue")
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertFalse(self.path.with_suffix(".json.tmp").exists())
        self.assertTrue(game.save_progress())
        self.assertEqual(SaveStore(self.path).load()["progress"]["dialogue_index"], 1)

    def test_every_playable_stage_round_trips(self):
        for state in ("prologue", "phase1", "interrogation", "puzzle", "profile", "finale", "epilogue"):
            with self.subTest(state=state):
                self.game.start_game()
                self.game.state = state
                self.assertTrue(self.game.save_progress())
                loaded = SaveStore(self.path).load()
                self.assertEqual(loaded, snapshot(self.game))
                self.game.saved_game = loaded
                self.game.continue_game()
                self.game.draw()


if __name__ == "__main__":
    unittest.main()
