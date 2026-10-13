"""Historical time zone corrections for places the IANA tzdb gets wrong.

The tzdb only promises accurate clock history from 1970. Before that, a place
with no zone of its own inherits the history of a big city nearby. Alabama,
for example, is filed under America/Chicago, so a 1956 Birmingham summer birth
gets Chicago's daylight saving time (CDT), although Alabama did not use
daylight saving time between the end of WWII war time and the Uniform Time
Act of 1966 (the tzdb "US" rule itself has no DST in 1946-1966).

Each entry below overrides the tzdb for a region and a date window. Entries
follow the conventions of the astrologers' atlases and are added only when
confirmed against a birth record or a trusted atlas. Anything outside these
windows still uses the tzdb, and a visitor can always give the time zone
written on the birth record instead (``record_offset`` in service.py).

Rule kinds
  ``standard``     clocks stayed on standard time all year (no DST)
  ``winter_central``  Indiana 1957-1961: Central Standard Time (UTC-6) was the
                   legal state time; communities could use daylight time (CDT,
                   UTC-5) in summer, which is also what the tzdb gives then.
"""

from __future__ import annotations

import datetime as dt

# US admin2 codes are county FIPS codes as used by GeoNames.
CORRECTIONS = [
    {
        "id": "us-al-no-dst-1946-1966",
        "country": "US", "admin1_code": "AL", "admin2_code": None,
        "start": dt.date(1945, 9, 30), "end": dt.date(1966, 12, 31),   # inclusive
        "kind": "standard", "std_minutes": -360, "abbrev": "CST",
        "note": "Alabama did not observe daylight saving time between WWII war time and the "
                "Uniform Time Act, so Central Standard Time (UTC-6) is used all year.",
    },
    {
        "id": "us-in-miami-county-cst-1957-1961",
        "country": "US", "admin1_code": "IN", "admin2_code": "103",    # Miami County (Peru)
        "start": dt.date(1957, 9, 29), "end": dt.date(1961, 4, 30),
        "kind": "winter_central", "std_minutes": -360, "abbrev": "CST",
        "note": "Under Indiana's 1957 time law, Central Standard Time (UTC-6) was the legal time in "
                "winter in this county, rather than the Eastern time the tzdb gives for central Indiana.",
    },
]


def _last_sunday(year: int, month: int) -> dt.date:
    d = dt.date(year, month + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)


def summer_fast_time(date: dt.date) -> bool:
    """Local-option daylight saving season of the 1950s: last Sunday of April
    to last Sunday of September (date-level; the 2 am changeover is ignored)."""
    return _last_sunday(date.year, 4) <= date < _last_sunday(date.year, 9)


def find(place: dict | None, date: dt.date) -> dict | None:
    """The correction that applies to this birthplace and date, if any."""
    if not place or place.get("manual"):
        return None
    for c in CORRECTIONS:
        if place.get("country_code") != c["country"] or place.get("admin1_code") != c["admin1_code"]:
            continue
        if c["admin2_code"] is not None and place.get("admin2_code") != c["admin2_code"]:
            continue
        if c["start"] <= date <= c["end"]:
            return c
    return None
