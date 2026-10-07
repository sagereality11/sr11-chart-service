"""Your 2027: personal year-ahead reading engine for Sage Reality 11.

Input: a natal chart in the sr11-chart-service response shape (bodies with lon and house,
houses.cusps / houses.angles) plus the birth date. Output: a structured reading dict
(story sections + calendar) that a PDF renderer turns into the product.

Calculations: Swiss Ephemeris (same settings as the chart service: SEFLG_SWIEPH,
geocentric tropical, True Node). Transits are sampled daily at 12:00 UT and exact
moments are found by linear interpolation (good to well under a day for slow planets).
"""
from __future__ import annotations

import datetime as dt
import math
from functools import lru_cache

import swisseph as swe

from . import engine as _engine
from . import yearahead_text as T

YEAR = 2027
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
         "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
RULER = {"Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon", "Leo": "Sun",
         "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
         "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
SLOW = {"jupiter": swe.JUPITER, "saturn": swe.SATURN, "uranus": swe.URANUS,
        "neptune": swe.NEPTUNE, "pluto": swe.PLUTO}
FAST = {"sun": swe.SUN, "mercury": swe.MERCURY, "venus": swe.VENUS, "mars": swe.MARS,
        "chiron": swe.CHIRON, "node": swe.TRUE_NODE}
TRANSIT_ORB = {"jupiter": 1.0, "saturn": 1.0, "uranus": 1.0, "neptune": 1.0, "pluto": 1.0}
TRANSIT_WEIGHT = {"jupiter": 2.0, "saturn": 3.0, "uranus": 3.0, "neptune": 3.0, "pluto": 4.0}
POINT_WEIGHT = {"sun": 1.5, "moon": 1.5, "asc": 1.5, "mc": 1.5, "ic": 1.2, "dsc": 1.2,
                "mercury": 1.0, "venus": 1.0, "mars": 1.0, "jupiter": 0.7, "saturn": 0.8}
ECLIPSE_EPICENTER = 3.0   # her tight orb (conjunction / opposition)
ECLIPSE_FELT = 5.0
ASPECTS = [0, 60, 90, 120, 180]
SOFT_FOR_SLOW = {"jupiter", "saturn"}   # trines/sextiles reported only for these two


def norm(x):
    return x % 360.0


def sep(a, b):
    """Signed difference a - b in (-180, 180]."""
    d = (a - b + 180.0) % 360.0 - 180.0
    return d if d != -180.0 else 180.0


def fmt_pos(lon):
    lon = norm(lon)
    s = int(lon // 30)
    total_min = int(round((lon - s * 30) * 60))
    d, m = divmod(total_min, 60)
    if d == 30:
        d, s = 0, (s + 1) % 12
    return f"{d}°{m:02d}' {SIGNS[s]}"


def jd_to_date(jd):
    y, m, d, h = swe.revjul(jd)
    base = dt.datetime(y, m, d) + dt.timedelta(hours=h)
    return base.date()


def nice(d: dt.date):
    return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"


def short(d: dt.date):
    return f"{MONTHS[d.month - 1][:3]} {d.day}"


def house_of(lon, cusps):
    lon = norm(lon)
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360.0 < (b - a) % 360.0:
            return i + 1
    return 12


# --------------------------------------------------------------------------------------
# The 2027 sky (shared by every reading; cached per process)
# --------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def sky(ephe_path: str | None = None):
    _engine._ensure_thread_setup()
    start = swe.julday(YEAR - 1, 12, 1, 12.0)
    end = swe.julday(YEAR + 1, 2, 1, 12.0)
    days = []
    jd = start
    while jd <= end:
        row = {"jd": jd}
        for k, p in {**SLOW, **FAST}.items():
            x = swe.calc_ut(jd, p, FLAGS)[0]
            row[k] = (x[0], x[3])
        days.append(row)
        jd += 1.0
    eclipses = []
    for fn, body, typ in ((swe.sol_eclipse_when_glob, swe.SUN, "solar"),
                          (swe.lun_eclipse_when, swe.MOON, "lunar")):
        j = swe.julday(YEAR, 1, 1, 0)
        while True:
            r = fn(j, swe.FLG_SWIEPH)
            t = r[1][0]
            if t >= swe.julday(YEAR + 1, 1, 1, 0):
                break
            f = r[0]
            if typ == "solar":
                kind = ("total" if f & swe.ECL_TOTAL else "annular" if f & swe.ECL_ANNULAR
                        else "hybrid" if f & swe.ECL_ANNULAR_TOTAL else "partial")
            else:
                kind = "total" if f & swe.ECL_TOTAL else "partial" if f & swe.ECL_PARTIAL else "penumbral"
            lon = swe.calc_ut(t, body, FLAGS)[0][0]
            # previous member of the same Saros family (18 years 11 days earlier)
            pr = fn(t - 6585.32 - 3, swe.FLG_SWIEPH)[1][0]
            eclipses.append({"type": typ, "kind": kind, "jd": t, "date": jd_to_date(t), "lon": lon,
                             "saros_prev_jd": pr, "saros_prev": jd_to_date(pr)})
            j = t + 20
    eclipses.sort(key=lambda e: e["jd"])
    lunations = []
    j = swe.julday(YEAR, 1, 1, 0)
    prev = None
    while j < swe.julday(YEAR + 1, 1, 1, 0):
        s_ = swe.calc_ut(j, swe.SUN, FLAGS)[0][0]
        m_ = swe.calc_ut(j, swe.MOON, FLAGS)[0][0]
        d = sep(m_, s_)
        if prev is not None and prev < 0 <= d:
            lunations.append({"jd": j, "date": jd_to_date(j), "lon": s_})
        prev = d
        j += 0.25
    # stations and ingresses inside the calendar year
    stations, ingresses = [], []
    y0, y1 = swe.julday(YEAR, 1, 1, 0), swe.julday(YEAR + 1, 1, 1, 0)
    for a, b in zip(days, days[1:]):
        if not (y0 <= b["jd"] < y1):
            continue
        for k in ("mercury", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"):
            if (a[k][1] < 0) != (b[k][1] < 0):
                stations.append({"planet": k, "jd": b["jd"], "date": jd_to_date(b["jd"]),
                                 "dir": "retrograde" if b[k][1] < 0 else "direct", "lon": b[k][0]})
        for k in ("jupiter", "saturn", "uranus", "neptune", "pluto", "chiron"):
            if int(a[k][0] // 30) != int(b[k][0] // 30):
                ingresses.append({"planet": k, "jd": b["jd"], "date": jd_to_date(b["jd"]),
                                  "sign": SIGNS[int(b[k][0] // 30)]})
    return {"days": days, "eclipses": eclipses, "stations": stations, "ingresses": ingresses,
            "new_moons": lunations}


def solar_return(natal_sun):
    jd = swe.julday(YEAR, 1, 1, 0)
    t = swe.solcross_ut(natal_sun, jd, swe.FLG_SWIEPH)
    return t


# --------------------------------------------------------------------------------------
# Natal input
# --------------------------------------------------------------------------------------
def natal_points(chart: dict, time_known: bool):
    """Normalize the service response to {id: lon}, cusps list, and house lookup."""
    pts = {}
    for b in chart["bodies"]:
        if b["id"] in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
                       "uranus", "neptune", "pluto", "north_node", "chiron"):
            pts[b["id"]] = b["lon"]
    if time_known and chart.get("houses"):
        cusps = [c["lon"] for c in chart["houses"]["cusps"]]
        ang = chart["houses"]["angles"]
        for k in ("asc", "mc", "ic", "dsc"):
            pts[k] = ang[k]["lon"]
        asc_sign = SIGNS[int(norm(ang["asc"]["lon"]) // 30)]
    else:
        # solar houses: whole-sign houses from the Sun's sign
        s0 = int(norm(pts["sun"]) // 30) * 30.0
        cusps = [norm(s0 + 30 * i) for i in range(12)]
        asc_sign = SIGNS[int(norm(pts["sun"]) // 30)]
    return pts, cusps, asc_sign


# --------------------------------------------------------------------------------------
# Transits
# --------------------------------------------------------------------------------------
def find_transits(pts, time_known):
    days = sky()["days"]
    y0, y1 = swe.julday(YEAR, 1, 1, 0), swe.julday(YEAR + 1, 1, 1, 0)
    targets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
    if time_known:
        targets += ["asc", "mc", "ic", "dsc"]
    hits = []
    for tp in SLOW:
        for np_ in targets:
            if np_ == tp and tp == "jupiter":
                continue
            for asp in ASPECTS:
                if np_ in ("uranus", "neptune", "pluto") and np_ != tp:
                    continue
                if np_ == tp and asp in (60, 120):
                    continue
                if asp in (60, 120) and tp not in SOFT_FOR_SLOW:
                    continue
                if np_ in ("ic", "dsc") and asp != 0:
                    continue
                if np_ in ("asc", "mc") and asp == 180:
                    continue  # covered as a conjunction to the DSC / IC
                exacts, inorb = [], []
                prev = None
                for row in days:
                    lon = row[tp][0]
                    # distance to nearest aspect point (both sides for non-0/180)
                    cands = {norm(pts[np_] + asp), norm(pts[np_] - asp)}
                    d = min((sep(lon, c) for c in cands), key=abs)
                    if abs(d) <= TRANSIT_ORB[tp] and y0 <= row["jd"] < y1:
                        inorb.append(row["jd"])
                    if prev is not None and prev[1] * d < 0 and abs(d) < 5 and abs(prev[1]) < 5:
                        t = prev[0] + (row["jd"] - prev[0]) * abs(prev[1]) / (abs(prev[1]) + abs(d))
                        if y0 <= t < y1:
                            exacts.append(t)
                    prev = (row["jd"], d)
                if not exacts and not inorb:
                    continue
                cls = "conj" if asp == 0 else "hard" if asp in (90, 180) else "soft"
                w = TRANSIT_WEIGHT[tp] * POINT_WEIGHT.get(np_, 1.0) * (1.0 if cls != "soft" else 0.6)
                if np_ == tp:
                    w = TRANSIT_WEIGHT[tp] * 1.6
                hits.append({"planet": tp, "point": np_, "aspect": asp, "class": cls,
                             "exacts": [jd_to_date(e) for e in exacts], "exact_jds": exacts,
                             "start": jd_to_date(min(inorb)) if inorb else jd_to_date(exacts[0]),
                             "end": jd_to_date(max(inorb)) if inorb else jd_to_date(exacts[-1]),
                             "weight": w * (1 + 0.25 * max(0, len(exacts) - 1))})
    hits.sort(key=lambda h: -h["weight"])
    return hits


def transit_paragraph(h, pts=None):
    if h["planet"] == h["point"]:
        key = (h["planet"], h["aspect"])
        if key in T.CYCLE:
            return T.CYCLE[key] + " " + T.TRANSIT_OCTAVE[h["planet"]]
    pname = T.POINT[h["point"]][0]
    pm = f"your natal {pname}, {T.POINT[h['point']][1]}"
    asp = T.ASPECT_WORD[h["aspect"]]
    body = T.TRANSIT_TEXT[(h["planet"], h["class"])].format(core=T.TRANSIT_CORE[h["planet"]], pm=pm, asp=asp)
    return body + " " + T.TRANSIT_OCTAVE[h["planet"]]


def transit_title(h):
    if h["planet"] == h["point"] and (h["planet"], h["aspect"]) in T.CYCLE_NAME:
        return T.CYCLE_NAME[(h["planet"], h["aspect"])]
    return f"{h['planet'].title()} {T.ASPECT_WORD[h['aspect']]} your {T.POINT[h['point']][0]}"


def _join(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def an(word):
    return ("an " if word[0] in "8aeiou" or word in ("11th", "18th") else "a ") + word


def transit_when(h):
    if h["exacts"]:
        ds = h["exacts"]
        ex = _join(f"{MONTHS[d.month - 1]} {d.day}" for d in ds) + f", {YEAR}"
        return f"Exact {ex}. Active {short(h['start'])} to {short(h['end'])}."
    if h["start"] == dt.date(YEAR, 1, 1):
        return f"Active from the start of the year through {short(h['end'])}, building toward 2028."
    return f"Active {short(h['start'])} to {short(h['end'])}, building toward 2028."


def group_cards(hits, limit=6):
    """Group same-planet, same-tone contacts (e.g. Saturn square Sun, Moon and Mercury) into one card."""
    cards, used = [], set()
    for i, h in enumerate(hits):
        if i in used or len(cards) >= limit:
            continue
        if h["planet"] == h["point"]:
            cards.append({"title": transit_title(h), "sub": transit_when(h), "body": transit_paragraph(h),
                          "hits": [h]})
            used.add(i)
            continue
        group = [h] + [g for j, g in enumerate(hits) if j > i and j not in used and g["planet"] == h["planet"]
                       and g["class"] == h["class"] and g["planet"] != g["point"]
                       and (g["class"] != "soft" or h["class"] == "soft")]
        for g in group:
            used.add(hits.index(g))
        group = group[:4]
        if len(group) == 1:
            cards.append({"title": transit_title(h), "sub": transit_when(h), "body": transit_paragraph(h),
                          "hits": group})
            continue
        asps = {T.ASPECT_WORD[g["aspect"]] for g in group}
        title = f"{h['planet'].title()} {'/'.join(sorted(asps))} your " + _join(T.POINT[g["point"]][0] for g in group)
        pm = "your natal " + _join(f"{T.POINT[g['point']][0]} ({T.POINT[g['point']][1]})" for g in group)
        body = T.TRANSIT_TEXT[(h["planet"], h["class"])].format(core=T.TRANSIT_CORE[h["planet"]], pm=pm,
                                                                asp=" and ".join(sorted(asps)))
        body += " " + T.GROUP_NOTE.format(n=len(group)) + " " + T.TRANSIT_OCTAVE[h["planet"]]
        sub = " ".join(f"{T.POINT[g['point']][0]}: {transit_when(g)}" for g in group)
        cards.append({"title": title, "sub": sub, "body": body, "hits": group})
    return cards


# --------------------------------------------------------------------------------------
# The reading
# --------------------------------------------------------------------------------------
def build_reading(chart: dict, birth_date: dt.date, name: str, time_known: bool = True,
                  place_label: str = "", birth_time: str = ""):
    _engine._ensure_thread_setup()
    S = sky()
    pts, cusps, asc_sign = natal_points(chart, time_known)
    H = lambda lon: house_of(lon, cusps)
    by_id = {b["id"]: b for b in chart["bodies"]}

    # ---- profection
    sr_jd = solar_return(pts["sun"])
    sr_date = jd_to_date(sr_jd)
    age_after = YEAR - birth_date.year
    age_before = age_after - 1
    asc_idx = SIGNS.index(asc_sign)
    prof_house = age_after % 12 + 1
    prev_house = age_before % 12 + 1
    prof_sign = SIGNS[(asc_idx + age_after) % 12]
    lord = RULER[prof_sign]
    lord_lon = pts[lord.lower()]
    lord_house = H(lord_lon)
    year_title = T.YEAR_TITLE[prof_house]

    # ---- eclipse axis (houses of the eclipse degrees, so the axis is personal)
    ecl = S["eclipses"]
    leo_house = H(130.0)       # ~10 Leo, the August 2027 solar eclipse zone
    aq_house = H(310.0)
    for e in ecl:
        if SIGNS[int(e["lon"] // 30)] == "Leo":
            leo_house = H(e["lon"])
        if e["type"] == "solar" and SIGNS[int(e["lon"] // 30)] == "Aquarius":
            aq_house = H(e["lon"])
    v_house, p_house = H(152.0), H(332.0)
    c_house, cp_house = H(112.0), H(292.0)

    eclipse_cards = []
    for e in ecl:
        h = H(e["lon"])
        contacts, near = [], []
        for pid, lon in pts.items():
            if pid in ("uranus", "neptune", "pluto", "chiron", "north_node"):
                continue
            for asp in (0, 180):
                d = abs(sep(e["lon"], norm(lon + asp)))
                if pid in ("ic", "dsc", "asc", "mc") and asp == 180:
                    continue  # an angle's opposite angle is its own point
                if d <= ECLIPSE_EPICENTER:
                    contacts.append((d, pid, asp))
                elif d <= ECLIPSE_FELT:
                    near.append((d, pid, asp))
        contacts.sort()
        near.sort()
        txt = [T.ECLIPSE_HOUSE[e["type"]].format(ord=T.ORD[h], topic=T.HOUSE_TOPIC[h])]
        if contacts:
            cs = contacts[:3]
            names = [f"{T.POINT[p][0]}{'' if a == 0 else ' (by opposition)'}" for _, p, a in cs]
            means = [T.POINT[p][1] for _, p, a in cs]
            txt.append(T.ECLIPSE_CONTACT.format(points=_join(f"natal {n}" for n in names),
                                                orb=f"{max(1, math.ceil(cs[-1][0]))}°",
                                                meanings=" and to ".join(means)))
        elif near:
            d, pid, asp = near[0]
            txt.append(T.ECLIPSE_NEAR.format(orb=f"{math.ceil(d)}°", point=T.POINT[pid][0],
                                             point_meaning_short=T.POINT[pid][2]))
        prev_age = (e["saros_prev"].year - birth_date.year
                    - ((e["saros_prev"].month, e["saros_prev"].day) < (birth_date.month, birth_date.day)))
        if e["saros_prev"] > birth_date:
            txt.append(T.SAROS_ECHO.format(prev_date=nice(e["saros_prev"]), age=prev_age))
        eclipse_cards.append({
            "date": e["date"], "title": f"{nice(e['date'])}: {T.ECLIPSE_KIND[(e['type'], e['kind'])].capitalize()}",
            "pos": fmt_pos(e["lon"]), "house": h, "text": " ".join(txt),
            "weight": 5.0 + 3.0 * len(contacts) + (1.0 if e["type"] == "solar" else 0.0),
            "contacts": [T.POINT[c[1]][0] for c in contacts],
        })

    # ---- transits
    hits = find_transits(pts, time_known)
    major = [h for h in hits if h["class"] != "soft" or h["planet"] in ("jupiter", "saturn")]
    top_transits = major[:6]

    # ---- slow planets by house (sampled where they spend the year)
    jup_leo_house = H(next(r["jupiter"][0] for r in S["days"] if jd_to_date(r["jd"]) == dt.date(YEAR, 3, 1)))
    jup_vir_house = H(next(r["jupiter"][0] for r in S["days"] if jd_to_date(r["jd"]) == dt.date(YEAR, 10, 15)))
    sat_mid = next(r["saturn"][0] for r in S["days"] if jd_to_date(r["jd"]) == dt.date(YEAR, 7, 1))
    sat_house = H(sat_mid)
    outer_house = {k: H(next(r[k][0] for r in S["days"] if jd_to_date(r["jd"]) == dt.date(YEAR, 7, 1)))
                   for k in ("uranus", "neptune", "pluto")}

    # ---- story sections
    sections = []
    sections.append({"heading": "Welcome to Your 2027", "body": T.OPENING})
    if not time_known:
        sections.append({"heading": "A Note About Your Birth Time", "body": T.UNTIMED_NOTE})

    prof = T.PROFECTION[prof_house] + "\n\n" + T.YEAR_LORD.format(
        lord=lord, sign=prof_sign, house_ord=T.ORD[prof_house],
        lord_sign=SIGNS[int(norm(lord_lon) // 30)], lord_house_ord=T.ORD[lord_house],
        lord_topic=T.HOUSE_TOPIC[lord_house])
    if prev_house != prof_house:
        prof += "\n\n" + T.PROFECTION_SWITCH.format(bday=nice(sr_date), prev_ord=an(T.ORD[prev_house]),
                                                  prev_short=T.HOUSE_SHORT[prev_house],
                                                  cur_ord=T.ORD[prof_house])
    sections.append({"heading": f"What 2027 Is About for You: The Year of {year_title}", "body": prof})

    axis = (T.ECLIPSE_TEACH + "\n\n" + T.ECLIPSE_SEASON_2027 + "\n\n"
            + T.AXIS_SIDES.format(leo_ord=T.ORD[leo_house], leo_topic=T.HOUSE_TOPIC[leo_house],
                                  aq_ord=T.ORD[aq_house], aq_topic=T.HOUSE_TOPIC[aq_house])
            + "\n\n" + T.AXIS_STORY[leo_house] + "\n\n"
            + T.ECLIPSE_CLOSING_VIRGO_PISCES.format(v_ord=T.ORD[v_house], v_short=T.HOUSE_SHORT[v_house],
                                                    p_ord=T.ORD[p_house], p_short=T.HOUSE_SHORT[p_house])
            + "\n\n" + T.ECLIPSE_OPENING_CANCER_CAP.format(c_ord=T.ORD[c_house], c_short=T.HOUSE_SHORT[c_house],
                                                          cp_ord=T.ORD[cp_house], cp_short=T.HOUSE_SHORT[cp_house]))
    sections.append({"heading": "Your Eclipse Story: The 12 to 18 Month Axis", "body": axis,
                     "cards": [{"title": c["title"], "sub": f"{c['pos']} · your {T.ORD[c['house']]} house",
                                "body": c["text"]} for c in eclipse_cards]})

    jup = (T.JUPITER_SIGN["Leo"] + " " + T.JUPITER_HOUSE[jup_leo_house] + "\n\n"
           + T.JUPITER_SIGN["Virgo"] + " " + T.JUPITER_HOUSE[jup_vir_house].replace("In your", "Now, in your", 1))
    sat = T.SATURN_ARIES + " " + T.SATURN_HOUSE[sat_house]
    bg = "\n\n".join(T.OUTER_BACKGROUND[k].format(ord=T.ORD[outer_house[k]], topic=T.HOUSE_TOPIC[outer_house[k]])
                     for k in ("uranus", "neptune", "pluto"))
    sections.append({"heading": "Your Great Teachers This Year",
                     "body": "Where Jupiter Brings Growth\n\n" + jup + "\n\nWhere Saturn Builds Strength\n\n"
                             + sat + "\n\nThe Slow Background Story\n\n" + bg,
                     "subheads": ["Where Jupiter Brings Growth", "Where Saturn Builds Strength",
                                  "The Slow Background Story"]})

    cards = group_cards(major, 5)
    if cards:
        for c in cards:
            c.pop("hits", None)
        sections.append({"heading": "The Big Personal Moments",
                         "body": ("These are the strongest contacts the slow-moving planets make to your own "
                                  "birth chart in 2027. They're the turning points that belong to you and no "
                                  "one else, which is why your year won't look like anyone else's."),
                         "cards": cards})

    # ---- the thread that ties it together
    thread = [T.THREAD_OPEN.format(title=year_title.lower(), prof_ord=T.ORD[prof_house],
                                   prof_short=T.HOUSE_SHORT[prof_house], leo_ord=T.ORD[leo_house],
                                   aq_ord=T.ORD[aq_house])]
    if prof_house in (leo_house, aq_house):
        thread.append(T.THREAD_ECHO.format(ord=T.ORD[prof_house]))
    if lord in ("Jupiter", "Saturn"):
        hh = (f"your {T.ORD[jup_leo_house]} and {T.ORD[jup_vir_house]} houses" if lord == "Jupiter"
              else f"your {T.ORD[sat_house]} house")
        thread.append(T.THREAD_LORD_SLOW.format(lord=lord, houses=hh))
    else:
        thread.append(T.THREAD_LORD_FAST.format(lord=lord))
    if cards:
        tt = cards[0]["title"]
        thread.append(T.THREAD_TOP.format(top=("your" + tt[4:]) if tt.startswith("Your ") else tt))
    thread.append(T.THREAD_CLOSE)
    sections.append({"heading": "The Thread That Ties It Together", "body": "\n\n".join(thread)})

    # ---- calendar events
    events = []   # (date, weight, text, kind, short label for the "why" line)
    for c in eclipse_cards:
        line = f"{c['title'].split(': ',1)[1]} at {c['pos']} in your {T.ORD[c['house']]} house ({T.HOUSE_SHORT[c['house']]})"
        if c["contacts"]:
            line += f", right on your {' and '.join(c['contacts'])}"
        kind_word = "solar" if "solar" in c["title"] else "lunar"
        lab = f"the {kind_word} eclipse in your {T.ORD[c['house']]} house"
        if c["contacts"]:
            lab += " landing on your " + _join(c["contacts"])
        events.append((c["date"], c["weight"], line + ".", "eclipse", lab))
    for h in hits:
        if h["class"] == "soft" and h["planet"] not in ("jupiter", "saturn"):
            continue
        tt = transit_title(h)
        what = tt if h["planet"] == h["point"] else f"{tt} ({T.POINT[h['point']][2]})"
        lab = tt[0].lower() + tt[1:] if tt.startswith("Your") else tt
        if h["exacts"]:
            for d in h["exacts"]:
                events.append((d, h["weight"], f"{what} is exact.", "transit", lab))
        elif h["start"] > dt.date(YEAR, 1, 1):
            events.append((h["start"], h["weight"] * 0.6, f"{what} begins to build.", "transit", lab))
        else:
            events.append((h["start"], h["weight"] * 0.3, f"{what} is active as the year opens.", "transit", lab))
    for s in S["stations"]:
        if s["planet"] == "mercury" and s["dir"] == "retrograde":
            end = next((x for x in S["stations"] if x["planet"] == "mercury" and x["dir"] == "direct"
                        and x["jd"] > s["jd"]), None)
            if end:
                h = H(s["lon"])
                events.append((s["date"], 1.0, T.MERCURY_RX.format(start=short(s["date"]), end=short(end["date"]),
                                                                   ord=T.ORD[h], topic=T.HOUSE_SHORT[h]), "retro",
                               f"Mercury retrograde in your {T.ORD[h]} house"))
        if s["planet"] == "mars" and s["dir"] == "direct":
            events.append((s["date"], 1.0, T.MARS_DIRECT.format(ord=T.ORD[H(s["lon"])]), "station", "Mars turning direct"))
        if s["planet"] == "saturn":
            events.append((s["date"], 1.5, T.SATURN_STATION.format(dir=s["dir"], date=short(s["date"]),
                                                                   pos=fmt_pos(s["lon"]), ord=T.ORD[sat_house]),
                           "station", f"Saturn stationing {s['dir']}"))
    jan_mars = S["days"][31]["mars"][0]
    events.append((dt.date(YEAR, 1, 1), 1.0, T.MARS_RX.format(ord=T.ORD[H(jan_mars)],
                                                              topic=T.HOUSE_SHORT[H(jan_mars)]), "retro", "Mars retrograde"))
    for ing in S["ingresses"]:
        if ing["planet"] == "jupiter" and ing["sign"] == "Virgo":
            events.append((ing["date"], 2.0, T.JUPITER_INGRESS.format(ord=T.ORD[jup_vir_house],
                                                                      topic=T.HOUSE_SHORT[jup_vir_house]), "ingress",
                           f"Jupiter entering your {T.ORD[jup_vir_house]} house"))
        if ing["planet"] == "chiron" and ing["sign"] == "Taurus":
            ch = H(45.0)
            events.append((ing["date"], 0.8, T.CHIRON_TAURUS.format(ord=T.ORD[ch], topic=T.HOUSE_SHORT[ch]), "ingress", "Chiron entering Taurus"))
    events.append((sr_date, 2.0, T.BIRTHDAY.format(date=nice(sr_date), ord=T.ORD[prof_house],
                                                   short=T.HOUSE_SHORT[prof_house]), "birthday",
                   "your birthday and the start of your new profection year"))
    ecl_dates = {c["date"] for c in eclipse_cards}
    for nm in S["new_moons"]:
        if any(abs((nm["date"] - d).days) <= 1 for d in ecl_dates):
            continue
        h = H(nm["lon"])
        events.append((nm["date"], 0.3, T.NEW_MOON.format(sign=SIGNS[int(nm["lon"] // 30)], ord=T.ORD[h],
                                                          topic=T.HOUSE_TOPIC[h]), "lunation", "a New Moon"))
    events.sort(key=lambda e: (e[0], -e[1]))

    months = []
    for m in range(1, 13):
        ev = [e for e in events if e[0].year == YEAR and e[0].month == m]
        score = sum(e[1] for e in ev)
        top = max(ev, key=lambda e: e[1]) if ev else None
        months.append({"month": MONTHS[m - 1], "num": m, "score": round(score, 1),
                       "events": [{"date": short(e[0]), "text": e[2], "kind": e[3]} for e in ev],
                       "quiet": T.MONTH_QUIET.format(short=T.HOUSE_SHORT[prof_house]) if score < 3 else None,
                       "headline": _headline(top, prof_house) if top else None})
    ranked = sorted(months, key=lambda x: -x["score"])
    power = sorted(ranked[:4], key=lambda x: x["num"])
    for p in power:
        p["power"] = True
        p["why"] = _why(p, events)

    # ---- where to go from here (personalized product links)
    picks = ["monthly"]
    if any(c["contacts"] for c in eclipse_cards):
        picks.append("prenatal")
    else:
        picks.append("saros")
    picks.append(T.OFFER_BY_HOUSE[prof_house])
    picks.append("solar_return")
    picks.append(T.COURSE_BY_HOUSE.get(prof_house, "course101"))
    seen, offers = set(), []
    for k in picks:
        if k in seen:
            continue
        seen.add(k)
        title, url, why = T.OFFERS[k]
        offers.append({"title": title, "url": url, "why": why.format(bday=nice(sr_date))})

    return {
        "next_intro": T.NEXT_INTRO,
        "offers": offers,
        "title": "Your 2027",
        "subtitle": f"The Year of {year_title}",
        "name": name,
        "birth": {"date": nice(birth_date), "time": birth_time if time_known else "unknown",
                  "place": place_label},
        "snapshot": {
            "Profection year": f"{T.ORD[prof_house]} house ({T.HOUSE_SHORT[prof_house]}) from {short(sr_date)}",
            "Lord of the year": lord,
            "Eclipse axis": f"Leo {T.ORD[leo_house]} house and Aquarius {T.ORD[aq_house]} house",
            "Jupiter": f"{T.ORD[jup_leo_house]} house, then {T.ORD[jup_vir_house]} house from Jul 26",
            "Saturn": f"{T.ORD[sat_house]} house all year",
            "Power months": ", ".join(p["month"] for p in power),
        },
        "sections": sections,
        "power_intro": T.POWER_INTRO,
        "power_months": power,
        "months": months,
        "final": T.FINAL.format(title=f"the Year of {year_title}", leo_ord=T.ORD[leo_house], aq_ord=T.ORD[aq_house]),
        "signoff": T.SIGNOFF,
        "disclaimer": T.DISCLAIMER,
    }


def _headline(top, prof_house):
    kind = top[3]
    return {"eclipse": "Eclipse month: a turning point", "transit": "A big personal contact",
            "birthday": "Your personal new year", "ingress": "A new chapter of growth",
            "retro": "Review and realign", "station": "A shift in momentum"}.get(kind, "")


def _why(month, events):
    ev = sorted([e for e in events if e[0].year == YEAR and e[0].month == month["num"]], key=lambda e: -e[1])
    labs = []
    for e in ev:
        if e[3] == "lunation":
            continue
        if e[4] not in labs:
            labs.append(e[4])
        if len(labs) == 3:
            break
    labs = [l[0].lower() + l[1:] if not l.startswith(("Mercury", "Mars", "Saturn", "Jupiter", "Uranus", "Neptune",
                                                       "Pluto", "Chiron")) else l for l in labs]
    return T.POWER_WHY.format(month=month["month"], items=_join(labs))
