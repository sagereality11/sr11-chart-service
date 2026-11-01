"""Historical time zone corrections for places the IANA tzdb gets wrong.

The tzdb only promises accurate clock history from 1970. Before that, a place
with no zone of its own inherits the history of a big city nearby. Alabama,
for example, is filed under America/Chicago, so a 1956 Birmingham summer birth
gets Chicago's daylight saving time (CDT), although Alabama did not use
daylight saving time between the end of WWII war time and the Uniform Time
Act of 1966 (the tzdb "US" rule itself has no DST in 1946-1966).

Each entry below overrides the tzdb for a region and a date window. Entries
follow the conventions of the astrologers' atlases and are added only when
confirmed against a birth record, a statute or official record, or a trusted
atlas (the source is noted on each entry). Anything outside these windows
still uses the tzdb, and a visitor can always give the time zone written on
the birth record instead (``record_offset`` in service.py).

Rule kinds
  ``standard``        clocks stayed on standard time all year (no DST)
  ``winter_central``  Indiana 1957-1961: Central Standard Time (UTC-6) was the
                      legal state time; communities could use daylight time (CDT,
                      UTC-5) in summer, which is also what the tzdb gives then.
  ``season``          standard time, plus one hour inside the season the entry's
                      ``season`` function gives for that year (a state's own
                      daylight saving law, or WWII war time)
  ``dst_over_tzdb``   the tzdb's standard offset for the zone, plus one hour inside
                      the season (Alaska 1968, where several zones apply)

Changeovers are taken at 2:00 a.m. local time unless a source says otherwise.
"""

from __future__ import annotations

import datetime as dt

# --------------------------------------------------------------------------- dates

def _nth_sunday(year: int, month: int, n: int) -> dt.date:
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def _last_weekday(year: int, month: int, weekday: int) -> dt.date:
    """Last given weekday (Mon=0 .. Sun=6) of the month."""
    d = (dt.date(year, month + 1, 1) if month < 12 else dt.date(year + 1, 1, 1)) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - weekday) % 7)


def _last_sunday(year: int, month: int) -> dt.date:
    return _last_weekday(year, month, 6)


def _labor_day(year: int) -> dt.date:          # first Monday in September
    d = dt.date(year, 9, 1)
    return d + dt.timedelta(days=(0 - d.weekday()) % 7)


def _at2(d: dt.date) -> dt.datetime:
    return dt.datetime(d.year, d.month, d.day, 2, 0)


def summer_fast_time(date: dt.date) -> bool:
    """Local-option daylight saving season of the 1950s: last Sunday of April
    to last Sunday of September (date-level; the 2 am changeover is ignored)."""
    return _last_sunday(date.year, 4) <= date < _last_sunday(date.year, 9)


# --------------------------------------------------------------------------- seasons
# Each returns the (start, end) local datetimes of daylight time for a year, or None.

def season_war_time(y):
    """WWII war time, 9 Feb 1942 to 30 Sep 1945 (2:00 a.m. both ends)."""
    if 1942 <= y <= 1945:
        return (_at2(dt.date(1942, 2, 9)) if y == 1942 else dt.datetime(y, 1, 1),
                _at2(dt.date(1945, 9, 30)) if y == 1945 else dt.datetime(y + 1, 1, 1))
    return None


def season_oregon_1962(y):
    """Measure 6 (1962): last Sunday in April to last Saturday in September."""
    return _at2(_last_sunday(y, 4)), _at2(_last_weekday(y, 9, 5))


def season_virginia_1962(y):
    """Acts 1962 ch. 617: between Memorial Day (30 May) and Labor Day."""
    return _at2(dt.date(y, 5, 30)), _at2(_labor_day(y))


def season_virginia_1964(y):
    """Acts 1964 ch. 646: first Sunday after Memorial Day to the Sunday before Labor Day."""
    md = dt.date(y, 5, 30)
    start = md + dt.timedelta(days=(6 - md.weekday()) % 7 or 7)
    return _at2(start), _at2(_labor_day(y) - dt.timedelta(days=1))


def season_west_virginia_1963(y):
    """1963 HB 14: fourth Sunday of April to fourth Sunday of September."""
    return _at2(_nth_sunday(y, 4, 4)), _at2(_nth_sunday(y, 9, 4))


def season_minnesota_1959(y):
    """1959 law: fourth Sunday in May to the Tuesday after Labor Day."""
    return _at2(_nth_sunday(y, 5, 4)), _at2(_labor_day(y) + dt.timedelta(days=1))


