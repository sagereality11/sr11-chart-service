"""Swiss Ephemeris calculations.

Settings (fixed, recorded in every response under ``engine``):

* Ephemeris: Swiss Ephemeris compressed files (SEFLG_SWIEPH) — sepl_18.se1
  (planets), semo_18.se1 (Moon), seas_18.se1 (main asteroids incl. Chiron),
  covering 1800–2399. If the files are missing the library would silently fall
  back to its Moshier ephemeris; we detect that from the returned flags and
  refuse to calculate rather than mix sources.
* Zodiac: tropical. Frame: geocentric, apparent positions (light-time,
  aberration, nutation applied — the Swiss Ephemeris default), true ecliptic
  and equinox of date. No SEFLG_TOPOCTR, SEFLG_HELCTR, SEFLG_SIDEREAL,
  SEFLG_TRUEPOS or SEFLG_NOABERR flags.
* Time: the UTC instant is converted to a Julian Day in UT with swe_julday
  (Gregorian calendar). swe_calc_ut and swe_houses_ex take UT and apply the
  library's own delta-T model internally to obtain TT where needed. We report
  delta-T (swe_deltat) and JD(TT) for auditing only; we never apply our own
  approximation.
* Node: SE_TRUE_NODE (osculating). South Node = North Node + 180°, normalized.
* Houses: swe_houses_ex with the selected house-system letter. Geographic
  longitude is east-positive, latitude north-positive (Swiss Ephemeris
  convention).
* House placement of bodies: by ecliptic longitude against the selected
  system's cusps. A body is in house N when
  0 <= (lon - cusp_N) mod 360 < (cusp_N+1 - cusp_N) mod 360.
  Boundary convention: a body exactly on a cusp belongs to the house that
  begins at that cusp. No "five-degree rule" is applied. The 3-D
  swe_house_pos method is NOT used, so methods are never mixed.
"""

from __future__ import annotations

import datetime as dt
import os
import threading
from pathlib import Path

import swisseph as swe

from . import __version__
from .aspects import find_aspects, sanitize_orbs
from .zodiac import SIGNS, norm360, sign_index, split_longitude

EPHE_PATH = os.environ.get("SR11_EPHE_PATH", str(Path(__file__).resolve().parent.parent / "ephe"))
REQUIRED_FILES = ["sepl_18.se1", "semo_18.se1"]
OPTIONAL_FILES = {"chiron": "seas_18.se1"}

CALC_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

BODIES = [
    # id, name, swiss ephemeris id, aspect category
    ("sun", "Sun", swe.SUN, "luminary"),
    ("moon", "Moon", swe.MOON, "luminary"),
    ("mercury", "Mercury", swe.MERCURY, "planet"),
    ("venus", "Venus", swe.VENUS, "planet"),
    ("mars", "Mars", swe.MARS, "planet"),
    ("jupiter", "Jupiter", swe.JUPITER, "planet"),
    ("saturn", "Saturn", swe.SATURN, "planet"),
    ("uranus", "Uranus", swe.URANUS, "planet"),
    ("neptune", "Neptune", swe.NEPTUNE, "planet"),
    ("pluto", "Pluto", swe.PLUTO, "planet"),
    ("north_node", "North Node (True)", swe.TRUE_NODE, "node"),
    ("chiron", "Chiron", swe.CHIRON, "planet"),
]

NODE_TYPES = {
    "true": (swe.TRUE_NODE, "True"),   # osculating node (default)
    "mean": (swe.MEAN_NODE, "Mean"),
}

# Optional points calculated from the Swiss Ephemeris files (no birth time needed).
OPTIONAL_BODIES = {
    "lilith_mean": ("Black Moon Lilith (Mean)", swe.MEAN_APOG),
    "lilith_true": ("Black Moon Lilith (True)", swe.OSCU_APOG),
    "ceres": ("Ceres", swe.CERES),
    "pallas": ("Pallas", swe.PALLAS),
    "juno": ("Juno", swe.JUNO),
    "vesta": ("Vesta", swe.VESTA),
}
# Optional points derived from the houses (birth time required).
TIMED_POINTS = {
    "fortune": "Part of Fortune",
    "spirit": "Part of Spirit",
    "vertex": "Vertex",
    "antivertex": "Anti-Vertex",
}
OPTIONAL_POINT_IDS = list(OPTIONAL_BODIES) + list(TIMED_POINTS)

