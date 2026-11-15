import unittest
from simulation.game_engine import create_new_game, perform_action, advance_day
from simulation.life_support import daily_consumption, initial_subsystem_health, repair_subsystems, wear_subsystems


class TestLifeSupportPhaseTwo(unittest.TestCase):
    def test_new_game_starts_with_healthy_equipment(self):
        game = create_new_game(seed=7)
        self.assertEqual(game["subsystem_health"], initial_subsystem_health())

    def test_healthy_equipment_has_no_extra_daily_consumption(self):
        self.assertEqual(daily_consumption(1.0, initial_subsystem_health()),
                         {"water": 6, "oxygen": 5, "energy": 7, "food": 6})

    def test_damaged_equipment_increases_matching_resource_use(self):
        health = initial_subsystem_health()
        health.update(water_recycler=59, oxygen_generator=50, solar_array=40)
        self.assertEqual(daily_consumption(1.0, health),
                         {"water": 8, "oxygen": 7, "energy": 10, "food": 6})

    def test_equipment_wears_down_at_end_of_day(self):
        game = create_new_game(seed=3)
        before = dict(game["subsystem_health"])
        advance_day(game)
        self.assertEqual(game["subsystem_health"]["water_recycler"], before["water_recycler"] - 7)
        self.assertEqual(game["subsystem_health"]["oxygen_generator"], before["oxygen_generator"] - 6)
        self.assertEqual(game["subsystem_health"]["solar_array"], before["solar_array"] - 8)

    def test_repair_action_restores_all_subsystems(self):
        game = create_new_game(seed=4)
        game["subsystem_health"].update(water_recycler=50, oxygen_generator=70, solar_array=90)
        result = perform_action(game, "repair_system")
        self.assertTrue(result["ok"])
        self.assertEqual(game["subsystem_health"], {
            "water_recycler": 68, "oxygen_generator": 88, "solar_array": 100
        })

    def test_repair_caps_health_at_one_hundred(self):
        health = initial_subsystem_health()
        health["solar_array"] = 95
        restored = repair_subsystems(health, 18)
        self.assertEqual(health["solar_array"], 100)
        self.assertEqual(restored["solar_array"], 5)

    def test_wear_reports_crossing_maintenance_threshold(self):
        health = initial_subsystem_health()
        health["solar_array"] = 61
        worn = wear_subsystems(health)
        self.assertIn("solar_array", worn)
        self.assertEqual(health["solar_array"], 53)


if __name__ == "__main__":
    unittest.main()
