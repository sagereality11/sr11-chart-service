"""Your Monthly Money Forecast: the facts for one calendar month, read against the Wealth Story.

Everything is measured against the same money points the Wealth Story uses (the ruler of the second
house, the career ruler, the Part of Fortune, the Lot of Assets, the Midheaven, Venus and Jupiter),
so the two readings speak the same language.

Techniques, in the order they carry weight for a single month:
  1. Transits to the money points. Slow planets (Jupiter to Pluto) set the month's currents; Mars,
     Venus, the Sun and Mercury mark the dated days.
  2. The New Moon and Full Moon by house, with eclipses flagged.
  3. The lord of the month (monthly profection, one sign per month from the birthday).
  4. The progressed Moon (secondary progressions), plus the progressed Sun and Venus when exact.
  5. Solar arc directions within half a degree of exact (a year-long background current).
  6. Money midpoints (Venus/Jupiter, Jupiter/Pluto, Sun/Jupiter, Jupiter/MC) touched within a degree.
  7. Mercury stations and retrograde periods, when they fall in a money house or on a money point.
"""
from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

import swisseph as swe

from . import engine as _engine
from . import wealth as W

BODY = {"sun": swe.SUN, "mercury": swe.MERCURY, "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
        "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE, "pluto": swe.PLUTO, "moon": swe.MOON}
SLOWS = ("jupiter", "saturn", "uranus", "neptune", "pluto")
STEP = 0.25  # days
MIDPOINTS = (("venus", "jupiter"), ("jupiter", "pluto"), ("sun", "jupiter"), ("jupiter", "mc"))


def _jd(d: dt.datetime) -> float:
    d = d.astimezone(dt.timezone.utc)
    return swe.julday(d.year, d.month, d.day, d.hour + d.minute / 60 + d.second / 3600)


def _local_date(jd: float, tz: ZoneInfo) -> dt.date:
    y, m, d, h = swe.revjul(jd)
    utc = dt.datetime(y, m, d, tzinfo=dt.timezone.utc) + dt.timedelta(hours=h)
    return utc.astimezone(tz).date()


def _pos(jd: float, pid: str):
    x = swe.calc_ut(jd, BODY[pid], W.FLAGS)[0]
    return x[0], x[3]


def midpoint(a: float, b: float) -> float:
    """Near midpoint (the shorter arc)."""
    d = W.norm(b - a)
    return W.norm(a + d / 2) if d <= 180 else W.norm(b + (360 - d) / 2)


def _crossings(samples, target, aspects):
    """Exact moments a moving point (list of (jd, lon)) makes one of `aspects` to `target`."""
    out = []
    for asp in aspects:
        for c in {W.norm(target + asp), W.norm(target - asp)}:
            prev = None
            for jd, lon in samples:
                d = W.sep(lon, c)
                if prev is not None and prev[1] * d < 0 and abs(d) < 5 and abs(prev[1]) < 5:
                    t = prev[0] + (jd - prev[0]) * abs(prev[1]) / (abs(prev[1]) + abs(d))
                    out.append((t, asp))
                prev = (jd, d)
    return out


def month_facts(a: dict, chart: dict, year: int, month: int, tz_name: str = "America/New_York",
                birth_date: dt.date | None = None) -> dict:
    """a = wealth.analyze(...) for the same chart. Returns everything the monthly reading needs."""
    _engine._ensure_thread_setup()
    tz = ZoneInfo(tz_name)
    start = dt.datetime(year, month, 1, tzinfo=tz)
    end = dt.datetime(year + (month == 12), month % 12 + 1, 1, tzinfo=tz)
    jd0, jd1 = _jd(start), _jd(end)
    P, lon, cusps = a["planets"], a["lon"], a["cusps"]
    untimed = bool(a.get("untimed"))
    R = a["rulers"]
    r2, rc = R[2], R[10]
    rf = W.RULER[P["fortune"]["sign"]] if "fortune" in P else None
    H = lambda x: W.house_of(x, cusps)
    in_month = lambda jd: jd0 <= jd < jd1
    when = lambda jd: _local_date(jd, tz)

    # ---- money points
    targets = {}
    for k in (r2, rc, "fortune", "assets", "mc", "venus", "jupiter", rf, "sun", "asc"):
        if k and k in lon and k not in targets:
            targets[k] = lon[k]

    # ---- sampled sky
    n = int((jd1 - jd0) / STEP) + 9
    grid = [jd0 - 1 + i * STEP for i in range(n)]
    sky = {pid: [(jd, *_pos(jd, pid)) for jd in grid] for pid in BODY if pid != "moon"}

    events = []
    # slow currents: active in the month within 1 degree
    currents = []
    for tp in SLOWS:
        for k, t in targets.items():
            asps = (0, 60, 90, 120, 180) if tp in ("jupiter", "saturn") else (0, 90, 180)
            for asp in asps:
                if tp == k and asp in (60, 120):
                    continue
                orbs = [min(abs(W.sep(l, W.norm(t + asp))), abs(W.sep(l, W.norm(t - asp)))) for jd, l, _ in sky[tp]
                        if in_month(jd)]
                if not orbs or min(orbs) > 1.0:
                    continue
                ex = [x for x, s in _crossings([(jd, l) for jd, l, _ in sky[tp]], t, (asp,)) if in_month(x)]
                currents.append({"planet": tp, "target": k, "aspect": asp, "orb": round(min(orbs), 2),
                                 "class": "conj" if asp == 0 else "hard" if asp in (90, 180) else "soft",
                                 "exact": when(ex[0]) if ex else None})
    currents.sort(key=lambda c: (c["orb"], SLOWS.index(c["planet"])))

    # dated days from the faster planets
    fast_rules = {"mars": (0, 90, 180), "venus": (0, 120, 60, 180), "sun": (0,), "mercury": (0,)}
    fast_targets = [k for k in (r2, rc, "fortune", "assets", "mc", "venus", "jupiter") if k in targets]
    fast_targets = list(dict.fromkeys(fast_targets))
    for tp, asps in fast_rules.items():
        for k in fast_targets:
            t = targets[k]
            if tp == "mercury" and k not in (r2, rc, "mc"):
                continue
            if tp == k:
                continue
            for x, asp in _crossings([(jd, l) for jd, l, _ in sky[tp]], t, asps):
                if in_month(x):
                    events.append({"kind": "day", "planet": tp, "target": k, "aspect": asp, "jd": x, "date": when(x)})

    # Mercury stations
    merc = sky["mercury"]
    stations = []
    for (j1, l1, s1), (j2, l2, s2) in zip(merc, merc[1:]):
        if s1 * s2 < 0:
            t = j1 + (j2 - j1) * abs(s1) / (abs(s1) + abs(s2))
            if in_month(t):
                kind = "retrograde" if s1 > 0 else "direct"
                stations.append({"kind": kind, "jd": t, "date": when(t), "lon": l1, "sign": W.sign_of(l1), "house": H(l1)})
    retro_in_month = any(s < 0 for jd, _, s in merc if in_month(jd))
    merc_mid = _pos((jd0 + jd1) / 2, "mercury")[0]

    # ---- lunations and eclipses
    lunations = []
    elong = []
    for jd in [jd0 - 1 + i * 0.25 for i in range(int((jd1 - jd0 + 2) / 0.25))]:
        s, m = _pos(jd, "sun")[0], _pos(jd, "moon")[0]
        elong.append((jd, W.norm(m - s)))
    for (j1, e1), (j2, e2) in zip(elong, elong[1:]):
        for kind, tgt in (("new", 0.0), ("full", 180.0)):
            d1, d2 = W.sep(e1, tgt), W.sep(e2, tgt)
            if d1 * d2 < 0 and abs(d1) < 20:
                t = j1 + (j2 - j1) * abs(d1) / (abs(d1) + abs(d2))
                if in_month(t):
                    ml = _pos(t, "moon")[0]
                    hits = []
                    for k, tl in targets.items():
                        for asp in (0, 90, 180):
                            o = min(abs(W.sep(ml, W.norm(tl + asp))), abs(W.sep(ml, W.norm(tl - asp))))
                            if o <= 3.0:
                                hits.append({"target": k, "aspect": asp, "orb": round(o, 1)})
                    hits.sort(key=lambda h: h["orb"])
                    lunations.append({"kind": kind, "jd": t, "date": when(t), "lon": ml, "sign": W.sign_of(ml),
                                      "deg": W.deg_of(ml), "house": H(ml), "hits": hits[:2], "eclipse": None})
    for e in W.eclipses_between(jd0 - 1, jd1 + 1):
        for L in lunations:
            if abs(L["jd"] - e["jd"]) < 1.0:
                L["eclipse"] = e["type"]
    lunations.sort(key=lambda L: L["jd"])

    # ---- monthly profection (one sign per month from the most recent birthday)
    prof = a["profection"]
    bd = birth_date or chart_birth_date(chart)
    mid = (start + (end - start) / 2).date()
    last = dt.date(mid.year, bd.month, min(bd.day, 28 if bd.month == 2 else bd.day))
    if last > mid:
        last = dt.date(mid.year - 1, last.month, last.day)
    k = int((mid - last).days / 30.4375) % 12
    m_sign = W.SIGNS[(W.SIGNS.index(prof["sign"]) + k) % 12]
    m_house = (prof["house"] - 1 + k) % 12 + 1
    monthly = {"sign": m_sign, "house": m_house, "lord": W.RULER[m_sign], "index": k,
               "year_house": prof["house"], "year_lord": prof["lord"]}

    # ---- secondary progressions
    bjd = chart_jd(chart)
    def prog_jd(jd):
        return bjd + (jd - bjd) / 365.2425
    pm0, pm1 = _pos(prog_jd(jd0), "moon")[0], _pos(prog_jd(jd1), "moon")[0]
    pmoon = {"sign": W.sign_of(pm0), "deg": W.deg_of(pm0), "house": H(pm0), "lon": pm0,
             "sign_change": W.sign_of(pm1) if W.sign_of(pm1) != W.sign_of(pm0) else None,
             "house_change": H(pm1) if H(pm1) != H(pm0) else None, "aspects": []}
    natal_pts = {p: lon[p] for p in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn") if p in lon}
    natal_pts.update({x: lon[x] for x in ("fortune", "assets", "mc", "asc") if x in lon})
    psamples = [(jd, _pos(prog_jd(jd), "moon")[0]) for jd in [jd0 - 40 + i * 2 for i in range(int((jd1 - jd0 + 80) / 2))]]
    for p, t in natal_pts.items():
        if untimed and p == "moon":
            continue
        for x, asp in _crossings(psamples, t, (0, 60, 90, 120, 180)):
            if jd0 - 15 <= x < jd1 + 15:
                pmoon["aspects"].append({"target": p, "aspect": asp, "date": when(x), "in_month": in_month(x)})
    pmoon["aspects"].sort(key=lambda x: x["date"])
    slow_prog = []
    for pid in ("sun", "venus", "mercury", "mars"):
        pl = _pos(prog_jd((jd0 + jd1) / 2), pid)[0]
        for k2 in (r2, rc, "fortune", "venus", "jupiter", "mc"):
            if k2 and k2 in lon and k2 != pid:
                for asp in (0, 60, 90, 120, 180):
                    o = min(abs(W.sep(pl, W.norm(lon[k2] + asp))), abs(W.sep(pl, W.norm(lon[k2] - asp))))
                    if o <= 0.25:
                        slow_prog.append({"planet": pid, "target": k2, "aspect": asp, "orb": round(o, 2)})

    # ---- solar arc directions (hard aspects, within half a degree)
    arc = W.norm(_pos(prog_jd((jd0 + jd1) / 2), "sun")[0] - lon["sun"])
    sa = []
    movers = [p for p in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "mc", "asc")
              if p in lon and not (untimed and p == "moon")]
    for m in movers:
        dl = W.norm(lon[m] + arc)
        for k2, t in targets.items():
            if k2 == m:
                continue
            for asp in (0, 90, 180):
                o = min(abs(W.sep(dl, W.norm(t + asp))), abs(W.sep(dl, W.norm(t - asp))))
                if o <= 0.5:
                    sa.append({"planet": m, "target": k2, "aspect": asp, "orb": round(o, 2)})
    sa.sort(key=lambda x: x["orb"])

    # ---- money midpoints touched by the slow planets and Mars
    mids = []
    for x, y in MIDPOINTS:
        if x not in lon or y not in lon:
            continue
        mp = midpoint(lon[x], lon[y])
        for tp in SLOWS + ("mars",):
            for xjd, asp in _crossings([(jd, l) for jd, l, _ in sky[tp]], mp, (0, 90, 180)):
                if in_month(xjd):
                    mids.append({"pair": (x, y), "planet": tp, "aspect": asp, "date": when(xjd), "lon": mp})
    mids.sort(key=lambda m: m["date"])

    # ---- next month's New Moon (one-line teaser)
    nxt = None
    for i in range(0, 40 * 4):
        j = jd1 + i * 0.25
        e1 = W.norm(_pos(j, "moon")[0] - _pos(j, "sun")[0])
        e2 = W.norm(_pos(j + 0.25, "moon")[0] - _pos(j + 0.25, "sun")[0])
        if e1 > 300 and e2 < 60:
            ml = _pos(j, "moon")[0]
            nxt = {"date": when(j), "sign": W.sign_of(ml), "house": H(ml)}
            break

    events += [{"kind": "lunation", **L} for L in lunations]
    events += [{"kind": "station", **s} for s in stations]
    events += [{"kind": "pmoon", "jd": None, **x} for x in pmoon["aspects"] if x["in_month"]]
    events += [{"kind": "midpoint", "jd": None, **m} for m in mids]
    events.sort(key=lambda e: e["date"])

    # house ingresses of the faster planets (for the calendar)
    house_moves = []
    for pid in ("sun", "mercury", "venus", "mars"):
        prev = None
        for jd, l, _ in sky[pid]:
            h = H(l)
            if prev is not None and h != prev and in_month(jd):
                house_moves.append({"planet": pid, "house": h, "date": when(jd), "retro": _ < 0})
            prev = h
    midjd = (jd0 + jd1) / 2
    moving = {pid: {"house": H(_pos(midjd, pid)[0]), "sign": W.sign_of(_pos(midjd, pid)[0])} for pid in ("sun", "venus", "mars")}

    return {"moving": moving, "year": year, "month": month, "month_name": W.MONTHS[month - 1], "start": start.date(), "tz": tz_name,
            "untimed": untimed, "targets": list(targets), "r2": r2, "rc": rc, "rf": rf,
            "currents": currents, "events": events, "lunations": lunations, "stations": stations,
            "mercury_retro": retro_in_month, "mercury_mid": {"sign": W.sign_of(merc_mid), "house": H(merc_mid)},
            "monthly": monthly, "pmoon": pmoon, "slow_prog": slow_prog, "solar_arcs": sa[:3], "arc": arc,
            "midpoints": mids, "next_new_moon": nxt, "house_moves": house_moves}


def chart_jd(chart: dict) -> float:
    t = chart["time"]["utc_iso"]
    d = dt.datetime.fromisoformat(t.replace("Z", "+00:00"))
    return _jd(d)


def chart_birth_date(chart: dict) -> dt.date:
    return dt.date.fromisoformat(chart["time"]["local_iso"][:10])
