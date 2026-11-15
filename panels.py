"""Secondary console modules: food alert, greenhouse, NASA data, learning center."""
import pandas as pd
import streamlit as st

from education.learning_content import LEARNING_CARDS, QUIZ
from i18n import tr
from simulation.eden_iss_data import CROPS, FACILITY, SETPOINTS, SOURCE, TOTALS
from simulation.food_challenge import CAUSES, FACTOR_COLUMNS, HINT, SAFE_RANGES
from simulation.game_engine import DIFFICULTIES, resolve_food_challenge
from simulation.greenhouse_link import (BEDS_M2, FOOD_KG_PER_POINT, LOW_ENERGY, LOW_WATER, TASKS_PER_DAY,
                                        plan_daily_flows, potential_harvest_kg_per_day)
from simulation.greenhouse_controls import assess_environment
from simulation.greenhouse_mission import (DAILY_TASKS, advance_greenhouse_day, complete_task,
                                           create_greenhouse_mission, greenhouse_summary)
from simulation.nasa_data import fetch_recent_flares, summarize

ss = st.session_state


def T(text, **kw):
    return tr(ss.get("lang", "en"), text, **kw)


# --------------------------------------------------------------------------- food alert
def food_alert(g):
    ch = g["pending_challenge"]
    d = f"{ss.run_id}_{g['day']}"
    st.error("🚨 " + T(ch["title"]))
    st.write(T(ch["story"]))
    df = pd.DataFrame(ch["rows"])
    shown = df.copy()
    shown["Crop"] = shown["Crop"].map(T)
    shown["Water tank"] = shown["Water tank"].map(T)
    shown = shown.rename(columns={c: T(c) for c in shown.columns})
    st.dataframe(shown, hide_index=True, width="stretch")
    st.caption(T(SAFE_RANGES) + " " + T("(Simplified game values.)"))
    st.caption(T("🔤 Words: CFU/g = how many tiny germs (microbes) are in one gram of food · ppm = parts per million, "
                 "a tiny amount of gas in the air · ethylene = a gas that ripe fruit gives off."))
    factor = st.selectbox(T("📈 Explore the data: compare spoilage with…"), list(FACTOR_COLUMNS), format_func=T,
                          key=f"ch_factor_{d}")
    st.scatter_chart(shown, x=T(FACTOR_COLUMNS[factor]), y=T("Spoiled (%)"))

    hint_key = f"hint_{d}"
    if st.button(T("💡 Hint (-5 bonus points)"), key=f"hintbtn_{d}"):
        ss[hint_key] = True
    if ss.get(hint_key):
        st.info(T(HINT))

    cause_ids = list(CAUSES)
    cause = st.radio(T("1️⃣ What is the cause?"), cause_ids, index=None, key=f"ch_cause_{d}",
                     format_func=lambda k: T(CAUSES[k]["label"]))
    fix = st.radio(T("2️⃣ What is the best fix?"), cause_ids, index=None, key=f"ch_fix_{d}",
                   format_func=lambda k: T(CAUSES[k]["fix"]))
    if st.button(T("✅ Submit solution"), type="primary", disabled=cause is None or fix is None, key=f"submit_{d}"):
        r = resolve_food_challenge(g, cause, fix, bool(ss.get(hint_key)))
        ss.log.append(T("Food alert: {msg}", msg=r["message"]))
        ss.lesson = r["lesson"]
        ss.alert_result = (r["correct"], r["message"])
        ss.keep_fresh = r["keep_fresh"]
        ss.gh_offer = True
        ss.gh_dialog = True  # app.py opens the Greenhouse choice right away
        st.rerun()


