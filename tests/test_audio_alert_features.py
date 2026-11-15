import unittest

from ui_html import audio_controls_html, danger_sound_html, gauges_html
from simulation.game_engine import RESOURCE_LABELS, create_new_game


class TestAudioAndDangerAdditions(unittest.TestCase):
    def test_optional_space_ambience_control_is_bilingual(self):
        en = audio_controls_html("en")
        ar = audio_controls_html("ar")
        self.assertIn("Space ambience", en)
        self.assertIn("موسيقى الفضاء", ar)
        self.assertIn("lb-music-toggle", en)
        self.assertIn("lb-music-volume", en)
        self.assertIn("state.toggle", en)

    def test_button_and_danger_sounds_are_generated_locally(self):
        html = audio_controls_html("en")
        self.assertIn("state.click", html)
        self.assertIn("state.danger", html)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)

    def test_critical_gauge_has_stable_navigation_target(self):
        game = create_new_game()
        game["resources"]["water"] = 20
        html = gauges_html(game["resources"], RESOURCE_LABELS)
        self.assertIn("id='lb-system-water'", html)
        self.assertIn("data-critical='true'", html)
        self.assertIn("data-critical='false'", html)

    def test_danger_sound_scrolls_to_critical_gauge(self):
        html = danger_sound_html()
        self.assertIn("scrollIntoView", html)
        self.assertIn("__lbAudio.danger()", html)

    def test_music_autoplays_on_entry_and_unlocks_on_first_gesture(self):
        html = audio_controls_html("en")
        self.assertIn("if(state.want)state.start();", html)          # autoplay attempt as soon as the page loads
        for ev in ("pointerdown", "touchstart", "keydown", "click"):
            self.assertIn(f"'{ev}'", html)                           # first gesture anywhere starts it
        self.assertIn("state.unlock", html)
        self.assertIn("Tap anywhere to start the music", html)
        self.assertIn("المس أي مكان لبدء الموسيقى", audio_controls_html("ar"))

    def test_music_is_a_looping_song_not_a_drone_and_respects_the_off_switch(self):
        html = audio_controls_html("en")
        self.assertIn("MEL=[", html)                                  # melody table
        self.assertIn("CHORD=[", html)
        self.assertIn("lb_music", html)                              # remembers when the player switched it off
        self.assertIn("visibilitychange", html)

    def test_audio_markup_has_no_unreplaced_placeholders(self):
        for lang in ("en", "ar"):
            self.assertNotRegex(audio_controls_html(lang), r"__[A-Z]+__")


if __name__ == "__main__":
    unittest.main()
