import ast
import glob
import os
import re
import string
import unittest

from i18n import AR, num, tr
from ai.mission_coach import get_coach_advice
from education.learning_content import LEARNING_CARDS, QUIZ
from simulation.eden_iss_data import CROPS as EDEN_CROPS
from simulation.food_challenge import CAUSES, CROPS, FACTOR_COLUMNS, HINT, SAFE_RANGES
from simulation.game_engine import (ACTIONS, ASTRONAUTS, DEPENDENCIES, EVENTS, FAILURE_INFO, RESOURCE_LABELS,
                                    advance_day, build_report, create_new_game, perform_action,
                                    resolve_food_challenge)
from simulation.greenhouse_mission import DAILY_TASKS
from simulation.emergency_training import DRILLS
from simulation.greenhouse_controls import CONTROL_LABELS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fields(text):
    return sorted(f[1] for f in string.Formatter().parse(text) if f[1])


def source_texts():
    """Every literal passed to tr(...) / T(...) in the code base."""
    found = set()
    for path in glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True):
        rel = os.path.relpath(path, ROOT)
        if rel.startswith("tests") or rel == "i18n_ar.py":
            continue
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "T" and node.args and isinstance(node.args[0], ast.Constant):
                    found.add(node.args[0].value)
                if node.func.id == "tr" and len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                    found.add(node.args[1].value)
    return found


def content_texts():
    out = set()
    for a in ACTIONS.values():
        out |= {a["name"], a["description"], a["lesson"]}
    for a in ASTRONAUTS:
        out |= {a["name"], a["role"], a["bonus"], a["description"]}
    for e in EVENTS:
        out |= {e[0], e[2], e[3]}
    out |= {d[3] for d in DEPENDENCIES} | set(RESOURCE_LABELS.values())
    for v in FAILURE_INFO.values():
        out |= {v["story"], v["tip"]}
    for c in CAUSES.values():
        out |= {c["keep_fresh"], c["label"], c["fix"], c["lesson"]}
    out |= set(FACTOR_COLUMNS) | set(FACTOR_COLUMNS.values()) | set(CROPS) | {SAFE_RANGES, HINT}
    out |= set(CONTROL_LABELS.values())
    for drill in DRILLS.values():
        out |= {drill["prompt"], drill["feedback_correct"], drill["feedback_wrong"], drill["coach"]}
        out |= set(drill["choices"].values())
    for tasks in DAILY_TASKS.values():
        out |= set(tasks)
    for c in LEARNING_CARDS:
        out |= {c["title"], c["body"], c["takeaway"]}
    for q in QUIZ:
        out |= {q["question"], q["explanation"]} | set(q["options"])
    for c in EDEN_CROPS:
        out |= {c["name"], c["category"], c["harvest"]}
    return out


class TestTranslationCoverage(unittest.TestCase):
    def test_every_text_in_the_code_has_arabic(self):
        missing = sorted(t for t in source_texts() | content_texts() if t not in AR)
        self.assertEqual(missing, [], f"{len(missing)} texts have no Arabic translation")

    def test_placeholders_match(self):
        for en, ar in AR.items():
            self.assertEqual(_fields(en), _fields(ar), en)

    def test_arabic_text_is_arabic(self):
        keep = {"Little Hero"}
        for en, ar in AR.items():
            if en in keep:
                continue
            self.assertTrue(re.search(r"[؀-ۿ]", ar) or not re.search("[A-Za-z]{3}", en), en)

    def test_tr_fallback_and_format(self):
        self.assertEqual(tr("en", "Day {d}", d=3), "Day 3")
        self.assertEqual(tr("ar", "text with no translation"), "text with no translation")
        self.assertIn("3", tr("ar", "Day {d}", d=3))
        self.assertEqual(num("en", 5, True), "+5")
        self.assertIn("+5", num("ar", 5, True))


class TestArabicGame(unittest.TestCase):
    def test_default_language_is_english(self):
        g = create_new_game(seed=1)
        self.assertEqual(g["lang"], "en")
        self.assertIn("completed", perform_action(g, "grow_food")["message"])

    def test_bad_language_falls_back_to_english(self):
        self.assertEqual(create_new_game(lang="fr")["lang"], "en")

    def test_arabic_messages(self):
        g = create_new_game("Easy", seed=3, lang="ar")
        msg = perform_action(g, "grow_food")["message"]
        self.assertRegex(msg, r"[؀-ۿ]")
        for m in advance_day(g)["messages"]:
            self.assertRegex(m, r"[؀-ۿ]")
        self.assertRegex(build_report(g), r"[؀-ۿ]")
        self.assertRegex(" ".join(get_coach_advice(g)["recommendations"]), r"[؀-ۿ]")

    def test_english_game_stays_english(self):
        g = create_new_game("Easy", seed=3)
        for m in advance_day(g)["messages"]:
            self.assertNotRegex(m, r"[؀-ۿ]")

    def test_food_alert_in_arabic(self):
        g = create_new_game("Easy", seed=1, lang="ar")
        for _ in range(2):
            advance_day(g)
        r = resolve_food_challenge(g, g["pending_challenge"]["cause"], g["pending_challenge"]["cause"])
        self.assertRegex(r["message"], r"[؀-ۿ]")
        self.assertRegex(r["keep_fresh"], r"[؀-ۿ]")


if __name__ == "__main__":
    unittest.main()