def season_dc_1953(y):
    """P.L. 83-22 (1953): DST in the District no later than the last Sunday in September."""
    return _at2(_last_sunday(y, 4)), _at2(_last_sunday(y, 9))


def season_alaska_1968(y):
    """First year Alaska observed the Uniform Time Act: 28 Apr to 27 Oct 1968."""
    return (_at2(dt.date(1968, 4, 28)), _at2(dt.date(1968, 10, 27))) if y == 1968 else None


# --------------------------------------------------------------------------- table
# US admin2 codes are county FIPS codes as used by GeoNames (Virginia's independent
# cities have their own codes, e.g. Alexandria 510).

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
    # ---- added Nov 2026, from statutes and official records -----------------------------
    {
        "id": "us-nc-no-dst-1946-1965",     # NCpedia "Time zones"
        "country": "US", "admin1_code": "NC", "admin2_code": None,
        "start": dt.date(1945, 9, 30), "end": dt.date(1965, 12, 31),
        "kind": "standard", "std_minutes": -300, "abbrev": "EST",
        "note": "North Carolina did not observe daylight saving time from 1946 to 1965, so "
                "Eastern Standard Time (UTC-5) is used all year.",
    },
    {
        "id": "us-wi-no-dst-1946-1956",     # state ban (1923, penalties 1931) until the April 1957 referendum
        "country": "US", "admin1_code": "WI", "admin2_code": None,
        "start": dt.date(1945, 9, 30), "end": dt.date(1956, 12, 31),
        "kind": "standard", "std_minutes": -360, "abbrev": "CST",
        "note": "Wisconsin law banned daylight saving time until the 1957 referendum, so "
                "Central Standard Time (UTC-6) is used all year.",
    },
    {
        "id": "us-wa-no-dst-1953-1960",     # 1952 initiative (HistoryLink 20953); statewide DST again from 1961
        "country": "US", "admin1_code": "WA", "admin2_code": None, "tz": ["America/Los_Angeles"],
        "start": dt.date(1953, 1, 1), "end": dt.date(1960, 12, 31),
        "kind": "standard", "std_minutes": -480, "abbrev": "PST",
        "note": "Daylight saving time was illegal in Washington from 1953 to 1960, so "
                "Pacific Standard Time (UTC-8) is used all year.",
    },
    {
        "id": "us-or-dst-to-last-saturday-september-1963-1966",   # Measure 6 (1962)
        "country": "US", "admin1_code": "OR", "admin2_code": None, "tz": ["America/Los_Angeles"],
        "start": dt.date(1963, 1, 1), "end": dt.date(1966, 12, 31),
        "kind": "season", "season": season_oregon_1962,
        "std_minutes": -480, "abbrev": "PST", "dst_abbrev": "PDT",
        "note": "Oregon's 1962 law ran daylight saving time from the last Sunday in April to the "
                "last Saturday in September.",
    },
    {
        "id": "us-va-dst-memorial-to-labor-day-1962-1963",       # Acts 1962 ch. 617
        "country": "US", "admin1_code": "VA", "admin2_code": None,
        "exclude_admin2": ["013", "059", "510", "600", "610", "520"],   # 10th District localities could choose Apr-Oct; Bristol
        "start": dt.date(1962, 1, 1), "end": dt.date(1963, 12, 31),
        "kind": "season", "season": season_virginia_1962,
        "std_minutes": -300, "abbrev": "EST", "dst_abbrev": "EDT",
        "note": "Virginia's 1962 law put daylight saving time between Memorial Day and Labor Day.",
    },
    {
        "id": "us-va-dst-june-to-september-1964-1965",           # Acts 1964 ch. 646
        "country": "US", "admin1_code": "VA", "admin2_code": None,
        "exclude_admin2": ["013", "059", "510", "600", "610", "520"],
        "start": dt.date(1964, 1, 1), "end": dt.date(1965, 12, 31),
        "kind": "season", "season": season_virginia_1964,
        "std_minutes": -300, "abbrev": "EST", "dst_abbrev": "EDT",
        "note": "Virginia's 1964 law ran daylight saving time from the first Sunday after Memorial Day "
                "to the Sunday before Labor Day.",
    },
    {
        "id": "us-wv-dst-to-fourth-sunday-september-1963-1966",  # 1963 HB 14
        "country": "US", "admin1_code": "WV", "admin2_code": None,
        "start": dt.date(1963, 1, 1), "end": dt.date(1966, 12, 31),
        "kind": "season", "season": season_west_virginia_1963,
        "std_minutes": -300, "abbrev": "EST", "dst_abbrev": "EDT",
        "note": "West Virginia's 1963 law ran daylight saving time from the fourth Sunday of April "
                "to the fourth Sunday of September.",
    },
    {
        "id": "us-mn-dst-may-to-september-1960-1966",            # 1959 special-session law
        "country": "US", "admin1_code": "MN", "admin2_code": None,
        "start": dt.date(1960, 1, 1), "end": dt.date(1966, 12, 31),
        "exclude_years_admin2": {1965: ["123"]},                 # St. Paul (Ramsey) started early in 1965
        "kind": "season", "season": season_minnesota_1959,
        "std_minutes": -360, "abbrev": "CST", "dst_abbrev": "CDT",
        "note": "Minnesota's 1959 law ran daylight saving time from the fourth Sunday in May to the "
                "Tuesday after Labor Day.",
    },
    {
        "id": "us-dc-dst-ends-september-1955-1956",              # P.L. 83-22 (1953)
        "country": "US", "admin1_code": "DC", "admin2_code": None,
        "start": dt.date(1955, 1, 1), "end": dt.date(1956, 12, 31),
        "kind": "season", "season": season_dc_1953,
        "std_minutes": -300, "abbrev": "EST", "dst_abbrev": "EDT",
        "note": "Federal law did not allow daylight saving time in Washington, D.C. after the last "
                "Sunday in September.",
    },
    {
        "id": "us-ak-dst-1968",       # Alaska Historical Society; Daily Sitka Sentinel 22 Apr 1968
        "country": "US", "admin1_code": "AK", "admin2_code": None,
        "start": dt.date(1968, 1, 1), "end": dt.date(1968, 12, 31),
        "kind": "dst_over_tzdb", "season": season_alaska_1968,
        "note": "Alaska first observed daylight saving time under the Uniform Time Act from "
                "28 April to 27 October 1968.",
    },
    {
        "id": "us-tn-knox-county-central-before-1946",           # Mayor's proclamation, 27 Apr 1946 (WATE)
        "country": "US", "admin1_code": "TN", "admin2_code": "093",
        "start": dt.date(1920, 1, 1), "end": dt.date(1946, 4, 26),
        "kind": "season", "season": season_war_time,
        "std_minutes": -360, "abbrev": "CST", "dst_abbrev": "CWT",
        "note": "Knoxville kept Central time (UTC-6, and Central War Time during WWII) until it moved "
                "to Eastern time on 27 April 1946.",
    },
    {
        "id": "us-ga-fulton-central-before-1941",                # GA law signed 21 Mar 1941 (Past Tense GA)
        "country": "US", "admin1_code": "GA", "admin2_code": "121",
        "start": dt.date(1920, 1, 1), "end": dt.date(1941, 3, 21),
        "kind": "standard", "std_minutes": -360, "abbrev": "CST",
        "note": "Atlanta kept Central Standard Time (UTC-6) until Georgia moved to Eastern time in "
                "March 1941.",
    },
]

