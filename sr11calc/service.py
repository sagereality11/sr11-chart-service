"""Request-level orchestration: validated input -> full chart response.

Kept separate from the HTTP layer (app.py) so the same function serves the
web endpoint, the test suite and the preview generator.
"""

from __future__ import annotations

import datetime as dt

from . import asteroids as ast
from . import engine, timeconv
from .aspects import OPTIONAL_ASPECTS, sanitize_orbs


class InputError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _int(v, name, lo, hi):
    if isinstance(v, bool):
        raise InputError("invalid_input", f"{name} must be a whole number.")
    if isinstance(v, str):
        s = v.strip()
        if not s.lstrip("-").isdigit() or len(s) > 6:
            raise InputError("invalid_input", f"{name} must be a whole number.")
        v = int(s)
    if not isinstance(v, int):
        raise InputError("invalid_input", f"{name} must be a whole number.")
    if not lo <= v <= hi:
        raise InputError("invalid_input", f"{name} is out of range.")
    return v


def _float(v, name, lo, hi):
    try:
        f = float(v)
    except (TypeError, ValueError):
        raise InputError("invalid_input", f"{name} must be a number.")
    if not (lo <= f <= hi):
        raise InputError("invalid_input", f"{name} must be between {lo} and {hi}.")
    return f


def parse_request(body: dict, places=None) -> dict:
    """Validate and normalize a chart request. Never trusts the browser."""
    if not isinstance(body, dict):
        raise InputError("invalid_input", "Malformed request.")
    year = _int(body.get("year"), "Year", 1, 9999)
    month = _int(body.get("month"), "Month", 1, 12)
    day = _int(body.get("day"), "Day", 1, 31)
    try:
        date = timeconv.validate_date(year, month, day)
    except timeconv.TimeInputError as e:
        raise InputError(e.code, e.message)

    time_known = body.get("time_known", True) is not False
    if time_known:
        hour = _int(body.get("hour"), "Hour", 0, 23)
        minute = _int(body.get("minute"), "Minute", 0, 59)
        time = dt.time(hour, minute)
    else:
        time = None

    loc = body.get("location") or {}
    mode = loc.get("mode")
    place = None
    tz_name = None
    offset = None
    if mode == "place":
        if places is None or not places.loaded:
            raise InputError("location_lookup_failed", "Birthplace search is unavailable. Please use the manual location option.")
        try:
            gid = int(loc.get("place_id"))
        except (TypeError, ValueError):
            raise InputError("location_lookup_failed", "Please choose a birthplace from the list.")
        place = places.get(gid)
        if not place:
            raise InputError("location_lookup_failed", "That birthplace could not be found. Please search again.")
        lat, lon, tz_name = place["lat"], place["lon"], place["tz"]
    elif mode == "manual":
        lat = _float(loc.get("lat"), "Latitude", -90.0, 90.0)
        lon = _float(loc.get("lon"), "Longitude", -180.0, 180.0)
        if loc.get("tz"):
            tz_name = str(loc.get("tz"))
            if tz_name not in timeconv.timezone_list():
                raise InputError("invalid_timezone", "Please choose a time zone from the list.")
        elif loc.get("utc_offset_minutes") is not None:
            offset = _int(loc.get("utc_offset_minutes"), "UTC offset", -16 * 60, 16 * 60)
        else:
            raise InputError("missing_timezone", "Manual locations need a time zone or a UTC offset.")
        label = str(loc.get("label") or "").strip()[:120]
        place = {"label": label or "Manual coordinates", "lat": lat, "lon": lon, "tz": tz_name, "manual": True}
    else:
        raise InputError("invalid_input", "Please choose a birthplace.")

    hsys = str(body.get("house_system") or engine.DEFAULT_HOUSE_SYSTEM)
    if hsys not in engine.HOUSE_SYSTEMS:
        raise InputError("invalid_house_system", "Unknown house system.")

    fold = body.get("fold")
    fold = int(fold) if fold in (0, 1, "0", "1") else None

    node = body.get("node", "true")
    if node not in engine.NODE_TYPES:
        raise InputError("invalid_input", "Node type must be true or mean.")
    points = body.get("points") or []
    if not isinstance(points, list) or any(p not in engine.OPTIONAL_POINT_IDS for p in points):
        raise InputError("invalid_input", "Unknown optional point.")
    raw_ast = body.get("asteroids") or []
    if not isinstance(raw_ast, list) or len(raw_ast) > ast.MAX_PER_CHART:
        raise InputError("invalid_input", f"Choose up to {ast.MAX_PER_CHART} asteroids.")
    asteroid_numbers = [_int(n, "Asteroid number", 1, ast.MAX_NUMBER) for n in raw_ast]
    for n in asteroid_numbers:   # Ceres-Vesta come from Swiss Ephemeris, Chiron is always shown
        eq = ast.SWISS_EQUIVALENT.get(n)
        if eq and eq != "chiron" and eq not in points:
            points.append(eq)
    asp = body.get("aspects") or []
    if not isinstance(asp, list) or any(a not in OPTIONAL_ASPECTS for a in asp):
        raise InputError("invalid_input", "Unknown aspect type.")
    return {
        "date": date, "time": time, "time_known": time_known,
        "lat": lat, "lon": lon, "tz": tz_name, "utc_offset_minutes": offset,
        "place": place, "house_system": hsys, "fold": fold,
        "accept_lmt": body.get("accept_lmt") is True,
        "orbs": sanitize_orbs(body.get("orbs")),
        "node": node, "points": list(dict.fromkeys(points)),
        "asteroids": [n for n in dict.fromkeys(asteroid_numbers) if n not in ast.SWISS_EQUIVALENT],
        "aspect_types": list(dict.fromkeys(asp)),
    }


