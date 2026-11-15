"""Food-spoilage data challenge: the player reads a data table and finds the cause."""
import random

CAUSES = {
    "temperature": {
        "keep_fresh": "Keep food cool! Cold storage slows down the tiny germs that make food rot.",
        "label": "Storage temperature is too high",
        "fix": "Repair the cooling unit and bring storage back to a cool temperature",
        "lesson": "Warm storage speeds up the growth of microbes that spoil food.",
    },
    "humidity": {
        "keep_fresh": "Keep food dry! Use sealed containers and fresh air so mold cannot grow.",
        "label": "Humidity in storage is too high",
        "fix": "Add a dehumidifier and improve ventilation to lower humidity",
        "lesson": "Damp air helps mold grow, so habitats must monitor and control humidity.",
    },
    "water": {
        "keep_fresh": "Use clean water! Wash hands and clean the water tank and filters before watering plants.",
        "label": "Irrigation water is contaminated with microbes",
        "fix": "Clean the water tank and filters, then disinfect the irrigation system",
        "lesson": "Clean water matters: contaminated irrigation can spread microbes to crops.",
    },
    "ethylene": {
        "keep_fresh": "Keep ripe fruit away from fresh veggies! Ripe fruit gives off a gas that makes other food rot sooner.",
        "label": "Ethylene gas is building up from ripening produce",
        "fix": "Ventilate or filter the air and separate ripe produce from fresh crops",
        "lesson": "Ripening produce releases ethylene gas, which can make nearby food ripen and rot faster.",
    },
}

FACTOR_COLUMNS = {
    "Temperature": "Temp (°C)",
    "Humidity": "Humidity (%)",
    "Microbes": "Microbes (CFU/g)",
    "Ethylene gas": "Ethylene (ppm)",
    "Days stored": "Days stored",
}

SAFE_RANGES = "Safe ranges in this game: temperature 2-8 °C, humidity 40-65 %, microbes below 1,000 CFU/g, ethylene below 1 ppm."
HINT = "Compare the bins with high Spoiled (%) against the healthy bins. Which column is clearly different for the spoiled bins only?"
CROPS = ["Lettuce", "Tomatoes", "Potatoes", "Beans", "Wheat", "Strawberries"]


def generate_food_challenge(rng, cause=None):
    """Build one challenge. Exactly one factor explains the spoiled bins."""
    cause = cause or rng.choice(list(CAUSES))
    if cause == "water":
        affected = {1, 3, 5}  # every bin fed by Tank 2
    else:
        affected = {rng.choice([0, 2, 4]), rng.choice([1, 3, 5])}  # mixed tanks, so tank is not the clue
        if rng.random() < 0.5:
            affected.add(rng.choice([i for i in range(6) if i not in affected]))
    crops = rng.sample(CROPS, 6)
    rows = []
    for i in range(6):
        bad = i in affected
        row = {
            "Bin": "ABCDEF"[i], "Crop": crops[i], "Days stored": rng.randint(3, 9),
            "Temp (°C)": round(rng.uniform(3, 7), 1), "Humidity (%)": rng.randint(45, 60),
            "Water tank": "Tank 1" if i % 2 == 0 else "Tank 2",
            "Microbes (CFU/g)": rng.randint(100, 500), "Ethylene (ppm)": round(rng.uniform(0.1, 0.4), 1),
        }
        if bad:
            if cause == "temperature": row["Temp (°C)"] = round(rng.uniform(12, 18), 1)
            elif cause == "humidity": row["Humidity (%)"] = rng.randint(80, 92)
            elif cause == "water": row["Microbes (CFU/g)"] = rng.randint(4000, 9000)
            elif cause == "ethylene": row["Ethylene (ppm)"] = round(rng.uniform(2.5, 4.5), 1)
        row["Spoiled (%)"] = rng.randint(35, 70) if bad else rng.randint(2, 8)
        rows.append(row)
    return {
        "cause": cause, "rows": rows, "affected_bins": ["ABCDEF"[i] for i in sorted(affected)],
        "title": "Food spoilage alert!",
        "story": "The crew found spoiled food in the storage area. Study the data to find what the spoiled bins have in common, then choose the cause and the best fix.",
    }
