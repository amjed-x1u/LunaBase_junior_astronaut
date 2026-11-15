import unittest
from simulation.greenhouse_mission import DAILY_TASKS, MAX_GREENHOUSE_DAYS, advance_greenhouse_day, complete_task, create_greenhouse_mission, greenhouse_summary

class TestGreenhouseMission(unittest.TestCase):
    def test_requires_all_daily_tasks(self):
        mission = create_greenhouse_mission()
        self.assertFalse(advance_greenhouse_day(mission)["ok"])
        self.assertEqual(mission["day"], 1)

    def test_duplicate_task_does_not_inflate_score(self):
        mission = create_greenhouse_mission()
        task = DAILY_TASKS[1][0]
        complete_task(mission, task)
        complete_task(mission, task)
        self.assertEqual(mission["score"], 1)

    def test_seven_day_completion(self):
        mission = create_greenhouse_mission()
        for day in range(1, MAX_GREENHOUSE_DAYS + 1):
            for task in DAILY_TASKS[day]:
                self.assertTrue(complete_task(mission, task)["ok"])
            self.assertTrue(advance_greenhouse_day(mission)["ok"])
        self.assertEqual(mission["status"], "completed")
        self.assertEqual(greenhouse_summary(mission)["progress_percent"], 100)

    def test_rejects_unknown_task(self):
        mission = create_greenhouse_mission()
        self.assertFalse(complete_task(mission, "Harvest tomatoes in seven days")["ok"])

    def test_missing_tasks_message_names_remaining_count(self):
        mission = create_greenhouse_mission()
        complete_task(mission, DAILY_TASKS[1][0])
        result = advance_greenhouse_day(mission, base_day=1)
        self.assertFalse(result["ok"])
        self.assertIn("3 remaining", result["message"])

    def test_one_greenhouse_day_per_base_day(self):
        mission = create_greenhouse_mission()
        for task in DAILY_TASKS[1]:
            complete_task(mission, task)
        self.assertTrue(advance_greenhouse_day(mission, base_day=3)["ok"])
        for task in DAILY_TASKS[2]:
            complete_task(mission, task)
        blocked = advance_greenhouse_day(mission, base_day=3)
        self.assertFalse(blocked["ok"])
        self.assertEqual(mission["day"], 2)
        self.assertTrue(advance_greenhouse_day(mission, base_day=4)["ok"])

if __name__ == "__main__":
    unittest.main()