def greenhouse_dialog(game):
    """Pop-up shown right after a food alert is solved: it takes the player to the Greenhouse choice."""
    @st.dialog(T("🌱 Next step: the Greenhouse!"), width="large")
    def _dialog():
        if ss.get("alert_result"):
            ok, msg = ss.alert_result
            (st.success if ok else st.warning)(msg)
        if ss.get("keep_fresh"):
            st.info(T("🧊 Keep food fresh: {tip}", tip=ss.keep_fresh))
        st.markdown("### " + T("Do you want to grow fresh food in the Greenhouse?"))
        st.write(T("Some food spoiled! Want to learn how to grow fresh food and keep it safe? This 7-day greenhouse "
                   "mission is optional — you can start it now or skip it."))
        c1, c2 = st.columns(2)
        if c1.button(T("🌱 Yes, take me to the Greenhouse"), type="primary", key="dlg_gh_yes", width="stretch"):
            game["greenhouse"] = create_greenhouse_mission()
            ss.gh_msg = (True, T("🌱 Greenhouse mission started! Finish today's tasks, then press END DAY on the base."))
            ss.gh_offer = False
            ss.goto = "greenhouse"
            st.rerun()
        if c2.button(T("Maybe later"), key="dlg_gh_later", width="stretch"):
            st.rerun()  # closes the pop-up; the offer stays in the Greenhouse tab

    _dialog()


# --------------------------------------------------------------------------- greenhouse
def greenhouse_tab(game):
    if game.get("greenhouse") is not None:
        _greenhouse_running(game)
    elif ss.get("gh_offer"):
        st.info(T("Some food spoiled! Want to learn how to grow fresh food and keep it safe? This 7-day greenhouse "
                  "mission is optional — you can start it now or skip it."))
        c1, c2 = st.columns(2)
        if c1.button(T("🌱 Yes, start the Greenhouse Mission"), type="primary", key="gh_accept"):
            game["greenhouse"] = create_greenhouse_mission()
            ss.gh_msg = None
            st.rerun()
        if c2.button(T("Maybe later"), key="gh_decline"):
            ss.gh_offer = False
            st.rerun()
    else:
        st.info(T("🔒 Solve a food alert (days 3 and 5) to unlock the optional Greenhouse Mission."))