_DST_NAMES = {-480: "PDT", -540: "YDT", -600: "AHDT", -660: "BDT"}


def find(place: dict | None, date: dt.date) -> dict | None:
    """The correction that applies to this birthplace and date, if any."""
    if not place or place.get("manual"):
        return None
    for c in CORRECTIONS:
        if place.get("country_code") != c["country"] or place.get("admin1_code") != c["admin1_code"]:
            continue
        a2 = place.get("admin2_code")
        if c["admin2_code"] is not None and a2 != c["admin2_code"]:
            continue
        if a2 in c.get("exclude_admin2", ()):
            continue
        if a2 in c.get("exclude_years_admin2", {}).get(date.year, ()):
            continue
        if c.get("tz") and place.get("tz") not in c["tz"]:
            continue
        if c["start"] <= date <= c["end"]:
            return c
    return None


def in_season(corr: dict, local: dt.datetime) -> bool:
    s = corr["season"](local.year)
    return bool(s) and s[0] <= local < s[1]


def offset_for(corr: dict, local: dt.datetime, tzdb_std_minutes: int | None = None):
    """(utc offset minutes, abbreviation, dst active) for a ``season`` or
    ``dst_over_tzdb`` correction at this local time."""
    if corr["kind"] == "dst_over_tzdb":
        dst = in_season(corr, local)
        return tzdb_std_minutes + (60 if dst else 0), (_DST_NAMES.get(tzdb_std_minutes) if dst else None), dst
    dst = in_season(corr, local)
    return corr["std_minutes"] + (60 if dst else 0), corr["dst_abbrev"] if dst else corr["abbrev"], dst
