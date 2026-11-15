"""LunaBase - Junior Astronaut Mission Trainer (spaceship-console UI, English + Arabic)."""
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
scene_component = components.declare_component("lunabase_scene", path=str(Path(__file__).parent / "scene_component"))

st.set_page_config(page_title="LunaBase | Mission Console", page_icon="🌕", layout="wide",
                   initial_sidebar_state="collapsed")

import panels
import theme
from ai.mission_coach import get_coach_advice
from i18n import LANGS, tr
from simulation.game_engine import (ACTIONS, ASTRONAUTS, DIFFICULTIES, MAX_DAYS, RESOURCE_LABELS, advance_day,
                                    build_report, create_new_game, dependency_warnings, get_final_evaluation,
                                    get_status, perform_action)
from ui_html import (audio_controls_html, danger_sound_html, gauges_html, header_html, loss_sign_html,
                      screen_html, welcome_html)
from scene_explorer import scene_html
from simulation.mission_progression import ensure_progress, record_science, complete_emergency_drill, certificate_text, SCIENCE_OBJECTIVES
from simulation.life_support import SUBSYSTEMS, daily_consumption, subsystem_status

ss = st.session_state
ss.setdefault("lang", "en")          # "en" or "ar" - chosen by the player
ss.setdefault("stage", "welcome")    # "welcome" -> "play"
ss.setdefault("player", "")          # the child's name (optional)
ss.setdefault("scene_view", "exterior")
ss.setdefault("rover_scan_index", 0)
ss.setdefault("astronaut_offset", [0, 0])
ss.setdefault("rover_offset", [0, 0])
ss.setdefault("selected_actor", "astronaut")
ss.setdefault("sample_count", 0)
ss.setdefault("interaction_message", None)
ss.setdefault("first_drag_done", False)   # False -> the first-play tutorial (hand + arrow) is shown on the scene


def T(text, **kw):
    return tr(ss.lang, text, **kw)


def html_frame(markup, height):
    """Small script/HTML frame (music control, alarm sound). `components.html` is deprecated since Streamlit 1.56:
    if a future release removes it, the game must stay playable (just without sound) instead of crashing."""
    try:
        components.html(markup, height=height, scrolling=False)
    except Exception:  # noqa: BLE001 - never let an optional audio frame break the game
        pass


def new_game(difficulty="Normal", astronaut="commander"):
    ss.run_id = ss.get("run_id", 0) + 1
    ss.game = create_new_game(difficulty, astronaut, lang=ss.lang)
    ss.log = [T("Mission initialized. Welcome, {name}!", name=ss.player or T("Commander"))]
    ss.lesson = None
    ss.alert_result = None
    ss.gh_offer = False
    ss.gh_dialog = False
    ss.keep_fresh = None
    ss.gh_msg = None
    ss.gh_run = ss.get("gh_run", 0) + 1
    ss.critical_resources = []
    ss.scene_view = "exterior"
    ss.rover_scan_index = 0
    ss.astronaut_offset = [0, 0]
    ss.rover_offset = [0, 0]
    ss.selected_actor = "astronaut"
    ss.sample_count = 0
    ss.interaction_message = None
    # Clear phase-4 widget selections and feedback when a fresh mission starts.
    for key in ("science_answer_ice", "science_answer_landing",
                "science_feedback_ice", "science_feedback_landing"):
        ss.pop(key, None)


def enter_mission(difficulty="Normal", astronaut="commander"):
    """Leave the ID page: the very first thing the child sees is the draggable scene, with the tutorial hint."""
    ss.show_welcome_card = ss.show_id_card = True
    new_game(difficulty, astronaut)
    ss.first_drag_done = False
    ss.stage = "play"


def title(text):
    st.markdown(f"<span class='lb-title'>{text}</span>", unsafe_allow_html=True)


def set_lang(code):
    ss.lang = code
    if "game" in ss:
        ss.game["lang"] = code


def lang_buttons(where):
    """A small 🌐 button in the top-left corner: it switches to the other language (shows that language's name)."""
    other = "ar" if ss.lang == "en" else "en"
    with st.container(key=f"lang_box_{where}"):
        small, _ = st.columns([1, 9])
        small.button("🌐", key=f"lang_{where}_toggle", on_click=set_lang, args=(other,),
                     help=f"Language / اللغة · {LANGS[other]}")