HOUSE_SYSTEMS = {
    # Swiss Ephemeris identifiers (swe_houses documentation)
    "P": "Placidus",
    "W": "Whole Sign",
    "E": "Equal (from Ascendant)",
    "K": "Koch",
    "O": "Porphyry",
    "R": "Regiomontanus",
    "C": "Campanus",
    "B": "Alcabitius",
    "T": "Topocentric (Polich/Page)",
}
DEFAULT_HOUSE_SYSTEM = "P"

ASPECT_POINT_IDS = [b[0] for b in BODIES] + ["asc", "mc"]

_tls = threading.local()


def _ensure_thread_setup():
    """Swiss Ephemeris keeps its settings (including the data-file path) in
    thread-local storage. Web servers run requests on worker threads, so the
    path must be set in every thread, or the library silently falls back to
    its Moshier ephemeris. Found during end-to-end testing."""
    if getattr(_tls, "path", None) != EPHE_PATH:
        swe.set_ephe_path(EPHE_PATH)
        _tls.path = EPHE_PATH


_ensure_thread_setup()


class CalculationError(RuntimeError):
    def __init__(self, code: str, message: str, extra: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.extra = extra or {}


def ephemeris_status() -> dict:
    p = Path(EPHE_PATH)
    files = {f: (p / f).is_file() for f in REQUIRED_FILES + list(OPTIONAL_FILES.values())}
    return {"path": str(p), "files": files, "ready": all(files[f] for f in REQUIRED_FILES)}


def engine_info() -> dict:
    st = ephemeris_status()
    present = [f for f, ok in st["files"].items() if ok]
    return {
        "name": "Swiss Ephemeris",
        "version": swe.version,
        "binding": f"pyswisseph {getattr(swe, '__version__', '')}".strip(),
        "service_version": __version__,
        "ephemeris": "Swiss Ephemeris files (" + ", ".join(present) + ")",
        "flags": ["SEFLG_SWIEPH", "SEFLG_SPEED"],
        "zodiac": "Tropical",
        "frame": "Geocentric, apparent positions, true equinox and ecliptic of date",
        "node": "True Node (osculating) by default; Mean Node on request",
        "time_scale": "UT input; delta-T applied internally by Swiss Ephemeris",
        "house_assignment": "Ecliptic longitude vs. cusp intervals; a body exactly on a cusp is in the house beginning there",
    }


def julian_day_ut(utc: dt.datetime) -> float:
    hours = utc.hour + utc.minute / 60.0 + (utc.second + utc.microsecond / 1e6) / 3600.0
    return swe.julday(utc.year, utc.month, utc.day, hours, swe.GREG_CAL)


def _require_ephemeris():
    _ensure_thread_setup()
    st = ephemeris_status()
    if not st["ready"]:
        missing = [f for f in REQUIRED_FILES if not st["files"][f]]
        raise CalculationError(
            "ephemeris_missing",
            "The calculation server is missing required ephemeris data (" + ", ".join(missing) +
            "). No chart was calculated.",
        )


def _point(bid, name, cat, lon, lat=None, dist=None, speed=None, **extra):
    """A chart point. Retrograde is only reported when a speed exists."""
    b = {"id": bid, "name": name, "category": cat, "lon": norm360(lon), "lat": lat,
         "distance_au": dist, "speed": speed, "retrograde": (speed < 0) if speed is not None else None}
    b.update({k: v for k, v in split_longitude(lon).items() if k != "lon"})
    b.update(extra)
    return b


def calc_bodies(jd_ut: float, node: str = "true", optional: list | None = None) -> tuple[list[dict], list[dict]]:
    """Return (bodies, omitted). Raises if a required body cannot be computed
    from the Swiss Ephemeris files. ``node`` is "true" or "mean"; ``optional``
    lists ids from OPTIONAL_BODIES (Lilith, Ceres, Pallas, Juno, Vesta)."""
    _require_ephemeris()
    node_id, node_label = NODE_TYPES[node]
    bodies, omitted = [], []
    todo = [(bid, (f"North Node ({node_label})" if bid == "north_node" else name),
             (node_id if bid == "north_node" else sweid), cat) for bid, name, sweid, cat in BODIES]
    todo += [(k, OPTIONAL_BODIES[k][0], OPTIONAL_BODIES[k][1], "extra") for k in (optional or []) if k in OPTIONAL_BODIES]
    for bid, name, sweid, cat in todo:
        asteroid_file = bid in ("chiron", "ceres", "pallas", "juno", "vesta")
        try:
            xx, retflag = swe.calc_ut(jd_ut, sweid, CALC_FLAGS)
        except swe.Error as e:
            if asteroid_file:
                omitted.append({"id": bid, "name": name,
                                "reason": f"{name} could not be calculated (asteroid ephemeris file seas_18.se1 unavailable or date outside its range)."})
                continue
            raise CalculationError("calculation_failed", f"{name} could not be calculated: {e}")
        if not retflag & swe.FLG_SWIEPH:
            # Library fell back to Moshier — data file missing for this date.
            if asteroid_file:
                omitted.append({"id": bid, "name": name, "reason": f"{name} ephemeris file not available for this date."})
                continue
            raise CalculationError("ephemeris_missing",
                                   f"Swiss Ephemeris data files do not cover this date for {name}. No chart was calculated.")
        lon, lat, dist, speed = xx[0], xx[1], xx[2], xx[3]
        bodies.append(_point(bid, name, cat, lon, lat, dist, speed))
        if bid == "north_node":
            bodies.append(_point("south_node", f"South Node ({node_label})", "node", lon + 180.0, -lat, None, speed,
                                 derived_from="north_node + 180°"))
    return bodies, omitted


def sect(sun_lon: float, asc_lon: float) -> str:
    """Day or night chart: the Sun is above the horizon when it lies in the
    half of the ecliptic from the Descendant through the Midheaven to the
    Ascendant (houses 7-12 of the horizon). A Sun exactly on the Descendant
    counts as day, exactly on the Ascendant as night."""
    return "day" if norm360(sun_lon - asc_lon) >= 180.0 else "night"


def timed_points(wanted: list, bodies: list, houses: dict) -> list:
    """Parts of Fortune and Spirit (sect-aware, Hellenistic) and Vertex/Anti-Vertex.
      Day:   Fortune = Asc + Moon - Sun     Spirit = Asc + Sun - Moon
      Night: Fortune = Asc + Sun - Moon     Spirit = Asc + Moon - Sun
    """
    by = {b["id"]: b for b in bodies}
    asc = houses["angles"]["asc"]["lon"]
    sun, moon = by["sun"]["lon"], by["moon"]["lon"]
    s = sect(sun, asc)
    out = []
    for k in wanted:
        if k == "fortune":
            lon = asc + moon - sun if s == "day" else asc + sun - moon
            out.append(_point(k, "Part of Fortune", "extra", lon, sect=s,
                              formula=("Asc + Moon − Sun (day chart)" if s == "day" else "Asc + Sun − Moon (night chart)")))
        elif k == "spirit":
            lon = asc + sun - moon if s == "day" else asc + moon - sun
            out.append(_point(k, "Part of Spirit", "extra", lon, sect=s,
                              formula=("Asc + Sun − Moon (day chart)" if s == "day" else "Asc + Moon − Sun (night chart)")))
        elif k == "vertex":
            out.append(_point(k, "Vertex", "extra", houses["vertex"]))
        elif k == "antivertex":
            out.append(_point(k, "Anti-Vertex", "extra", houses["vertex"] + 180.0))
    return out


def calc_houses(jd_ut: float, lat: float, lon: float, hsys: str) -> dict:
    if hsys not in HOUSE_SYSTEMS:
        raise CalculationError("invalid_house_system", "Unknown house system.")
    try:
        cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, hsys.encode())
    except swe.Error:
        raise CalculationError(
            "house_system_unavailable",
            f"{HOUSE_SYSTEMS[hsys]} houses cannot be calculated at latitude {lat:.4f}°. "
            "Near and beyond the polar circles some house systems are mathematically undefined. "
            "Please choose another house system.",
            {"house_system": hsys, "available": available_house_systems(jd_ut, lat, lon)},
        )
    cusps = [norm360(c) for c in cusps[:12]]
    # Detect a silent engine fallback to Porphyry (the C library's documented
    # behaviour on failure). pyswisseph raises instead, but we double-check.
    if hsys in ("P", "K", "T", "C", "R", "B"):
        pc, _ = swe.houses_ex(jd_ut, lat, lon, b"O")
        if all(abs(a - norm360(b)) < 1e-9 for a, b in zip(cusps, pc[:12])):
            # Identical to Porphyry for a system that should differ — only
            # plausible as an engine fallback. Refuse rather than mislabel.
            raise CalculationError(
                "house_system_unavailable",
                f"The engine returned Porphyry cusps instead of {HOUSE_SYSTEMS[hsys]} at this latitude.",
                {"house_system": hsys, "available": available_house_systems(jd_ut, lat, lon),
                 "engine_fallback": "Porphyry"},
            )
    asc, mc = norm360(ascmc[0]), norm360(ascmc[1])
    angles = {}
    for key, name, val in (("asc", "Ascendant", asc), ("mc", "Midheaven", mc),
                           ("dsc", "Descendant", norm360(asc + 180)), ("ic", "Imum Coeli (IC)", norm360(mc + 180))):
        a = {"id": key, "name": name, "lon": val, "category": "angle"}
        a.update({k: v for k, v in split_longitude(val).items() if k != "lon"})
        angles[key] = a
    cusp_info = []
    for i, c in enumerate(cusps):
        d = {"house": i + 1, "lon": c}
        d.update({k: v for k, v in split_longitude(c).items() if k != "lon"})
        cusp_info.append(d)
    return {
        "system": hsys,
        "name": HOUSE_SYSTEMS[hsys],
        "cusps": cusp_info,
        "angles": angles,
        "armc": ascmc[2],
        "vertex": norm360(ascmc[3]),
        **sign_distribution(cusps),
    }


