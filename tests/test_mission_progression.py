import unittest
from simulation.game_engine import create_new_game
from simulation.mission_progression import (SCIENCE_OBJECTIVES, complete_emergency_drill,
    ensure_progress, record_science, certificate_text)

class TestMissionProgression(unittest.TestCase):
    def setUp(self):
        self.game = create_new_game(seed=4)
        ensure_progress(self.game)

    def test_science_objective_rewards_once(self):
        before = self.game['score']
        first = record_science(self.game, 'ice')
        second = record_science(self.game, 'ice')
        self.assertTrue(first['ok'])
        self.assertFalse(second['ok'])
        self.assertEqual(self.game['score'], before + 5)
        self.assertTrue(self.game['science']['ice'])

    def test_all_surface_objectives_are_defined(self):
        self.assertEqual({x['id'] for x in SCIENCE_OBJECTIVES}, {'sample','rover','ice','landing'})

    def test_emergency_drill_is_one_time(self):
        self.assertTrue(complete_emergency_drill(self.game, 'shelter')['ok'])
        self.assertFalse(complete_emergency_drill(self.game, 'shelter')['ok'])
        self.assertEqual(len(self.game['emergency_drills']), 1)

    def test_progress_migration_adds_emergency_answer_storage(self):
        self.assertIsInstance(self.game["emergency_answers"], dict)

    def test_report_includes_emergency_training_progress(self):
        from simulation.game_engine import build_report
        self.game["emergency_drills"] = ["shelter"]
        self.game["emergency_answers"] = {"shelter": "shelter"}
        report = build_report(self.game)
        self.assertIn("Emergency training:", report)
        self.assertIn("Radiation shelter scenario: Completed", report)
        self.assertIn("Guide the crew to the designated shielded shelter", report)

    def test_certificate_is_clear_about_educational_status(self):
        cert = certificate_text(self.game, 'Nova')
        self.assertIn('Awarded to: Nova', cert)
        self.assertIn('not an official astronaut qualification', cert)

if __name__ == '__main__':
    unittest.main()