# =========================================================================== WELCOME SCREEN
if ss.stage == "welcome":
    ss.player = str(ss.get("player_input", ss.player)).strip()  # newest typed name, so the card greets it at once
    theme.apply_theme(ss.lang)
    lang_buttons("welcome")
    html_frame(audio_controls_html(ss.lang), 42)
    ss.setdefault("show_welcome_card", True)
    ss.setdefault("show_id_card", True)

    def close_button(key):
        """Small round ✕ in the corner of a message card."""
        with st.container(key=f"close_box_{key}"):
            return st.button("✕", key=f"close_{key}", help=T("Close"))

    if ss.show_welcome_card:
        if close_button("welcome"):
            ss.show_welcome_card = False
            st.rerun()
        st.markdown(welcome_html(ss.player, ss.lang), unsafe_allow_html=True)
    if ss.show_id_card:
        _, mid, _ = st.columns([1, 2.4, 1])
        with mid:
            if close_button("id"):  # closing the ID card starts the mission with the default crew
                enter_mission("Normal", "commander")
                st.rerun()
            with st.container(border=True, key="panel_welcome"):
                title(T("🧑‍🚀 Your astronaut ID"))
                ss.player = st.text_input(T("What is your name, hero? (optional)"), value=ss.player, max_chars=20,
                                          key="player_input").strip()
                diff = st.selectbox(T("Difficulty"), list(DIFFICULTIES), index=1, format_func=T, key="w_diff")
                crew_by_id = {a["id"]: a for a in ASTRONAUTS}
                crew = st.selectbox(T("Astronaut"), list(crew_by_id), key="w_crew",
                                    format_func=lambda i: f"{T(crew_by_id[i]['name'])} — {T(crew_by_id[i]['role'])}")
                st.caption(T("{desc} Special ability: {bonus}", desc=T(crew_by_id[crew]["description"]),
                             bonus=T(crew_by_id[crew]["bonus"])))
                if st.button(T("🚀 Enter LunaBase"), type="primary", key="enter_base", width="stretch"):
                    enter_mission(diff, crew)
                    st.rerun()
    else:
        # both messages closed: only the enter button is left
        _, mid, _ = st.columns([1, 2.4, 1])
        with mid:
            if st.button(T("🚀 Enter LunaBase"), type="primary", key="enter_base_closed", width="stretch"):
                enter_mission("Normal", "commander")
                st.rerun()
    st.stop()

# =========================================================================== GAME
if "game" not in ss:
    new_game()
for key, default in (("log", []), ("lesson", None), ("alert_result", None), ("gh_run", 0)):
    ss.setdefault(key, default)
g = ss.game
g["lang"] = ss.lang
ensure_progress(g)

theme.apply_theme(ss.lang)
lang_buttons("play")
# Critical-resource alerts are additive: the game engine and its thresholds remain unchanged.
critical_now = {k: int(v) for k, v in g["resources"].items() if int(v) <= 20}
critical_previous = set(ss.get("critical_resources", []))
new_critical = {k: v for k, v in critical_now.items() if k not in critical_previous}
ss.critical_resources = list(critical_now)
if new_critical and get_status(g) == "active":
    ss.scene_view = "emergency"
html_frame(audio_controls_html(ss.lang), 42)

# ---- FIRST THING THE CHILD SEES: the interactive moon scene (drag the astronaut / rover with a finger).
# Presentation + events only: the simulation rules are untouched.
show_guide = ss.scene_view == "exterior" and not ss.first_drag_done
# The scene is reloaded only when this key changes (view, language, resources, new mission...), never on a plain drag.
scene_key = "|".join(str(x) for x in (ss.run_id, ss.lang, ss.scene_view, ss.rover_scan_index,
                                      *(g["resources"][k] for k in sorted(g["resources"]))))
scene_event = scene_component(
    html=scene_html(g["resources"], ss.lang, ss.scene_view, ss.rover_scan_index,
                    tuple(ss.astronaut_offset), tuple(ss.rover_offset), guide=show_guide),
    scene_key=scene_key,
    key="lunabase_interactive_scene",
    default=None,
)

# Scene selector (kept on ONE row even on phones, see theme CSS).
scene_options = [
    ("exterior", "🌕 الخارج" if ss.lang == "ar" else "🌕 Exterior"),
    ("interior", "🏠 القاعدة" if ss.lang == "ar" else "🏠 Habitat"),
    ("emergency", "🚨 الطوارئ" if ss.lang == "ar" else "🚨 Emergency"),
    ("rover", "🛻 المركبة" if ss.lang == "ar" else "🛻 Rover"),
]
with st.container(key="scene_tabs"):
    scene_cols = st.columns(4)
    for col, (scene_id, scene_label) in zip(scene_cols, scene_options):
        with col:
            if st.button(scene_label, key=f"scene_{scene_id}", type="primary" if ss.scene_view == scene_id else "secondary", width="stretch"):
                ss.scene_view = scene_id
                st.rerun()

