import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
from pathlib import Path
import unittest
import pygame

from scripts.cenas import Game
from scripts.instrucoes import PAGES, PUZZLE_INSTRUCTIONS
from scripts.interfaces import wrap_text
from scripts.roteiro_expandido import PUZZLES
from scripts.salvamento import snapshot


class InstructionsTests(unittest.TestCase):
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

    def key(self, key):
        self.game.handle_events([pygame.event.Event(pygame.KEYDOWN, key=key, unicode="")])

    def test_all_pages_fit_and_do_not_change_saved_progress(self):
        before = snapshot(self.game)
        self.game.set_message("Teste", 8)
        self.key(pygame.K_F1)
        for index, (_, sections) in enumerate(PAGES):
            self.assertEqual(self.game.instructions.page, index)
            for heading, body in sections:
                self.assertLessEqual(self.game.fonts.h2.size(heading)[0], 1000)
                lines = wrap_text(body, self.game.fonts.body, 1000)
                self.assertLessEqual(len(lines) * self.game.fonts.body.get_height() + (len(lines)-1)*5, 94)
            self.game.draw()
            self.game.update(1)
            self.assertEqual(self.game.message_timer, 8)
            self.key(pygame.K_RIGHT)
        self.key(pygame.K_ESCAPE)
        self.assertFalse(self.game.instructions.active)
        self.assertFalse(self.game.paused)
        self.game.set_message("")
        self.assertEqual(snapshot(self.game), before)

    def test_puzzle_input_selections_and_score_survive_help(self):
        for puzzle, kind in (("final_code", "code"), ("gallery", "grid"), ("lock_a", "order"), ("photos", "set"), ("witness", "proof")):
            self.game.campaign.open_puzzle(puzzle)
            self.game.campaign_data.update(input="12", page=0)
            before = snapshot(self.game)
            self.key(pygame.K_F1)
            self.assertEqual(self.game.instructions.page, 3 if kind == "proof" else 2)
            self.key(pygame.K_RETURN)
            self.key(pygame.K_ESCAPE)
            self.assertEqual(snapshot(self.game), before)
        self.assertEqual(set(PUZZLE_INSTRUCTIONS), {p["kind"] for p in PUZZLES.values()})

    def test_button_available_in_menu_and_existing_campaign(self):
        for state in ("menu", "campaign"):
            self.game.state = state
            self.game.campaign_data.update(view="explore", chapter=3, room="lab")
            button = self.game.instructions.button()
            self.game.handle_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=button.rect.center)])
            self.assertTrue(self.game.instructions.active)
            self.key(pygame.K_ESCAPE)
            self.assertEqual(self.game.state, state)

    def test_new_player_receives_guide_without_replacing_opening(self):
        self.game.reset_to_menu()
        self.game.player_screens.ask_name()
        self.game.player_screens.name = "Novo jogador"
        self.game.player_screens.accept_name()
        self.assertTrue(self.game.instructions.active)
        self.assertEqual(self.game.campaign_data["dialogue"], "opening")
        self.assertEqual(self.game.campaign_data["line"], 0)
        self.key(pygame.K_ESCAPE)
        self.assertEqual(self.game.campaign_data["line"], 0)
