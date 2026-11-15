import unittest
from simulation.greenhouse_controls import DEFAULT_ENVIRONMENT, assess_environment, environment_snapshot
from simulation.greenhouse_link import apply_greenhouse_flows, plan_daily_flows
from simulation.greenhouse_mission import create_greenhouse_mission, DAILY_TASKS, complete_task
from simulation.game_engine import create_new_game


class TestGreenhouseControls(unittest.TestCase):
    def test_default_environment_is_within_target(self):
        result = assess_environment()
        self.assertEqual(result["status"], "optimal")
        self.assertEqual(result["factor"], 1.0)

    def test_moderate_deviation_reduces_growth_factor(self):
        result = assess_environment({**DEFAULT_ENVIRONMENT, "humidity_pct": 50})
        self.assertEqual(result["deviations"], 1)
        self.assertEqual(result["factor"], 0.8)

    def test_severe_deviation_reduces_growth_factor_further(self):
        result = assess_environment({**DEFAULT_ENVIRONMENT, "temperature_c": 35})
        self.assertEqual(result["factor"], 0.55)

    def test_snapshot_is_detached(self):
        env = dict(DEFAULT_ENVIRONMENT)
        snap = environment_snapshot(env)
        snap["temperature_c"] = 99
        self.assertEqual(env["temperature_c"], 21)

    def test_climate_changes_harvest_forecast(self):
        game = create_new_game(seed=1)
        game["greenhouse"] = create_greenhouse_mission()
        for task in DAILY_TASKS[1]:
            complete_task(game["greenhouse"], task)
        normal = plan_daily_flows(game)
        game["greenhouse"]["environment"]["humidity_pct"] = 50
        reduced = plan_daily_flows(game)
        self.assertLess(reduced["kg"], normal["kg"])
        self.assertEqual(reduced["climate"]["factor"], 0.8)

    def test_applied_flow_records_environment_history(self):
        game = create_new_game(seed=1)
        game["greenhouse"] = create_greenhouse_mission()
        apply_greenhouse_flows(game)
        self.assertEqual(len(game["greenhouse"]["environment_history"]), 1)
        self.assertEqual(game["greenhouse"]["environment_history"][0]["status"], "optimal")


if __name__ == "__main__":
    unittest.main()
