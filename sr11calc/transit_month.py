"""Your Monthly Transit Forecast: the facts for one calendar month (one person or two).

Works from a natal chart in the chart-service response shape (Placidus, True or Mean Node).

Techniques (Sage Reality 11 methodology):
  * Annual and monthly profections, whole sign from the rising sign (from the Sun sign when the
    birth time is unknown), traditional rulers.
  * Slow transits (Jupiter, Saturn, Uranus, Neptune, Pluto, Chiron, the nodal axis) to the natal
    planets, nodes and angles, 1 degree orb, with every pass of the cycle dated.
  * Stations of every planet Mercury to Pluto and Chiron, with the natal points they sit on.
  * The Sun, Mercury, Venus and Mars on their exact days (conjunctions, squares, oppositions,
    plus Venus trines).
  * New and Full Moons by house, eclipses flagged.
  * Secondary progressions (progressed Moon, lunation phase, progressed planets within 1 degree)
    and true solar arc directions within 1 degree.
  * Short-way midpoints touched by the slow planets by conjunction, square or opposition, 1 degree.
  * Life cycles (returns, oppositions and squares of Jupiter, Saturn, Uranus, Neptune, Pluto, Chiron
    and the nodes) when they are in orb this year.
Two-person forecasts add synastry links within 2 degrees (planets, Chiron, nodes, angles) and the
transits that touch both ends of a link within 1.5 degrees, including temporary T-squares.
"""
from __future__ import annotations

import datetime as dt
from functools import lru_cache
from zoneinfo import ZoneInfo

import swisseph as swe

from . import engine as _engine

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
         "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
RULER = ["mars", "venus", "mercury", "moon", "sun", "mercury", "venus", "mars", "jupiter",
         "saturn", "saturn", "jupiter"]
NAME = {"sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus", "mars": "Mars",
        "jupiter": "Jupiter", "saturn": "Saturn", "uranus": "Uranus", "neptune": "Neptune",
        "pluto": "Pluto", "chiron": "Chiron", "north_node": "North Node", "south_node": "South Node",
        "asc": "Ascendant", "mc": "Midheaven"}
SWE = {"sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY, "venus": swe.VENUS, "mars": swe.MARS,
       "jupiter": swe.JUPITER, "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE,
       "pluto": swe.PLUTO, "chiron": swe.CHIRON}
NODE_ID = {"true": swe.TRUE_NODE, "mean": swe.MEAN_NODE}
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
ASPN = {0: "conjunct", 60: "sextile", 90: "square", 120: "trine", 180: "opposite"}
SLOWS = ("jupiter", "saturn", "uranus", "neptune", "pluto", "chiron", "north_node")
FASTS = ("sun", "mercury", "venus", "mars")
PERSONAL_TARGETS = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "asc", "mc",
                    "north_node", "south_node", "uranus", "neptune", "pluto", "chiron")
OUTER_T = ("uranus", "neptune", "pluto", "chiron")
TARGETS = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune",
           "pluto", "chiron", "north_node", "asc", "mc")
MIDPOINTS = (("sun", "moon"), ("asc", "mc"), ("venus", "mars"), ("sun", "jupiter"), ("venus", "jupiter"),
             ("sun", "venus"), ("moon", "venus"), ("sun", "mc"), ("moon", "mc"), ("sun", "asc"),
             ("mercury", "neptune"), ("sun", "north_node"), ("saturn", "pluto"), ("mars", "saturn"),
             ("moon", "saturn"), ("sun", "saturn"), ("mars", "pluto"), ("jupiter", "saturn"))
PHASES = ["New", "Crescent", "First Quarter", "Gibbous", "Full", "Disseminating", "Last Quarter", "Balsamic"]
YEAR = 365.2422


def norm(x):
    return x % 360.0


def sep(a, b):
    d = abs(norm(a - b))
    return min(d, 360 - d)