def _greenhouse_running(game):
    gh = game["greenhouse"]
    gs = greenhouse_summary(gh)
    st.write(T("Run a parallel greenhouse mission: establish new crops in empty beds while protecting "
               "already-established tomato and cucumber plants."))
    if ss.get("gh_msg"):
        ok, msg = ss.gh_msg
        (st.success if ok else st.warning)(msg)
    a, b, c = st.columns(3)
    a.metric(T("Greenhouse day"), f"{gs['day']} / 7")
    b.metric(T("Tasks recorded"), f"{gs['completed_tasks']} / {gs['total_tasks']}")
    c.metric(T("Mission status"), T(gs["status"].title()))
    st.progress(gs["progress_percent"] / 100)
    st.caption(T("New beds: radish, arugula, and lettuce seedlings. Existing fruiting crops: tomatoes and cucumbers."))

    # Phase 6: adjustable, explainable climate controls. Values are saved in mission state.
    st.markdown(T("### 🧪 Greenhouse climate control"))
    st.caption(T("Tune the growing environment. These are simplified learning targets, not certified lunar-farm engineering limits."))
    env = gh.setdefault("environment", {"temperature_c": 21, "humidity_pct": 65, "light_hours": 16, "nutrient_ph": 6.0})
    e1, e2 = st.columns(2)
    with e1:
        env["temperature_c"] = st.slider(T("Air temperature (°C)"), 10, 35, int(env.get("temperature_c", 21)), key=f"gh_temp_{ss.gh_run}")
        env["humidity_pct"] = st.slider(T("Relative humidity (%)"), 30, 90, int(env.get("humidity_pct", 65)), key=f"gh_humidity_{ss.gh_run}")
    with e2:
        env["light_hours"] = st.slider(T("Daily light period (hours)"), 8, 20, int(env.get("light_hours", 16)), key=f"gh_light_{ss.gh_run}")
        env["nutrient_ph"] = st.slider(T("Nutrient solution pH"), 4.0, 8.0, float(env.get("nutrient_ph", 6.0)), step=0.1, key=f"gh_ph_{ss.gh_run}")
    climate = assess_environment(env)
    if climate["status"] == "optimal":
        st.success(T("All greenhouse controls are within the learning target ranges."))
    else:
        st.warning(T("{n} greenhouse control(s) need adjustment. The simulated growth factor is {factor:.0%}.", n=climate["deviations"], factor=climate["factor"]))
    with st.expander(T("Why do these controls matter?")):
        st.write(T("Temperature affects plant processes; humidity changes transpiration; light duration supports photosynthesis; nutrient-solution pH affects nutrient availability."))

    st.markdown(T("**🔗 Connected to base resources**"))
    if gh["status"] == "active":
        p = plan_daily_flows(game, DIFFICULTIES[game["difficulty"]]["mult"])
        k1, k2, k3, k4 = st.columns(4)
        k1.metric(T("⚡ Energy tonight"), f"{p['energy']:+d}")
        k2.metric(T("💧 Water tonight"), f"{p['water']:+d}")
        k3.metric(T("🫁 Oxygen tonight"), f"{p['oxygen']:+d}")
        k4.metric(T("🥬 Food tonight"), f"{p['food']:+d}")
        st.caption(T("Care today: {done} / {total} greenhouse tasks done since the last base day "
                     "(finish {total} for a full harvest). Applied when you press END DAY.",
                     done=p["tasks_done"], total=TASKS_PER_DAY))
        if p["dim_lights"]:
            st.warning(T("⚠️ Base energy is below {limit}: grow lights will dim and the harvest will be halved. Charge the batteries!",
                         limit=LOW_ENERGY))
        if p["low_water"]:
            st.warning(T("⚠️ Base water is below {limit}: irrigation will be cut and the harvest will be halved. Recycle water!",
                         limit=LOW_WATER))
        if p["climate"]["deviations"]:
            st.warning(T("⚠️ Climate settings reduce the simulated harvest. Adjust temperature, humidity, light, and pH before END DAY."))
    st.caption(T("Harvest so far: {kg:.2f} kg over {days} base day(s). Grow lights and irrigation "
                 "use energy and water; plants give back food, oxygen, and some water from condensation.",
                 kg=gh["harvest_kg"], days=gh["linked_days"]))

    with st.expander(T("📚 Real data: EDEN ISS greenhouse in Antarctica (2018)")):
        st.write(T("The yields behind your harvest come from a real research greenhouse near Neumayer Station III in "
                   "Antarctica: {area} m² of growing area, {days} days of operation, {kg} kg of fresh food, and an "
                   "average of {rate} kg per m² per day.", area=FACILITY["cultivation_area_m2"],
                   days=FACILITY["operation_days"], kg=TOTALS["edible_fresh_kg"], rate=TOTALS["productivity_kg_m2_d"]))
        cdf = pd.DataFrame(CROPS)
        for col in ("name", "category", "harvest"):
            cdf[col] = cdf[col].map(T)
        st.bar_chart(cdf.set_index("name")["rate_kg_m2_d"], horizontal=True)
        st.caption(T("Edible fresh weight per m² of growing area per day (EDEN ISS 2018 season)."))
        st.dataframe(cdf.rename(columns={"name": T("Crop"), "category": T("Category"), "harvest": T("Harvest"),
                                         "cycle_days": T("Cycle (days)"), "rate_kg_m2_d": T("kg/m²/day"),
                                         "dry_weight_pct": T("Dry weight (%)"), "plants_per_m2": T("Plants/m²")}),
                     hide_index=True, width="stretch")
        st.caption(T("Even the fastest crop took about {days:.0f} days, so a 7-day mission only checks seedlings. "
                     "Environment used: {temp} °C day, {hum}% humidity, {co2} ppm CO₂, {light} h light per day.",
                     days=min(c["cycle_days"] for c in CROPS), temp=SETPOINTS["air_temp_day_c"],
                     hum=SETPOINTS["relative_humidity_pct"], co2=SETPOINTS["co2_ppm"], light=SETPOINTS["photoperiod_h"]))
        beds = ", ".join(f"{a} m² {T(n)}" for n, a in BEDS_M2.items())
        st.caption(T("Game assumptions (not from the paper): beds of {beds}; 1 food point = {pt} kg; "
                     "potential harvest {pot:.2f} kg/day. Source: {cite}, doi:{doi} ({lic}).",
                     beds=beds, pt=FOOD_KG_PER_POINT, pot=potential_harvest_kg_per_day(),
                     cite=SOURCE["citation"], doi=SOURCE["doi"], lic=SOURCE["license"]))

    if gh["status"] == "active":
        st.markdown(T("**Day {day} tasks**", day=gh["day"]))
        for idx, task in enumerate(DAILY_TASKS[gh["day"]]):
            key = f"greenhouse_{ss.gh_run}_{gh['day']}_{idx}"
            checked = task in gh["completed"][gh["day"]]
            if st.checkbox(T(task), value=checked, key=key, disabled=checked):
                complete_task(gh, task)
                st.rerun()
        if st.button(T("Advance greenhouse day"), key="advance_greenhouse"):
            result = advance_greenhouse_day(gh, game["day"], ss.get("lang", "en"))
            ss.gh_msg = (result["ok"], result["message"])
            st.rerun()
    else:
        st.success(T("The seven-day greenhouse mission is complete. New crops are assessed for germination or early "
                     "establishment; existing tomato and cucumber plants are assessed for fruit survival and condition."))
    if st.button(T("Restart greenhouse mission"), key="restart_greenhouse"):
        game["greenhouse"] = create_greenhouse_mission()
        ss.gh_msg = None
        ss.gh_run += 1
        st.rerun()
    st.caption(T("Scientific note: the seven-day window is for early establishment of new crops, not growing tomatoes from "
                 "seed to fruit. Crop growth varies by variety and environment; calcium management depends on crop and system."))


