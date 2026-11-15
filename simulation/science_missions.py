"""Evidence-based, child-friendly decision tasks for the lunar surface science module.

These questions teach broad scientific reasoning. They are not operational landing
criteria, proof of water ice, or real mission certification data.
"""

SCIENCE_ANALYSIS = {
    "ice": {
        "question": "A rover is comparing two places. Which is the better first place to investigate for possible water ice?",
        "choices": {
            "shadowed": "A permanently shadowed polar area, followed by checking several independent measurements.",
            "sunlit": "A warm, sunlit plain, because sunlight makes water ice easiest to preserve.",
            "visual": "Any bright patch that looks white in one photograph; appearance alone proves ice.",
        },
        "answer": "shadowed",
        "feedback_correct": "Good scientific reasoning! Permanently shadowed regions can stay very cold. Multiple measurements are needed; a signal is not proof of accessible ice.",
        "feedback_wrong": "Not quite. Look for places that can remain extremely cold, and remember that one image or signal cannot prove accessible water ice.",
    },
    "landing": {
        "question": "Which candidate is the better starting choice for a simplified landing-site study?",
        "choices": {
            "level": "A broad, relatively level area with fewer visible rocks and useful lighting and communications.",
            "rim": "A steep crater rim with many rocks, because it gives a wide view.",
            "unknown": "A place with no terrain observations, because unknown ground has fewer hazards.",
        },
        "answer": "level",
        "feedback_correct": "Well chosen! A relatively level, well-observed area with fewer hazards is a better candidate to study. Real landing decisions need detailed engineering data.",
        "feedback_wrong": "Try again. Consider slope, rocks, lighting, communications, and how much is known about the terrain.",
    },
}


def check_science_answer(objective_id, answer_id):
    """Return an assessment without changing game state or awarding points."""
    task = SCIENCE_ANALYSIS.get(objective_id)
    if task is None or not isinstance(answer_id, str) or answer_id not in task["choices"]:
        return {"correct": False, "feedback": "That answer is not part of this science task."}
    correct = answer_id == task["answer"]
    return {
        "correct": correct,
        "feedback": task["feedback_correct"] if correct else task["feedback_wrong"],
    }
