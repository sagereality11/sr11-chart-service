"""Your Birth Chart's Wealth Story: chart analysis for Sage Reality 11.

Takes a natal chart in the chart-service response shape (Placidus, True Node, Part of
Fortune requested) and returns the facts the Wealth Story reading is written from:
house rulers, roles, essential and accidental condition, solar condition, aspects,
Lots, fixed stars on key points, annual profection and the next 12 months of transits.

Conventions (Sage Reality 11 house methodology, not universal rules):
* Traditional rulers for all rulerships; outer planets add story only.
* Aspects by degree: 8 deg when a luminary is involved, 6 deg otherwise, 3 deg for the
  Lots, the nodes and the angles.
* Cazimi within 17', combust to 8 deg 30', under the beams to 17 deg.
* Part of Fortune by sect (night: Asc + Sun - Moon). Lot of Assets: Asc + 2nd cusp
  minus the 2nd ruler, day and night.
* Transits: Jupiter through Pluto to the money points, 1 deg orb, sampled daily at 12:00 UT.
"""
from __future__ import annotations

import datetime as dt
from functools import lru_cache

import swisseph as swe

from . import engine as _engine

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
         "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
RULER = {"Aries": "mars", "Taurus": "venus", "Gemini": "mercury", "Cancer": "moon", "Leo": "sun",
         "Virgo": "mercury", "Libra": "venus", "Scorpio": "mars", "Sagittarius": "jupiter",
         "Capricorn": "saturn", "Aquarius": "saturn", "Pisces": "jupiter"}
EXALT = {"sun": "Aries", "moon": "Taurus", "mercury": "Virgo", "venus": "Pisces", "mars": "Capricorn",
         "jupiter": "Cancer", "saturn": "Libra"}
OPP = lambda s: SIGNS[(SIGNS.index(s) + 6) % 12]
TRAD = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
ALL = TRAD + ["uranus", "neptune", "pluto", "chiron"]
NAME = {"sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus", "mars": "Mars",
        "jupiter": "Jupiter", "saturn": "Saturn", "uranus": "Uranus", "neptune": "Neptune",
        "pluto": "Pluto", "chiron": "Chiron", "north_node": "North Node", "south_node": "South Node",
        "asc": "Ascendant", "mc": "Midheaven", "ic": "IC", "dsc": "Descendant",
        "fortune": "Part of Fortune", "assets": "Lot of Assets"}
ASPECTS = {0: "conjunction", 60: "sextile", 90: "square", 120: "trine", 180: "opposition"}
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
SLOW = {"jupiter": swe.JUPITER, "saturn": swe.SATURN, "uranus": swe.URANUS,
        "neptune": swe.NEPTUNE, "pluto": swe.PLUTO}

# Fixed stars worth naming on a money point or an angle (Swiss Ephemeris names).
STARS = ["Regulus", "Spica", "Aldebaran", "Antares", "Fomalhaut", "Sirius", "Algol", "Arcturus",
         "Vega", "Pollux", "Castor", "Procyon", "Deneb Algedi", "Alcyone", "Rigel", "Betelgeuse",
         "Canopus", "Zubenelgenubi", "Zubeneschamali", "Scheat", "Markab", "Alphard", "Denebola",
         "Vindemiatrix", "Achernar", "Capella", "Altair", "Hamal", "Alpheratz", "Deneb Adige"]
STAR_ORB = 1.0


def norm(x):
    return x % 360.0


def sep(a, b):
    d = (a - b + 180.0) % 360.0 - 180.0
    return d if d != -180.0 else 180.0


