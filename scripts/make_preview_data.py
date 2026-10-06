"""Generate the labeled SAMPLE charts used by the preview page.

Every number comes from the real calculation pipeline (Swiss Ephemeris),
computed for each house system. None of these are real people's charts.

Usage: python scripts/make_preview_data.py > preview-data.json
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SR11_GEONAMES_DIR", str(ROOT / "tests" / "fixtures" / "geonames"))

from sr11calc import engine  # noqa: E402
from sr11calc.places import PlaceIndex  # noqa: E402
from sr11calc.service import build_chart, parse_request  # noqa: E402

PLACES = PlaceIndex()

SAMPLES = [
    {"key": "a", "label": "Sample A — New York, 17 May 1990, 2:30 PM",
     "req": {"year": 1990, "month": 5, "day": 17, "hour": 14, "minute": 30, "place": 5128581}},
    {"key": "b", "label": "Sample B — Stellium test: New Delhi, 4 Feb 1962, 5:00 PM",
     "req": {"year": 1962, "month": 2, "day": 4, "hour": 17, "minute": 0, "place": 1261481}},
    {"key": "c", "label": "Sample C — Southern Hemisphere: Sydney, 9 Oct 1985, 6:45 AM",
     "req": {"year": 1985, "month": 10, "day": 9, "hour": 6, "minute": 45, "place": 2147714}},
    {"key": "d", "label": "Sample D — High latitude: Tromsø, Norway, 21 Dec 1990, 12:00 PM",
     "req": {"year": 1990, "month": 12, "day": 21, "hour": 12, "minute": 0, "place": 3133895}},
    {"key": "e", "label": "Sample E — Unknown birth time: London, 21 Mar 2003",
     "req": {"year": 2003, "month": 3, "day": 21, "hour": None, "minute": None, "place": 2643743}},
]


def body_for(r, hsys):
    b = {"year": r["year"], "month": r["month"], "day": r["day"], "house_system": hsys,
         "location": {"mode": "place", "place_id": r["place"]}}
    if r["hour"] is None:
        b["time_known"] = False
    else:
        b.update(hour=r["hour"], minute=r["minute"])
    return b


out = []
for smp in SAMPLES:
    entry = {"key": smp["key"], "label": smp["label"], "charts": {}}
    if smp["req"]["hour"] is None:
        entry["charts"]["none"] = build_chart(parse_request(body_for(smp["req"], "P"), PLACES))
    else:
        for code in engine.HOUSE_SYSTEMS:
            entry["charts"][code] = build_chart(parse_request(body_for(smp["req"], code), PLACES))
    out.append(entry)

json.dump({"generated_with": engine.engine_info(), "samples": out,
           "house_systems": engine.HOUSE_SYSTEMS}, sys.stdout, ensure_ascii=False)
