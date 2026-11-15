"""Simple, explainable greenhouse climate controls for the educational simulator.

Thresholds are teaching assumptions, not lunar agriculture engineering limits.
"""
DEFAULT_ENVIRONMENT = {
    "temperature_c": 21,
    "humidity_pct": 65,
    "light_hours": 16,
    "nutrient_ph": 6.0,
}

CONTROL_RANGES = {
    "temperature_c": (18, 24),
    "humidity_pct": (55, 75),
    "light_hours": (14, 18),
    "nutrient_ph": (5.5, 6.5),
}

CONTROL_LABELS = {
    "temperature_c": "Air temperature (°C)",
    "humidity_pct": "Relative humidity (%)",
    "light_hours": "Daily light period (hours)",
    "nutrient_ph": "Nutrient solution pH",
}


def assess_environment(environment=None):
    """Return control-by-control status and a conservative game-only growth factor."""
    env = dict(DEFAULT_ENVIRONMENT)
    if environment:
        env.update(environment)
    checks = {}
    deviations = 0
    severe = 0
    for key, (low, high) in CONTROL_RANGES.items():
        value = float(env[key])
        if low <= value <= high:
            status = "optimal"
        else:
            status = "adjust"
            deviations += 1
            if value < low - (high - low) * 0.5 or value > high + (high - low) * 0.5:
                severe += 1
        checks[key] = {"value": value, "low": low, "high": high, "status": status}
    factor = 1.0 if deviations == 0 else (0.55 if severe or deviations >= 3 else 0.8)
    return {"checks": checks, "deviations": deviations, "severe": severe,
            "factor": factor, "status": "optimal" if deviations == 0 else "needs_adjustment"}


def environment_snapshot(environment=None):
    env = dict(DEFAULT_ENVIRONMENT)
    if environment:
        env.update(environment)
    return {key: env[key] for key in DEFAULT_ENVIRONMENT}