# Scene gestures produce real application events, not presentation-only toasts.
if scene_event and scene_event.get("event_id") != ss.get("last_scene_event_id"):
    ss.last_scene_event_id = scene_event.get("event_id")
    ss.first_drag_done = True
    event_type = scene_event.get("type")
    needs_rerun = False   # a plain move only saves the position: the scene on screen is already correct
    # Persist the final drag position (absolute offset) before processing the interaction.
    actor = scene_event.get("actor")
    offset = scene_event.get("offset") or {}

    def _clamped(raw):
        try:
            return [max(-260, min(260, int(raw.get("x", 0)))), max(-85, min(75, int(raw.get("y", 0))))]
        except (TypeError, ValueError, AttributeError):
            return [0, 0]

    if actor in ("astronaut", "astro"):
        ss.astronaut_offset = _clamped(offset)
    elif actor == "rover":
        ss.rover_offset = _clamped(offset)
    if event_type == "astro_door":
        ss.scene_view = "interior"
        ss.astronaut_offset = [0, 0]          # inside the habitat the astronaut starts at the entrance again
        ss.interaction_message = T("You entered the habitat. Check the life-support systems.")
        needs_rerun = True
    elif event_type == "astro_sample":
        if not g["science"].get("sample"):
            record_science(g, "sample")
            ss.sample_count = int(ss.get("sample_count", 0)) + 1
            message = T("Lunar sample collected! Samples recorded: {n}.", n=ss.sample_count)
            ss.log.append(message)
            ss.interaction_message = message
            needs_rerun = True
    elif event_type == "rover_scan":
        if not g["science"].get("rover"):
            record_science(g, "rover")
            ss.rover_scan_index += 1
            message = T("Rover survey completed. Scientific observation recorded.")
            ss.log.append(message)
            ss.scene_view = "rover"
            ss.interaction_message = message
            needs_rerun = True
    if needs_rerun:
        st.rerun()
_interaction_message = ss.pop("interaction_message", None)   # shown once, then cleared
if _interaction_message:
    st.success(_interaction_message)

st.markdown(header_html(g, MAX_DAYS, ss.lang), unsafe_allow_html=True)


# Character movement is handled directly on the scene artwork by touch/mouse drag.
if ss.scene_view == "emergency":
    if critical_now:
        st.error(("أنظمة حرجة: " if ss.lang == "ar" else "Critical systems: ") + ", ".join(f"{k} ({v}%)" for k, v in critical_now.items()))
    else:
        st.success("لا توجد حالة طوارئ حالياً." if ss.lang == "ar" else "No active emergency. All monitored systems are above the critical threshold.")
if new_critical and get_status(g) == "active":
    resource_names = {"water": T("Water"), "oxygen": T("Oxygen"), "energy": T("Energy"),
                      "food": T("Food"), "protection": T("Radiation protection")}
    danger_names = "، ".join(f"{resource_names.get(k, k)} ({v}%)" for k, v in new_critical.items()) if ss.lang == "ar" else ", ".join(f"{resource_names.get(k, k)} ({v}%)" for k, v in new_critical.items())
    alert_title = T("‼️ DANGER APPROACHING!")
    alert_copy = T("Mission control detected a critical system. Check it now: {systems}", systems=danger_names)
    st.markdown(f"<div class='lb-danger-notice' role='alert'><span class='lb-danger-icon'>‼️</span><div><div class='lb-danger-copy'>{alert_title}</div><div class='lb-danger-sub'>{alert_copy}</div></div></div><style>.lb-danger-notice{{animation:lbNoticeIn .25s ease-out,lbNoticeOut .45s ease-in 4.55s forwards}}@keyframes lbNoticeOut{{to{{opacity:0;transform:translateY(-8px);visibility:hidden}}}}</style>", unsafe_allow_html=True)

# ---- the big "MISSION FAILED" sign for the astronauts
if get_status(g) == "lost":
    st.markdown(loss_sign_html(g, ss.lang, ss.player), unsafe_allow_html=True)
    if ss.get("loss_toast") != ss.run_id:
        ss.loss_toast = ss.run_id
        st.toast(T("🚨 MISSION FAILED"), icon="🚨")
    b1, b2 = st.columns(2)
    if b1.button(T("🔁 Try again"), type="primary", key="retry", width="stretch"):
        new_game(g["difficulty"], g["astronaut"]["id"])
        st.rerun()
    if b2.button(T("🏠 Back to welcome"), key="back_welcome", width="stretch"):
        ss.stage = "welcome"
        ss.show_welcome_card = ss.show_id_card = True
        set_lang("en")  # the welcome screen always opens in English first
        st.rerun()

