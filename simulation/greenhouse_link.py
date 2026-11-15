"""Connects the Greenhouse Mission to the lunar base's shared resources.

Each time the base day ends, an *active* greenhouse mission:
  - draws energy (LED grow lights) and water (irrigation), and gets some water back
    from condensation recovery,
  - adds a little oxygen,
  - delivers a harvest of food from the established tomato and cucumber beds.

Harvest size comes from REAL EDEN ISS yields (eden_iss_data.py) multiplied by:
  - care:   how many greenhouse tasks the crew finished since the last base day
  - factor: a limiting factor - low base energy dims the lights, low water cuts irrigation

Everything numeric in this file other than the yield rates is a simplified GAME
ASSUMPTION, not mission engineering data. EDEN ISS measured energy, water and crew
time, but those figures are not in the paper this module is based on.
"""
from i18n import num, tr
from simulation.eden_iss_data import get_crop
from simulation.greenhouse_controls import assess_environment, environment_snapshot

# --- Game assumptions -------------------------------------------------------
FOOD_KG_PER_POINT = 0.25          # 1 food point = 0.25 kg of fresh produce
BEDS_M2 = {                        # established fruiting beds in the base greenhouse
    "Cucumber Picowell": 2.0,
    "Tomato F1 1202": 1.5,
    "Tomato F1 3496B": 1.5,
}
ENERGY_DRAW = 3                    # grow lights, per base day (before difficulty multiplier)
WATER_DRAW = 3                     # irrigation, per base day (before difficulty multiplier)
WATER_RECOVERED = 2                # condensation recovery returns part of the water
OXYGEN_GAIN = 2                    # per base day at full care
TASKS_PER_DAY = 3                  # greenhouse tasks needed per base day for full care
LOW_ENERGY = 25                    # below this the lights are dimmed
LOW_WATER = 20                     # below this irrigation is cut back
STRESS_FACTOR = 0.5


def _clamp(x):
    return max(0, min(100, int(round(x))))


def potential_harvest_kg_per_day():
    """Edible fresh kg/day of the established beds at full care, from EDEN ISS yields."""
    return sum(area * get_crop(name)["rate_kg_m2_d"] for name, area in BEDS_M2.items())


def is_linked(game):
    gh = game.get("greenhouse")
    return bool(gh) and gh["status"] == "active"


def plan_daily_flows(game, mult=1.0):
    """Work out tonight's greenhouse flows without changing anything."""
    gh = game["greenhouse"]
    res = game["resources"]
    care = min(1.0, gh["tasks_since_flow"] / TASKS_PER_DAY)
    light = 1.0 if res["energy"] >= LOW_ENERGY else STRESS_FACTOR
    water = 1.0 if res["water"] >= LOW_WATER else STRESS_FACTOR
    climate = assess_environment(gh.get("environment"))
    factor = min(light, water) * climate["factor"]
    kg = potential_harvest_kg_per_day() * care * factor
    return {
        "care": care,
        "tasks_done": gh["tasks_since_flow"],
        "factor": factor,
        "dim_lights": light < 1.0,
        "low_water": water < 1.0,
        "climate": climate,
        "environment": environment_snapshot(gh.get("environment")),
        "energy": -max(1, round(ENERGY_DRAW * mult)),
        "water": -max(1, round(WATER_DRAW * mult)) + WATER_RECOVERED,
        "oxygen": round(OXYGEN_GAIN * care * factor),
        "food": round(kg / FOOD_KG_PER_POINT),
        "kg": kg,
    }


def apply_greenhouse_flows(game, mult=1.0):
    """Apply the nightly flows to the base. Returns log messages (empty if not linked)."""
    if not is_linked(game):
        return []
    gh = game["greenhouse"]
    res = game["resources"]
    p = plan_daily_flows(game, mult)
    before = dict(res)
    for key in ("energy", "water", "oxygen", "food"):
        res[key] = _clamp(res[key] + p[key])
    gh["harvest_kg"] += p["kg"]
    gh["linked_days"] += 1
    gh["tasks_since_flow"] = 0
    gh["last_flow"] = p
    gh.setdefault("environment_history", []).append({"base_day": game.get("day"),
        "environment": p["environment"], "status": p["climate"]["status"],
        "growth_factor": p["climate"]["factor"]})
    if p["care"] >= 1.0 and p["climate"]["factor"] == 1.0:
        game["learning_points"] += 1
    L = game.get("lang", "en")
    d = {k: res[k] - before[k] for k in ("energy", "water", "oxygen", "food")}
    msgs = [tr(L, "🌱 Greenhouse: energy {e}, water {w}, oxygen {o}, food {f} ({kg:.2f} kg harvested).",
               e=num(L, d["energy"], True), w=num(L, d["water"], True), o=num(L, d["oxygen"], True),
               f=num(L, d["food"], True), kg=p["kg"])]
    if p["care"] < 1.0:
        msgs.append(tr(L, "Only {done}/{total} greenhouse tasks were done, so the harvest was smaller.",
                       done=p["tasks_done"], total=TASKS_PER_DAY))
    if p["dim_lights"]:
        msgs.append(tr(L, "Low base energy dimmed the grow lights and cut the harvest."))
    if p["low_water"]:
        msgs.append(tr(L, "Low base water reduced irrigation and cut the harvest."))
    if p["climate"]["deviations"]:
        msgs.append(tr(L, "Greenhouse climate controls were outside the target range; the simulated growth factor was {factor:.0%}.", factor=p["climate"]["factor"]))
    return msgs
