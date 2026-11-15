"""Choice-based, age-appropriate emergency learning scenarios.

These are simplified educational exercises, not operational flight procedures.
"""

DRILLS = {
    "shelter": {
        "prompt": "A radiation alert arrives while the crew is outside. What is the safest first choice in this simulation?",
        "choices": {
            "shelter": "Guide the crew to the designated shielded shelter and monitor mission updates.",
            "wait": "Stay outside until the alert disappears.",
            "split": "Send each crew member in a different direction.",
        },
        "correct": "shelter",
        "feedback_correct": "Correct. Protecting the crew and following updated mission guidance come first.",
        "feedback_wrong": "Try again. Choose the response that gets the whole crew to shielding and keeps them informed.",
        "coach": "Mission Coach: keep the crew together, use the planned shielded area, and wait for updated guidance.",
    },
    "isolate": {
        "prompt": "A habitat sensor reports a leak in one module. What should the crew do first in this training scenario?",
        "choices": {
            "isolate": "Follow the habitat plan to isolate the affected module and check crew safety.",
            "ignore": "Ignore the sensor because it may be a false alarm.",
            "open": "Open every hatch to equalize the habitat.",
        },
        "correct": "isolate",
        "feedback_correct": "Correct. Treat the warning seriously, protect the crew, and isolate the affected area using the simulated plan.",
        "feedback_wrong": "Not quite. Avoid ignoring the alarm or changing every hatch. Select the controlled isolation response.",
        "coach": "Mission Coach: confirm the alert, account for the crew, and use the designated isolation plan in the simulation.",
    },
    "backup": {
        "prompt": "The main power system fails. Which choice best protects essential habitat functions in this simulation?",
        "choices": {
            "backup": "Switch to the backup-power plan and reduce non-essential loads.",
            "keep_all": "Keep every device running at full power.",
            "disconnect": "Disconnect all systems, including life support.",
        },
        "correct": "backup",
        "feedback_correct": "Correct. Preserve essential systems and manage limited power carefully.",
        "feedback_wrong": "Try again. The best choice protects essential systems without wasting the remaining power.",
        "coach": "Mission Coach: prioritize life support and communications, then reduce non-essential power use.",
    },
}


def evaluate_drill(drill_id, choice_id):
    """Evaluate one answer without awarding points or mutating game state."""
    drill = DRILLS.get(drill_id)
    if not drill or choice_id not in drill["choices"]:
        return {"ok": False, "correct": False, "feedback": "Unknown drill or answer."}
    correct = choice_id == drill["correct"]
    return {
        "ok": True,
        "correct": correct,
        "feedback": drill["feedback_correct"] if correct else drill["feedback_wrong"],
        "coach": drill["coach"],
    }
