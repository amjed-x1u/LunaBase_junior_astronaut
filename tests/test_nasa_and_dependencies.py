import io, json, unittest
from simulation.nasa_data import parse_flares, summarize, fetch_recent_flares
from simulation.game_engine import create_new_game, apply_dependencies, dependency_warnings, advance_day, DIFFICULTIES


class FakeResp(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): return False


class TestNasaData(unittest.TestCase):
    def test_parse_and_summary(self):
        raw = [{"classType": "C2.1", "peakTime": "2026-11-01T01:00Z"}, {"classType": "M1.5", "beginTime": "x"}, {"bad": 1}, "junk", {"classType": "Z9"}]
        rows = parse_flares(raw)
        self.assertEqual(len(rows), 2)
        s = summarize(rows)
        self.assertEqual((s["count"], s["strongest"]), (2, "M1.5"))
        self.assertEqual(summarize([])["count"], 0)

    def test_fetch_ok_and_offline(self):
        ok = lambda url, timeout: FakeResp(json.dumps([{"classType": "X1.0"}]).encode())
        self.assertEqual(fetch_recent_flares(opener=ok)[0]["Class"], "X1.0")
        def boom(url, timeout): raise OSError("offline")
        self.assertIsNone(fetch_recent_flares(opener=boom))
        self.assertIsNone(fetch_recent_flares(opener=lambda u, timeout: FakeResp(b"not json")))


class TestDependencies(unittest.TestCase):
    def test_low_energy_drags_oxygen_and_water(self):
        g = create_new_game("Normal", seed=1); g["resources"]["energy"] = 10
        o, w = g["resources"]["oxygen"], g["resources"]["water"]
        self.assertTrue(dependency_warnings(g)); apply_dependencies(g, 1.0)
        self.assertLess(g["resources"]["oxygen"], o); self.assertLess(g["resources"]["water"], w)

    def test_no_penalty_when_healthy(self):
        g = create_new_game("Easy", seed=1)
        self.assertEqual(dependency_warnings(g), []); before = dict(g["resources"])
        self.assertEqual(apply_dependencies(g, 1.0), []); self.assertEqual(before, g["resources"])

    def test_dependency_message_in_advance_day(self):
        g = create_new_game("Normal", seed=2); g["resources"]["protection"] = 20
        msgs = advance_day(g)["messages"]
        self.assertTrue(any("🔗" in m for m in msgs))

    def test_hard_is_harder(self):
        self.assertGreater(DIFFICULTIES["Hard"]["mult"], DIFFICULTIES["Normal"]["mult"])


if __name__ == "__main__":
    unittest.main()