def build_chart(req: dict) -> dict:
    """Run the full pipeline. Returns a dict with ``status``."""
    date, place = req["date"], req["place"]
    warnings: list[str] = []
    base = {
        "engine": engine.engine_info(),
        "input": {
            "date": date.isoformat(),
            "time": req["time"].strftime("%H:%M") if req["time"] else None,
            "time_known": req["time_known"],
            "place": place,
            "house_system": req["house_system"] if req["time_known"] else None,
            "node": req["node"],
        },
        "location": {"lat": req["lat"], "lon": req["lon"], "tz": req["tz"],
                     "convention": "Latitude north positive, longitude east positive (decimal degrees)"},
    }

    ref_time = req["time"] if req["time_known"] else dt.time(12, 0)
    conv = timeconv.resolve_local_time(date, ref_time, req["tz"], req["utc_offset_minutes"],
                                       req["fold"], req["accept_lmt"])
    if conv["status"] != "ok":
        return {**base, **conv}
    t = conv["time"]
    warnings += conv["notes"]
    utc = dt.datetime.fromisoformat(t["utc_iso"].rstrip("Z"))

    hsys = req["house_system"] if req["time_known"] else None
    ast_points, ast_omitted = [], []
    if req["asteroids"]:
        found, ast_omitted = ast.positions(req["asteroids"], engine.julian_day_ut(utc))
        for a in found:
            ast_points.append(engine._point(a["id"], a["name"], "extra", a["lon"], a["lat"], None, a["speed"],
                                            label=a["label"], number=a["number"], source=a["source"]))
    try:
        core = engine.chart_at(utc, req["lat"], req["lon"], hsys, req["orbs"], node=req["node"],
                               optional=req["points"], asteroids=ast_points, aspect_types=req["aspect_types"])
    except engine.CalculationError as e:
        return {**base, "status": "error", "code": e.code, "message": e.message, **e.extra}
    core["omitted"] += ast_omitted

    out = {
        **base,
        "status": "ok",
        "timed": req["time_known"],
        "time": {**t, "reliability": conv["reliability"],
                 "jd_ut": core["jd_ut"], "jd_tt": core["jd_tt"],
                 "delta_t_seconds": core["delta_t_seconds"]},
        "bodies": core["bodies"],
        "omitted": core["omitted"],
        "houses": core["houses"],
        "aspects": core["aspects"],
        "orbs": core["orbs"],
        "sect": core["sect"],
        "options": {"node": req["node"], "points": req["points"], "asteroids": req["asteroids"],
                    "aspects": req["aspect_types"]},
        "warnings": warnings,
    }
    if req["asteroids"]:
        warnings.append("Asteroid positions (other than Ceres, Pallas, Juno and Vesta) come from NASA/JPL Horizons.")
    if core["omitted"]:
        warnings += [o["reason"] for o in core["omitted"]]

    if not req["time_known"]:
        # Local day bounds for the 'what could change' analysis.
        def local_to_utc(d, tm):
            r = timeconv.resolve_local_time(d, tm, req["tz"], req["utc_offset_minutes"], 0, True)
            if r["status"] == "nonexistent":  # midnight skipped by a DST change: use 01:00
                r = timeconv.resolve_local_time(d, dt.time(1, 0), req["tz"], req["utc_offset_minutes"], 0, True)
            return dt.datetime.fromisoformat(r["time"]["utc_iso"].rstrip("Z"))
        start = local_to_utc(date, dt.time(0, 0))
        try:
            end = local_to_utc(date + dt.timedelta(days=1), dt.time(0, 0))
        except timeconv.TimeInputError:
            end = start + dt.timedelta(days=1)
        if date + dt.timedelta(days=1) > timeconv.MAX_DATE:
            end = start + dt.timedelta(days=1)
        try:
            out["untimed"] = engine.untimed_analysis(start, end, core, req["orbs"], req["node"], req["aspect_types"])
        except engine.CalculationError as e:
            return {**base, "status": "error", "code": e.code, "message": e.message}
        out["untimed"]["reference_time_local"] = "12:00 (local noon)"
        warnings.insert(0, "Untimed chart: positions are calculated for local noon. Houses, the Ascendant, "
                           "Descendant, Midheaven and IC depend on the exact birth time and are not shown.")
    return out