with st.expander(T("⚙️ Mission setup · start a new mission")):
    c1, c2 = st.columns(2)
    diff = c1.selectbox(T("Difficulty"), list(DIFFICULTIES), index=list(DIFFICULTIES).index(g["difficulty"]),
                        format_func=T)
    crew_by_id = {a["id"]: a for a in ASTRONAUTS}
    crew = c2.selectbox(T("Astronaut"), list(crew_by_id), index=list(crew_by_id).index(g["astronaut"]["id"]),
                        format_func=lambda i: f"{T(crew_by_id[i]['name'])} — {T(crew_by_id[i]['role'])}")
    st.caption(T("Current crew: {desc} Special ability: {bonus}", desc=T(g["astronaut"]["description"]),
                 bonus=T(g["astronaut"]["bonus"])))
    if st.button(T("🚀 Start new mission"), type="primary", key="new_mission"):
        new_game(diff, crew)
        st.rerun()
theme.how_to_play(ss.lang)

# ---- after a food alert is solved: take the player to the Greenhouse choice
if ss.pop("gh_dialog", False) and g.get("greenhouse") is None and get_status(g) == "active":
    panels.greenhouse_dialog(g)

# --------------------------------------------------------------------------- systems gauges
labels = {k: T(v) for k, v in RESOURCE_LABELS.items()}
with st.container(border=True, key="panel_systems"):
    title(T("📡 SYSTEMS"))
    st.markdown(gauges_html(g["resources"], RESOURCE_LABELS, ss.lang), unsafe_allow_html=True)
    if get_status(g) == "active":
        for warning in dependency_warnings(g):
            st.warning(T("🔗 Chain reaction risk: {w} Fix the low gauge first!", w=warning))
    # Phase 2: actual subsystem condition and next-day resource forecast.
    with st.expander(T("🧰 LIFE-SUPPORT EQUIPMENT HEALTH"), expanded=True):
        health = g.setdefault("subsystem_health", {key: 100 for key in SUBSYSTEMS})
        equipment_cols = st.columns(3)
        for col, (system_key, spec) in zip(equipment_cols, SUBSYSTEMS.items()):
            value = int(health.get(system_key, 100))
            with col:
                st.metric(T(spec["label"]), f"{value}%", T(subsystem_status(value)))
                st.progress(value / 100)
        forecast = daily_consumption(DIFFICULTIES[g["difficulty"]]["mult"], health)
        st.markdown("**" + T("Estimated base use at the next END DAY") + "**")
        forecast_cols = st.columns(4)
        for col, (resource, amount) in zip(forecast_cols, forecast.items()):
            with col:
                col.metric(T(resource.title()), f"−{amount}")
        st.caption(T("Forecast excludes random events and any greenhouse flow. Equipment wear is applied at the end of each day."))
        if any(int(health.get(key, 100)) < 60 for key in SUBSYSTEMS):
            st.warning(T("One or more life-support systems are damaged. Use Repair life-support to restore equipment health."))
    if g.get("greenhouse") and g["greenhouse"]["status"] == "active":
        st.caption(T("🌱 Greenhouse linked: it uses base energy and water each night and returns food and oxygen."))
if new_critical and get_status(g) == "active":
    html_frame(danger_sound_html(), 1)

left, right = st.columns([1.35, 1])

# --------------------------------------------------------------------------- command console
with left:
    with st.container(border=True, key="panel_actions"):
        title(T("🧭 COMMAND CONSOLE"))
        if ss.alert_result:
            ok, msg = ss.alert_result
            (st.success if ok else st.warning)(msg)
            if ss.get("keep_fresh"):
                st.info(T("🧊 Keep food fresh: {tip}", tip=ss.keep_fresh))
        if g.get("pending_challenge") and get_status(g) == "active":
            panels.food_alert(g)
        if g.get("greenhouse") is None and ss.get("gh_offer"):
            st.info(T("🌱 New: the Greenhouse Mission is unlocked! Open the **Greenhouse** tab below to start it."))
            if st.button(T("🌱 Take me to the Greenhouse choice"), key="goto_gh"):
                ss.goto = "greenhouse"
                st.rerun()
        st.write(T("Actions remaining today: **{n} / {total}**", n=g["actions_remaining"], total=g["actions_per_day"]))

        if get_status(g) == "active":
            cols = st.columns(2)
            for i, (aid, a) in enumerate(ACTIONS.items()):
                with cols[i % 2]:
                    blocked = g["actions_remaining"] <= 0 or g["resources"]["energy"] < a["cost"]
                    if st.button(f"{a['emoji']} {T(a['name'])}\n\n{T(a['description'])}", key="act_" + aid,
                                 width="stretch", disabled=blocked):
                        result = perform_action(g, aid)
                        ss.log.append(result["message"])
                        ss.lesson = result.get("lesson")
                        st.rerun()
            if ss.lesson:
                st.info(T("Learning insight: {lesson}", lesson=ss.lesson))
            if st.button(T("🌅 END DAY"), key="end_day", width="stretch", disabled=bool(g.get("pending_challenge"))):
                ss.alert_result = None
                result = advance_day(g)
                ss.log.extend(result["messages"])
                if result.get("event"):
                    ss.lesson = result["event"]["lesson"]
                st.rerun()
        else:
            st.warning(T("Mission ended. Open “Mission setup” at the top to start a new mission."))

