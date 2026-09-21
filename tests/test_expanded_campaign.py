import os
from pathlib import Path
import tempfile
import unittest
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from scripts.cenas import Game
from scripts.campanha import validate_campaign
from scripts.roteiro_expandido import PROLOGUE, OPENING, BRIEFING, EPILOGUE, PUZZLES, ITEMS, ROOMS, OBJECTS, EVIDENCE_DATA, PUZZLE_HINTS
from scripts.salvamento import snapshot, validate, SaveStore
from scripts.interfaces import wrap_text
from scripts.campanha_visual import ROOM_LINKS, COMPANIONS


class ExpandedCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.root = Path(__file__).resolve().parents[1]
        cls.screen = pygame.display.set_mode((1120, 720))
        cls.game = Game(cls.screen, cls.root)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.game.save_store = None
        self.game.start_game()
        self.c = self.game.campaign

    def click(self, value):
        buttons = self.c.buttons()
        button = next((b for b in buttons if b.value == value), None)
        for _ in range(10):
            if button is not None:
                break
            following = next((b for b in buttons if b.value == "next" and b.enabled), None)
            self.assertIsNotNone(following, f"Nao encontrei {value}; view={self.c.data['view']}")
            self.game.handle_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=following.rect.center)])
            buttons = self.c.buttons()
            button = next((b for b in buttons if b.value == value), None)
        self.assertIsNotNone(button)
        self.assertTrue(button.enabled, value)
        self.game.handle_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=button.rect.center)])
        validate(snapshot(self.game))

    def test_inventory_labels_fit_visible_slots(self):
        font = self.c.visual.item_font
        for key, item in ITEMS.items():
            lines = wrap_text(item[0], font, 112)
            self.assertLessEqual(len(lines) * font.get_height(), 37, key)
            self.assertTrue(all(font.size(line)[0] <= 112 for line in lines), key)

    def test_phase_completion_notice_survives_save_and_keeps_score(self):
        destinations = ["reception", "interview", "lab", "garden", "hidden", "final_chamber", "final_chamber"]
        with tempfile.TemporaryDirectory() as folder:
            store = SaveStore(Path(folder) / "transition.json")
            for phase, room in enumerate(destinations, 1):
                self.c.data["chapter"] = phase - 1
                self.game.investigation.score = 135
                self.c.advance(phase, room)
                self.assertEqual(self.c.data["view"], "note")
                expected = "Prologo concluido" if phase == 1 else f"Fase {phase-1} concluida!"
                self.assertEqual(self.c.data["note_title"], expected)
                self.assertIn("135 pontos", self.c.data["note_text"])
                self.assertEqual(self.game.investigation.score, 135)
                self.game.draw()
                store.write(snapshot(self.game))
                self.game.saved_game = store.load()
                self.game.continue_game()
                self.assertEqual(self.c.data["note_title"], expected)
                self.click("note_back")
                self.assertEqual(self.c.data["view"], "dialogue" if phase == 7 else "explore")
                if phase == 7:
                    self.assertEqual(self.c.data["dialogue"], "epilogue")
                    self.assertEqual(self.c.data["line"], 0)

    def test_extended_prologue_renders_and_saves_every_line(self):
        with tempfile.TemporaryDirectory() as folder:
            store = SaveStore(Path(folder) / "prologue.json")
            for index, (speaker, text) in enumerate(OPENING):
                self.assertEqual(self.c.data["line"], index)
                briefing = index < len(BRIEFING)
                lines = wrap_text(text, self.game.fonts.body, 1000 if briefing else 1020)
                height = len(lines) * self.game.fonts.body.get_height() + max(0, len(lines) - 1) * (8 if briefing else 5)
                self.assertLessEqual(height, 145 if briefing else 84, speaker)
                self.game.draw()
                payload = snapshot(self.game)
                validate(payload)
                store.write(payload)
                self.assertEqual(store.load()["progress"]["campaign_data"]["line"], index)
                self.click("dialogue_next")
        self.assertEqual(self.c.data["view"], "explore")
        self.assertEqual(self.c.data["chapter"], 0)
        self.assertEqual(self.c.data["room"], "intro")

    def test_previous_prologue_save_remains_valid(self):
        self.c.data.update(dialogue="prologue", line=12)
        validate(snapshot(self.game))
        self.game.draw()
        for _ in PROLOGUE[12:]:
            self.click("dialogue_next")
        self.assertEqual(self.c.data["view"], "explore")

    def dismiss(self):
        if self.c.data["view"] == "note":
            self.click("note_back")

    def travel(self, room):
        self.dismiss()
        self.click("map")
        phase = ROOMS[room]["phase"]
        if room == "hidden" and self.c.data["chapter"] == 5:
            phase = 5
        self.click(("phase", phase))
        self.click(("room", room))
        self.dismiss()
        self.assertEqual(self.c.data["room"], room)

    def inspect(self, key):
        self.dismiss()
        self.click(("object", key))
        self.dismiss()

    def use(self, *keys):
        self.dismiss()
        self.click("inventory")
        for key in list(self.c.data["selected_items"]):
            self.c.data["page"] = 0
            self.click(("item", key))
        for key in keys:
            self.c.data["page"] = 0
            self.click(("item", key))
        self.click("back")

    def answer(self, key):
        self.assertEqual(self.c.data["puzzle"], key)
        content = PUZZLES[key]
        kind = content["kind"]
        if kind == "code":
            for char in content["answer"]:
                if char != " ":
                    self.click(("digit", char))
        elif kind in ("order", "set"):
            for value in content["answer"]:
                self.click(("answer", value))
        elif kind == "grid":
            for row, value in enumerate(content["answer"]):
                for _ in range(10):
                    if self.c.data["answers"][row] == value:
                        break
                    self.click(("grid", row))
        else:
            self.click(("answer", content["answer"]))
            for proof in content["proofs"]:
                self.c.data["page"] = 0
                self.click(("proof", proof))
        self.game.draw()
        self.click("submit")
        self.assertIn(key, self.c.data["flags"])
        self.dismiss()

    def complete_office(self, photo=False):
        for _ in OPENING:
            self.click("dialogue_next")
        for key in ("redding_notes", "reflection", "stopped_watch", "leave_intro"):
            self.inspect(key)
        self.assertEqual(self.c.data["chapter"], 1)
        self.inspect("card_holder")
        self.travel("office")
        for key in ("desk", "phone", "chair", "glass", "bin"):
            self.inspect(key)
        self.use("carbon")
        self.inspect("lamp")
        self.answer("writing")
        self.travel("archive")
        self.use("clip")
        self.inspect("drawer_cover")
        self.travel("pantry")
        self.inspect("key_board")
        self.travel("archive")
        self.use("key417")
        self.inspect("drawer")
        if photo:
            self.inspect("folded_photo")
        self.travel("service")
        self.use("badge")
        self.inspect("maintenance_door")
        self.inspect("supply")
        self.travel("office")
        self.inspect("new_envelope")
        self.answer("office_conclusion")

    def complete_house(self):
        self.travel("vestibule")
        self.inspect("box")
        self.travel("library")
        self.inspect("shelves")
        self.answer("books")
        self.use("magnet", "strip")
        self.click("inventory")
        self.click("combine")
        self.dismiss()
        self.click("back")
        self.travel("kitchen")
        self.use("magnetic_tool")
        self.inspect("grate")
        self.travel("vestibule")
        self.use("hand")
        self.inspect("clock")
        self.answer("clock")
        self.travel("gallery")
        self.inspect("portrait_notes")
        self.inspect("portraits")
        self.answer("gallery")
        self.travel("bedroom")
        self.inspect("altered")
        self.answer("altered")
        self.travel("house_office")
        self.use("punched")
        self.inspect("office_light")
        self.travel("basement")
        for key in ("lock_a", "lock_b", "lock_c"):
            self.inspect(key)
            self.answer(key)
        self.travel("hidden")
        self.inspect("hidden_symbol")

    def choose_from_bar(self, *items):
        for key in list(self.c.data["selected_items"]) + list(items):
            while self.c.data["page"] > 0:
                self.click("previous")
            self.click(("item", key))

    def walk_to(self, destination):
        queue = deque([(self.c.data["room"], [])])
        seen = set()
        while queue:
            room, path = queue.popleft()
            if room == destination:
                for step in path:
                    self.click(("walk", step))
                    self.dismiss()
                    self.assertEqual(self.c.data["room"], step)
                return
            if room in seen:
                continue
            seen.add(room)
            for neighbour in ROOM_LINKS[room]:
                if ROOMS[neighbour]["phase"] <= self.c.data["chapter"] and all(self.c.has(k) for k in ROOMS[neighbour]["needs"]):
                    queue.append((neighbour, path + [neighbour]))
        self.fail(f"Sem caminho de {self.c.data['room']} para {destination}")

    def test_complete_point_and_click_route_without_map_or_inventory_screen(self):
        for _ in range(240):
            view = self.c.data["view"]
            self.game.draw()
            if view == "report":
                break
            if view == "dialogue":
                self.click("dialogue_next")
            elif view == "note":
                self.dismiss()
            elif view == "puzzle":
                self.answer(self.c.data["puzzle"])
            else:
                self.assertEqual(view, "explore")
                room, key = self.c.next_step()
                for button in self.c.buttons():
                    self.assertTrue(self.game.screen.get_rect().contains(button.rect))
                    self.assertNotEqual(button.value, "follow_step")
                self.walk_to(room)
                if key == "magnetic_tool":
                    self.choose_from_bar("magnet", "strip")
                    self.click("combine")
                else:
                    if OBJECTS[key]["use"]:
                        self.choose_from_bar(*OBJECTS[key]["use"])
                    self.click(("object", key))
        self.assertEqual(self.c.data["view"], "report")
        self.assertTrue(self.c.has("x_final"))
        self.assertEqual(self.game.investigation.mistakes, 0)

    def test_old_blocked_save_can_use_direct_exit(self):
        self.c.data.update(chapter=6, room="exit", view="explore")
        for flag in ("manual", "photos", "panel_locked"):
            self.c.flag(flag)
        self.game.investigation.add_evidence("x_verified")
        self.assertEqual(self.c.next_step(), ("exit", "final_panel"))
        saved = validate(snapshot(self.game))
        self.game.campaign_data = saved["progress"]["campaign_data"]
        self.click(("object", "final_panel"))
        self.answer("final_code")
        self.assertEqual(self.c.next_step(), ("transmission", "transmission"))

    def test_all_rooms_have_visual_controls_and_conversations(self):
        self.c.data["inventory"] = list(ITEMS)
        self.c.data["flags"] = sorted(set(OBJECTS) | set(PUZZLES))
        for room in ROOMS:
            self.c.data.update(chapter=max(ROOMS[room]["phase"], 1), room=room, view="explore", page=0)
            self.game.draw()
            objects = [b for b in self.c.buttons() if isinstance(b.value, tuple) and b.value[0] == "object"]
            self.assertEqual(len(objects), len(ROOMS[room]["objects"]))
            for button in self.c.buttons():
                self.assertTrue(self.game.screen.get_rect().contains(button.rect))
            if room in COMPANIONS:
                score = self.game.investigation.score
                self.click(("talk", room))
                self.assertEqual(self.c.data["note_title"], COMPANIONS[room])
                self.game.draw()
                self.dismiss()
                self.assertEqual(score, self.game.investigation.score)

    def test_items_require_selection_and_world_hint_does_not_advance(self):
        self.c.data.update(chapter=1, room="office", view="explore", inventory=["carbon"])
        self.inspect("lamp")
        self.assertFalse(self.c.has("x_writing"))
        self.click("world_hint")
        self.dismiss()
        self.assertEqual(self.c.data["room"], "office")
        self.choose_from_bar("carbon")
        self.inspect("lamp")
        self.assertEqual(self.c.data["puzzle"], "writing")

    def test_complete_six_phases_with_inventory_and_backtracking(self):
        self.complete_office()
        self.inspect("witness")
        self.answer("witness")
        self.travel("hall")
        self.inspect("hall_log")
        self.travel("technical")
        self.inspect("backup_labels")
        self.travel("security")
        self.inspect("camera")
        self.answer("camera")
        for obj, key in (("sequence", "sequence"), ("intruder", "intruder"), ("positional", "positional")):
            self.inspect(obj)
            self.answer(key)
        self.travel("evidence")
        self.inspect("photo_table")
        self.assertFalse(self.c.has("x_address"))
        self.travel("archive")
        self.inspect("folded_photo")
        self.travel("evidence")
        self.use("overlay", "folded_photo")
        self.inspect("photo_table")
        self.answer("overlay")
        self.travel("digital")
        self.inspect("digital")
        self.travel("connections")
        self.inspect("target_board")
        self.answer("target")
        self.complete_house()
        self.assertEqual(self.c.data["chapter"], 5)
        self.inspect("recordings")
        self.answer("recordings")
        self.travel("recording")
        self.inspect("logic_grid")
        self.answer("grid")
        self.inspect("continue_final")
        self.travel("photo_archive")
        self.inspect("nine_photos")
        self.answer("photos")
        self.travel("exit")
        self.inspect("final_panel")
        self.answer("final_code")
        self.travel("transmission")
        self.inspect("transmission")
        self.answer("final_deduction")
        self.assertEqual(self.c.data["chapter"], 7)
        self.assertEqual(self.c.data["view"], "dialogue")
        for _ in EPILOGUE:
            self.click("dialogue_next")
        self.assertEqual(self.c.data["view"], "report")
        self.assertTrue(self.game.investigation.has("x_final"))
        self.assertFalse(self.game.investigation.has("final_deduction"))
        self.assertEqual(self.game.investigation.mistakes, 0)
        self.game.draw()

    def test_repeated_object_does_not_duplicate_rewards(self):
        self.c.data.update(view="explore", chapter=1, room="reception")
        self.inspect("card_holder")
        score = self.game.investigation.score
        self.inspect("card_holder")
        self.assertEqual(self.c.data["inventory"].count("clip"), 1)
        self.assertEqual(self.game.investigation.score, score)

    def test_wrong_key_and_order_do_not_unlock_or_punish(self):
        self.c.data.update(view="explore", chapter=1, room="archive", flags=["drawer_cover"], inventory=["key471"], selected_items=["key471"])
        self.click(("object", "drawer"))
        self.assertEqual(self.c.data["exposure"], 0)
        self.assertNotIn("badge", self.c.data["inventory"])
        self.c.data.update(chapter=4, room="basement")
        self.click(("object", "lock_c"))
        self.assertEqual(self.c.data["exposure"], 0)
        self.assertNotIn("lock_c", self.c.data["flags"])

    def test_errors_cost_five_points_without_blocking_or_negative_score(self):
        self.c.data.update(view="explore", chapter=1, room="reception")
        self.c.checkpoint()
        self.inspect("card_holder")
        self.game.investigation.score = 18
        self.c.penalize("Primeiro erro")
        self.assertEqual(self.game.investigation.score, 13)
        for _ in range(4):
            self.c.penalize("Ruido")
        self.assertEqual(self.c.data["inventory"], ["clip"])
        self.assertEqual(self.c.data["exposure"], 0)
        self.assertEqual(self.game.investigation.mistakes, 5)
        self.assertEqual(self.game.investigation.score, 0)
        validate(snapshot(self.game))

    def test_partial_puzzle_checkpoint_and_inventory_round_trip(self):
        self.c.data.update(view="explore", chapter=4, room="library", inventory=["magnet"])
        self.c.checkpoint()
        self.inspect("shelves")
        self.click(("answer", "3"))
        expected = snapshot(self.game)
        with tempfile.TemporaryDirectory() as directory:
            store = SaveStore(Path(directory) / "save.json")
            store.write(expected)
            self.game.saved_game = store.load()
            self.game.continue_game()
            self.assertEqual(snapshot(self.game), expected)
            self.c.data["answers"].append("5")
            self.assertEqual(self.game.saved_game["progress"]["campaign_data"]["answers"], ["3"])

    def test_errors_do_not_add_cooldown(self):
        self.c.data.update(view="explore", chapter=3, room="lab")
        self.inspect("sequence")
        self.click("submit")
        self.assertEqual(self.game.investigation.mistakes, 0)
        for _ in range(3):
            self.c.data["input"] = "99"
            self.click("submit")
        self.assertEqual(self.c.data["cooldown"], 0)
        self.game.paused = True
        self.game.update(10)
        self.assertEqual(self.c.data["cooldown"], 0)
        self.game.paused = False
        self.game.update(5)
        self.assertEqual(self.c.data["cooldown"], 0)

    def test_final_code_remains_open_after_repeated_errors(self):
        self.c.data.update(view="explore", chapter=6, room="exit")
        self.game.investigation.add_evidence("x_verified")
        self.inspect("final_panel")
        for _ in range(2):
            self.c.data["input"] = "1111 11 11"
            self.click("submit")
        self.dismiss()
        self.assertFalse(self.c.has("panel_locked"))
        self.assertEqual(self.c.data["view"], "puzzle")
        self.click("clear")
        self.answer("final_code")
        self.assertTrue(self.c.has("final_code"))

    def test_progressive_hints_cover_every_puzzle_and_preserve_answers(self):
        self.assertEqual(set(PUZZLES), set(PUZZLE_HINTS))
        for proof in EVIDENCE_DATA:
            self.game.investigation.add_evidence(proof)
        for key in PUZZLES:
            self.c.open_puzzle(key)
            self.c.data["input"] = "12"
            score = self.game.investigation.score
            for level in (1, 2, 3, 3):
                self.click("hint")
                self.assertEqual(self.c.data["view"], "note")
                self.assertEqual(self.c.hint_level(), level)
                self.assertEqual(self.c.data["puzzle"], key)
                self.assertTrue(self.c.data["note_text"])
                self.game.draw()
                self.dismiss()
                self.assertEqual(self.c.data["view"], "puzzle")
                self.assertEqual(self.c.data["input"], "12")
                self.assertNotIn(key, self.c.data["flags"])
                self.assertEqual(self.game.investigation.score, score)
            saved = validate(snapshot(self.game))
            self.game.campaign_data = saved["progress"]["campaign_data"]
            self.assertEqual(self.c.hint_level(), 3)

    def test_only_two_terminals_and_no_identity_reward(self):
        self.c.data.update(view="explore", chapter=5, room="recording")
        for name in ("Lia", "Michael", "Sloane", "Lia"):
            self.inspect("terminals")
            self.click(("consult", name))
            self.dismiss()
        self.assertEqual(len(self.c.data["help_used"]), 2)
        self.game.investigation.add_evidence("x_recording")
        self.inspect("logic_grid")
        self.click("unsupported")
        self.assertTrue(self.c.data["best_blocked"])
        self.assertFalse(self.game.investigation.has("x_grid"))

    def test_puzzle_layout_and_validation(self):
        self.c.data["inventory"] = list(ITEMS)
        for key in EVIDENCE_DATA:
            self.game.investigation.add_evidence(key)
        for key, puzzle in PUZZLES.items():
            self.c.data["flags"] = list(OBJECTS)
            self.c.open_puzzle(key)
            self.game.draw()
            for button in self.c.buttons():
                with self.subTest(puzzle=key, button=button.text):
                    self.assertTrue(self.screen.get_rect().contains(button.rect))
                    lines = wrap_text(button.text, self.game.fonts.button, button.rect.width - 24)
                    self.assertLessEqual(len(lines), 3)
                    self.assertLessEqual(len(lines) * self.game.fonts.button.get_height() + max(0, len(lines) - 1) * 3, button.rect.height)
        invalid = snapshot(self.game)
        invalid["progress"]["campaign_data"]["inventory"].append("unknown")
        with self.assertRaises(ValueError):
            validate(invalid)


if __name__ == "__main__":
    unittest.main()
