"""Live NASA open data: recent solar flares from DONKI (Space Weather Database Of Notifications,
Knowledge, Information, run by NASA CCMC) through the NASA Open APIs (https://api.nasa.gov).

The app works offline: every function returns None/[] on any network or format problem.
Set NASA_API_KEY (free at https://api.nasa.gov); DEMO_KEY works but is rate-limited.
"""
import json, os, urllib.request
from datetime import date, timedelta

DONKI_FLR = "https://api.nasa.gov/DONKI/FLR?startDate={start}&endDate={end}&api_key={key}"
CLASS_ORDER = "ABCMX"
CLASS_HELP = {"A": "tiny", "B": "very small", "C": "small", "M": "medium", "X": "the strongest kind"}


def parse_flares(raw):
    """Turn the DONKI JSON list into simple rows; ignore anything malformed."""
    rows = []
    if not isinstance(raw, list):
        return rows
    for f in raw:
        if not isinstance(f, dict):
            continue
        cls = str(f.get("classType") or "").strip()
        if not cls or cls[0].upper() not in CLASS_ORDER:
            continue
        rows.append({"Class": cls, "Peak time (UTC)": str(f.get("peakTime") or f.get("beginTime") or "")})
    return rows


def strength(cls):
    letter = CLASS_ORDER.index(cls[0].upper())
    try:
        num = float(cls[1:])
    except ValueError:
        num = 0.0
    return letter * 1000 + num


def summarize(rows):
    if not rows:
        return {"count": 0, "strongest": None, "help": ""}
    top = max(rows, key=lambda r: strength(r["Class"]))["Class"]
    return {"count": len(rows), "strongest": top, "help": CLASS_HELP.get(top[0].upper(), "")}


def fetch_recent_flares(days=14, key=None, timeout=6, opener=urllib.request.urlopen):
    """Return parsed rows (newest last), or None if NASA could not be reached."""
    key = key or os.environ.get("NASA_API_KEY", "DEMO_KEY")
    end = date.today(); start = end - timedelta(days=days)
    url = DONKI_FLR.format(start=start.isoformat(), end=end.isoformat(), key=key)
    try:
        with opener(url, timeout=timeout) as r:
            return parse_flares(json.loads(r.read().decode("utf-8")))
    except Exception:
        return None