# --------------------------------------------------------------------------- NASA data
@st.cache_data(ttl=3600, show_spinner=False)
def load_flares():
    return fetch_recent_flares()


def nasa_tab():
    st.write(T("Solar storms start with flares on the Sun, and in the game they can weaken your radiation shield. "
               "NASA keeps a public record of real flares called DONKI."))
    st.caption(T("Live DONKI observations are shown for context only; they do not change the game's simulated events or resource values."))
    with st.expander(T("🌕 Lunar science data: LRO and LOLA")):
        st.write(T("NASA's Lunar Reconnaissance Orbiter (LRO) studies the Moon from orbit. Its Lunar Orbiter Laser Altimeter (LOLA) measures surface topography, helping scientists build elevation and slope maps. These data can inform terrain research and landing-site studies."))
        st.write(T("LunaBase does not download or display live LOLA terrain tiles in this prototype. The landing-zone activity is a simplified educational exercise, not a real landing-site certification."))
        st.markdown("- [NASA Lunar Reconnaissance Orbiter](https://science.nasa.gov/mission/lro/)\n- [NASA LOLA instrument](https://lunar.gsfc.nasa.gov/lola/)\n- [NASA Moon water research](https://science.nasa.gov/moon/)")
    if st.button(T("📡 Load the latest solar flares from NASA"), key="load_flares"):
        ss.show_flares = True
    if ss.get("show_flares"):
        rows = load_flares()
        if rows is None:
            st.warning(T("Could not reach NASA right now (no internet, or too many requests). The game still works offline!"))
        else:
            sm = summarize(rows)
            if sm["count"] == 0:
                st.info(T("NASA listed no solar flares in the last 14 days."))
            else:
                a, b = st.columns(2)
                a.metric(T("Flares in 14 days"), sm["count"])
                b.metric(T("Strongest flare"), sm["strongest"])
                st.caption(T("A {cls} flare is {help}. Classes go A, B, C, M, X.", cls=sm["strongest"], help=T(sm["help"])))
                flares = pd.DataFrame(rows).tail(10)
                st.dataframe(flares.rename(columns={c: T(c) for c in flares.columns}), hide_index=True, width="stretch")
        st.caption(T("Source: NASA DONKI through the NASA Open APIs (api.nasa.gov)."))


