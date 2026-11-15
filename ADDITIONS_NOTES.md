# LunaBase – additive experience enhancements

This update keeps the existing mission rules, resource calculations, screens, modules, and game flow intact. It adds the following optional experience layer:

- **Button feedback:** short, synthesized confirmation sounds for enabled buttons. The sound is generated locally with the browser Web Audio API; no external audio file or service is required.
- **Critical-system warning:** when any of the five resources (water, oxygen, energy, food, or radiation protection) first reaches **20% or lower**, a bilingual `‼️` warning appears. It fades away after approximately five seconds and is not repeatedly shown while that resource remains in the critical range. If it rises above 20% and later becomes critical again, a new warning is shown.
- **Danger sound and navigation:** a short three-note alert plays and the page scrolls to the first critical resource gauge, which is visually highlighted.
- **Optional space ambience:** a quiet, original synthesized space ambience with a slow, gentle melody can be turned on or off with the `♫ Space ambience` control. It starts **off** and has its own volume slider. Browser audio policies require a user tap before audio can play.
- **Language control:** the existing language switch remains in the upper-left area and is now a compact globe icon.

## Validation

- Python compilation passed for the changed Python modules.
- All **67 automated tests** passed.
- The generated JavaScript passed Node.js syntax checks.

The Streamlit runtime itself could not be launched in the build environment because Streamlit was not installed and package downloads were unavailable. Please run the project in its normal environment using the existing `requirements.txt` to confirm browser-specific audio behavior on the target device.

## 2.5D lunar scene addition
- Added a responsive, self-contained SVG/CSS lunar outpost scene above the mission gauges: habitat dome, solar arrays, rover, junior astronaut, Earth, stars, and subtle motion/parallax styling.
- The scene reads the current game resource values directly and displays all five live percentages. Any resource at 20% or below is highlighted in red in the scene status and resource chips.
- English and Arabic labels are supported; the scene adapts its direction for Arabic. Reduced-motion preferences are respected.
- This is a lightweight 2.5D visual scene, not a real-time 3D engine. It adds no new runtime dependency and does not change the simulation engine, game rules, actions, or resource calculations.
- Validation after this addition: Python compilation passed and all **69 automated tests** passed. A live Streamlit/browser visual smoke test is still recommended on the target phone.

## Phase 1 – Drag & Move event integration
- Replaced the scene's presentation-only proximity toasts with structured scene events for habitat entry, lunar sample collection, and rover survey completion.
- Added a small Streamlit custom-component bridge (`scene_component/`) so touch/mouse interactions inside the scene iframe reach Python session state.
- Habitat entry switches to the interior view; sample collection and rover surveys update the mission score, learning points, decisions, and activity log.
- Added Arabic translations and regression coverage for the new scene-event bridge.
- Validation: 78/78 unit tests pass; Python syntax compilation passes. Full browser/device validation remains necessary because this build environment does not have Streamlit installed.

## Integrated mission phases (2026-11-14)

- **Phase 1 — Drag & Move:** retained the custom Streamlit scene bridge; astronaut and rover gestures produce application events.
- **Phase 2 — Life support:** retained the five linked resource gauges, daily consumption, action costs, dependencies, alerts, and Mission Coach.
- **Phase 3 — Interactive base:** retained exterior/interior/emergency/rover scene navigation and connected habitat entry to the game state; resource actions remain available in the command console.
- **Phase 4 — Scientific exploration:** added one-time surface-science objectives for sample collection, rover survey, possible ice-site evaluation, and landing-zone assessment.
- **Phase 5 — Emergencies:** added repeat-proof safety drills for radiation shelter, habitat isolation, and backup power; these are educational scenarios, not operational procedures.
- **Phase 6 — Greenhouse:** retained the seven-day greenhouse mission and its linked water/energy/food/oxygen flows, with EDEN ISS crop research data.
- **Phase 7 — NASA context:** retained NASA DONKI solar-flare lookup and added clearly labeled LRO/LOLA and lunar-water research context. Live LOLA terrain tiles are not integrated in this prototype.
- **Phase 8 — Learning evaluation:** added progress tracking and a downloadable educational certificate, with explicit wording that it is not an official astronaut qualification.

