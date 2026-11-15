"""Real measurements from the EDEN ISS space-greenhouse analog in Antarctica (2018 season).

Source: Zabel P., Zeidler C., Vrakking V., Dorn M., Schubert D. (2020).
"Biomass Production of the EDEN ISS Space Greenhouse in Antarctica During the 2018
Experiment Phase." Frontiers in Plant Science 11:656. doi:10.3389/fpls.2020.00656 (CC BY).

Everything in this file is copied from the paper's tables and text. Anything LunaBase
*invents* (energy use, water use, bed sizes, food-point conversion) lives in
greenhouse_link.py and is labelled as a game assumption.

Note on a paper inconsistency: the abstract lists tomatoes as 50 kg, but the Results
category totals (fruit crops 105.4 kg) and the Discussion shares (cucumber 25%, tomato
14%) imply about 37-38 kg of tomatoes. The category totals below are used for that reason.
Table 8 also prints the tomato cultivar as "3689B"; elsewhere in the paper it is "3496B".
"""

SOURCE = {
    "citation": "Zabel et al. (2020), Front. Plant Sci. 11:656",
    "doi": "10.3389/fpls.2020.00656",
    "license": "CC BY",
}

FACILITY = {
    "name": "EDEN ISS Mobile Test Facility",
    "location": "~400 m south of Neumayer Station III, Antarctica",
    "cultivation_area_m2": 12.5,
    "operation_days": 286,  # 7 Feb - 20 Nov 2018
    "winter_crew_size": 10,
    "lowest_outside_temp_c": -43.5,
    "led_fixtures": 42,
    "crops_grown": 26,
}

# Environmental set points (all crops grown together in one compromise climate).
SETPOINTS = {
    "air_temp_day_c": 21,
    "air_temp_night_c": 19,
    "relative_humidity_pct": 65,
    "co2_ppm": 1000,
    "light_umol_m2_s": (330, 600),  # depends on crop; measured at canopy
    "photoperiod_h": 17,  # 15 h full light + 1 h reduced before and after
    "dark_period_h": 7,
    "irrigation": "30 s of misting every 6 min (aeroponic + nutrient film)",
}

TOTALS = {
    "edible_fresh_kg": 268,
    "productivity_kg_m2_d": 0.075,
    "productivity_kg_m2_286d": 21.44,
    "productivity_kg_m2_year": 27.4,  # 0.075 kg/m2/d extrapolated to 365 d
    "productivity_without_pepper_kg_m2_d": 0.089,
    "pepper_area_share_pct": 11,
    "south_pole_chamber_kg_m2_d": 0.130,  # comparison facility, 2006
}

# Edible fresh biomass by category, first Antarctic season (Results: Overview).
CATEGORY_YIELD_KG = {
    "Fruit crops": 105.4,
    "Lettuce": 56.4,
    "Leafy greens": 49.1,
    "Tuber crops": 26.8,
    "Herbs": 12.2,
    "Miscellaneous": 18.4,
}

# name, category, harvest type, mean cycle length (d), edible fresh weight rate
# (kg per m2 of cultivation area per day), edible dry-weight ratio (%), plants per m2.
# Tables 1, 3, 4, 6, 7, 8, 9. None = not reported.
_ROWS = [
    ("Batavia lettuce", "Lettuce", "Batch", 38.0, 0.043, 5.79, 18.3),
    ("Expertise lettuce", "Lettuce", "Batch", 38.0, 0.065, 6.09, 18.3),
    ("Outredgeous lettuce", "Lettuce", "Batch", 37.9, 0.058, 6.61, 18.3),
    ("Waldmann's Green lettuce", "Lettuce", "Batch", 37.9, 0.080, 6.35, 18.3),
    ("Arugula (330 light)", "Leafy greens", "Batch", 24.2, 0.111, 6.52, 594.5),
    ("Arugula (600 light)", "Leafy greens", "Batch", 29.0, 0.188, 6.52, 594.5),
    ("Swiss chard", "Leafy greens", "Spread", 90.0, 0.102, 7.16, 36.6),
    ("Red mustard Red Giant", "Leafy greens", "Spread", 82.7, 0.130, 6.09, 61.0),
    ("Red mustard Frizzy Lizzy", "Leafy greens", "Spread", 82.7, 0.107, 6.04, 61.0),
    ("Mizuna", "Leafy greens", "Spread", 119.0, 0.194, 6.37, 36.6),
    ("Basil", "Herbs", "Spread", 121.0, 0.060, 8.64, 61.0),
    ("Chives", "Herbs", "Spread", 266.0, 0.053, 8.84, 609.8),
    ("Parsley", "Herbs", "Spread", 266.0, 0.062, 10.93, 304.9),
    ("Tomato F1 3496B", "Fruit crops", "Spread", 286.0, 0.046, 12.66, 12.2),
    ("Tomato F1 1202", "Fruit crops", "Spread", 286.0, 0.052, 13.36, 12.2),
    ("Cucumber Picowell", "Fruit crops", "Spread", 161.0, 0.321, 4.43, 6.1),
    ("Radish Raxe", "Tuber crops", "Batch", 22.6, 0.078, 5.79, 109.8),
    ("Radish Lennox", "Tuber crops", "Batch", 23.0, 0.059, None, 109.8),
    ("Kohlrabi", "Tuber crops", "Batch", 58.71, 0.141, 7.17, 16.8),  # 15.2-18.3 plants/m2
]
_KEYS = ("name", "category", "harvest", "cycle_days", "rate_kg_m2_d", "dry_weight_pct", "plants_per_m2")
CROPS = [dict(zip(_KEYS, row)) for row in _ROWS]


def get_crop(name):
    """Return one crop record by exact name."""
    for c in CROPS:
        if c["name"] == name:
            return c
    raise KeyError(name)


def crops_in_category(category):
    return [c for c in CROPS if c["category"] == category]


def crops_ready_within(days):
    """Crops whose average cultivation cycle is no longer than `days`."""
    return [c for c in CROPS if c["cycle_days"] <= days]


def shortest_cycle():
    return min(CROPS, key=lambda c: c["cycle_days"])