# --------------------------------------------------------------------------- coach + log screens
with right:
    with st.container(border=True, key="panel_coach"):
        title(T("🤖 MISSION COACH"))
        coach = get_coach_advice(g)
        st.markdown(screen_html([coach["summary"], T("PRIORITY: {p}", p=coach["priority"])]
                                + ["▶ " + t for t in coach["recommendations"]]), unsafe_allow_html=True)
        st.caption(T("Rule-based, explainable advice — not a trained machine-learning model."))
    with st.container(border=True, key="panel_log"):
        title(T("📜 MISSION LOG"))
        st.markdown(screen_html(["• " + x for x in reversed(ss.log[-8:])]), unsafe_allow_html=True)

# --------------------------------------------------------------------------- final debrief
if get_status(g) in ("won", "lost"):
    with st.container(border=True, key="panel_debrief"):
        title(T("🏆 MISSION DEBRIEF"))
        ev = get_final_evaluation(g)
        a, b, c = st.columns(3)
        a.metric(T("Score"), f"{ev['score']}/100")
        b.metric(T("Commander level"), T(ev["grade"]))
        c.metric(T("Mission"), T("Success") if g["status"] == "won" else T("Not completed"))
        st.write(T(ev["feedback"]))
        st.write(T("Decisions: {d} · Learning points: {lp} · Average resources: {avg}/100", d=ev["decisions"],
                   lp=ev["learning_points"], avg=ev["average_resources"]))
        st.download_button(T("⬇️ Download mission report"), build_report(g), file_name="lunabase_report.txt")
        if g["status"] == "won" and ss.get("balloons_run") != ss.run_id:
            ss.balloons_run = ss.run_id
            st.balloons()

# --------------------------------------------------------------------------- extra modules (navigation)
NAV = ("greenhouse", "expedition", "systems", "history", "nasa", "learn", "about")
NAV_LABELS = {"greenhouse": "🌱 Greenhouse", "expedition": "🧪 Science missions", "systems": "🚨 Safety drills", "history": "📈 History", "nasa": "🛰️ NASA data",
              "learn": "🧑‍🚀 Learn", "about": "ℹ️ About"}


def nav_label(key):
    text = T(NAV_LABELS[key])
    if key == "greenhouse" and g.get("greenhouse") is None and ss.get("gh_offer"):
        text += " 🆕"
    return text


# panels can ask to jump to a module (e.g. the Greenhouse after a food alert): set before the widget is built
if ss.get("goto") in NAV:
    ss.nav = ss.pop("goto")
if ss.get("nav") not in NAV:
    ss.nav = ss.get("nav_last", "greenhouse")
st.segmented_control(T("Modules"), NAV, key="nav", format_func=nav_label, label_visibility="collapsed")
page = ss.get("nav") if ss.get("nav") in NAV else ss.get("nav_last", "greenhouse")
ss.nav_last = page

if page == "greenhouse":
    panels.greenhouse_tab(g)
elif page == "expedition":
    panels.expedition_tab(g, SCIENCE_OBJECTIVES, record_science)
elif page == "systems":
    panels.safety_tab(g, complete_emergency_drill, certificate_text, ss.player)
elif page == "history":
    if g["history"]:
        st.line_chart(pd.DataFrame(g["history"]).set_index("Day").rename(columns=labels))
    else:
        st.caption(T("The chart appears after you complete the first day."))
elif page == "nasa":
    panels.nasa_tab()
elif page == "learn":
    panels.learn_tab()
else:
    panels.about_tab()

st.caption(T("LunaBase educational prototype • Python + Streamlit • Greenhouse data: Zabel et al. 2020 (DLR EDEN ISS). "
             "Not an official NASA product; game numbers are simplified."))
