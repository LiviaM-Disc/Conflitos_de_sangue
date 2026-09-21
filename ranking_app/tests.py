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