def sign_of(lon):
    return SIGNS[int(norm(lon) // 30)]


def deg_of(lon):
    return int(norm(lon) % 30)


def house_of(lon, cusps):
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if norm(lon - a) < norm(b - a):
            return i + 1
    return 12


def fmt(lon):
    d = norm(lon) % 30
    dd, mm = int(d), int(round((d - int(d)) * 60))
    if mm == 60:
        dd, mm = dd + 1, 0
    return f"{dd}°{mm:02d}' {sign_of(lon)}"


def _jd(t: dt.datetime) -> float:
    t = t.astimezone(dt.timezone.utc)
    return swe.julday(t.year, t.month, t.day, t.hour + t.minute / 60 + t.second / 3600)


def _local(jd: float, tz: ZoneInfo) -> dt.datetime:
    y, m, d, h = swe.revjul(jd)
    return (dt.datetime(y, m, d, tzinfo=dt.timezone.utc) + dt.timedelta(hours=h)).astimezone(tz)


class Sky:
    """Cached planet positions for one node choice."""

    def __init__(self, node="true"):
        self.node = node if node in NODE_ID else "true"

    @lru_cache(maxsize=200000)
    def calc(self, jd, pid):
        if pid in ("north_node", "south_node"):
            x = swe.calc_ut(jd, NODE_ID[self.node], FLAGS)[0]
            lon = x[0] if pid == "north_node" else norm(x[0] + 180)
            return lon, x[3]
        x = swe.calc_ut(jd, SWE[pid], FLAGS)[0]
        return x[0], x[3]

    def lon(self, jd, pid):
        return self.calc(round(jd, 5), pid)[0]

    def speed(self, jd, pid):
        return self.calc(round(jd, 5), pid)[1]


def _min_in(sky, pid, target, asp, jd0, jd1, step):
    """(orb, jd) of the closest approach of `pid` to `target`+/-asp between jd0 and jd1."""
    best = (999.0, jd0)
    j = jd0
    while j <= jd1:
        o = abs(sep(sky.lon(j, pid), target) - asp)
        if o < best[0]:
            best = (o, j)
        j += step
    # refine
    a, b = max(jd0, best[1] - step), min(jd1, best[1] + step)
    for _ in range(30):
        m1, m2 = a + (b - a) / 3, b - (b - a) / 3
        if abs(sep(sky.lon(m1, pid), target) - asp) < abs(sep(sky.lon(m2, pid), target) - asp):
            b = m2
        else:
            a = m1
    j = (a + b) / 2
    return abs(sep(sky.lon(j, pid), target) - asp), j


def _exacts(sky, pid, target, asp, jd0, jd1, step):
    """All moments in [jd0, jd1] when pid is exactly at `asp` from target."""
    out = []
    pts = {norm(target + asp), norm(target - asp)}
    for c in pts:
        prev = None
        j = jd0
        while j <= jd1 + step:
            d = ((sky.lon(j, pid) - c + 540) % 360) - 180
            if prev is not None and prev[1] * d < 0 and abs(d) < 10 and abs(prev[1]) < 10:
                a, b, da = prev[0], j, prev[1]
                for _ in range(40):
                    m = (a + b) / 2
                    dm = ((sky.lon(m, pid) - c + 540) % 360) - 180
                    if dm * da < 0:
                        b = m
                    else:
                        a, da = m, dm
                t = (a + b) / 2
                if jd0 <= t <= jd1 and not any(abs(t - x) < 0.5 for x in out):
                    out.append(t)
            prev = (j, d)
            j += step
    return sorted(out)


def natal_points(chart: dict) -> dict:
    """{id: lon} plus angles from a chart-service response."""
    pts = {b["id"]: b["lon"] for b in chart["bodies"] if b["id"] in NAME}
    retro = {b["id"]: bool(b.get("retrograde")) for b in chart["bodies"]}
    if chart.get("timed") and chart.get("houses"):
        ang = chart["houses"]["angles"]
        pts["asc"], pts["mc"] = ang["asc"]["lon"], ang["mc"]["lon"]
    return pts, retro


def cusps_for(chart: dict, pts: dict):
    """Placidus cusps when timed, otherwise solar whole sign houses from the Sun sign."""
    if chart.get("timed") and chart.get("houses"):
        return [c["lon"] for c in chart["houses"]["cusps"]], False
    s = int(pts["sun"] // 30) * 30
    return [norm(s + 30 * i) for i in range(12)], True


def natal_block(chart: dict, birth_date: dt.date):
    pts, retro = natal_points(chart)
    cusps, solar = cusps_for(chart, pts)
    H = lambda x: house_of(x, cusps)
    rising = int(pts["asc"] // 30) if "asc" in pts else int(pts["sun"] // 30)
    nat = {}
    for k, v in pts.items():
        nat[k] = {"lon": round(v, 4), "pos": fmt(v), "sign": sign_of(v), "deg": deg_of(v), "house": H(v),
                  "whole": (int(v // 30) - rising) % 12 + 1, "retro": retro.get(k, False)}
    # natal configurations: conjunctions within 8 degrees (planets, Chiron, nodes, angles) and stelliums
    CONJ_PTS = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto",
                "chiron", "north_node", "south_node", "asc", "mc")
    have = [k for k in CONJ_PTS if k in pts or (k == "south_node" and "north_node" in pts)]
    lonof = lambda k: pts[k] if k in pts else norm(pts["north_node"] + 180)
    conj = []
    for i, a in enumerate(have):
        for b in have[i + 1:]:
            if {a, b} == {"north_node", "south_node"} or {a, b} == {"asc", "mc"}:
                continue
            o = sep(lonof(a), lonof(b))
            if o <= 8.0:
                conj.append({"a": a, "b": b, "orb": round(o, 2)})
    stell = []
    for si, sname in enumerate(SIGNS):
        ks = [k for k in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto")
              if k in pts and int(pts[k] // 30) == si]
        if len(ks) >= 3:
            stell.append({"sign": sname, "points": ks})
    chart_ruler = RULER[rising]
    return {"points": nat, "conjunctions": conj, "stelliums": stell, "chart_ruler": chart_ruler,
            "cusps": [round(c, 4) for c in cusps], "cusp_signs": [sign_of(c) for c in cusps],
            "solar_houses": solar, "timed": not solar, "rising_sign": SIGNS[rising],
            "day_chart": chart.get("sect") == "day", "jd_ut": chart["time"]["jd_ut"],
            "birth_date": birth_date.isoformat()}


def _age_on(birth: dt.date, d: dt.date) -> int:
    a = d.year - birth.year
    if (d.month, d.day) < (birth.month, birth.day if not (birth.month == 2 and birth.day == 29) else 28):
        a -= 1
    return a


def _bday(birth: dt.date, year: int) -> dt.date:
    try:
        return dt.date(year, birth.month, birth.day)
    except ValueError:
        return dt.date(year, 2, 28)


def profections(nat, birth: dt.date, year: int, month: int):
    rising = SIGNS.index(nat["rising_sign"])
    P = nat["points"]
    mid = dt.date(year, month, 15)
    age = _age_on(birth, mid)
    ann = (rising + age) % 12
    last = _bday(birth, mid.year if mid >= _bday(birth, mid.year) else mid.year - 1)
    # monthly profection: one sign per ~30.44 days from the birthday
    k = int((mid - last).days // 30.44)
    msign = (ann + k) % 12
    shift = None
    for kk in range(1, 13):
        d = last + dt.timedelta(days=round(30.44 * kk))
        if d.year == year and d.month == month:
            shift = {"date": d.isoformat(), "sign": SIGNS[(ann + kk) % 12], "lord": RULER[(ann + kk) % 12],
                     "house": (kk + age) % 12 + 1}
    lord = RULER[ann]
    nxt = _bday(birth, last.year + 1)
    return {"age": age, "house": age % 12 + 1, "sign": SIGNS[ann], "lord": lord,
            "lord_sign": P[lord]["sign"], "lord_house": P[lord]["house"], "lord_whole": P[lord]["whole"],
            "since": last.isoformat(), "until": nxt.isoformat(),
            "month_house": (age + k) % 12 + 1, "month_sign": SIGNS[msign], "month_lord": RULER[msign],
            "month_lord_sign": P[RULER[msign]]["sign"], "month_lord_house": P[RULER[msign]]["house"],
            "month_shift": shift}


def month_facts(chart: dict, birth_date: dt.date, year: int, month: int, tz_name: str = "America/New_York",
                node: str = "true", detail: bool = True) -> dict:
    _engine._ensure_thread_setup()
    tz = ZoneInfo(tz_name)
    sky = Sky(node)
    nat = natal_block(chart, birth_date)
    P = nat["points"]
    cusps = nat["cusps"]
    H = lambda x: house_of(x, cusps)
    jb = nat["jd_ut"]
    start = dt.datetime(year, month, 1, tzinfo=tz)
    end = dt.datetime(year + (month == 12), month % 12 + 1, 1, tzinfo=tz)
    jd0, jd1 = _jd(start), _jd(end)
    day = lambda j: _local(j, tz).date().isoformat()
    targets = {k: P[k]["lon"] for k in TARGETS if k in P}
    if "north_node" in P:
        targets["south_node"] = P["south_node"]["lon"] if "south_node" in P else norm(P["north_node"]["lon"] + 180)

    out = {"natal": nat, "year": year, "month": month, "month_name": MONTHS[month - 1], "tz": tz_name,
           "node": sky.node, "profection": profections(nat, birth_date, year, month)}

    # ---- stations and ingresses
    stations, ingresses = [], []
    for pid in ("mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "chiron"):
        j, step = jd0 - 0.5, 0.25
        prev = None
        while j < jd1:
            lon, spd = sky.calc(round(j, 5), pid)
            if prev is not None:
                if prev[1] * spd < 0:
                    a, b, sa = prev[0], j, prev[1]
                    for _ in range(40):
                        m = (a + b) / 2
                        sm = sky.calc(round(m, 6), pid)[1]
                        if sm * sa < 0:
                            b = m
                        else:
                            a, sa = m, sm
                    t = (a + b) / 2
                    if jd0 <= t < jd1:
                        sl = sky.lon(t, pid)
                        on = []
                        for k, tl in targets.items():
                            for asp in (0, 90, 180, 120, 60):
                                o = abs(sep(sl, tl) - asp)
                                if o <= (1.0 if pid in SLOWS else 1.0) and not (k == pid and asp == 0 and False):
                                    on.append({"target": k, "aspect": asp, "orb": round(o, 2)})
                        on.sort(key=lambda x: x["orb"])
                        stations.append({"planet": pid, "kind": "retrograde" if sa > 0 else "direct",
                                         "date": day(t), "jd": t, "lon": round(sl, 3), "pos": fmt(sl),
                                         "sign": sign_of(sl), "house": H(sl), "on": on})
                if int(prev[2] // 30) != int(lon // 30):
                    ingresses.append({"planet": pid, "kind": "sign", "sign": sign_of(lon), "date": day(j),
                                      "jd": j, "retro": spd < 0})
                if H(prev[2]) != H(lon):
                    ingresses.append({"planet": pid, "kind": "house", "house": H(lon), "date": day(j), "jd": j,
                                      "retro": spd < 0})
            prev = (j, spd, lon)
            j += step
    # Sun ingresses
    j, prev = jd0, None
    while j < jd1:
        lon = sky.lon(j, "sun")
        if prev is not None:
            if int(prev // 30) != int(lon // 30):
                ingresses.append({"planet": "sun", "kind": "sign", "sign": sign_of(lon), "date": day(j), "jd": j})
            if H(prev) != H(lon):
                ingresses.append({"planet": "sun", "kind": "house", "house": H(lon), "date": day(j), "jd": j})
        prev = lon
        j += 0.25
    ingresses = [i for i in ingresses if jd0 <= i["jd"] < jd1]
    out["stations"] = sorted(stations, key=lambda s: s["jd"])
    out["ingresses"] = sorted(ingresses, key=lambda s: s["jd"])

    # ---- slow contacts (month orb within 1 degree), with every pass of the cycle
    slow = []
    for tp in SLOWS:
        for k, tl in targets.items():
            if tp == "north_node" and k in ("north_node", "south_node"):
                continue
            for asp in (0, 60, 90, 120, 180):
                if tp == k and asp in (60, 120):
                    continue
                if tp in ("north_node",) and asp in (60, 120):
                    continue
                o, jbest = _min_in(sky, tp, tl, asp, jd0, jd1 - 0.01, 1.0)
                if o > 1.0:
                    continue
                passes = _exacts(sky, tp, tl, asp, jd0 - 400, jd1 + 400, 2.0)
                near = _near_misses(sky, tp, tl, asp, jd0 - 400, jd1 + 400, passes)
                exact_in = [p for p in passes if jd0 <= p < jd1]
                o0 = abs(sep(sky.lon(jd0, tp), tl) - asp)
                o1 = abs(sep(sky.lon(jd1, tp), tl) - asp)
                tl_ = sky.lon(jbest, tp)
                slow.append({"planet": tp, "target": k, "aspect": asp, "orb": round(o, 2),
                             "orb_start": round(o0, 2), "orb_end": round(o1, 2),
                             "applying": o1 < o0, "closest": day(jbest),
                             "exact": [day(p) for p in exact_in],
                             "passes": [day(p) for p in passes],
                             "near": [{"date": day(j), "orb": round(o, 2)} for j, o in near],
                             "pos": fmt(tl_), "sign": sign_of(tl_), "house": H(tl_),
                             "retro": sky.speed(jbest, tp) < 0})
    for s in slow:
        s["weight"] = _weight(s, out["profection"])
    slow.sort(key=lambda s: -s["weight"])
    out["slow"] = slow

    # ---- transit planet positions (mid month) and houses
    jm = (jd0 + jd1) / 2
    out["sky"] = {pid: {"lon": round(sky.lon(jm, pid), 3), "pos": fmt(sky.lon(jm, pid)),
                        "sign": sign_of(sky.lon(jm, pid)), "house": H(sky.lon(jm, pid)),
                        "house_start": H(sky.lon(jd0, pid)), "house_end": H(sky.lon(jd1 - 0.01, pid)),
                        "sign_start": sign_of(sky.lon(jd0, pid)), "sign_end": sign_of(sky.lon(jd1 - 0.01, pid)),
                        "retro": sky.speed(jm, pid) < 0}
                  for pid in ("sun", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune",
                              "pluto", "chiron", "north_node", "south_node")}

    # ---- fast planets on their exact days
    fast = []
    for tp in FASTS:
        for k in PERSONAL_TARGETS:
            if k not in targets:
                continue
            asps = (0, 90, 180, 120) if tp == "venus" else (0, 90, 180)
            if tp == "sun":
                asps = (0, 180, 90)
            if k in OUTER_T:
                asps = (0, 90, 180) if tp in ("mars", "sun") else (0,)
            if k == "south_node" or (k == "north_node" and tp != "sun"):
                asps = (0,)
            for asp in asps:
                if tp == k and asp == 0 and tp == "sun":
                    pass
                for t in _exacts(sky, tp, targets[k], asp, jd0, jd1 - 1e-6, 0.25):
                    fast.append({"planet": tp, "target": k, "aspect": asp, "date": day(t), "jd": t,
                                 "house": H(sky.lon(t, tp)), "retro": sky.speed(t, tp) < 0})
    fast.sort(key=lambda f: f["jd"])
    out["fast"] = fast

    # ---- lunations and eclipses
    lun = []
    el = lambda j: norm(sky.lon(j, "moon") - sky.lon(j, "sun")) if False else norm(
        swe.calc_ut(j, swe.MOON, FLAGS)[0][0] - swe.calc_ut(j, swe.SUN, FLAGS)[0][0])
    j, pv = jd0, el(jd0)
    while j < jd1:
        j2 = j + 1 / 8
        e = el(j2)
        for tgt, nm in ((0, "new"), (180, "full")):
            if norm(pv - tgt) > 300 and norm(e - tgt) < 60:
                a, b = j, j2
                for _ in range(40):
                    m = (a + b) / 2
                    if norm(el(m) - tgt) > 300:
                        a = m
                    else:
                        b = m
                ml = swe.calc_ut(b, swe.MOON, FLAGS)[0][0]
                lt = _local(b, tz)
                ecl = _eclipse_at(b, nm)
                hits = []
                for k, tl in targets.items():
                    for asp in (0, 90, 180):
                        o = abs(sep(ml, tl) - asp)
                        if o <= 3.0:
                            hits.append({"target": k, "aspect": asp, "orb": round(o, 2)})
                hits.sort(key=lambda h: h["orb"])
                sm = ml if nm == "new" else swe.calc_ut(b, swe.SUN, FLAGS)[0][0]
                lun.append({"kind": nm, "date": lt.date().isoformat(), "time": lt.strftime("%-I:%M %p").lower(),
                            "jd": b, "lon": round(ml, 3), "pos": fmt(ml), "sign": sign_of(ml), "deg": deg_of(ml),
                            "house": H(ml), "sun_house": H(sm), "ruler": RULER[int(ml // 30)],
                            "eclipse": ecl, "hits": hits})
        j, pv = j2, e
    out["lunations"] = lun

    # ---- progressions (mid month) and solar arcs
    tm = _jd(dt.datetime(year, month, 15, 12, tzinfo=tz))
    pj = jb + (tm - jb) / YEAR
    prog = {}
    for pid in ("sun", "moon", "mercury", "venus", "mars"):
        x = swe.calc_ut(pj, SWE[pid], FLAGS)[0]
        prog[pid] = {"lon": round(x[0], 3), "pos": fmt(x[0]), "sign": sign_of(x[0]), "house": H(x[0]),
                     "retro": x[3] < 0}
    pm0 = swe.calc_ut(jb + (jd0 - jb) / YEAR, swe.MOON, FLAGS)[0][0]
    pm1 = swe.calc_ut(jb + (jd1 - jb) / YEAR, swe.MOON, FLAGS)[0][0]
    prog["moon"].update({"start": fmt(pm0), "end": fmt(pm1), "sign_change": sign_of(pm0) != sign_of(pm1),
                         "house_change": H(pm0) != H(pm1)})
    # when the progressed Moon entered its current sign, and when it leaves
    pmon = lambda t: swe.calc_ut(jb + (t - jb) / YEAR, swe.MOON, FLAGS)[0][0]
    s0 = int(pmon(tm) // 30)
    a = tm
    while int(pmon(a) // 30) == s0 and a > tm - 1000:
        a -= 5
    b = tm
    while int(pmon(b) // 30) == s0 and b < tm + 1000:
        b += 5
    prog["moon"]["entered"] = _local(a, tz).date().isoformat()
    prog["moon"]["leaves"] = _local(b, tz).date().isoformat()
    phase = norm(prog["moon"]["lon"] - prog["sun"]["lon"])
    # last progressed new moon
    t = tm
    while t > tm - 365 * 31:
        if norm(swe.calc_ut(jb + (t - jb) / YEAR, swe.MOON, FLAGS)[0][0] -
                swe.calc_ut(jb + (t - jb) / YEAR, swe.SUN, FLAGS)[0][0]) > 350:
            break
        t -= 10
    pnm = _local(t, tz).date()
    pnm_lon = swe.calc_ut(jb + (t - jb) / YEAR, swe.MOON, FLAGS)[0][0]
    out["progressed"] = {"planets": prog, "phase_angle": round(phase, 1), "phase": PHASES[int(phase // 45)],
                         "last_new": pnm.isoformat(), "last_new_sign": sign_of(pnm_lon), "last_new_house": H(pnm_lon)}
    pc = []
    for a_, pv_ in prog.items():
        for b_, tl in targets.items():
            if a_ == b_ and a_ != "moon":
                continue
            for asp in (0, 60, 90, 120, 180):
                o = abs(sep(pv_["lon"], tl) - asp)
                if o <= 1.0:
                    pc.append({"from": a_, "target": b_, "aspect": asp, "orb": round(o, 2)})
    pc.sort(key=lambda x: (x["from"] == "moon", x["orb"]))
    out["progressed"]["contacts"] = pc
    arc = norm(prog["sun"]["lon"] - P["sun"]["lon"])
    sa = []
    rate = 0.0027  # degrees of arc per day, about one degree a year
    for a_, al in targets.items():
        if a_ == "south_node":
            continue
        s_ = norm(al + arc)
        for b_, tl in targets.items():
            if a_ == b_ or (a_, b_) in (("north_node", "south_node"),):
                continue
            for asp in (0, 90, 180):
                d = sep(s_, tl) - asp
                if abs(d) <= 1.0:
                    # approaching when moving the arc forward closes the gap
                    d2 = abs(sep(norm(s_ + 0.05), tl) - asp)
                    app = d2 < abs(d)
                    days = abs(d) / rate
                    when = dt.date(year, month, 15) + dt.timedelta(days=days if app else -days)
                    sa.append({"from": a_, "target": b_, "aspect": asp, "orb": round(abs(d), 2), "applying": app,
                               "exact": f"{MONTHS[when.month - 1]} {when.year}"})
    sa = [x for x in sa if not (x["from"] == "asc" and x["target"] == "mc") and not (x["from"] == "mc" and x["target"] == "asc")]
    sa.sort(key=lambda x: x["orb"])
    out["solar_arcs"] = {"arc": round(arc, 2), "contacts": sa}

    # ---- midpoints
    mps = []
    for a_, b_ in MIDPOINTS:
        if a_ not in targets or b_ not in targets:
            continue
        m = _midpoint(targets[a_], targets[b_])
        for tp in ("jupiter", "saturn", "uranus", "neptune", "pluto", "chiron"):
            for asp in (0, 90, 180):
                o, jb_ = _min_in(sky, tp, m, asp, jd0, jd1 - 0.01, 1.0)
                if o <= 1.0:
                    mps.append({"planet": tp, "pair": [a_, b_], "aspect": asp, "orb": round(o, 2),
                                "pos": fmt(m), "closest": day(jb_), "house": H(m)})
    mps.sort(key=lambda x: x["orb"])
    out["midpoints"] = mps

    # ---- life cycles in orb this year
    cyc = []
    for tp in ("jupiter", "saturn", "uranus", "neptune", "pluto", "chiron", "north_node"):
        if tp not in targets:
            continue
        for asp in (0, 90, 180):
            o = abs(sep(sky.lon(jm, tp), targets[tp]) - asp)
            if o <= (3.0 if tp in ("jupiter", "north_node") else 4.0):
                passes = _exacts(sky, tp, targets[tp], asp, jm - 500, jm + 500, 2.0)
                if tp == "north_node" and asp == 90:
                    continue
                cyc.append({"planet": tp, "aspect": asp, "orb": round(o, 2), "passes": [day(p) for p in passes]})
    out["cycles"] = cyc

    # ---- eclipses ahead (next solar and lunar after the month)
    ahead = []
    t = swe.sol_eclipse_when_glob(jd1, swe.FLG_SWIEPH, 0, False)[1][0]
    ahead.append(("solar", t))
    t = swe.lun_eclipse_when(jd1, swe.FLG_SWIEPH, 0, False)[1][0]
    ahead.append(("lunar", t))
    out["eclipses_ahead"] = []
    for kind, t in sorted(ahead, key=lambda x: x[1]):
        ml = swe.calc_ut(t, swe.MOON, FLAGS)[0][0]
        out["eclipses_ahead"].append({"kind": kind, "date": day(t), "pos": fmt(ml), "sign": sign_of(ml), "house": H(ml)})

    # ---- next two months: what begins (slow contacts and stations)
    if detail:
        nxt = []
        for k in (1, 2):
            yy, mm = year + (month + k - 1) // 12, (month + k - 1) % 12 + 1
            a0 = _jd(dt.datetime(yy, mm, 1, tzinfo=tz))
            a1 = _jd(dt.datetime(yy + (mm == 12), mm % 12 + 1, 1, tzinfo=tz))
            items = []
            for tp in SLOWS:
                for k_, tl in targets.items():
                    if tp == "north_node" and k_ in ("north_node", "south_node"):
                        continue
                    for asp in (0, 90, 180, 120):
                        if tp == k_ and asp == 120:
                            continue
                        ex = _exacts(sky, tp, tl, asp, a0, a1, 1.0)
                        if ex:
                            items.append({"planet": tp, "target": k_, "aspect": asp, "date": day(ex[0]),
                                          "house": H(sky.lon(ex[0], tp))})
            for pid in ("mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "chiron"):
                j = a0
                while j < a1:
                    if sky.speed(j, pid) * sky.speed(j + 1, pid) < 0:
                        a_, b_, sa = j, j + 1, sky.speed(j, pid)
                        for _ in range(30):
                            m_ = (a_ + b_) / 2
                            if sky.calc(round(m_, 6), pid)[1] * sa > 0:
                                a_ = m_
                            else:
                                b_ = m_
                        t_ = (a_ + b_) / 2
                        sl = sky.lon(t_, pid)
                        on = [k_ for k_, tl in targets.items() for asp in (0, 90, 180, 120) if abs(sep(sl, tl) - asp) <= 1.0]
                        items.append({"station": pid, "kind": "retrograde" if sa > 0 else "direct",
                                      "date": day(t_), "sign": sign_of(sl), "house": H(sl), "on": on[:2]})
                    j += 1
            lunx = []
            j, pv = a0, el(a0)
            while j < a1:
                j2 = j + 0.25
                e = el(j2)
                for tgt, nm in ((0, "new"), (180, "full")):
                    if norm(pv - tgt) > 300 and norm(e - tgt) < 60:
                        ml = swe.calc_ut(j2, swe.MOON, FLAGS)[0][0]
                        lunx.append({"kind": nm, "date": day(j2), "sign": sign_of(ml), "house": H(ml),
                                     "eclipse": _eclipse_at(j2, nm)})
                j, pv = j2, e
            nxt.append({"year": yy, "month": mm, "month_name": MONTHS[mm - 1], "items": items, "lunations": lunx})
        out["ahead"] = nxt

    # ---- wheel data
    out["wheel"] = {"natal": {k: round(v["lon"], 3) for k, v in P.items()},
                    "natal_retro": [k for k, v in P.items() if v["retro"]],
                    "cusps": cusps, "timed": nat["timed"],
                    "transit": {k: v["lon"] for k, v in out["sky"].items()},
                    "transit_retro": [k for k, v in out["sky"].items() if v["retro"]],
                    "transit_date": f"{year}-{month:02d}-15"}
    return out


def _near_misses(sky, pid, target, asp, jd0, jd1, passes):
    """Stations that come within 0.3 degrees of exact without perfecting."""
    out = []
    j, prev = jd0, None
    while j <= jd1:
        sp = sky.speed(j, pid)
        if prev is not None and prev * sp < 0:
            a_, b_ = j - 2.0, j
            for _ in range(30):
                m_ = (a_ + b_) / 2
                if sky.calc(round(m_, 6), pid)[1] * prev > 0:
                    a_ = m_
                else:
                    b_ = m_
            j = (a_ + b_) / 2
            o = abs(sep(sky.lon(j, pid), target) - asp)
            if o <= 0.3 and not any(abs(j - p) < 40 for p in passes):
                out.append((j, o))
            j = b_
        prev = sp
        j += 2.0
    return out


def _weight(s, prof):
    w = {"pluto": 9, "neptune": 8, "uranus": 8, "saturn": 8, "chiron": 6, "jupiter": 6, "north_node": 4}[s["planet"]]
    w += {"sun": 4, "moon": 4, "asc": 4, "mc": 4, "venus": 3, "mars": 3, "mercury": 2.5, "saturn": 2,
          "jupiter": 2, "north_node": 2.5, "south_node": 2, "chiron": 2, "uranus": 1, "neptune": 1, "pluto": 1}.get(s["target"], 1)
    w += {0: 3, 180: 2.5, 90: 2.5, 120: 1, 60: 0.5}[s["aspect"]]
    w += (1.0 - s["orb"]) * 3
    if s["exact"]:
        w += 2
    if s["planet"] == prof["lord"] or s["target"] == prof["lord"]:
        w += 3
    if s["planet"] == prof["month_lord"] or s["target"] == prof["month_lord"]:
        w += 1
    if s["planet"] == s["target"]:
        w -= 1
    return round(w, 2)


def _midpoint(a, b):
    d = norm(b - a)
    return norm(a + d / 2) if d <= 180 else norm(b + (360 - d) / 2)


@lru_cache(maxsize=512)
def _eclipse_at(jd, kind):
    """Eclipse type when a lunation is an eclipse, else None."""
    try:
        if kind == "new":
            r = swe.sol_eclipse_when_glob(jd - 2, swe.FLG_SWIEPH, 0, False)
            t, typ = r[1][0], r[0]
            if abs(t - jd) < 1:
                if typ & swe.ECL_TOTAL:
                    return "total solar eclipse"
                if typ & swe.ECL_ANNULAR:
                    return "annular solar eclipse"
                if typ & swe.ECL_PARTIAL:
                    return "partial solar eclipse"
                return "solar eclipse"
        else:
            r = swe.lun_eclipse_when(jd - 2, swe.FLG_SWIEPH, 0, False)
            t, typ = r[1][0], r[0]
            if abs(t - jd) < 1:
                if typ & swe.ECL_TOTAL:
                    return "total lunar eclipse"
                if typ & swe.ECL_PARTIAL:
                    return "partial lunar eclipse"
                if typ & swe.ECL_PENUMBRAL:
                    return "penumbral lunar eclipse"
                return "lunar eclipse"
    except Exception:
        return None
    return None


# ---------------------------------------------------------------- two people
LINK_POINTS = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto",
               "chiron", "north_node", "south_node", "asc", "mc")


def pair_facts(fa: dict, fb: dict, node: str = "true") -> dict:
    """fa, fb: month_facts for each person (same month and time zone)."""
    sky = Sky(node)
    tz = ZoneInfo(fa["tz"])
    A, B = fa["natal"]["points"], fb["natal"]["points"]
    HA = lambda x: house_of(x, fa["natal"]["cusps"])
    HB = lambda x: house_of(x, fb["natal"]["cusps"])
    links = []
    for a in LINK_POINTS:
        if a not in A:
            continue
        for b in LINK_POINTS:
            if b not in B:
                continue
            if a in ("north_node", "south_node") and b in ("north_node", "south_node") and a != b:
                continue
            for asp in (0, 60, 90, 120, 180):
                o = abs(sep(A[a]["lon"], B[b]["lon"]) - asp)
                lim = 2.0
                if o <= lim:
                    if a == "south_node" and asp != 0 or b == "south_node" and asp != 0:
                        continue
                    links.append({"a": a, "b": b, "aspect": asp, "orb": round(o, 2),
                                  "a_in_b_house": HB(A[a]["lon"]), "b_in_a_house": HA(B[b]["lon"]),
                                  "weight": _link_weight(a, b, asp, o)})
    links.sort(key=lambda x: -x["weight"])
    year, month = fa["year"], fa["month"]
    jd0 = _jd(dt.datetime(year, month, 1, tzinfo=tz))
    jd1 = _jd(dt.datetime(year + (month == 12), month % 12 + 1, 1, tzinfo=tz))
    day = lambda j: _local(j, tz).date().isoformat()
    shared = []
    for L in links:
        la, lb = A[L["a"]]["lon"], B[L["b"]]["lon"]
        for tp in ("jupiter", "saturn", "uranus", "neptune", "pluto", "chiron", "north_node"):
            best = None
            for asp_a in (0, 90, 180, 60, 120):
                for asp_b in (0, 90, 180, 60, 120):
                    if tp == "north_node" and (asp_a in (60, 120) or asp_b in (60, 120)):
                        continue
                    j = jd0
                    while j < jd1:
                        l = sky.lon(j, tp)
                        oa, ob = abs(sep(l, la) - asp_a), abs(sep(l, lb) - asp_b)
                        m = max(oa, ob)
                        if m <= 1.5 and (best is None or m < best[0]):
                            best = (m, j, asp_a, asp_b, oa, ob)
                        j += 1.0
            if best:
                m, j, asp_a, asp_b, oa, ob = best
                tl = sky.lon(j, tp)
                shape = None
                if L["aspect"] == 180 and asp_a == 90 and asp_b == 90:
                    shape = {"kind": "tsquare", "apex": "transit", "open": norm(tl + 180)}
                elif L["aspect"] == 90 and {asp_a, asp_b} == {90, 180}:
                    apex = "a" if asp_a == 90 else "b"
                    shape = {"kind": "tsquare", "apex": apex, "open": norm((la if apex == "b" else lb) + 180)}
                elif L["aspect"] == 120 and asp_a == 120 and asp_b == 120:
                    shape = {"kind": "grand_trine"}
                elif L["aspect"] == 0 and asp_a == 0:
                    shape = {"kind": "stack"}
                shared.append({"planet": tp, "link": L, "asp_a": asp_a, "asp_b": asp_b, "orb_a": round(oa, 2),
                               "orb_b": round(ob, 2), "date": day(j), "pos": fmt(tl), "house_a": HA(tl),
                               "house_b": HB(tl), "shape": shape,
                               "weight": round(L["weight"] + {"pluto": 4, "neptune": 3.5, "uranus": 3.5, "saturn": 3.5,
                                                              "chiron": 3, "jupiter": 2.5, "north_node": 2}[tp]
                                               + (2 if shape and shape["kind"] == "tsquare" else 0)
                                               + (1.5 - m), 2)})
    shared.sort(key=lambda s: -s["weight"])
    # one entry per transit planet + link pair, best first, and keep at most two per transit planet
    seen, keep, per = set(), [], {}
    for s in shared:
        key = (s["planet"], s["link"]["a"], s["link"]["b"])
        if key in seen or per.get(s["planet"], 0) >= 2:
            continue
        seen.add(key)
        per[s["planet"]] = per.get(s["planet"], 0) + 1
        keep.append(s)
    # same slow planet active in both solo charts
    both = []
    for tp in SLOWS:
        sa = [s for s in fa["slow"] if s["planet"] == tp]
        sb = [s for s in fb["slow"] if s["planet"] == tp]
        if sa and sb:
            both.append({"planet": tp, "a": sa[:3], "b": sb[:3]})
    houses = {pid: {"a": fa["sky"][pid]["house"], "b": fb["sky"][pid]["house"], "sign": fa["sky"][pid]["sign"]}
              for pid in fa["sky"]}
    return {"links": links, "shared": keep[:6], "both": both, "houses": houses,
            "lunations": [{"kind": l["kind"], "date": l["date"], "time": l["time"], "pos": l["pos"], "sign": l["sign"],
                           "deg": l["deg"], "eclipse": l["eclipse"], "house_a": l["house"],
                           "house_b": house_of(l["lon"], fb["natal"]["cusps"]),
                           "hits_a": l["hits"], "hits_b": _hits(l["lon"], B)} for l in fa["lunations"]]}


def _hits(lon, pts):
    out = []
    for k, v in pts.items():
        for asp in (0, 90, 180):
            o = abs(sep(lon, v["lon"]) - asp)
            if o <= 3.0:
                out.append({"target": k, "aspect": asp, "orb": round(o, 2)})
    return sorted(out, key=lambda h: h["orb"])


def _link_weight(a, b, asp, o):
    imp = {"sun": 4, "moon": 4, "venus": 3, "mars": 3, "asc": 3, "mc": 2.5, "mercury": 2, "saturn": 2.5,
           "jupiter": 2, "north_node": 2.5, "south_node": 2.5, "chiron": 2, "pluto": 2, "uranus": 1.5, "neptune": 1.5}
    w = imp.get(a, 1) + imp.get(b, 1) + {0: 3, 180: 2.5, 90: 2.5, 120: 1.5, 60: 1}[asp] + (2 - o)
    if a in ("uranus", "neptune", "pluto") and b in ("uranus", "neptune", "pluto"):
        w -= 4  # generational
    return round(w, 2)