def sign_distribution(cusps: list[float]) -> dict:
    """Intercepted signs (no cusp falls in them) and signs on several cusps."""
    counts = [0] * 12
    for c in cusps:
        counts[sign_index(c)] += 1
    return {
        "intercepted_signs": [SIGNS[i] for i in range(12) if counts[i] == 0],
        "repeated_cusp_signs": [SIGNS[i] for i in range(12) if counts[i] > 1],
    }


def house_of(lon: float, cusps: list[float]) -> int:
    lon = norm360(lon)
    for i in range(12):
        start, end = cusps[i], cusps[(i + 1) % 12]
        width = (end - start) % 360.0
        if (lon - start) % 360.0 < width:
            return i + 1
    # Only reachable with degenerate (zero-width) cusp sets.
    raise CalculationError("calculation_failed", "Could not assign a house.")


def available_house_systems(jd_ut: float, lat: float, lon: float) -> list[str]:
    ok = []
    for code in HOUSE_SYSTEMS:
        try:
            swe.houses_ex(jd_ut, lat, lon, code.encode())
            ok.append(code)
        except swe.Error:
            pass
    return ok


def aspect_points(bodies: list[dict], angles: dict | None) -> list[dict]:
    pts = [{"id": b["id"], "lon": b["lon"], "category": b["category"]}
           for b in bodies if b["id"] not in ("south_node", "antivertex")]
    if angles:
        pts += [{"id": k, "lon": angles[k]["lon"], "category": "angle"} for k in ("asc", "mc")]
    return pts


