"""Educational surface-science progression and emergency drills for LunaBase.

All thresholds and rewards here are game mechanics, not flight rules or engineering data.
"""
from datetime import datetime, timezone

SCIENCE_OBJECTIVES = (
    {"id": "sample", "title": "Collect a lunar rock sample", "detail": "Drag the astronaut to the sample marker in the exterior scene.", "reward": 5},
    {"id": "rover", "title": "Complete a rover surface survey", "detail": "Drag the rover to the survey marker in the scene.", "reward": 5},
    {"id": "ice", "title": "Evaluate a possible water-ice site", "detail": "Compare a permanently shadowed region with a sunlit area; this is a hypothesis, not proof of accessible ice.", "reward": 5},
    {"id": "landing", "title": "Select a safer landing zone", "detail": "Prefer a relatively level, well-observed area and avoid steep crater rims and obvious hazards.", "reward": 5},
)


def ensure_progress(game):
    # Merge defaults instead of replacing or trusting partially migrated save data.
    science_defaults = {"sample": False, "rover": False, "ice": False, "landing": False}
    science = game.setdefault("science", {})
    if not isinstance(science, dict):
        science = {}
        game["science"] = science
    for key, default in science_defaults.items():
        science.setdefault(key, default)
    if not isinstance(game.get("science_answers"), dict):
        game["science_answers"] = {}
    game.setdefault("emergency_drills", [])
    if not isinstance(game.get("emergency_answers"), dict):
        game["emergency_answers"] = {}
    game.setdefault("greenhouse_badges", [])
    return game


def record_science(game, objective_id):
    ensure_progress(game)
    if objective_id not in game["science"] or game["science"][objective_id]:
        return {"ok": False, "message": "Objective already completed or unknown."}
    game["science"][objective_id] = True
    game["score"] = min(100, game.get("score", 0) + 5)
    game["learning_points"] = game.get("learning_points", 0) + 1
    game["decisions_count"] = game.get("decisions_count", 0) + 1
    title = next(x["title"] for x in SCIENCE_OBJECTIVES if x["id"] == objective_id)
    message = f"Science objective completed: {title}."
    game.setdefault("events_log", []).append({"day": game.get("day", 1), "message": message})
    return {"ok": True, "message": message}


def complete_emergency_drill(game, drill_id):
    ensure_progress(game)
    allowed = {"shelter": "Move crew to the shielded shelter", "isolate": "Isolate a damaged habitat module", "backup": "Switch to backup power"}
    if drill_id not in allowed or drill_id in game["emergency_drills"]:
        return {"ok": False, "message": "Drill already completed or unknown."}
    game["emergency_drills"].append(drill_id)
    game["score"] = min(100, game.get("score", 0) + 3)
    game["learning_points"] = game.get("learning_points", 0) + 1
    message = f"Emergency drill completed: {allowed[drill_id]}."
    game.setdefault("events_log", []).append({"day": game.get("day", 1), "message": message})
    return {"ok": True, "message": message}


def certificate_text(game, player="Astronaut"):
    ensure_progress(game)
    done = sum(bool(v) for v in game["science"].values())
    status = "completed" if game.get("status") == "won" else "practiced"
    return ("LUNABASE JUNIOR ASTRONAUT CERTIFICATE\n"
            "======================================\n"
            f"Awarded to: {player or 'Astronaut'}\n"
            f"Mission status: {status}\n"
            f"Science objectives: {done}/{len(game['science'])}\n"
            f"Emergency drills: {len(game['emergency_drills'])}/3\n"
            f"Learning points: {game.get('learning_points', 0)}\n"
            f"Score: {game.get('score', 0)}\n"
            f"Issued: {datetime.now(timezone.utc).strftime('%Y-%m-%d')} UTC\n\n"
            "This is an educational game certificate, not an official astronaut qualification.\n")
