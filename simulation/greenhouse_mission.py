"""Seven-day greenhouse learning mission: establish new seedlings and protect mature crops."""

from i18n import tr
from simulation.greenhouse_controls import DEFAULT_ENVIRONMENT

MAX_GREENHOUSE_DAYS = 7
NEW_CROPS = ("Radish", "Arugula", "Lettuce seedlings")
ESTABLISHED_CROPS = ("Tomatoes", "Cucumbers")

DAILY_TASKS = {
    1: ["Inspect the greenhouse and record the starting condition of all beds.",
        "Plant radish, arugula, and lettuce in the empty beds.",
        "Check water delivery and confirm suitable light for the planted beds.",
        "Inspect existing tomato and cucumber plants; record fruit and leaf condition."],
    2: ["Check moisture in the newly planted beds and water only as needed.",
        "Inspect tomato and cucumber root zones and maintain steady irrigation.",
        "Check light exposure and remove avoidable shading from established crops."],
    3: ["Inspect emergence and early seedling condition; record observations without assuming a fixed growth rate.",
        "Check established crops for leaf or fruit stress.",
        "Review calcium availability for tomatoes and cucumbers according to the cultivation system."],
    4: ["Check moisture and drainage in the new planting beds.",
        "Inspect established fruits for signs of physiological stress.",
        "Verify that lighting remains appropriate for both new and established crops."],
    5: ["Record seedling development and compare it with Day 1 observations.",
        "Maintain consistent irrigation for established tomato and cucumber plants.",
        "Reassess calcium management and correct only if the crop system indicates a need."],
    6: ["Inspect seedlings for early establishment and note any uneven growth.",
        "Protect existing tomato and cucumber fruits; check plant support and leaf condition.",
        "Review water, light, and nutrient observations before the final assessment."],
    7: ["Evaluate germination or early establishment of radish, arugula, and lettuce.",
        "Evaluate the condition and survival of existing tomato and cucumber fruits.",
        "Summarize water, light, and calcium-management decisions and identify next steps."],
}


def create_greenhouse_mission():
    return {"day": 1, "completed": {day: [] for day in DAILY_TASKS},
            "status": "active", "observations": [], "score": 0,
            # base-resource link (see simulation/greenhouse_link.py)
            "tasks_since_flow": 0, "harvest_kg": 0.0, "linked_days": 0, "last_flow": None,
            "last_advance_base_day": None,
            "environment": dict(DEFAULT_ENVIRONMENT), "environment_history": []}


def complete_task(mission, task):
    if mission["status"] != "active":
        return {"ok": False, "message": "The greenhouse mission is complete."}
    tasks = DAILY_TASKS[mission["day"]]
    if task not in tasks:
        return {"ok": False, "message": "Unknown task for this day."}
    done = mission["completed"][mission["day"]]
    if task not in done:
        done.append(task)
        mission["score"] += 1
        mission["tasks_since_flow"] += 1
    return {"ok": True, "message": "Task recorded."}


def advance_greenhouse_day(mission, base_day=None, lang="en"):
    """Advance the greenhouse day. If base_day is given, allow only one advance per base day."""
    if mission["status"] != "active":
        return {"ok": False, "message": tr(lang, "The greenhouse mission is complete.")}
    day = mission["day"]
    missing = [task for task in DAILY_TASKS[day] if task not in mission["completed"][day]]
    if missing:
        return {"ok": False, "message": tr(lang, "Complete the {n} remaining task(s) before advancing.", n=len(missing))}
    if base_day is not None and mission.get("last_advance_base_day") == base_day:
        return {"ok": False, "message": tr(lang, "One greenhouse day per base day. Press End day on the base first.")}
    if base_day is not None:
        mission["last_advance_base_day"] = base_day
    if day == MAX_GREENHOUSE_DAYS:
        mission["status"] = "completed"
        return {"ok": True, "message": tr(lang, "Seven-day greenhouse assessment completed.")}
    mission["day"] += 1
    return {"ok": True, "message": tr(lang, "Greenhouse Day {day} started.", day=mission["day"])}


def greenhouse_summary(mission):
    total = sum(len(tasks) for tasks in DAILY_TASKS.values())
    done = sum(len(tasks) for tasks in mission["completed"].values())
    return {"day": mission["day"], "completed_tasks": done, "total_tasks": total,
            "progress_percent": round(done / total * 100), "score": mission["score"],
            "status": mission["status"]}
