"""Real-browser checks (Chromium via Playwright) of the music engine and the drag & drop scene.

Skipped automatically when Playwright/Chromium is not installed. The page below imitates Streamlit's structure:
parent page -> audio iframe + component iframe -> nested scene iframe.
"""
import html
import json
import os
import shutil
import tempfile
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover - optional dependency
    sync_playwright = None

from scene_explorer import scene_html  # noqa: E402
from ui_html import audio_controls_html  # noqa: E402

RES = {"water": 75, "oxygen": 80, "energy": 75, "food": 70, "protection": 65}
PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0"><h3 id="t">Mock Streamlit page</h3>
<iframe id="audio" height="42" style="width:100%;border:0" sandbox="allow-scripts allow-same-origin" allow="autoplay" srcdoc="__AUDIO__"></iframe>
<iframe id="comp" src="comp/index.html" style="width:100%;border:0;height:396px" sandbox="allow-scripts allow-same-origin" allow="autoplay"></iframe>
<script>
window.log=[];window.heights=[];const comp=document.getElementById('comp');
fetch('scenes.json').then(r=>r.json()).then(j=>{window.scenes=j});
window.render=(name,key)=>comp.contentWindow.postMessage({type:'streamlit:render',args:{html:scenes[name],scene_key:key||name}},'*');
window.addEventListener('message',e=>{const d=e.data;if(!d||!d.isStreamlitMessage)return;
 if(d.type==='streamlit:componentReady')window.ready=true;
 if(d.type==='streamlit:setComponentValue')window.log.push(d.value);
 if(d.type==='streamlit:setFrameHeight'){window.heights.push(d.height);comp.style.height=d.height+'px'}});