# --------------------------------------------------------------------------- learning + about
def learn_tab():
    for card in LEARNING_CARDS:
        with st.expander(T(card["title"])):
            st.write(T(card["body"]))
            st.caption(T("Key idea: {idea}", idea=T(card["takeaway"])))
    st.markdown(T("**🧠 Knowledge check**"))
    qi = st.selectbox(T("Question"), range(len(QUIZ)), format_func=lambda i: T("Question {n}", n=i + 1))
    q = QUIZ[qi]
    answer = st.radio(T(q["question"]), q["options"], key=f"quiz_answer_{qi}", format_func=T)
    if st.button(T("Check my answer"), key="check_quiz"):
        if answer == q["answer"]:
            st.success(T(q["explanation"]))
        else:
            st.error(T("Try again. {why}", why=T(q["explanation"])))


def about_tab():
    st.markdown(T("""**Made for the NASA Space Apps 2026 challenge “Build a Junior Astronaut Mission Trainer”.**
Players run a lunar base and balance **life support (water, oxygen), power, food and radiation shielding**.
The systems are connected: low energy slows life support, weak shielding damages electronics, and low water means less food.

**Sources**
- Greenhouse yields: Zabel et al. (2020), *Biomass Production of the EDEN ISS Space Greenhouse in Antarctica* — https://doi.org/10.3389/fpls.2020.00656 (German Aerospace Center, DLR).
- Space weather: NASA DONKI via https://api.nasa.gov
- Challenge: https://www.spaceappschallenge.org

All game numbers are simplified teaching assumptions, not real mission engineering. LunaBase is not an official NASA product."""))


# --------------------------------------------------------------------------- phase 4/5/7/8: surface science, safety and graduation

def expedition_tab(game, objectives, record_science):
    """Surface-science tasks with assessed decisions and one-time rewards."""
    from simulation.science_missions import SCIENCE_ANALYSIS, check_science_answer

    st.write(T("Explore the lunar surface like a science team. Your observations are learning activities; they do not prove that a resource is commercially or safely usable."))
    st.caption(T("Drag the astronaut to the sample marker and the rover to the survey marker in the scene above. Then complete the two analysis tasks here."))
    done = game["science"]
    completed = sum(bool(done.get(item["id"])) for item in objectives)
    st.progress(completed / len(objectives), text=T("Science mission progress: {n}/{total}", n=completed, total=len(objectives)))

    for item in objectives:
        objective_id = item["id"]
        with st.container(border=True):
            st.markdown(f"**{'✅' if done.get(objective_id) else '⬜'} {T(item['title'])}**")
            st.caption(T(item["detail"]))
            if objective_id in ("sample", "rover"):
                st.info(T("Complete this by dragging the actor in the scene."))
            elif objective_id in SCIENCE_ANALYSIS:
                task = SCIENCE_ANALYSIS[objective_id]
                answer_key = f"science_answer_{objective_id}"
                feedback_key = f"science_feedback_{objective_id}"
                st.write(T(task["question"]))
                choice_ids = list(task["choices"])
                selected = st.radio(
                    T("Choose the best scientific decision"), choice_ids,
                    index=None, key=answer_key,
                    format_func=lambda choice: T(task["choices"][choice]),
                    disabled=bool(done.get(objective_id)),
                )
                if st.button(T("Submit science decision"), key=f"science_submit_{objective_id}",
                             disabled=bool(done.get(objective_id)) or selected is None):
                    result = check_science_answer(objective_id, selected)
                    if result["correct"]:
                        awarded = record_science(game, objective_id)
                        if awarded["ok"]:
                            game.setdefault("science_answers", {})[objective_id] = selected
                            st.session_state[feedback_key] = (True, result["feedback"])
                        else:
                            st.session_state[feedback_key] = (False, awarded["message"])
                    else:
                        st.session_state[feedback_key] = (False, result["feedback"])
                    st.rerun()
                if st.session_state.get(feedback_key):
                    ok, feedback = st.session_state[feedback_key]
                    (st.success if ok else st.warning)(T(feedback))
            else:
                st.caption(T("This science objective is not available in this version."))

    with st.expander(T("Science note: lunar water ice")):
        st.write(T("Scientists use orbital measurements, neutron data, radar, and illumination maps to investigate possible water ice, especially in permanently shadowed regions. A signal is evidence to study, not a guarantee of accessible ice."))
    with st.expander(T("Science note: landing-zone selection")):
        st.write(T("A real landing assessment considers slope, rocks, lighting, communications, terrain uncertainty, and mission hardware limits. LunaBase uses a simplified learning checklist only."))
    st.caption(T("Science rewards are educational game points, not real-world mission certifications."))


