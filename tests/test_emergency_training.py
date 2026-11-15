import unittest
from simulation.emergency_training import DRILLS, evaluate_drill


class TestEmergencyTraining(unittest.TestCase):
    def test_all_three_scenarios_have_valid_answers(self):
        self.assertEqual(set(DRILLS), {"shelter", "isolate", "backup"})
        for drill_id, drill in DRILLS.items():
            result = evaluate_drill(drill_id, drill["correct"])
            self.assertTrue(result["ok"])
            self.assertTrue(result["correct"])

    def test_wrong_answers_do_not_pass(self):
        for drill_id, drill in DRILLS.items():
            wrong = next(choice for choice in drill["choices"] if choice != drill["correct"])
            result = evaluate_drill(drill_id, wrong)
            self.assertTrue(result["ok"])
            self.assertFalse(result["correct"])

    def test_invalid_drill_and_choice_are_rejected(self):
        self.assertFalse(evaluate_drill("unknown", "x")["ok"])
        self.assertFalse(evaluate_drill("shelter", "unknown")["ok"])


if __name__ == "__main__":
    unittest.main()
