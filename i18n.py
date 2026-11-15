"""English / Arabic support for LunaBase.

Every visible text in the game is written in English in the code and looked up in AR (English -> Arabic)
at display time:  tr(lang, "Start new mission")  ->  "ابدأ مهمة جديدة"  when lang == "ar".
A text that has no Arabic entry simply stays in English, so nothing can crash.
Texts with values use {name} placeholders:  tr(lang, "Day {day}", day=3).
"""
from i18n_ar import AR

LANGS = {"en": "English", "ar": "العربية"}
RTL_LANGS = ("ar",)


def is_rtl(lang):
    return lang in RTL_LANGS


def tr(lang, text, **kw):
    """Translate `text` (English) into `lang`, then fill the {placeholders}."""
    out = AR.get(text, text) if lang == "ar" else text
    return out.format(**kw) if kw else out


def num(lang, value, signed=False):
    """A number that keeps its sign and digits in the right order inside Arabic sentences."""
    s = f"{value:+d}" if signed else str(value)
    return f"⁦{s}⁩" if lang == "ar" else s
