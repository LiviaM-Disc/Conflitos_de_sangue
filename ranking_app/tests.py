from uuid import uuid4
from django.test import TestCase
from ranking_app.models import Player, GameResult
from scripts.ranking import DjangoRanking, normalize_name


class RankingTests(TestCase):
    def setUp(self):
        self.store = DjangoRanking()
        self.store.initialized = True

    def test_normalization_and_invalid_names(self):
        self.assertEqual(normalize_name("  Ana   Silva "), "Ana Silva")
        self.store.player("Ana")
        self.store.player("ANA")
        self.assertEqual(Player.objects.count(), 1)
        for value in ("", " ", "-", "<script>", "a" * 25):
            with self.assertRaises(ValueError):
                normalize_name(value)

    def test_window_close_persists_actual_database_result_from_menu(self):
        import os
        from pathlib import Path
        from tempfile import TemporaryDirectory
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        import pygame
        from scripts.cenas import Game
        from scripts.salvamento import SaveStore
        pygame.init()
        try:
            with TemporaryDirectory() as folder:
                path = Path(folder) / "progress.json"
                game = Game(pygame.display.set_mode((1120, 720)),
                            Path(__file__).resolve().parents[1], path, ranking_store=self.store)
                game.start_game(player_name="Fechamento teste")
                game.campaign_data.update(chapter=4, room="garden", view="explore")
                game.investigation.score = 275
                game.reset_to_menu()
                game.handle_events([pygame.event.Event(pygame.QUIT)])
                self.assertFalse(game.running)
                result = GameResult.objects.get(id=game.run_id)
                self.assertEqual(result.score, 275)
                self.assertEqual(result.phase, 4)
                self.assertFalse(result.completed)
                self.assertEqual(self.store.standings()[0]["score"], 275)
                self.assertTrue(SaveStore(path).load()["progress"]["result_saved"])
                reopened = Game(game.screen, game.root, path, ranking_store=self.store)
                reopened.handle_events([pygame.event.Event(pygame.QUIT)])
                self.assertEqual(GameResult.objects.count(), 1)
        finally:
            pygame.quit()

    def test_best_score_ties_and_full_history(self):
        self.store.record(uuid4(), "Ana", 100, 3)
        self.store.record(uuid4(), "Ana", 80, 0)
        self.store.record(uuid4(), "Bia", 100, 1)
        self.store.record(uuid4(), "Caio", 100, 1)
        self.store.record(uuid4(), "Antigo", 999, 0, False)
        rows = self.store.standings("ana")
        self.assertEqual([r["name"] for r in rows], ["Bia", "Caio", "Ana"])
        self.assertEqual(rows[2]["score"], 100)
        self.assertTrue(rows[2]["current"])
        self.assertEqual(GameResult.objects.count(), 5)

    def test_retry_is_idempotent_and_conflicts_do_not_overwrite(self):
        run = uuid4()
        self.store.record(run, "Ana", 150, 2)
        self.store.record(run, "ana", 150, 2)
        self.assertEqual(GameResult.objects.count(), 1)
        with self.assertRaises(ValueError):
            self.store.record(run, "Ana", 151, 2)
        with self.assertRaises(ValueError):
            self.store.record(run, "Bia", 150, 2)
        self.assertEqual(GameResult.objects.get(pk=run).score, 150)
        self.assertFalse(Player.objects.filter(identity="bia").exists())

    def test_invalid_scores_rejected(self):
        for score, mistakes in ((-1, 0), (True, 0), (10, -1), (1000001, 0)):
            with self.assertRaises(ValueError):
                self.store.record(uuid4(), "Ana", score, mistakes)

    def test_early_result_enters_ranking_without_claiming_completion(self):
        run = uuid4()
        self.store.record(run, "Ana", 90, 2, completed=False, phase=2)
        self.store.record(run, "Ana", 90, 2, completed=False, phase=2)
        self.store.record(uuid4(), "Bia", 80, 0)
        rows = self.store.standings("Ana")
        self.assertEqual(rows[0]["name"], "Ana")
        self.assertFalse(rows[0]["completed"])
        self.assertEqual(rows[0]["phase"], 2)
        self.assertEqual(GameResult.objects.filter(player__nickname="Ana").count(), 1)
        with self.assertRaises(ValueError):
            self.store.record(run, "Ana", 90, 2, completed=True, phase=6)
        for phase in (-1, 7, True):
            with self.assertRaises(ValueError):
                self.store.record(uuid4(), "Ana", 90, 2, completed=False, phase=phase)