All game rewards and checklists are simplified educational mechanics, not real spacecraft specifications or flight procedures.

## Phase 1 focused refinement — Drag & Move reliability

- Drag completion now sends the actor identity and final X/Y offsets back to the Streamlit component bridge. Python stores those offsets in session state, so astronaut and rover positions survive component rerenders and scene changes.
- Added visible, animated drop-zone rings for the habitat entrance, sample site, and rover survey area.
- Enabled astronaut dragging inside the habitat as well as the exterior; interaction triggers are restricted to the scenes where their targets are visible.
- Enabled the rover survey target in the dedicated rover scene. The rover's movement bounds allow it to reach the survey zone.
- Kept movement touch/mouse based (no movement buttons), using pointer capture and requestAnimationFrame easing. Motion respects the reduced-motion preference for scene decoration.
- Validation: 85/85 Python tests pass; `py_compile` passes. Headless Chromium browser tests confirmed the nested iframe → component message bridge for sample collection and rover survey, with no browser JavaScript errors. A full Streamlit server/device run remains pending because Streamlit is not installed in this build environment.

## Phase 2 — Life Support System (2026-11-14)

- Added explicit health values for the water recycler, oxygen generator, and solar array.
- Equipment wears down at the end of each mission day; when a subsystem drops below 60%, its matching resource uses extra reserve per day.
- The existing Repair life-support action now restores water and oxygen and repairs all three subsystem health values by 18 points (capped at 100).
- Added a live equipment-health dashboard and a next-day base resource-use estimate. The estimate explicitly excludes random events and greenhouse flows.
- Added subsystem health to the downloadable mission report.
- Added Arabic translations and seven focused life-support tests.
- All 92 automated tests pass; `py_compile` passes. Full Streamlit browser/device testing remains dependent on the user's runtime environment.

## Phase 4 refinement — evidence-based lunar science missions

- Kept the existing drag-to-collect lunar sample and drag-to-survey rover interactions connected to the mission's one-time science rewards.
- Replaced the instant-complete ice and landing buttons with assessed multiple-choice decisions. The ice task teaches permanently shadowed regions and the need for multiple independent measurements; the landing task asks players to consider slope, rocks, lighting, communications, and terrain knowledge.
- Incorrect answers provide a learning hint but do not complete the objective or award points. Correct answers complete the objective once and award the existing small learning reward.
- Added safe migration for older or partially populated science progress, persisted the accepted analysis answers, and included all four science objectives and accepted answers in the downloadable mission report.
- Added Arabic translations and nine focused tests for answer validation, duplicate rewards, progress migration, and report output.
- Validation: Python compilation passes and **101/101 automated tests pass**. A live Streamlit UI/browser test could not be run in this build environment because Streamlit is not installed; run `pip install -r requirements.txt` and launch the app in the target environment for final device verification.

Scientific caveat: these are simplified educational decisions. A possible ice signal does not prove accessible water, and the landing activity is not a real landing-site safety assessment or certification.


## Component recovery + Phase 5 implementation

- Removed the external `streamlit-component-lib` CDN script from `scene_component/index.html`. The local frontend now performs the Streamlit component-ready, render, frame-height, and component-value message handshake itself, and relays scene drag events to Python.
- Kept the artwork inline as SVG, and removed Google Fonts `@import` dependencies so the scene and typography do not rely on external asset hosts.
- Replaced one-click emergency completion with three multiple-choice scenarios: radiation shelter, habitat leak isolation, and backup-power management. A drill only completes and awards its existing one-time reward after the correct choice.
- Added contextual Mission Coach guidance, saved accepted decisions, backward-compatible game-state migration, and emergency-training details in the downloadable mission report.
- Added Arabic translations and regression tests for offline component initialization, message bridge protocol, correct/incorrect emergency answers, translation coverage, migration, and report output.
- Validation: **109/109 automated tests pass** and `compileall` passes. The Streamlit package is not installed in this build environment, so an actual Streamlit server/browser test is not claimed; verify once deployed.


