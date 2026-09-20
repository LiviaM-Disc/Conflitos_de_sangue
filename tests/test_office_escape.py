import json
import os
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from scripts.cenas import Game
from scripts.escritorio_escape import new_escape, validate_escape, POINTS
from scripts.salvamento import SaveStore


class OfficeEscapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1120, 720))
        cls.game = Game(cls.screen, Path(__file__).resolve().parents[1])

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.game.save_store = None
        self.game.office_escape.path = None
        self.e = self.game.office_escape
        self.e.start()

    def click(self, value):
        button = next(b for b in self.e.buttons() if b.value == value)
        self.game.handle_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=button.rect.center)])
        validate_escape(self.e.data)
        self.game.draw()

    def open_drawer(self):
        self.click(("hotspot", "desk"))
        self.click(("take", "note"))
        self.click("back")
        self.click(("hotspot", "shelf"))
        for n in (3, 5, 8):
            self.click(("book", n))
        self.click(("take", "key"))
        self.click("back")
        self.click(("item", "key"))
        self.click(("hotspot", "drawer"))

    def test_complete_room_with_mouse_only(self):
        self.open_drawer()
        self.click(("take", "photo"))
        self.click(("take", "badge"))
        self.click("back")
        self.click(("hotspot", "phone"))
        self.click("back")
        self.click(("item", "badge"))
        self.click(("hotspot", "door"))
        self.click(("hotspot", "terminal"))
        self.assertEqual(self.e.data["scene"], "records")
        self.click("back")
        self.click("back")
        self.assertEqual(self.e.data["scene"], "room")
        self.click(("hotspot", "desk"))
        self.click(("take", "envelope"))
        self.click("back")
        self.click(("hotspot", "door"))
        self.click(("hotspot", "dean"))
        self.assertEqual(self.e.data["scene"], "finished")
        self.assertEqual(self.e.score, sum(POINTS.values()))
        self.click("restart")
        self.assertEqual(self.e.data, new_escape())

    def test_wrong_order_items_and_repeated_actions(self):
        self.click(("hotspot", "door"))
        self.assertEqual(self.e.data["scene"], "team")
        self.click(("hotspot", "dean"))
        self.assertFalse(self.e.has("case_closed"))
        self.click(("hotspot", "terminal"))
        self.assertFalse(self.e.has("records"))
        self.click("back")
        self.click(("hotspot", "drawer"))
        self.assertEqual(self.e.data["scene"], "room")
        self.click(("hotspot", "shelf"))
        self.click(("book", 3))
        self.assertEqual(self.e.data["books"], [])
        self.click("back")
        self.click(("hotspot", "desk"))
        self.click(("take", "note"))
        self.click("back")
        self.click(("hotspot", "shelf"))
        for n in (1, 2, 3):
            self.click(("book", n))
        self.assertFalse(self.e.has("books"))
        self.assertEqual(self.e.score, 10)
        self.click("reset_books")
        for n in (3, 5, 8):
            self.click(("book", n))
        self.assertTrue(self.e.has("books"))
        self.click(("take", "key"))
        self.assertNotIn(("take", "key"), [b.value for b in self.e.buttons()])

    def test_hints_preserve_score_and_choices(self):
        self.open_drawer()
        state = deepcopy(self.e.data)
        score = self.e.score
        for _ in range(4):
            self.click("hint")
        self.assertEqual(self.e.data["hints"]["photo"], 3)
        self.assertEqual(self.e.score, score)
        self.assertEqual(self.e.data["books"], state["books"])
        self.assertEqual(self.e.data["scene"], "drawer")

    def test_separate_save_roundtrip_and_failed_replace(self):
        self.open_drawer()
        with tempfile.TemporaryDirectory() as directory:
            self.e.path = Path(directory) / "escritorio_escape.json"
            campaign = Path(directory) / "progresso.json"
            campaign.write_text("existing campaign", encoding="utf-8")
            self.assertTrue(self.e.save())
            saved = self.e.path.read_bytes()
            expected = deepcopy(self.e.data)
            self.e.start()
            self.assertEqual(self.e.data, expected)
            self.click(("take", "badge"))
            with patch("scripts.escritorio_escape.os.replace", side_effect=OSError("busy")):
                self.assertFalse(self.e.save())
            self.assertEqual(self.e.path.read_bytes(), saved)
            self.assertEqual(campaign.read_text(encoding="utf-8"), "existing campaign")
            self.e.path.write_text("invalid", encoding="utf-8")
            self.assertFalse(self.e.start())
            self.assertEqual(self.e.path.read_text(), "invalid")

    def test_validation_and_ui_bounds(self):
        self.open_drawer()
        self.click(("take", "badge"))
        self.click("back")
        self.click(("item", "badge"))
        self.click(("hotspot", "door"))
        self.click(("hotspot", "terminal"))
        for scene in ("room", "desk", "drawer", "phone", "shelf", "team", "records"):
            self.e.data["scene"] = scene
            self.game.draw()
            for button in self.e.buttons():
                self.assertTrue(self.screen.get_rect().contains(button.rect))
        invalid = deepcopy(self.e.data)
        invalid["selected"] = "missing"
        with self.assertRaises(ValueError):
            validate_escape(invalid)

    def test_old_escape_save_keeps_objects_without_inventing_new_discoveries(self):
        old = dict(scene="finished", flags=["note", "books", "key", "drawer", "photo", "badge", "phone", "door", "escaped"],
                   selected="badge", books=[3, 5, 8], code="2042", hints={"door": 3},
                   message="Cassie: Estou fora.")
        migrated = validate_escape(old)
        self.assertEqual(migrated["version"], 2)
        self.assertEqual(migrated["scene"], "team")
        self.assertIn("badge", migrated["flags"])
        self.assertNotIn("records", migrated["flags"])
        self.assertNotIn("case_closed", migrated["flags"])
        self.assertNotIn("code", migrated)
        self.assertEqual(old["scene"], "finished")
        self.assertIn("escaped", old["flags"])

    def test_envelope_appears_after_records_and_conclusion_requires_evidence(self):
        self.click(("hotspot", "desk"))
        self.assertNotIn(("take", "envelope"), [b.value for b in self.e.buttons()])
        self.click("back")
        self.open_drawer()
        self.click(("take", "badge"))
        self.click("back")
        self.click(("item", "badge"))
        self.click(("hotspot", "door"))
        self.click(("hotspot", "terminal"))
        self.click("back")
        self.click("back")
        self.click(("hotspot", "desk"))
        self.click(("take", "envelope"))
        self.click("back")
        self.click(("hotspot", "door"))
        self.click(("hotspot", "dean"))
        self.assertEqual(self.e.data["scene"], "team")
        self.assertFalse(self.e.has("case_closed"))
        invalid = new_escape()
        invalid["flags"] = ["escaped"]
        with self.assertRaises(ValueError):
            validate_escape(invalid)

    def test_menu_autosave_pause_and_return_preserve_campaign(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progresso.json"
            self.game.save_store = SaveStore(path)
            self.game.start_game()
            self.assertTrue(self.game.save_progress())
            original = path.read_bytes()
            self.game.reset_to_menu()
            self.e.path = path.with_name("escritorio_escape.json")
            button = next(b for b in self.game.menu_buttons() if b.value == "escape")
            self.game.handle_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=button.rect.center)])
            self.assertEqual(self.game.state, "escape_room")
            self.click(("hotspot", "desk"))
            self.click(("take", "note"))
            self.assertIn("note", json.loads(self.e.path.read_text())["flags"])
            self.game.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
            self.assertTrue(self.game.paused)
            self.game.draw()
            self.game.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
            self.click("menu")
            self.assertEqual(self.game.state, "menu")
            self.assertEqual(path.read_bytes(), original)
            self.game.continue_game()
            self.assertEqual(self.game.state, "campaign")


if __name__ == "__main__":
    unittest.main()
