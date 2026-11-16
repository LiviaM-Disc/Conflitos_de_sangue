import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import pygame
from scripts.cenas import Game
from scripts.aventura_visual import STAGES, TASKS, circuit_solution, powered_cells, validate_visual
from scripts.salvamento import snapshot, validate, SaveStore
from scripts.interfaces import wrap_text, draw_text, draw_clue_panel
from scripts.pistas import EVIDENCES
from scripts.equipe_visual import TEAM_TASKS


class VisualAdventureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1120, 720))
        cls.root = Path(__file__).resolve().parents[1]

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.g = Game(self.screen, self.root)
        self.g.start_game(player_name="Visual tester", visual=True)
        self.c = self.g.campaign

    def click(self, action):
        b = next(b for b in self.c.buttons() if b.value == action)
        self.assertTrue(b.enabled)
        self.g.handle_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=b.rect.center)])
        validate(snapshot(self.g))
        self.g.draw()

    def solve_screen(self):
        d = self.c.data
        view = d["view"]
        if view == "circuit":
            for i in range(len(d["rotations"])):
                for _ in range(4):
                    if d["view"] != "circuit" or d["rotations"][i] == 0:
                        break
                    self.click(("rotate", i))
            self.assertNotEqual(d["view"], "circuit")
        elif view == "tiles":
            for i in range(6):
                if d["view"] != "tiles":
                    break
                other = d["tiles"].index(i)
                if other != i:
                    self.click(("tile", i))
                    self.click(("tile", other))
        elif view == "memory":
            self.c.update(self.c.demo_duration() + 1)
            for pad in list(d["sequence"]):
                self.click(("pad", pad))
        elif view == "clock":
            for _ in range(3):
                self.click(("dial", 0))
            for _ in range(7):
                self.click(("dial", 1))
        elif view == "timing":
            for _ in range(4):
                if d["view"] != "timing":
                    break
                low, high = self.c.timing_window()
                speed = .39 if d["chapter"] == 7 else .55
                self.c.elapsed = (low + high) / 2 / speed
                self.click("pulse")
        elif view == "team_task":
            if d["team_selection"]:
                self.click("team_clear")
            for index in self.c.team.current()["answer"]:
                self.click(("team_card", index))
            self.click("team_confirm")
        else:
            self.fail("Unexpected view: " + view)

    def test_complete_eight_stages_by_mouse_and_roundtrip_each_screen(self):
        self.click("begin")
        with TemporaryDirectory() as folder:
            store = SaveStore(Path(folder) / "save.json")
            for stage in range(1, 9):
                self.assertEqual(self.c.data["chapter"], stage)
                for _ in range(15):
                    d = self.c.data
                    self.g.draw()
                    store.write(snapshot(self.g))
                    self.assertEqual(store.load(), snapshot(self.g))
                    if d["view"] == "complete":
                        break
                    if d["view"] == "explore":
                        self.click("combine" if self.c.task()[0] == "combine" else ("task", d["step"]))
                    else:
                        self.solve_screen()
                self.assertEqual(self.c.data["view"], "complete")
                self.assertEqual(self.c.data["flags"], list(range(1, stage + 1)))
                score = self.g.investigation.score
                self.c.complete()
                self.assertEqual(self.g.investigation.score, score)
                self.click("next")
            self.assertEqual(self.c.data["view"], "epilogue")
            self.click("report")
            self.assertEqual(self.c.data["view"], "report")
            self.assertEqual(len(self.g.investigation.evidence), 8)
            self.assertEqual(self.c.data["team_done"], list(range(1, 9)))
            self.assertEqual(self.g.investigation.correct_connections, sum(map(len, TEAM_TASKS.values())))
            self.assertEqual(self.g.investigation.lies_found, 3)
            self.assertEqual({key.rsplit("_", 1)[-1] for key in self.g.investigation.used_abilities},
                             {"cassie", "dean", "michael", "lia", "sloane"})

    def test_difficulty_changes_mechanics_not_only_stage_label(self):
        self.assertEqual(len(STAGES), 8)
        self.assertEqual([len(circuit_solution(n)) for n in (2, 6, 8)], [6, 12, 16])
        for chapter, length in ((4, 4), (6, 5), (8, 7)):
            self.c.data.update(chapter=chapter, sequence=[])
            self.c.open_puzzle("memory")
            self.assertEqual(len(self.c.data["sequence"]), length)
        self.c.data["chapter"] = 7
        easier = self.c.timing_window()
        self.c.data["chapter"] = 8
        harder = self.c.timing_window()
        self.assertGreater(easier[1] - easier[0], harder[1] - harder[0])

    def test_pause_freezes_memory_and_timing(self):
        self.c.data["chapter"] = 4
        self.c.open_puzzle("memory")
        self.g.paused = True
        before = self.c.replay_time
        self.g.update(5)
        self.assertEqual(self.c.replay_time, before)

    def test_memory_error_retry_and_free_replay(self):
        self.c.data["chapter"] = 4
        self.c.open_puzzle("memory")
        self.g.investigation.score = 20
        self.c.update(10)
        self.click(("pad", (self.c.data["sequence"][0] + 1) % 4))
        self.assertEqual(self.g.investigation.score, 15)
        self.assertEqual(self.c.data["answer"], [])
        self.assertGreater(self.c.replay_time, 0)
        self.click("replay")
        self.assertEqual(self.g.investigation.score, 15)

    def test_tools_work_without_hidden_selection_requirement(self):
        self.click("begin")
        self.click(("task", 1))
        self.assertEqual(self.c.data["step"], 0)
        self.click(("task", 0))
        self.assertEqual(self.c.data["selected_items"], [])
        self.click(("task", 1))
        self.assertEqual(self.c.data["view"], "team_task")
        self.solve_screen()
        self.assertEqual(self.c.data["view"], "complete")

    def test_reopen_keeps_visual_edition_and_close_records_stage_eight(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "save.json"
            self.g.save_store = SaveStore(path)
            self.g.campaign_data.update(chapter=8, view="explore")
            self.g.save_progress()
            store = Mock()
            reopened = Game(self.screen, self.root, path, ranking_store=store)
            reopened.continue_game()
            self.assertEqual(reopened.campaign.__class__.__name__, "VisualCampaign")
            reopened.handle_events([pygame.event.Event(pygame.QUIT)])
            self.assertFalse(reopened.running)
            self.assertEqual(store.record.call_args.kwargs["campaign"], "visual8")
            self.assertEqual(store.record.call_args.kwargs["phase"], 8)
            self.assertFalse(store.record.call_args.kwargs["completed"])

    def test_legacy_campaign_stays_legacy(self):
        self.g.start_game(player_name="Old")
        data = snapshot(self.g)
        self.g.saved_game = validate(data)
        self.g.continue_game()
        self.assertEqual(self.g.campaign.__class__.__name__, "ExpandedCampaign")

    def test_all_buttons_fit_screen(self):
        for chapter in range(1, 9):
            self.c.data.update(chapter=chapter, step=0, view="explore")
            for b in self.c.buttons():
                self.assertTrue(self.screen.get_rect().contains(b.rect))
        for chapter, kind in ((2, "circuit"), (8, "circuit"), (3, "tiles"), (8, "memory"), (5, "clock"), (7, "timing")):
            self.c.data.update(chapter=chapter, rotations=[], sequence=[])
            self.c.open_puzzle(kind)
            self.g.draw()
            for b in self.c.buttons():
                self.assertTrue(self.screen.get_rect().contains(b.rect))

    def test_corrupt_visual_save_is_rejected(self):
        for key, value in (("chapter", 9), ("rotations", [5]), ("tiles", [1] * 6), ("inventory", ["not_real"])):
            data = deepcopy(self.c.data)
            data[key] = value
            with self.assertRaises(ValueError):
                validate_visual(data)

    def test_circuits_are_solvable_and_start_unpowered(self):
        for chapter in (2, 6, 8):
            self.c.data.update(chapter=chapter, rotations=[])
            self.c.open_puzzle("circuit")
            self.assertFalse(powered_cells(chapter, self.c.data["rotations"])[1])
            self.assertTrue(powered_cells(chapter, [0] * len(circuit_solution(chapter)))[1])

    def test_materials_can_be_collected_in_either_order_without_duplicate_points(self):
        for order in ((0, 1), (1, 0)):
            self.g.start_game(player_name="Collector", visual=True)
            self.c = self.g.campaign
            self.c.data.update(chapter=5, view="explore")
            self.click(("task", order[0]))
            self.assertIn(TASKS[5][order[0]][4], self.c.data["inventory"])
            self.assertNotIn(("task", order[0]), [b.value for b in self.c.buttons()])
            score = self.g.investigation.score
            self.c.act(("task", order[0]))
            self.assertEqual(self.g.investigation.score, score)
            self.click(("task", order[1]))
            self.assertEqual(set(self.c.data["inventory"]), {"magnet", "strip"})
            self.assertEqual(self.c.data["step"], 2)
            self.assertEqual(self.g.investigation.score, 20)
            self.click("combine")
            self.assertEqual(self.c.data["inventory"], ["magnetic_tool"])
            self.click(("task", 3))
            self.click(("task", 4))
            self.assertEqual(self.c.data["view"], "clock")

    def test_memory_back_replay_and_resume_preserve_correct_prefix(self):
        self.c.data.update(chapter=6, locks=1, flags=list(range(1, 6)), stars=[3] * 5)
        self.c.open_puzzle("memory")
        self.c.update(20)
        self.click(("pad", self.c.data["sequence"][0]))
        prefix = list(self.c.data["answer"])
        score = self.g.investigation.score
        self.click("back")
        self.click(("task", 0))
        self.assertEqual(self.c.data["answer"], prefix)
        self.assertEqual(self.c.demo_offset, len(prefix))
        self.click("replay")
        self.assertEqual(self.c.data["answer"], prefix)
        self.g.saved_game = validate(snapshot(self.g))
        self.g.continue_game()
        self.c = self.g.campaign
        self.assertEqual(self.c.data["answer"], prefix)
        self.assertEqual(self.g.investigation.score, score)
        self.c.update(self.c.demo_interval() * 1.1)
        self.assertEqual(self.c.lit_pad(), self.c.data["sequence"][1])
        self.c.update(20)
        for pad in self.c.data["sequence"][1:]:
            self.click(("pad", pad))
        self.assertEqual(self.c.data["view"], "team_task")

    def test_clock_can_correct_overshoot_in_both_directions(self):
        self.c.data.update(chapter=5, view="clock", dial=[4, 24], flags=list(range(1, 5)), stars=[3] * 4)
        self.click(("dial_back", 0))
        self.assertEqual(self.c.data["dial"], [3, 24])
        self.click(("dial_back", 1))
        self.assertEqual(self.c.data["view"], "team_task")
        self.assertEqual(self.g.investigation.mistakes, 0)

    def test_clock_wrap_and_item_titles_fit(self):
        self.c.data.update(chapter=5, view="clock")
        self.click(("dial_back", 0))
        self.click(("dial_back", 1))
        self.assertEqual(self.c.data["dial"], [11, 57])
        self.click(("dial", 0))
        self.click(("dial", 1))
        self.assertEqual(self.c.data["dial"], [0, 0])
        self.c.data.update(view="explore", inventory=["magnetic_tool"], step=3)
        b = next(b for b in self.c.buttons() if b.value == ("item", "magnetic_tool"))
        with patch("scripts.aventura_visual.draw_text", wraps=draw_text) as render_text:
            self.g.draw()
        call = next(call for call in render_text.call_args_list if call.args[1] == b.text)
        font, rect = call.args[2], call.args[4]
        lines = len(wrap_text(b.text, font, rect.width))
        height = lines * font.get_height() + (lines - 1) * call.kwargs.get("line_spacing", 5)
        self.assertLessEqual(height, rect.height)
        self.assertTrue(b.rect.contains(rect))

    def test_completed_locks_stay_complete_when_returning_to_scene(self):
        self.c.data.update(chapter=8, view="explore")
        self.click(("task", 0))
        self.solve_screen()
        self.assertEqual(self.c.data["locks"], 1)
        self.solve_screen()
        self.assertEqual(self.c.data["locks"], 2)
        score = self.g.investigation.score
        self.click("back")
        self.click("team_continue")
        self.assertEqual(self.c.data["view"], "team_task")
        self.assertEqual(self.g.investigation.score, score)
        for _ in range(5):
            self.solve_screen()
        self.assertEqual(self.c.data["view"], "timing")
        score = self.g.investigation.score
        self.click("back")
        self.click(("task", 0))
        self.assertEqual(self.c.data["view"], "timing")
        self.assertEqual(self.g.investigation.score, score)

    def test_guidance_tracks_remaining_items_and_blocked_click_is_free(self):
        self.c.data.update(chapter=5, view="explore")
        before = snapshot(self.g)
        self.click(("task", 4))
        self.assertEqual(snapshot(self.g), before)
        self.assertIn("Ima", self.c.feedback)
        self.assertIn("Tira", self.c.feedback)
        self.click(("task", 1))
        self.assertIn("Ima", self.c.next_action())
        self.assertNotIn("Tira", self.c.next_action())
        self.click(("task", 0))
        self.assertIn("Combinar", self.c.next_action())
        self.click("combine")
        self.assertIn("Ferramenta magnetica", self.c.next_action())
        self.assertIn("Grelha", self.c.next_action())
        self.click(("task", 3))
        self.assertIn("Ponteiro", self.c.next_action())
        self.assertIn("Relogio", self.c.next_action())

    def test_pickup_animation_does_not_delay_inventory_or_modify_save(self):
        self.click("begin")
        self.click(("task", 0))
        self.assertEqual(len(self.c.pickups), 1)
        self.assertIn("key417", self.c.data["inventory"])
        before = snapshot(self.g)
        self.g.update(.2)
        self.g.draw()
        self.assertEqual(snapshot(self.g), before)
        age = self.c.pickups[0]["age"]
        self.g.paused = True
        self.g.update(.2)
        self.assertEqual(self.c.pickups[0]["age"], age)
        self.g.paused = False
        self.click(("task", 1))
        self.assertEqual(self.c.data["view"], "team_task")
        self.assertEqual(self.g.investigation.score, 10)
        self.solve_screen()
        self.assertEqual(self.c.data["view"], "complete")
        self.assertEqual(self.g.investigation.score, 100)
        self.click("next")
        self.assertEqual(self.c.pickups, [])

    def test_visual_dossier_has_only_recovered_story_and_pauses_challenge(self):
        legacy = EVIDENCES["x_envelope"]
        self.click("begin")
        self.click(("task", 0))
        self.click(("task", 1))
        self.solve_screen()
        self.click("next")
        self.c.data.update(chapter=4)
        self.c.open_puzzle("memory")
        before = snapshot(self.g)
        countdown = self.c.replay_time
        with patch("scripts.cenas.draw_clue_panel", wraps=draw_clue_panel) as draw_dossier:
            self.click("dossier")
        evidences = draw_dossier.call_args.args[2]
        self.assertEqual([e.id for e in evidences], ["x_envelope"])
        self.assertEqual(evidences[0].description, STAGES[0][4])
        self.assertNotEqual(evidences[0].description, legacy.description)
        self.assertEqual(EVIDENCES["x_envelope"], legacy)
        self.g.update(5)
        self.assertEqual(self.c.replay_time, countdown)
        self.assertEqual(snapshot(self.g), before)
        self.g.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
        self.assertFalse(self.g.show_clues)
        self.assertFalse(self.g.paused)
        self.g.update(.1)
        self.assertLess(self.c.replay_time, countdown)

    def test_team_error_back_and_confirm_preserve_finished_mechanisms(self):
        self.c.data.update(chapter=2, view="explore", flags=[1], stars=[3], team_done=[1])
        self.click(("task", 0))
        self.click(("task", 1))
        self.solve_screen()
        self.assertEqual(self.c.data["view"], "team_task")
        rotations = list(self.c.data["rotations"])
        score = self.g.investigation.score
        self.click(("team_card", 1))
        self.click("team_confirm")
        self.assertEqual(self.g.investigation.score, score - 5)
        self.assertEqual(self.c.data["team_round"], 0)
        self.click("back")
        self.assertFalse(any(isinstance(b.value, tuple) and b.value[0] == "task" for b in self.c.buttons()))
        self.click("team_continue")
        self.assertEqual(self.c.data["team_selection"], [1])
        self.assertEqual(self.c.data["rotations"], rotations)
        self.click(("team_card", 0))
        self.click("team_confirm")
        self.assertEqual(self.c.data["team_round"], 1)
        score = self.g.investigation.score
        self.c.act("team_confirm")
        self.assertEqual(self.g.investigation.score, score)
        self.solve_screen()
        self.assertEqual(self.c.data["view"], "complete")
        score = self.g.investigation.score
        self.c.act("team_confirm")
        self.c.puzzle_done()
        self.assertEqual(self.g.investigation.score, score)

    def test_partial_team_order_survives_save_and_roster_freezes_memory(self):
        with TemporaryDirectory() as folder:
            self.g.save_store = SaveStore(Path(folder) / "save.json")
            self.c.data.update(chapter=8, view="team_task", team_ready=True, team_round=1)
            self.click(("team_card", 2))
            self.click(("team_card", 0))
            saved = self.g.save_store.load()
            self.assertEqual(saved["progress"]["campaign_data"]["team_selection"], [2, 0])
            self.g.saved_game = saved
            self.g.continue_game()
            self.c = self.g.campaign
            self.assertEqual(self.c.data["team_selection"], [2, 0])
            self.click(("team_card", 1))
            self.click("team_confirm")
            self.assertEqual(self.c.data["team_round"], 2)
            self.assertEqual(self.g.investigation.score, 10)
        self.g.save_store = None
        self.c.data.update(team_ready=False, team_round=0, sequence=[], answer=[])
        self.c.open_puzzle("memory")
        before = snapshot(self.g)
        timer = self.c.replay_time
        self.click("team")
        self.g.update(5)
        self.assertEqual(self.c.replay_time, timer)
        self.assertEqual(snapshot(self.g), before)
        self.g.handle_events([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)])
        self.assertFalse(self.c.team.roster_open)
        self.assertFalse(self.g.paused)
        self.g.update(.1)
        self.assertLess(self.c.replay_time, timer)

    def test_team_selection_is_reversible_and_incomplete_answers_are_free(self):
        self.c.data.update(chapter=8, view="team_task", team_ready=True, team_round=4)
        self.click(("team_card", 0))
        self.c.act("team_confirm")
        self.assertEqual(self.g.investigation.mistakes, 0)
        self.click(("team_card", 1))
        self.click(("team_card", 2))
        self.click(("team_card", 3))
        self.assertEqual(self.c.data["team_selection"], [0, 1, 2])
        self.click(("team_card", 1))
        self.click(("team_card", 3))
        self.assertEqual(self.c.data["team_selection"], [0, 2, 3])
        self.click("team_clear")
        self.assertEqual(self.c.data["team_selection"], [])
        self.assertEqual(self.g.investigation.score, 0)

    def test_version_six_upgrade_preserves_scores_and_completed_phases(self):
        for view, flags in (("explore", [1, 2]), ("complete", [1, 2, 3]), ("ended", [1, 2])):
            self.c.data.update(chapter=3, view=view, flags=flags, stars=[3] * len(flags))
            self.g.investigation.score = 237
            old = snapshot(self.g)
            old["version"] = 6
            for key in ("team_ready", "team_round", "team_selection", "team_done"):
                del old["progress"]["campaign_data"][key]
            before = deepcopy(old)
            migrated = validate(old)
            self.assertEqual(old, before)
            self.assertEqual(migrated["version"], 7)
            self.assertEqual(migrated["investigation"], old["investigation"])
            self.assertEqual(migrated["progress"]["run_id"], self.g.run_id)
            data = migrated["progress"]["campaign_data"]
            self.assertEqual(data["team_done"], flags)
            self.assertEqual(data["view"], view)
            self.assertFalse(data["team_ready"])
            if view == "complete":
                self.g.saved_game = migrated
                self.g.continue_game()
                self.c = self.g.campaign
                self.click("next")
                self.assertEqual(self.c.data["chapter"], 4)
                self.assertEqual(self.g.investigation.score, 237)

    def test_close_during_team_analysis_records_score_and_keeps_save_valid(self):
        with TemporaryDirectory() as folder:
            store = Mock()
            g = Game(self.screen, self.root, Path(folder) / "save.json", ranking_store=store)
            g.start_game(player_name="Equipe", visual=True)
            g.campaign_data.update(chapter=8, view="team_task", team_ready=True, team_round=1, team_selection=[2])
            g.investigation.score = 621
            g.handle_events([pygame.event.Event(pygame.QUIT)])
            self.assertFalse(g.running)
            self.assertEqual(store.record.call_args.args[2], 621)
            self.assertEqual(store.record.call_args.kwargs["phase"], 8)
            self.assertEqual(g.save_store.load()["progress"]["campaign_data"]["view"], "ended")

    def test_team_task_and_roster_text_fits_every_screen(self):
        for chapter, rounds in TEAM_TASKS.items():
            for index, task in enumerate(rounds):
                self.c.data.update(chapter=chapter, view="team_task", team_ready=True, team_round=index, team_selection=[])
                with patch("scripts.aventura_visual.draw_text", wraps=draw_text) as render:
                    self.g.draw()
                for call in render.call_args_list:
                    _, text, font, _, rect = call.args
                    lines = len(wrap_text(text, font, rect.width))
                    height = lines * font.get_height() + max(0, lines - 1) * call.kwargs.get("line_spacing", 5)
                    self.assertLessEqual(height, rect.height, (chapter, index, text))
                for b in self.c.buttons():
                    self.assertTrue(self.screen.get_rect().contains(b.rect))
        self.c.team.roster_open = True
        for page in (0, 1):
            self.c.team.roster_page = page
            self.g.draw()

    def test_invalid_team_save_is_rejected(self):
        for changes in ({"team_round": 99}, {"team_selection": [99]}, {"view": "team_task"},
                        {"team_ready": True, "team_done": [1]}, {"team_selection": [1, 1]}):
            data = deepcopy(self.c.data)
            data.update(changes)
            with self.assertRaises(ValueError):
                validate_visual(data)

    def test_final_review_happens_before_transmission_and_completion(self):
        self.c.data.update(chapter=8, view="explore", flags=list(range(1, 8)), stars=[3] * 7,
                           team_done=list(range(1, 8)))
        self.click(("task", 0))
        self.solve_screen()
        self.solve_screen()
        self.assertEqual(self.c.data["view"], "team_task")
        self.assertNotIn("pulse", [b.value for b in self.c.buttons()])
        self.assertEqual(self.c.data["hits"], 0)
        for _ in range(5):
            self.solve_screen()
        self.assertEqual(self.c.data["view"], "timing")
        self.assertIn(8, self.c.data["team_done"])
        self.assertNotIn(8, self.c.data["flags"])
        self.assertNotIn("x_final", self.g.investigation.evidence)
        self.g.saved_game = validate(snapshot(self.g))
        self.g.continue_game()
        self.c = self.g.campaign
        self.assertEqual(self.c.data["view"], "timing")
        self.solve_screen()
        self.assertEqual(self.c.data["view"], "complete")
        self.assertIn("x_final", self.g.investigation.evidence)
        self.assertEqual(self.g.investigation.score, 205)

    def test_old_partial_transmission_requires_review_without_losing_packets(self):
        self.c.data.update(chapter=8, view="timing", hits=2, locks=2,
                           flags=list(range(1, 8)), stars=[3] * 7, team_done=list(range(1, 8)))
        self.g.investigation.score = 650
        self.g.saved_game = validate(snapshot(self.g))
        self.g.continue_game()
        self.c = self.g.campaign
        self.assertEqual(self.c.data["view"], "team_task")
        self.assertEqual(self.c.data["hits"], 2)
        self.assertEqual(self.g.investigation.score, 650)
        for _ in range(5):
            self.solve_screen()
        self.assertEqual(self.c.data["view"], "timing")
        self.assertEqual(self.c.data["hits"], 2)
        self.solve_screen()
        self.assertEqual(self.c.data["view"], "complete")
        self.assertEqual(self.g.investigation.score, 805)

    def test_old_finished_transmission_does_not_have_to_be_sent_twice(self):
        self.c.data.update(chapter=8, view="team_task", hits=4, locks=3, team_ready=True,
                           team_round=4, flags=list(range(1, 8)), stars=[3] * 7, team_done=list(range(1, 8)))
        self.g.investigation.score = 650
        self.solve_screen()
        self.assertEqual(self.c.data["view"], "complete")
        self.assertEqual(self.g.investigation.score, 740)
