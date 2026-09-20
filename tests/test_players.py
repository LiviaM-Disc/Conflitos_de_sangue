import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock
import pygame
from scripts.cenas import Game
from scripts.salvamento import snapshot, validate, SaveStore
from scripts.roteiro_expandido import EPILOGUE


class PlayerFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1120, 720))
        cls.root = Path(__file__).resolve().parents[1]

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "save.json"
        self.store = Mock()
        self.store.player.return_value.nickname = "Ana"
        self.store.standings.return_value = []
        self.g = Game(self.screen, self.root, self.path, ranking_store=self.store)

    def test_name_required_new_game_and_saved_identity(self):
        self.g.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="")])
        self.assertEqual(self.g.player_screens.active, "name")
        self.g.player_screens.accept_name()
        self.assertEqual(self.g.state, "menu")
        self.g.player_screens.name = "Ana"
        self.g.player_screens.accept_name()
        saved = SaveStore(self.path).load()
        self.assertEqual(saved["progress"]["player_name"], "Ana")
        resumed = Game(self.screen, self.root, self.path, ranking_store=self.store)
        resumed.continue_game()
        self.assertEqual(resumed.run_id, self.g.run_id)
        self.assertEqual(resumed.player_name, "Ana")

    def test_completed_result_is_saved_once_and_retry_after_failure(self):
        self.g.start_game(player_name="Ana")
        self.g.campaign_data.update(chapter=7, room="final_chamber", dialogue="epilogue", line=len(EPILOGUE)-1, view="dialogue")
        self.g.investigation.score = 150
        self.store.record.side_effect = OSError("database locked")
        self.g.campaign.activate("dialogue_next")
        self.assertFalse(self.g.result_saved)
        self.assertIn("pendente", self.g.player_screens.result_notice)
        self.store.record.side_effect = None
        self.g.player_screens.show_ranking()
        self.assertTrue(self.g.result_saved)
        self.assertEqual(self.store.record.call_count, 2)
        self.g.player_screens.show_ranking()
        self.assertEqual(self.store.record.call_count, 2)

    def test_version_four_is_preserved_but_not_ranked(self):
        self.g.start_game(player_name="Ana")
        data = snapshot(self.g)
        data["version"] = 4
        for key in ("player_name", "run_id", "ranking_eligible", "result_saved"):
            data["progress"].pop(key)
        migrated = validate(data)
        self.assertFalse(migrated["progress"]["ranking_eligible"])
        self.assertEqual(migrated["investigation"], data["investigation"])
        self.assertEqual(validate(data)["progress"]["run_id"], migrated["progress"]["run_id"])

    def test_failed_registration_keeps_previous_save(self):
        self.g.start_game(player_name="Ana")
        self.g.save_progress()
        previous = self.path.read_bytes()
        self.g.reset_to_menu()
        self.g.player_screens.ask_name()
        self.g.player_screens.name = "Bia"
        self.store.player.side_effect = OSError("database locked")
        self.g.player_screens.accept_name()
        self.assertEqual(self.g.state, "menu")
        self.assertEqual(self.path.read_bytes(), previous)

    def test_pending_result_cannot_be_overwritten_by_new_game(self):
        self.g.start_game(player_name="Ana")
        self.g.campaign_data.update(chapter=7, room="final_chamber", view="report")
        self.g.investigation.score = 150
        self.g.save_progress()
        original_run = self.g.run_id
        self.g.reset_to_menu()
        self.store.record.side_effect = OSError("database locked")
        self.g.player_screens.new_game()
        self.assertEqual(self.g.run_id, original_run)
        self.assertEqual(self.g.campaign_data["view"], "report")
        self.assertEqual(self.g.player_screens.active, "ranking")
        self.assertFalse(self.g.result_saved)

    def test_ranking_pagination_and_name_screen_render(self):
        self.g.start_game(player_name="Ana")
        self.store.standings.return_value = [{"position": i+1, "name": "W"*24,
            "score": 500-i, "mistakes": i, "current": i == 10} for i in range(15)]
        self.g.player_screens.show_ranking()
        for page in range(3):
            self.assertEqual(self.g.player_screens.page, page)
            self.g.draw()
            if page < 2:
                button = next(b for b in self.g.player_screens.buttons() if b.value == "next")
                self.g.handle_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=button.rect.center)])
        self.g.player_screens.ask_name()
        self.g.player_screens.name = "W"*24
        self.assertLessEqual(self.g.fonts.h2.size("W"*24 + "|")[0], 576)
        self.g.draw()