def sign_of(lon):
    return SIGNS[int(norm(lon) // 30)]


def deg_of(lon):
    return int(norm(lon) % 30)


def house_of(lon, cusps):
    lon = norm(lon)
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360.0 < (b - a) % 360.0:
            return i + 1
    return 12


def jd_to_date(jd):
    y, m, d, _h = swe.revjul(jd)
    return dt.date(y, m, d)


def month_year(d: dt.date):
    return f"{MONTHS[d.month - 1]} {d.year}"


def part_of_month(d: dt.date):
    return "early" if d.day <= 10 else "mid" if d.day <= 20 else "late"


# --------------------------------------------------------------------------------------
# Condition
# --------------------------------------------------------------------------------------
def dignity(pid, sign):
    if pid not in TRAD:
        return None
    if RULER[sign] == pid:
        return "domicile"
    if EXALT.get(pid) == sign:
        return "exaltation"
    if RULER[OPP(sign)] == pid:
        return "detriment"
    if EXALT.get(pid) and OPP(EXALT[pid]) == sign:
        return "fall"
    return None


def solar_condition(pid, lon, sun_lon):
    if pid == "sun":
        return None
    d = abs(sep(lon, sun_lon))
    if d <= 17 / 60:
        return "cazimi"
    if d <= 8.5:
        return "combust"
    if d <= 17.0:
        return "beams"
    return None


def moon_phase(moon, sun):
    e = norm(moon - sun)
    names = ["new", "crescent", "first quarter", "gibbous", "full", "disseminating", "last quarter", "balsamic"]
    return names[int(e // 45)], e


def angularity(h):
    return "angular" if h in (1, 4, 7, 10) else "succedent" if h in (2, 5, 8, 11) else "cadent"


def orb_for(a, b):
    tight = {"fortune", "assets", "north_node", "south_node", "asc", "mc", "ic", "dsc"}
    if a in tight or b in tight:
        return 3.0
    if a in ("sun", "moon") or b in ("sun", "moon"):
        return 8.0
    return 6.0


def aspects_between(points: dict):
    out = []
    ids = list(points)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if {a, b} <= {"asc", "mc", "ic", "dsc"} or {a, b} == {"north_node", "south_node"}:
                continue
            if {a, b} <= {"fortune", "assets"}:
                continue
            d = abs(sep(points[a], points[b]))
            for ang, nm in ASPECTS.items():
                o = abs(d - ang)
                if o <= orb_for(a, b):
                    out.append({"a": a, "b": b, "type": nm, "angle": ang, "orb": o})
    return out


# --------------------------------------------------------------------------------------
# Fixed stars
# --------------------------------------------------------------------------------------
def star_positions(jd):
    _engine._ensure_thread_setup()
    out = {}
    for s in STARS:
        try:
            x = swe.fixstar2_ut(s, jd, swe.FLG_SWIEPH)[0]
            out[s] = x[0]
        except Exception:  # star file missing or name unknown: skip quietly
            continue
    return out


# --------------------------------------------------------------------------------------
# Transits over a 12-month window
# --------------------------------------------------------------------------------------
@lru_cache(maxsize=4)
def window_sky(start_iso: str, days: int = 366, back: int = 0):
    _engine._ensure_thread_setup()
    s = dt.date.fromisoformat(start_iso)
    jd0 = swe.julday(s.year, s.month, s.day, 12.0) - back
    rows = []
    for i in range(days + back):
        jd = jd0 + i
        row = {"jd": jd}
        for k, p in SLOW.items():
            x = swe.calc_ut(jd, p, FLAGS)[0]
            row[k] = (x[0], x[3])
        rows.append(row)
    return rows


def eclipses_between(jd_a, jd_b):
    _engine._ensure_thread_setup()
    out = []
    for fn, body, typ in ((swe.sol_eclipse_when_glob, swe.SUN, "solar"), (swe.lun_eclipse_when, swe.MOON, "lunar")):
        j = jd_a
        while True:
            r = fn(j, swe.FLG_SWIEPH)
            t = r[1][0]
            if t >= jd_b:
                break
            lon = swe.calc_ut(t, body, FLAGS)[0][0]
            out.append({"type": typ, "jd": t, "date": jd_to_date(t), "lon": lon})
            j = t + 20
    out.sort(key=lambda e: e["jd"])
    return out


def find_transits(targets: dict, start: dt.date, days=366):
    """targets: {key: lon}. Returns contacts active inside [start, start+days)."""
    rows = window_sky(start.isoformat(), days)
    jd_a, jd_b = rows[0]["jd"] - 0.5, rows[-1]["jd"] + 0.5
    hits = []
    for tp in SLOW:
        for key, lon0 in targets.items():
            natal_planet = key.split(":")[0]
            for asp in (0, 60, 90, 120, 180):
                if asp in (60, 120) and tp not in ("jupiter", "saturn"):
                    continue
                if natal_planet == tp and asp in (60, 120):
                    continue
                if natal_planet == "jupiter" and tp == "jupiter" and asp == 0:
                    pass
                cands = {norm(lon0 + asp), norm(lon0 - asp)}
                inorb, exacts, prev = [], [], None
                for r in rows:
                    lon = r[tp][0]
                    d = min((sep(lon, c) for c in cands), key=abs)
                    if abs(d) <= 1.0:
                        inorb.append(r["jd"])
                    if prev is not None and prev[1] * d < 0 and abs(d) < 3 and abs(prev[1]) < 3:
                        exacts.append(prev[0] + (r["jd"] - prev[0]) * abs(prev[1]) / (abs(prev[1]) + abs(d)))
                    prev = (r["jd"], d)
                if not inorb:
                    continue
                hits.append({"planet": tp, "target": key, "aspect": asp,
                             "class": "conj" if asp == 0 else "hard" if asp in (90, 180) else "soft",
                             "start": jd_to_date(min(inorb)), "end": jd_to_date(max(inorb)),
                             "exacts": [jd_to_date(e) for e in exacts],
                             "ongoing_start": min(inorb) <= jd_a + 1, "ongoing_end": max(inorb) >= jd_b - 1})
    return hits


def recent_jupiter(targets: dict, start: dt.date, back=365):
    """Jupiter conjunctions to the money points in the year before the reading date."""
    rows = window_sky(start.isoformat(), 1, back)
    hit = []
    for key, lon0 in targets.items():
        for r in rows[:-1]:
            if abs(sep(r["jupiter"][0], lon0)) <= 1.0:
                hit.append(key)
                break
    return hit


def ingresses(cusp_lons: dict, start: dt.date, days=366):
    """Slow planets crossing the cusps that matter for money (2, 5, 8, 10, 11)."""
    rows = window_sky(start.isoformat(), days)
    out = []
    for tp in ("saturn", "uranus", "neptune", "pluto", "jupiter"):
        for h, c in cusp_lons.items():
            inorb = [r["jd"] for r in rows if abs(sep(r[tp][0], c)) <= 1.0]
            if inorb:
                out.append({"planet": tp, "house": h, "start": jd_to_date(min(inorb)), "end": jd_to_date(max(inorb))})
    return out


# --------------------------------------------------------------------------------------
# The analysis
# --------------------------------------------------------------------------------------
def analyze(chart: dict, birth_date: dt.date, today: dt.date | None = None) -> dict:
    """Facts for the Wealth Story. Requires a timed Placidus chart with the Part of Fortune."""
    today = today or dt.date.today()
    bodies = {b["id"]: b for b in chart["bodies"]}
    cusps = [c["lon"] for c in chart["houses"]["cusps"]]
    ang = chart["houses"]["angles"]
    H = lambda lon: house_of(lon, cusps)
    lon = {k: bodies[k]["lon"] for k in ALL + ["north_node", "south_node"] if k in bodies}
    for k in ("asc", "mc", "ic", "dsc"):
        lon[k] = ang[k]["lon"]
    night = chart.get("sect") == "night"
    sun, moon, asc = lon["sun"], lon["moon"], lon["asc"]
    fortune = bodies["fortune"]["lon"] if "fortune" in bodies else norm(asc + (sun - moon if night else moon - sun))
    lon["fortune"] = fortune
    ruler2 = RULER[sign_of(cusps[1])]
    assets = norm(asc + cusps[1] - lon[ruler2])
    lon["assets"] = assets

    planets = {}
    for pid in ALL + ["north_node", "south_node"]:
        if pid not in lon:
            continue
        s = sign_of(lon[pid])
        b = bodies.get(pid, {})
        planets[pid] = {
            "id": pid, "name": NAME[pid], "lon": lon[pid], "sign": s, "deg": deg_of(lon[pid]),
            "house": b.get("house") or H(lon[pid]), "retro": bool(b.get("retrograde")) and pid not in ("north_node", "south_node"),
            "speed": b.get("speed"), "dignity": dignity(pid, s),
            "solar": solar_condition(pid, lon[pid], sun) if pid in TRAD else None,
        }
        planets[pid]["angularity"] = angularity(planets[pid]["house"])
    for pid in ("fortune", "assets"):
        planets[pid] = {"id": pid, "name": NAME[pid], "lon": lon[pid], "sign": sign_of(lon[pid]),
                        "deg": deg_of(lon[pid]), "house": H(lon[pid])}

    house_sign = {h: sign_of(cusps[h - 1]) for h in range(1, 13)}
    rulers = {h: RULER[house_sign[h]] for h in range(1, 13)}
    occupants = {h: [p for p in ALL if p in planets and planets[p]["house"] == h] for h in range(1, 13)}
    # intercepted signs inside money houses
    intercepted = {}
    for h in range(1, 13):
        a, b = cusps[h - 1], cusps[h % 12]
        sa, sb = int(norm(a) // 30), int(norm(b) // 30)
        inner = []
        k = (sa + 1) % 12
        while k != sb:
            inner.append(SIGNS[k])
            k = (k + 1) % 12
        if inner:
            intercepted[h] = inner

    roles = {}
    def add(pid, role):
        roles.setdefault(pid, [])
        if role not in roles[pid]:
            roles[pid].append(role)
    add(rulers[1], "asc")
    add(rulers[2], "second")
    add(RULER[planets["fortune"]["sign"]], "fortune")
    add(RULER[planets["assets"]["sign"]], "assets")
    add(rulers[10], "career")
    add(rulers[5], "fifth")
    add(rulers[8], "eighth")
    add(rulers[11], "eleventh")
    add(rulers[6], "sixth")

    pts = {k: lon[k] for k in TRAD + ["uranus", "neptune", "pluto", "chiron", "north_node", "asc", "mc", "ic", "dsc",
                                      "fortune", "assets"] if k in lon}
    asp = aspects_between(pts)
    def aspects_of(pid):
        res = []
        for a in asp:
            if pid in (a["a"], a["b"]):
                other = a["b"] if a["a"] == pid else a["a"]
                res.append({"other": other, "type": a["type"], "angle": a["angle"], "orb": a["orb"]})
        return sorted(res, key=lambda x: x["orb"])
    for pid in list(planets):
        planets[pid]["aspects"] = aspects_of(pid) if pid in pts else []

    # fixed stars on key points
    jd = chart["time"]["jd_ut"]
    stars = star_positions(jd)
    key_pts = {k: lon[k] for k in ("asc", "mc", "ic", "dsc", "fortune")}
    for pid in set([rulers[2], rulers[10], rulers[5], rulers[8], rulers[11], "jupiter", "venus",
                    RULER[planets["fortune"]["sign"]]]):
        key_pts[pid] = lon[pid]
    star_hits = []
    for s, slon in stars.items():
        for k, l in key_pts.items():
            d = abs(sep(slon, l))
            if d <= STAR_ORB:
                star_hits.append({"star": s, "point": k, "orb": d})
    star_hits.sort(key=lambda x: x["orb"])

    # profection (age at the reading date)
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    prof_house = age % 12 + 1
    prof_sign = SIGNS[(SIGNS.index(sign_of(asc)) + age) % 12]
    lord = RULER[prof_sign]
    next_bday = dt.date(today.year + (1 if (today.month, today.day) >= (birth_date.month, birth_date.day) else 0),
                        birth_date.month, min(birth_date.day, 28 if birth_date.month == 2 else birth_date.day))

    # transits to the money points
    tkeys = {}
    for pid in ("sun", "moon", "venus", "jupiter", "saturn", rulers[2], rulers[10], RULER[planets["fortune"]["sign"]]):
        tkeys[pid] = lon[pid]
    for k in ("asc", "mc", "fortune", "assets"):
        tkeys[k] = lon[k]
    tkeys["ic"] = lon["ic"]
    hits = find_transits(tkeys, today)
    ing = ingresses({2: cusps[1], 5: cusps[4], 8: cusps[7], 11: cusps[10]}, today)
    window_end = today + dt.timedelta(days=365)
    ecl = [e for e in eclipses_between(swe.julday(today.year, today.month, today.day, 0) - 200,
                                       swe.julday(window_end.year, window_end.month, window_end.day, 0))]
    ecl_hits = []
    for e in ecl:
        for k in ("mc", "ic", "asc", "dsc", "fortune", rulers[2], rulers[10]):
            if abs(sep(e["lon"], lon[k])) <= 3.0:
                ecl_hits.append({**e, "point": k})
    recent = recent_jupiter({k: lon[k] for k in ("asc", "fortune", rulers[2], "mc", "sun", "moon", "venus")}, today, 480)
    # where the slow planets are working right now (money houses only)
    now_rows = window_sky(today.isoformat(), 366)
    now_houses = {}
    for tp in ("saturn", "uranus", "neptune", "pluto"):
        h0, h1 = H(now_rows[0][tp][0]), H(now_rows[-1][tp][0])
        now_houses[tp] = (h0, h1)

    phase, elong = moon_phase(moon, sun)
    return {
        "today": today, "window_end": window_end, "night": night,
        "planets": planets, "lon": lon, "cusps": cusps, "house_sign": house_sign, "rulers": rulers,
        "occupants": occupants, "intercepted": intercepted, "roles": roles, "aspects": asp,
        "stars": star_hits, "moon_phase": phase, "moon_elong": elong,
        "profection": {"age": age, "house": prof_house, "sign": prof_sign, "lord": lord,
                       "until": next_bday, "today": today,
                       "next_lord": RULER[SIGNS[(SIGNS.index(sign_of(asc)) + age + 1) % 12]]},
        "transits": hits, "ingresses": ing, "now_houses": now_houses, "eclipses": ecl_hits, "recent_jupiter": recent,
    }
