import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TestComponentFrontend(unittest.TestCase):
    def test_component_has_no_external_cdn_dependency(self):
        html = (ROOT / "scene_component" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("unpkg.com", html)
        self.assertNotIn("https://", html)

    def test_ui_styles_do_not_require_remote_font_assets(self):
        from ui_html import css
        self.assertNotIn("@import", css("en"))
        self.assertNotIn("fonts.googleapis.com", css("ar"))

    def test_component_implements_streamlit_handshake_and_value_bridge(self):
        html = (ROOT / "scene_component" / "index.html").read_text(encoding="utf-8")
        self.assertIn("streamlit:componentReady", html)
        self.assertIn("streamlit:render", html)
        self.assertIn("streamlit:setComponentValue", html)
        self.assertIn("streamlit:setFrameHeight", html)
        self.assertIn("lunabaseSceneEvent", html)

    def test_component_only_reloads_the_scene_when_the_scene_key_changes(self):
        html = (ROOT / "scene_component" / "index.html").read_text(encoding="utf-8")
        self.assertIn("scene_key", html)
        self.assertIn("key !== renderedKey", html)

    def test_component_relays_height_and_audio_unlock_from_the_scene_only(self):
        html = (ROOT / "scene_component" / "index.html").read_text(encoding="utf-8")
        self.assertIn("lunabaseFrameHeight", html)
        self.assertIn("lunabaseUnlockAudio", html)
        self.assertIn("event.source === frame.contentWindow", html)
