import unittest
from scene_explorer import scene_html


class TestSceneExplorer(unittest.TestCase):
    def setUp(self):
        self.resources = {"water": 80, "oxygen": 75, "energy": 66, "food": 90, "protection": 85}

    def test_all_four_scenes_render_distinct_content(self):
        exterior = scene_html(self.resources, "en", "exterior")
        interior = scene_html(self.resources, "en", "interior")
        emergency = scene_html(self.resources, "en", "emergency")
        rover = scene_html(self.resources, "en", "rover")
        self.assertIn("EXTERIOR OUTPOST", exterior)
        self.assertIn("LIFE SUPPORT", interior)
        self.assertIn("MISSION CONTROL", emergency)
        self.assertIn("SURFACE SURVEY", rover)
        self.assertNotEqual(exterior, interior)
        self.assertNotEqual(interior, rover)

    def test_emergency_scene_uses_live_critical_resources(self):
        self.resources["oxygen"] = 12
        html = scene_html(self.resources, "en", "emergency")
        self.assertIn("OXYGEN", html)
        self.assertIn("12%", html)
        self.assertIn("CRITICAL", html)

    def test_arabic_scene_is_rtl_and_localized(self):
        html = scene_html(self.resources, "ar", "interior")
        self.assertIn("داخل القاعدة", html)
        self.assertIn("direction:rtl", html)
        self.assertIn("الأكسجين", html)

    def test_rover_scan_message_changes_with_scan_index(self):
        first = scene_html(self.resources, "en", "rover", 1)
        second = scene_html(self.resources, "en", "rover", 3)
        self.assertIn("layered lunar rocks", first)
        self.assertIn("ancient impact craters", second)

    def test_actor_offsets_change_svg_positions(self):
        moved_outside = scene_html(self.resources, "en", "exterior", astronaut_offset=(24, 18), rover_offset=(-24, 0))
        self.assertIn('translate(284 253)', moved_outside)
        self.assertIn('translate(676 265)', moved_outside)
        moved_inside = scene_html(self.resources, "en", "interior", astronaut_offset=(24, 18))
        self.assertIn('translate(154 243)', moved_inside)

    def test_resource_values_are_clamped_and_unknown_scene_falls_back(self):
        html = scene_html({"water": 180}, "en", "unknown")
        self.assertIn("100%", html)
        self.assertIn("EXTERIOR OUTPOST", html)

    def test_scene_actors_support_direct_touch_drag(self):
        html = scene_html(self.resources, "en", "exterior")
        self.assertIn('class="astro"', html)
        self.assertIn('class="rover"', html)
        self.assertIn("pointerdown", html)
        self.assertIn("pointermove", html)
        self.assertIn("requestAnimationFrame(animate)", html)
        self.assertIn("Drag the astronaut or rover", html)

    def test_drag_position_is_sent_back_to_game_state(self):
        html = scene_html(self.resources, "en", "exterior")
        self.assertIn("let type='actor_moved'", html)
        self.assertIn("sendEvent(type,a.kind", html)
        self.assertIn("{x:Math.round(a.tx),y:Math.round(a.ty)}", html)
        self.assertIn("const view='exterior'", html)

    def test_interaction_zones_are_visible_and_rover_scan_is_available_in_rover_view(self):
        exterior = scene_html(self.resources, "en", "exterior")
        rover = scene_html(self.resources, "en", "rover")
        self.assertIn('class="drop-zones"', exterior)
        self.assertIn("HABITAT", exterior)
        self.assertIn("SCAN AREA", rover)
        self.assertIn("view==='rover'", rover)

    def test_interior_astronaut_remains_draggable(self):
        html = scene_html(self.resources, "en", "interior")
        self.assertIn('<g class="astro" transform="translate(130 225)">', html)

    def test_scene_sends_real_events_to_streamlit_bridge(self):
        html = scene_html(self.resources, "en", "exterior")
        self.assertIn("lunabaseSceneEvent", html)
        self.assertIn("astro_door", html)
        self.assertIn("astro_sample", html)
        self.assertIn("rover_scan", html)

    def test_drag_hint_is_arabic_when_arabic_selected(self):
        html = scene_html(self.resources, "ar", "exterior")
        self.assertIn("اسحب رائد الفضاء أو المركبة بإصبعك", html)

    def test_a_light_touch_cannot_trigger_a_zone_and_offsets_are_absolute(self):
        html = scene_html(self.resources, "en", "exterior", astronaut_offset=(40, 10))
        self.assertIn("const MIN_DRAG=14", html)
        self.assertIn("moved>=MIN_DRAG", html)
        # the server bakes the saved offset into the transform; the script must subtract it to find the real base
        self.assertIn('INIT={"astro": [40, 10], "rover": [0, 0]}', html)
        self.assertIn("Number(m[1])-ox", html)

    def test_zone_labels_sit_above_the_rings_not_under_the_hud(self):
        html = scene_html(self.resources, "en", "exterior")
        for label_y in ('y="236"', 'y="222"', 'y="197"'):
            self.assertIn(label_y, html)
        self.assertNotIn('y="345"', html)

    def test_first_play_guide_is_optional_and_localized(self):
        plain = scene_html(self.resources, "en", "exterior")
        guided = scene_html(self.resources, "en", "exterior", guide=True)
        guided_ar = scene_html(self.resources, "ar", "exterior", guide=True)
        self.assertNotIn('class="guide"', plain)
        self.assertIn('class="guide"', guided)
        self.assertIn("scene exterior guided", guided)
        self.assertIn("Drag the astronaut into the glowing HABITAT circle", guided)
        self.assertIn("اسحب رائد الفضاء إلى الدائرة المضيئة", guided_ar)
        self.assertNotIn('class="guide"', scene_html(self.resources, "en", "interior", guide=True))

    def test_phone_layout_shows_the_whole_world_and_reports_its_height(self):
        html = scene_html(self.resources, "en", "exterior")
        self.assertIn("xMidYMax meet", html)
        self.assertIn("lunabaseFrameHeight", html)

    def test_keyboard_and_audio_unlock_support(self):
        html = scene_html(self.resources, "en", "exterior")
        self.assertIn("ArrowRight", html)
        self.assertIn("lunabaseUnlockAudio", html)
        self.assertIn("tabindex", html)


if __name__ == "__main__":
    unittest.main()
