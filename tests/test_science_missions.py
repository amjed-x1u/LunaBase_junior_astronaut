import unittest
from simulation.science_missions import SCIENCE_ANALYSIS, check_science_answer
from simulation.mission_progression import ensure_progress, record_science
from simulation.game_engine import build_report, create_new_game


class TestScienceMissions(unittest.TestCase):
    def test_each_analysis_has_one_defined_correct_answer(self):
        self.assertEqual(set(SCIENCE_ANALYSIS), {"ice", "landing"})
        for objective, task in SCIENCE_ANALYSIS.items():
            self.assertIn(task["answer"], task["choices"])
            self.assertGreaterEqual(len(task["choices"]), 3)

    def test_ice_answer_teaches_evidence_not_proof(self):
        result = check_science_answer("ice", "shadowed")
        self.assertTrue(result["correct"])
        self.assertIn("not proof", result["feedback"])

    def test_ice_wrong_answer_does_not_pass(self):
        self.assertFalse(check_science_answer("ice", "visual")["correct"])

    def test_landing_answer_uses_multiple_hazards(self):
        result = check_science_answer("landing", "level")
        self.assertTrue(result["correct"])
        self.assertIn("engineering data", result["feedback"])

    def test_unknown_question_or_answer_is_rejected(self):
        self.assertFalse(check_science_answer("unknown", "level")["correct"])
        self.assertFalse(check_science_answer("landing", "made_up")["correct"])
        self.assertFalse(check_science_answer("landing", ["level"])["correct"])

    def test_progress_migration_preserves_existing_science_and_adds_missing_fields(self):
        game = {"science": {"sample": True}}
        ensure_progress(game)
        self.assertTrue(game["science"]["sample"])
        self.assertFalse(game["science"]["ice"])
        self.assertIn("science_answers", game)

    def test_recording_analysis_objective_awards_once(self):
        game = create_new_game(seed=11)
        ensure_progress(game)
        first = record_science(game, "ice")
        second = record_science(game, "ice")
        self.assertTrue(first["ok"])
        self.assertFalse(second["ok"])
        self.assertEqual(game["score"], 5)
        self.assertEqual(game["learning_points"], 1)

    def test_all_four_objectives_can_be_recorded_once(self):
        game = create_new_game(seed=13)
        ensure_progress(game)
        for objective in ("sample", "rover", "ice", "landing"):
            self.assertTrue(record_science(game, objective)["ok"])
            self.assertFalse(record_science(game, objective)["ok"])
        self.assertEqual(sum(game["science"].values()), 4)
        self.assertEqual(game["score"], 20)

    def test_mission_report_includes_science_progress_and_answer(self):
        game = create_new_game(seed=12)
        ensure_progress(game)
        record_science(game, "ice")
        game["science_answers"]["ice"] = "shadowed"
        report = build_report(game)
        self.assertIn("Surface science objectives:", report)
        self.assertIn("Water-ice investigation: Completed", report)
        self.assertIn("permanently shadowed", report)


if __name__ == "__main__":
    unittest.main()