def chart_at(utc: dt.datetime, lat: float, lon: float, hsys: str | None, orbs: dict | None,
             node: str = "true", optional: list | None = None, asteroids: list | None = None,
             aspect_types: list | None = None) -> dict:
    """Core natal calculation for one UTC instant. hsys=None -> untimed.
    ``asteroids`` is a list of already-calculated asteroid points (from
    sr11calc.asteroids) added before houses and aspects are assigned."""
    orbs = sanitize_orbs(orbs)
    optional = [k for k in (optional or []) if k in OPTIONAL_POINT_IDS]
    _ensure_thread_setup()
    jd_ut = julian_day_ut(utc)
    delta_t_days = swe.deltat(jd_ut)
    bodies, omitted = calc_bodies(jd_ut, node, [k for k in optional if k in OPTIONAL_BODIES])
    bodies += asteroids or []
    houses = None
    chart_sect = None
    wanted_timed = [k for k in optional if k in TIMED_POINTS]
    if hsys:
        houses = calc_houses(jd_ut, lat, lon, hsys)
        chart_sect = sect(bodies[0]["lon"], houses["angles"]["asc"]["lon"])
        bodies += timed_points(wanted_timed, bodies, houses)
        cusp_lons = [c["lon"] for c in houses["cusps"]]
        for b in bodies:
            b["house"] = house_of(b["lon"], cusp_lons)
        # Bodies lying exactly on a cusp (to the arc-second) are flagged.
        for b in bodies:
            for c in houses["cusps"]:
                if abs(((b["lon"] - c["lon"] + 180) % 360) - 180) < 1 / 3600:
                    b["on_cusp"] = c["house"]
    else:
        for k in wanted_timed:
            omitted.append({"id": k, "name": TIMED_POINTS[k],
                            "reason": f"The {TIMED_POINTS[k]} needs an exact birth time, so it is not shown on an untimed chart."})
    aspects = find_aspects(aspect_points(bodies, houses["angles"] if houses else None), orbs, aspect_types)
    return {
        "jd_ut": jd_ut,
        "delta_t_seconds": delta_t_days * 86400.0,
        "jd_tt": jd_ut + delta_t_days,
        "bodies": bodies,
        "omitted": omitted,
        "houses": houses,
        "sect": chart_sect,
        "aspects": aspects,
        "orbs": orbs,
    }