## Phase 6 — Greenhouse climate management

- Added interactive greenhouse climate controls for temperature (18–24 °C target), relative humidity (55–75%), light period (14–18 hours), and nutrient-solution pH (5.5–6.5).
- Added a transparent, deterministic climate assessment. One or two moderate deviations reduce the simulated growth factor to 80%; three or more deviations or a severe deviation reduce it to 55%. All target ranges and multipliers are educational game assumptions, not lunar-agriculture engineering standards.
- The climate factor now affects the harvest forecast and the end-of-day greenhouse yield alongside the existing base energy, water, and care factors.
- Climate settings are saved in mission state; each applied greenhouse flow records the environment snapshot and growth factor, and the mission report includes the latest climate result.
- Preserved the existing EDEN ISS crop-yield data and greenhouse tasks; no claim is made that a seven-day mission grows mature fruit from seed.
- Added six focused greenhouse-control tests and Arabic translations.
- Validation: **115/115 automated tests pass**, `compileall` passes. Streamlit is not installed in this build environment, so a live Streamlit browser test remains to be performed in the deployment environment.


## Review & fix pass (2026-11-15) — drag & drop first view, autoplay music, scene reliability

**Experience**
- **First view = the draggable scene.** After the ID page the child lands directly on the moon scene (above the mission header). A first-play tutorial shows an animated hand and dashed arrow from the astronaut to the glowing HABITAT ring; it disappears at the first touch. Scene selector sits under the scene and stays on one row on phones.
- **Music starts by itself on entry.** A new original synthesized song ("Moon Lullaby": melody + bass + soft pads, 92 BPM, 8-bar loop, no audio files) starts on the very first page. Browsers may refuse sound before any interaction; in that case the button reads "Tap anywhere to start the music" and the first touch / click / key press anywhere — including a touch on the scene — starts it. Switching it off is remembered (localStorage); the song pauses when the tab is hidden.

**Bugs fixed**
1. A 3 px nudge of the astronaut or rover triggered "sample collected" / "rover survey" because the actors start inside the zone tolerance. Now the actor's *centre* must be inside the ring and it must have been dragged at least 14 units.
2. Saved drag offsets were reported relative to the already-offset position after a rerun, so the actor snapped back to a wrong place. The scene now recovers the true base position and always reports absolute offsets.
3. On phones the SVG was cropped to its middle 38%, hiding the astronaut, rover and two zones. Phones now show the whole world, the frame height follows the scene, and ring labels are legible. Zone labels were hidden under the resource chips on all screens; they now sit above the rings.
4. The scene iframe reloaded (flicker, lost drag) on every Streamlit rerun. The component now reloads only when the scene itself changes (`scene_key`), and a plain drag no longer causes an extra rerun.
5. The old ambience reported "on" while the browser kept the audio context suspended (silent), and queued notes burst out on resume. The engine now schedules against the audio clock and shows the real state.
6. The "scene tabs" stacked into four full-width rows on phones; they stay on one row now.
7. The interaction message stayed on screen forever; it is shown once.
8. Entering the habitat keeps the astronaut at the entrance (the exterior offset no longer leaks inside).
9. Safety-checklist widget keys used Python `hash()` (different in every server process); now stable.
10. `components.html` is deprecated since Streamlit 1.56: the audio frame is wrapped so a future removal cannot crash the game.
11. Scene actors are keyboard accessible (Tab, arrow keys; Shift = bigger step).
12. Launchers install requirements on first run (`RUN_LUNABASE.bat`, new `RUN_LUNABASE.sh`).

**Verification** — 133 unit/flow tests + 7 real-Chromium tests (music autoplay allowed/blocked, drag zones, absolute offsets, keyboard, phone layout). `app.py` was also executed end-to-end against a fake Streamlit API (welcome → play → events → every scene × module in EN/AR → win/loss/retry). A bot played 1,440 full missions in EN/AR with no exception (Easy 100% / Normal 100% / Hard ≈64% wins).

**Not verified here:** a real `streamlit run` session (Streamlit could not be installed in the build sandbox). Run it once on the target device.
