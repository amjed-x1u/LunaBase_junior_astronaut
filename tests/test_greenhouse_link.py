import random
import unittest
from simulation.eden_iss_data import CROPS, CATEGORY_YIELD_KG, TOTALS, crops_ready_within, get_crop, shortest_cycle
from simulation.game_engine import advance_day, build_report, create_new_game
from simulation.greenhouse_link import (BEDS_M2, FOOD_KG_PER_POINT, TASKS_PER_DAY, apply_greenhouse_flows,
                                        plan_daily_flows, potential_harvest_kg_per_day)
from simulation.greenhouse_mission import DAILY_TASKS, complete_task, create_greenhouse_mission
from ai.mission_coach import get_coach_advice


def linked_game(**kw):
    g = create_new_game("Normal", seed=kw.get("seed", 1))
    g["greenhouse"] = create_greenhouse_mission()
    return g


def do_tasks(g, n):
    for task in DAILY_TASKS[g["greenhouse"]["day"]][:n]:
        complete_task(g["greenhouse"], task)


class TestEdenData(unittest.TestCase):
    def test_paper_totals(self):
        self.assertAlmostEqual(sum(CATEGORY_YIELD_KG.values()), TOTALS["edible_fresh_kg"], delta=1.0)
        self.assertAlmostEqual(TOTALS["productivity_kg_m2_286d"] / 286, TOTALS["productivity_kg_m2_d"], places=3)

    def test_no_crop_finishes_in_seven_days(self):
        self.assertEqual(crops_ready_within(7), [])
        self.assertGreater(shortest_cycle()["cycle_days"], 20)

    def test_cucumber_is_highest_rate(self):
        self.assertEqual(max(CROPS, key=lambda c: c["rate_kg_m2_d"])["name"], "Cucumber Picowell")

    def test_beds_use_known_crops(self):
        for name in BEDS_M2:
            get_crop(name)


class TestGreenhouseLink(unittest.TestCase):
    def test_not_linked_changes_nothing(self):
        g = create_new_game(seed=1)
        self.assertEqual(apply_greenhouse_flows(g), [])
        self.assertIsNone(g["greenhouse"])

    def test_full_care_matches_eden_yield(self):
        g = linked_game()
        do_tasks(g, TASKS_PER_DAY)
        p = plan_daily_flows(g)
        self.assertAlmostEqual(p["kg"], potential_harvest_kg_per_day())
        self.assertEqual(p["food"], round(potential_harvest_kg_per_day() / FOOD_KG_PER_POINT))

    def test_neglect_gives_no_food_but_still_costs(self):
        g = linked_game()
        before = dict(g["resources"])
        msgs = apply_greenhouse_flows(g)
        self.assertEqual(g["resources"]["food"], before["food"])
        self.assertLess(g["resources"]["energy"], before["energy"])
        self.assertTrue(any("tasks were done" in m for m in msgs))

    def test_low_energy_dims_lights(self):
        g = linked_game()
        do_tasks(g, TASKS_PER_DAY)
        full = plan_daily_flows(g)["kg"]
        g["resources"]["energy"] = 10
        p = plan_daily_flows(g)
        self.assertTrue(p["dim_lights"])
        self.assertAlmostEqual(p["kg"], full * 0.5)

    def test_flows_reset_task_counter_and_accumulate(self):
        g = linked_game()
        do_tasks(g, TASKS_PER_DAY)
        apply_greenhouse_flows(g)
        gh = g["greenhouse"]
        self.assertEqual(gh["tasks_since_flow"], 0)
        self.assertEqual(gh["linked_days"], 1)
        self.assertGreater(gh["harvest_kg"], 0)

    def test_repeated_task_cannot_farm_care(self):
        g = linked_game()
        t = DAILY_TASKS[1][0]
        for _ in range(5):
            complete_task(g["greenhouse"], t)
        self.assertEqual(g["greenhouse"]["tasks_since_flow"], 1)

    def test_advance_day_applies_flows(self):
        a = create_new_game("Normal", seed=7)
        b = create_new_game("Normal", seed=7)
        b["greenhouse"] = create_greenhouse_mission()
        do_tasks(b, TASKS_PER_DAY)
        advance_day(a)
        advance_day(b)
        self.assertEqual(a["last_event"], b["last_event"])  # rng stream is unchanged
        self.assertGreater(b["greenhouse"]["harvest_kg"], 0)
        self.assertEqual(b["greenhouse"]["linked_days"], 1)

    def test_completed_mission_stops_flows(self):
        g = linked_game()
        g["greenhouse"]["status"] = "completed"
        self.assertEqual(apply_greenhouse_flows(g), [])

    def test_resources_stay_in_range_random_runs(self):
        for seed in range(300):
            rng = random.Random(seed)
            g = create_new_game(rng.choice(["Easy", "Normal", "Hard"]), rng.choice(["commander", "engineer", "botanist", "life_support"]), seed)
            g["greenhouse"] = create_greenhouse_mission()
            for _ in range(10):
                if g["status"] != "active":
                    break
                if g["pending_challenge"]:
                    g["pending_challenge"] = None
                do_tasks(g, rng.randint(0, 3))
                advance_day(g)
                for v in g["resources"].values():
                    self.assertTrue(0 <= v <= 100)

    def test_report_and_coach_mention_greenhouse(self):
        g = linked_game()
        self.assertIn("greenhouse", " ".join(get_coach_advice(g)["recommendations"]).lower())
        do_tasks(g, TASKS_PER_DAY)
        advance_day(g)
        self.assertIn("Greenhouse: linked 1 day", build_report(g))


if __name__ == "__main__":
    unittest.main()
