"""Executes app.py end to end against a fake Streamlit API (welcome -> play -> scene events -> modules -> end states)."""
import os
import random
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fake_streamlit as F  # noqa: E402

APP = os.path.join(ROOT, "app.py")
PROJECT_MODULES = ("panels", "theme", "ui_html", "scene_explorer")


class TestAppFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._old = F.install()
        cls._cwd = os.getcwd()
        os.chdir(ROOT)
        # panels/theme import `streamlit` at import time: drop any copy bound to a different streamlit
        for name in PROJECT_MODULES:
            sys.modules.pop(name, None)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._cwd)
        for name in PROJECT_MODULES:
            sys.modules.pop(name, None)
        F.uninstall(cls._old)

    def setUp(self):
        F.state.clear()
        F.CALLS.clear()
        F.CLICK.clear()
        F.COMPONENT.update(value=None, last_kwargs=None)

    def run_app(self):
        return F.run_app(APP)

    def enter(self, name="Sara"):
        self.run_app()
        F.state["player_input"] = name
        F.CLICK.add("enter_base")
        self.run_app()
        self.assertEqual(F.state.stage, "play")

    def emit(self, **event):
        event.setdefault("event_id", f"t-{len(F.CALLS['events'])}")
        F.CALLS["events"].append(event)
        F.COMPONENT["value"] = event
        return self.run_app()

    # ---- first view
    def test_welcome_then_first_view_is_the_draggable_scene_with_tutorial(self):
        self.run_app()
        self.assertEqual(F.state.stage, "welcome")
        self.assertTrue(any("components.html" in k for k in F.CALLS), "music control must load on the first page")
        self.enter()
        kwargs = F.COMPONENT["last_kwargs"]
        self.assertIsNotNone(kwargs, "the scene component must be rendered on entry")
        self.assertIn("Drag the astronaut into the glowing HABITAT circle", kwargs["html"])
        self.assertEqual(F.state.scene_view, "exterior")
        src = open(APP, encoding="utf-8").read()
        self.assertLess(src.index("scene_component("), src.index("header_html(g, MAX_DAYS"))

    def test_plain_drag_saves_position_without_reload_or_extra_rerun(self):
        self.enter()
        passes, _ = self.emit(type="actor_moved", actor="astro", offset={"x": 50, "y": -10})
        self.assertEqual(passes, 1)
        self.assertEqual(F.state.astronaut_offset, [50, -10])
        self.assertTrue(F.state.first_drag_done)
        key = F.COMPONENT["last_kwargs"]["scene_key"]
        self.run_app()
        self.assertEqual(F.COMPONENT["last_kwargs"]["scene_key"], key)
        self.assertNotIn("Drag the astronaut into", F.COMPONENT["last_kwargs"]["html"])

    def test_same_event_is_not_processed_twice(self):
        self.enter()
        self.emit(type="actor_moved", actor="astro", offset={"x": 5, "y": 5}, event_id="same")
        F.COMPONENT["value"] = {"type": "actor_moved", "actor": "astro", "offset": {"x": 99, "y": 0}, "event_id": "same"}
        self.run_app()
        self.assertEqual(F.state.astronaut_offset, [5, 5])

    def test_science_rewards_are_given_once(self):
        self.enter()
        before = F.state.game["score"]
        self.emit(type="astro_sample", actor="astro", offset={"x": -100, "y": 20})
        self.assertTrue(F.state.game["science"]["sample"])
        self.assertEqual(F.state.game["score"], before + 5)
        self.emit(type="astro_sample", actor="astro", offset={"x": -100, "y": 20})
        self.assertEqual(F.state.game["score"], before + 5)
        self.emit(type="rover_scan", actor="rover", offset={"x": -130, "y": -26})
        self.assertTrue(F.state.game["science"]["rover"])
        self.assertEqual(F.state.scene_view, "rover")
        self.assertEqual(F.state.rover_offset, [-130, -26])

    def test_door_enters_habitat_and_resets_astronaut(self):
        self.enter()
        self.emit(type="astro_door", actor="astro", offset={"x": 180, "y": 10})
        self.assertEqual(F.state.scene_view, "interior")
        self.assertEqual(F.state.astronaut_offset, [0, 0])

    def test_malformed_events_never_crash(self):
        self.enter()
        for i, bad in enumerate(({"type": "astro_door", "actor": "astro", "offset": "oops"}, {"type": "?"},
                                 {"actor": "rover", "offset": {"x": "NaN"}})):
            bad["event_id"] = f"bad-{i}"
            self.emit(**bad)

    # ---- everything renders
    def test_every_scene_and_module_renders_in_both_languages(self):
        self.enter()
        for lang in ("en", "ar"):
            F.state.lang = lang
            for view in ("exterior", "interior", "emergency", "rover"):
                F.state.scene_view = view
                self.run_app()
            for nav in ("greenhouse", "expedition", "systems", "history", "nasa", "learn", "about"):
                F.state.nav = nav
                self.run_app()

    def test_full_mission_win_loss_retry_and_critical_alert(self):
        from simulation.game_engine import resolve_food_challenge
        self.enter()
        F.state.game["rng"] = random.Random(3)   # the game's events are random: make this test deterministic
        for _ in range(12):
            if F.state.game["status"] != "active":
                break
            challenge = F.state.game.get("pending_challenge")
            if challenge:
                resolve_food_challenge(F.state.game, challenge["cause"], challenge["cause"])
            for action in ("act_solar_charge", "act_recycle_water"):
                F.CLICK.add(action)
                self.run_app()
            F.CLICK.add("end_day")
            self.run_app()
        self.assertEqual(F.state.game["status"], "won")
        for lang in ("en", "ar"):
            F.state.lang = lang
            self.run_app()
        self.assertTrue(any("download" in k for k in F.CALLS))
        F.state.game["status"] = "lost"
        F.state.game["failure_resource"] = "water"
        for lang in ("en", "ar"):
            F.state.lang = lang
            self.run_app()
        F.CLICK.add("retry")
        self.run_app()
        self.assertEqual(F.state.game["status"], "active")
        self.assertEqual(F.state.astronaut_offset, [0, 0])
        F.state.game["resources"]["oxygen"] = 15
        F.state.scene_view = "exterior"
        self.run_app()
        self.assertEqual(F.state.scene_view, "emergency")


if __name__ == "__main__":
    unittest.main()
