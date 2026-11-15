import unittest
from ui_html import gauge, gauges_html, header_html, screen_html, status_of
from simulation.game_engine import create_new_game, RESOURCE_LABELS, MAX_DAYS


class TestUiHtml(unittest.TestCase):
    def test_status_levels(self):
        self.assertIn("Good", status_of(80)[0]); self.assertIn("Watch", status_of(30)[0]); self.assertIn("Danger", status_of(5)[0])

    def test_gauge_clamps_and_labels(self):
        self.assertIn("100", gauge("💧 Water", 250)); self.assertIn("aria-label", gauge("💧 Water", -5))

    def test_five_gauges(self):
        g = create_new_game()
        self.assertEqual(gauges_html(g["resources"], RESOURCE_LABELS).count("lb-gauge'>"), 5)

    def test_header_has_seven_day_leds_and_escapes(self):
        g = create_new_game(); g["astronaut"] = dict(g["astronaut"], name="<b>x</b>")
        h = header_html(g, MAX_DAYS)
        self.assertEqual(h.count("title='Day "), 7); self.assertNotIn("<b>x</b>", h)

    def test_screen_escapes_html(self):
        self.assertNotIn("<script>", screen_html(["<script>alert(1)</script>"]))


if __name__ == "__main__":
    unittest.main()


class TestWelcomeAndLoss(unittest.TestCase):
    def test_welcome_greets_the_hero_by_name_and_escapes(self):
        from ui_html import welcome_html
        h = welcome_html("<i>Sara</i>", "en")
        self.assertIn("Welcome to the Moon", h); self.assertNotIn("<i>", h); self.assertIn("&lt;i&gt;Sara", h)
        self.assertIn("Little Hero", welcome_html("", "en"))
        ar = welcome_html("سارة", "ar")
        self.assertIn("مرحبًا بك على القمر", ar); self.assertIn("سارة", ar)

    def test_loss_sign_shows_failed_resource(self):
        from ui_html import loss_sign_html
        g = create_new_game(seed=1); g["resources"]["oxygen"] = 2
        from simulation.game_engine import advance_day
        advance_day(g)
        self.assertEqual(g["status"], "lost"); self.assertEqual(g["failure_resource"], "oxygen")
        h = loss_sign_html(g, "en", "Sam")
        self.assertIn("MISSION FAILED", h); self.assertIn("OXYGEN FAILURE", h); self.assertIn("Sam", h); self.assertIn("role='alert'", h)
        self.assertIn("فشلت المهمة", loss_sign_html(g, "ar", "سام"))

    def test_rtl_css_only_for_arabic(self):
        from ui_html import css
        self.assertNotIn("direction:rtl", css("en")); self.assertIn("direction:rtl", css("ar"))

    def test_ui_helpers_translate(self):
        g = create_new_game(seed=1)
        self.assertIn("اليوم", header_html(g, MAX_DAYS, "ar")); self.assertIn("جيد", gauge("💧 Water", 80, "ar"))

class TestMissionScene(unittest.TestCase):
    def test_scene_shows_outpost_and_live_resource_values(self):
        from mission_scene import mission_scene_html
        html = mission_scene_html({"water": 88, "oxygen": 76, "energy": 54, "food": 63, "protection": 91}, "en")
        self.assertIn("LUNABASE · LUNAR OUTPOST", html)
        self.assertIn("88%", html)
        self.assertIn("ALL SYSTEMS NOMINAL", html)
        self.assertIn("class=\"astro\"", html)
        self.assertIn("class=\"rover\"", html)

    def test_scene_highlights_critical_resource_in_arabic(self):
        from mission_scene import mission_scene_html
        html = mission_scene_html({"water": 20, "oxygen": 80, "energy": 60, "food": 70, "protection": 90}, "ar")
        self.assertIn("خطر في الماء", html)
        self.assertIn("chip low", html)
        self.assertIn("direction:rtl", html)