def safety_tab(game, complete_emergency_drill, certificate_text, player):
    from simulation.emergency_training import DRILLS, evaluate_drill

    st.write(T("Practice calm, crew-first responses. These are educational scenarios, not real emergency procedures."))
    completed = set(game["emergency_drills"])
    st.progress(len(completed) / len(DRILLS), text=T("Safety training: {n}/{total}", n=len(completed), total=len(DRILLS)))
    game.setdefault("emergency_answers", {})
    for drill_id, drill in DRILLS.items():
        with st.container(border=True):
            st.markdown("**" + T({"shelter": "Radiation shelter scenario", "isolate": "Habitat leak scenario", "backup": "Power failure scenario"}[drill_id]) + "**")
            st.write(T(drill["prompt"]))
            done = drill_id in completed
            if done:
                st.success(T("Scenario completed. Your correct decision is saved."))
                st.caption(T(drill["coach"]))
                continue
            choice = st.radio(
                T("Choose the safest response"), list(drill["choices"]),
                key=f"emergency_choice_{drill_id}", index=None,
                format_func=lambda option, choices=drill["choices"]: T(choices[option]),
            )
            if st.button(T("Submit emergency decision"), key=f"emergency_submit_{drill_id}", disabled=choice is None):
                evaluation = evaluate_drill(drill_id, choice)
                if evaluation["correct"]:
                    result = complete_emergency_drill(game, drill_id)
                    if result["ok"]:
                        game["emergency_answers"][drill_id] = choice
                        st.success(T(evaluation["feedback"]))
                        st.info(T(evaluation["coach"]))
                    else:
                        st.warning(T(result["message"]))
                else:
                    st.warning(T(evaluation["feedback"]))
                    st.info(T(evaluation["coach"]))
    st.divider()
    st.markdown("**" + T("Mission Coach checklist") + "**")
    for n, label in enumerate(("Check all five resource gauges before ending the day.", "Protect energy: life-support and greenhouse systems depend on it.", "Use the habitat shelter during a radiation scenario.", "Do not assume a scientific observation is a confirmed resource.")):
        st.checkbox(T(label), key=f"safety_check_{n}", value=False)  # stable key (str hash() changes per process)
    st.divider()
    st.markdown("**" + T("Junior Astronaut certificate") + "**")
    st.caption(T("Complete the mission and explore the science and safety activities to build your learning record."))
    st.download_button(T("🎓 Download learning certificate"), certificate_text(game, player), file_name="LunaBase_Junior_Astronaut_Certificate.txt", mime="text/plain")