</script></body></html>"""


@unittest.skipIf(sync_playwright is None, "playwright is not installed")
class TestBrowserScene(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(cls.tmp, "comp"))
        shutil.copy(os.path.join(ROOT, "scene_component", "index.html"), os.path.join(cls.tmp, "comp", "index.html"))
        scenes = {"exterior": scene_html(RES, "en", "exterior", guide=True),
                  "exterior_saved": scene_html(RES, "en", "exterior", astronaut_offset=(40, 10), guide=False),
                  "ar": scene_html(RES, "ar", "exterior", guide=True)}
        with open(os.path.join(cls.tmp, "scenes.json"), "w", encoding="utf-8") as fh:
            json.dump(scenes, fh)
        with open(os.path.join(cls.tmp, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(PAGE.replace("__AUDIO__", html.escape(audio_controls_html("en"), quote=True)))

        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *a):
                pass

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=cls.tmp))
        cls.url = f"http://127.0.0.1:{cls.server.server_address[1]}/index.html"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.pw = sync_playwright().start()
        try:
            cls.browser_allowed = cls.pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
            cls.browser_blocked = cls.pw.chromium.launch(args=["--autoplay-policy=document-user-activation-required"])
        except Exception as exc:  # pragma: no cover - browser binary missing
            cls.pw.stop()
            cls.server.shutdown()
            raise unittest.SkipTest(f"Chromium unavailable: {exc}")

    @classmethod
    def tearDownClass(cls):
        for name in ("browser_allowed", "browser_blocked"):
            getattr(cls, name).close()
        cls.pw.stop()
        cls.server.shutdown()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def open(self, browser, width=1100, height=700):
        page = browser.new_page(viewport={"width": width, "height": height})
        self.errors = []
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        page.goto(self.url)
        page.wait_for_function("window.ready&&window.scenes")
        return page

    def audio_state(self, page):
        return page.evaluate("()=>({state:__lbAudio.ctx&&__lbAudio.ctx.state,mode:__lbAudio.mode()})")

    PEAK = """()=>{const A=window.__lbAudio;if(!window.__an){const an=A.ctx.createAnalyser();an.fftSize=2048;A.musicBus.connect(an);window.__an=an;window.__mx=0}
      const d=new Float32Array(2048);window.__an.getFloatTimeDomainData(d);let m=0;for(const x of d)m=Math.max(m,Math.abs(x));window.__mx=Math.max(window.__mx,m);return window.__mx}"""

    def measure_peak(self, page):
        page.evaluate(self.PEAK)
        peak = 0
        for _ in range(12):
            page.wait_for_timeout(250)
            peak = page.evaluate(self.PEAK)
        return peak

    # ---------------------------------------------------------------- music
    def test_music_autoplays_when_the_browser_allows_it(self):
        page = self.open(self.browser_allowed)
        page.wait_for_timeout(1000)
        self.assertEqual(self.audio_state(page), {"state": "running", "mode": "playing"})
        peak = self.measure_peak(page)
        self.assertGreater(peak, 0.01, "the song must actually produce sound")
        self.assertLess(peak, 0.95, "the song must not clip")
        self.assertEqual(self.errors, [])

    def test_music_starts_on_first_touch_when_autoplay_is_blocked(self):
        page = self.open(self.browser_blocked)
        page.wait_for_timeout(800)
        self.assertEqual(self.audio_state(page)["mode"], "blocked")
        self.assertIn("Tap anywhere", page.frame_locator("#audio").locator("#lb-music-toggle").inner_text())
        page.mouse.click(400, 15)
        page.wait_for_timeout(1200)
        self.assertEqual(self.audio_state(page), {"state": "running", "mode": "playing"})
        self.assertGreater(self.measure_peak(page), 0.01)

    def test_music_switch_off_is_remembered(self):
        page = self.open(self.browser_allowed)
        page.wait_for_timeout(800)
        toggle = page.frame_locator("#audio").locator("#lb-music-toggle")
        toggle.click()
        page.wait_for_timeout(300)
        self.assertEqual(self.audio_state(page)["mode"], "off")
        self.assertEqual(page.evaluate("localStorage.getItem('lb_music')"), "off")
        toggle.click()
        page.wait_for_timeout(500)
        self.assertEqual(self.audio_state(page)["mode"], "playing")

    # ---------------------------------------------------------------- scene
    def drag(self, page, selector, dx, dy):
        scene = page.frame_locator("#comp").frame_locator("iframe")
        cx, cy = scene.locator(selector).evaluate("e=>{const r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}")
        ox, oy = page.evaluate("()=>{const r=document.getElementById('comp').getBoundingClientRect();return [r.x,r.y]}")
        page.mouse.move(cx + ox, cy + oy)
        page.mouse.down()
        page.mouse.move(cx + ox + dx, cy + oy + dy, steps=12)
        page.mouse.up()
        page.wait_for_timeout(250)

    def scale(self, page):
        return page.frame_locator("#comp").frame_locator("iframe").locator("svg.art").evaluate("e=>e.getScreenCTM().a")

    def test_drag_and_drop_zones_events_and_music_unlock(self):
        page = self.open(self.browser_blocked)
        page.evaluate("render('exterior')")
        page.wait_for_timeout(700)
        k = self.scale(page)
        self.assertEqual(self.audio_state(page)["mode"], "blocked")
        self.drag(page, ".astro", 3, 1)                       # a light touch: moved, but no zone reward
        self.assertEqual([e["type"] for e in page.evaluate("window.log")], ["actor_moved"])
        self.assertEqual(self.audio_state(page)["mode"], "playing", "touching the scene unlocks the music")
        self.drag(page, ".astro", 178 * k, 10 * k)            # real drag to the HABITAT ring
        self.assertEqual(page.evaluate("window.log")[-1]["type"], "astro_door")
        self.drag(page, ".rover", 2, 0)
        self.assertEqual(page.evaluate("window.log")[-1]["type"], "actor_moved")
        self.drag(page, ".rover", -132 * k, -26 * k)          # real drag to the SCAN ring
        self.assertEqual(page.evaluate("window.log")[-1]["type"], "rover_scan")
        self.assertEqual(self.errors, [])

    def test_saved_offsets_are_absolute_and_same_key_does_not_reload(self):
        page = self.open(self.browser_allowed)
        page.evaluate("render('exterior_saved','k1')")
        page.wait_for_timeout(700)
        k = self.scale(page)
        scene = page.frame_locator("#comp").frame_locator("iframe")
        before = scene.locator(".astro").get_attribute("transform")
        page.evaluate("render('exterior_saved','k1')")
        page.wait_for_timeout(300)
        self.assertEqual(scene.locator(".astro").get_attribute("transform"), before)
        self.drag(page, ".astro", 20 * k, 0)
        self.assertEqual(page.evaluate("window.log")[-1]["offset"], {"x": 60, "y": 10})

    def test_keyboard_moves_the_astronaut(self):
        page = self.open(self.browser_allowed)
        page.evaluate("render('exterior_saved','k1')")
        page.wait_for_timeout(700)
        page.frame_locator("#comp").frame_locator("iframe").locator(".astro").focus()
        for _ in range(3):
            page.keyboard.press("ArrowRight")
        page.wait_for_timeout(900)
        self.assertEqual(page.evaluate("window.log")[-1]["offset"]["x"], 88)

    def test_phone_shows_the_whole_world_and_resizes_the_frame(self):
        page = self.open(self.browser_allowed, width=390, height=800)
        page.evaluate("render('exterior')")
        page.wait_for_timeout(900)
        self.assertIn(292, page.evaluate("window.heights"))
        scene = page.frame_locator("#comp").frame_locator("iframe")
        self.assertEqual(scene.locator("svg.art").get_attribute("preserveAspectRatio"), "xMidYMax meet")
        for selector in (".astro", ".rover"):
            box = scene.locator(selector).bounding_box()
            self.assertGreaterEqual(box["x"], 0)
            self.assertLessEqual(box["x"] + box["width"], 390)


if __name__ == "__main__":
    unittest.main()