def untimed_analysis(day_start_utc: dt.datetime, day_end_utc: dt.datetime, noon_chart: dict, orbs: dict,
                     node: str = "true", aspect_types: list | None = None) -> dict:
    """What could change across the local birth date (local 00:00 -> 24:00).

    * Sign changes: each body's sign at local start vs. end of day. Bodies move
      far less than 30° per day, so comparing the two ends finds every change.
    * Aspects: sampled every hour of the local day (25 samples). An aspect at
      the reference time that is not present at every sample is reported as
      'may not apply all day'; an aspect absent at the reference time but
      present at some sample is reported as 'possible depending on birth time'.
      The Moon moves about 0.5° per hour, so hourly sampling cannot miss an
      aspect window for orbs of 1° or more.
    """
    start, _ = calc_bodies(julian_day_ut(day_start_utc), node)
    end, _ = calc_bodies(julian_day_ut(day_end_utc), node)
    by_id_s = {b["id"]: b for b in start}
    by_id_e = {b["id"]: b for b in end}
    changes = []
    for b in noon_chart["bodies"]:
        s, e = by_id_s.get(b["id"]), by_id_e.get(b["id"])
        if s and e and s["sign_index"] != e["sign_index"]:
            changes.append({"id": b["id"], "name": b["name"],
                            "start": s["display"], "end": e["display"],
                            "start_sign": s["sign"], "end_sign": e["sign"]})
    moon_s, moon_e = by_id_s["moon"], by_id_e["moon"]

    core = {b[0] for b in BODIES}
    noon_set = {(a["a"], a["b"], a["type"]) for a in noon_chart["aspects"] if a["a"] in core and a["b"] in core}
    total_seconds = (day_end_utc - day_start_utc).total_seconds()
    steps = max(1, round(total_seconds / 3600))
    present_count: dict = {}
    for k in range(steps + 1):
        t = day_start_utc + dt.timedelta(seconds=total_seconds * k / steps)
        bb, _ = calc_bodies(julian_day_ut(t), node)
        for a in find_aspects(aspect_points(bb, None), orbs, aspect_types):
            key = (a["a"], a["b"], a["type"])
            present_count[key] = present_count.get(key, 0) + 1
    samples = steps + 1
    not_all_day = [list(k) for k in noon_set if present_count.get(k, 0) < samples]
    possible = [list(k) for k, n in present_count.items() if k not in noon_set and n > 0]
    return {
        "moon": {
            "start": moon_s["display"], "end": moon_e["display"],
            "start_lon": moon_s["lon"], "end_lon": moon_e["lon"],
            "sign_changes": moon_s["sign_index"] != moon_e["sign_index"],
            "travel_degrees": (moon_e["lon"] - moon_s["lon"]) % 360.0,
        },
        "sign_changes": changes,
        "aspects_not_all_day": sorted(not_all_day),
        "aspects_possible_other_times": sorted(possible),
        "sampling": f"{samples} samples across the local day",
    }
