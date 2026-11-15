"""Life-support subsystem health and resource-use estimates for LunaBase.

All values are simplified educational game rules, not spacecraft engineering data.
"""
from __future__ import annotations

BASE_DAILY_USE = {"water": 6, "oxygen": 5, "energy": 7, "food": 6}
SUBSYSTEMS = {
    "water_recycler": {"label": "Water recycler", "emoji": "💧", "daily_wear": 7},
    "oxygen_generator": {"label": "Oxygen generator", "emoji": "🫁", "daily_wear": 6},
    "solar_array": {"label": "Solar array", "emoji": "☀️", "daily_wear": 8},
}
HEALTHY_THRESHOLD = 60


def initial_subsystem_health() -> dict[str, int]:
    return {key: 100 for key in SUBSYSTEMS}


def daily_consumption(difficulty_multiplier: float, subsystem_health: dict[str, int] | None = None) -> dict[str, int]:
    """Estimate the next base-day draw, including penalties from damaged equipment."""
    health = subsystem_health or initial_subsystem_health()
    use = {key: round(value * difficulty_multiplier) for key, value in BASE_DAILY_USE.items()}
    if health.get("water_recycler", 100) < HEALTHY_THRESHOLD:
        use["water"] += 2
    if health.get("oxygen_generator", 100) < HEALTHY_THRESHOLD:
        use["oxygen"] += 2
    if health.get("solar_array", 100) < HEALTHY_THRESHOLD:
        use["energy"] += 3
    return use


def wear_subsystems(subsystem_health: dict[str, int]) -> list[str]:
    """Apply one day of normal wear and return localized-by-caller system keys."""
    worn = []
    for key, spec in SUBSYSTEMS.items():
        before = subsystem_health.get(key, 100)
        subsystem_health[key] = max(0, before - spec["daily_wear"])
        if before >= HEALTHY_THRESHOLD > subsystem_health[key]:
            worn.append(key)
    return worn


def repair_subsystems(subsystem_health: dict[str, int], amount: int = 18) -> dict[str, int]:
    """Restore all three critical subsystems, capped at 100."""
    restored = {}
    for key in SUBSYSTEMS:
        before = subsystem_health.get(key, 100)
        subsystem_health[key] = min(100, before + amount)
        restored[key] = subsystem_health[key] - before
    return restored


def subsystem_status(health: int) -> str:
    if health >= 75:
        return "Good"
    if health >= HEALTHY_THRESHOLD:
        return "Watch"
    return "Repair"
