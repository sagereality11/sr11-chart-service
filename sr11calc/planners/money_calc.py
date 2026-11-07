"""Money & Business Planner data: money blueprint, profections, money transits, stations,
void Moon, green and caution days, money moons and eclipses."""

from __future__ import annotations

import datetime as dt
from datetime import timedelta

from .common import Ctx, RULER, fmt, sign


def compute(ctx: Ctx) -> dict:
    natal, house, tojd, fromjd, lon = ctx.natal, ctx.house, ctx.tojd, ctx.fromjd, ctx.lon
    spd = lambda p, jd: ctx.pos(p, jd)[1]
    JD0, JD1, start, end, tz = ctx.J0, ctx.J1, ctx.start, ctx.end, ctx.tz
    cusps = ctx.cusps
    c2 = sign(cusps[1]); r2 = RULER[c2]
    mc = sign(natal["Midheaven"]); r10 = RULER[mc]
    blueprint = dict(
        second=dict(sign=c2, ruler=r2, ruler_sign=sign(natal[r2]), ruler_house=house(natal[r2])),
        venus=dict(sign=sign(natal["Venus"]), house=house(natal["Venus"]), deg=fmt(natal["Venus"])),
        jupiter=dict(sign=sign(natal["Jupiter"]), house=house(natal["Jupiter"]), deg=fmt(natal["Jupiter"])),
        mc=dict(sign=mc, ruler=r10, ruler_sign=sign(natal[r10]), ruler_house=house(natal[r10])),
    )
    POINTS = {"Venus": natal["Venus"], "Jupiter": natal["Jupiter"], "Midheaven": natal["Midheaven"]}
    if r2 not in POINTS:
        POINTS[r2] = natal[r2]
    prof = ctx.profections()

    # ---- hourly scan for transits ----
    events = []
    MONEY_H = {2,6,8,10,11}
    STEP = 1/24
    slow = ["Sun","Mercury","Venus","Mars","Jupiter","Saturn"]
    ASPECTS = {0:"conjunct",60:"sextile",90:"square",120:"trine",180:"opposite"}
    prev = None
    jd = JD0 - 2
    hourly = []
    while jd <= JD1 + 2:
        row = {p: lon(p, jd) for p in slow + ["Moon"]}
        row["_sp"] = {p: spd(p, jd) for p in ["Mercury","Venus","Mars","Jupiter","Saturn"]}
        hourly.append((jd, row)); jd += STEP


    for i in range(1, len(hourly)):
        j0, r0 = hourly[i-1]; j1, r1 = hourly[i]
        if not (JD0 <= j1 <= JD1): continue
        # house ingresses (daily resolution is fine; use hourly)
        for p in slow:
            h0, h1 = house(r0[p]), house(r1[p])
            if h0 != h1 and h1 in MONEY_H:
                events.append(dict(type="ingress", planet=p, house=h1, jd=j1, retro=r1["_sp"].get(p,1) < 0 if p in r1["_sp"] else False))
        # stations
        for p in ["Mercury","Venus","Mars","Jupiter","Saturn"]:
            s0, s1 = r0["_sp"][p], r1["_sp"][p]
            if (s0 > 0) != (s1 > 0):
                events.append(dict(type="station", planet=p, direction="retrograde" if s1 < 0 else "direct", jd=j1, deg=fmt(r1[p]), house=house(r1[p])))
        # aspects to money points
        for p in ["Sun","Venus","Mars","Jupiter","Saturn"]:
            for n, nl in POINTS.items():
                for a, nm in ASPECTS.items():
                    for sgn in ((1,) if a in (0,180) else (1,-1)):
                        f = lambda r: ((r[p] - nl - sgn*a + 180) % 360) - 180
                        v0, v1 = f(r0), f(r1)
                        if abs(v0) < 5 and (v0 < 0 <= v1 or v0 > 0 >= v1) and v0 != v1:
                            events.append(dict(type="aspect", planet=p, aspect=nm, point=n, jd=j0 + (j1-j0)*abs(v0)/(abs(v0)+abs(v1)),
                                               flow=a in (60,120) or (a==0 and p in ("Venus","Jupiter","Sun")), house=house(r1[p])))

    # dedupe ingresses that flip back within 3 days (house-cusp jitter)
    events.sort(key=lambda e: e["jd"])
    clean = []
    for e in events:
        if e["type"] == "ingress" and any(c["type"]=="ingress" and c["planet"]==e["planet"] and c["house"]==e["house"] and e["jd"]-c["jd"] < 3 for c in clean):
            continue
        clean.append(e)
    events = clean
    for e in events:
        e["dt"] = fromjd(e["jd"]).isoformat()

    # daily data
    days = []
    d = start.date()
    stations = [e for e in events if e["type"]=="station"]
    ecl = [(k, j) for k, j, _ in ctx.eclipses()]

    # Moon aspects + void of course
    moon_aspects = []  # (jd, planet, aspect)
    ingress = []
    for i in range(1, len(hourly)):
        j0, r0 = hourly[i-1]; j1, r1 = hourly[i]
        if int(r0["Moon"]//30) != int(r1["Moon"]//30): ingress.append(j1)
        for p in ["Sun","Mercury","Venus","Mars","Jupiter","Saturn"]:
            for a in (0,60,90,120,180):
                for sgn in ((1,) if a in (0,180) else (1,-1)):
                    v0 = ((r0["Moon"]-r0[p]-sgn*a+180)%360)-180; v1 = ((r1["Moon"]-r1[p]-sgn*a+180)%360)-180
                    if v0 < 0 <= v1 and abs(v0) < 20:
                        moon_aspects.append((j0+(j1-j0)*abs(v0)/(abs(v0)+abs(v1)), p, ASPECTS[a]))
    voc = []
    for k in range(1, len(ingress)):
        a, b = ingress[k-1], ingress[k]
        asp = [m for m in moon_aspects if a < m[0] < b]
        if asp: voc.append((max(m[0] for m in asp), b))

    def overlap(x0, x1, y0, y1): return max(0, min(x1,y1) - max(x0,y0))
    elong = ctx.elong
    while d < end.date():
        base = dt.datetime(d.year, d.month, d.day, tzinfo=tz)
        b0, b1 = tojd(base.replace(hour=9)), tojd(base.replace(hour=17))
        dj0, dj1 = tojd(base), tojd(base + timedelta(days=1))
        noon = tojd(base.replace(hour=12))
        vh = sum(overlap(v0, v1, b0, b1) for v0, v1 in voc) * 24
        el = elong(noon); mh = house(lon("Moon", noon)); ms = sign(lon("Moon", noon))
        merc_rx = spd("Mercury", noon) < 0; ven_rx = spd("Venus", noon) < 0; mars_rx = spd("Mars", noon) < 0
        near_ecl = any(abs(e[1] - noon) < 1.0 for e in ecl)
        near_station = [s for s in stations if s["planet"] in ("Mercury","Venus") and abs(s["jd"] - noon) < 0.6]
        good_asp = [m for m in moon_aspects if dj0 <= m[0] < dj1 and m[1] in ("Venus","Jupiter") and m[2] in ("conjunct","sextile","trine")]
        hard_asp = [m for m in moon_aspects if b0 <= m[0] < b1 and m[1] in ("Saturn","Mars") and m[2] in ("square","opposite")]
        status, why = None, []
        if near_ecl: status, why = "caution", ["eclipse window"]
        elif near_station: status, why = "caution", [f"{near_station[0]['planet']} stations {near_station[0]['direction']}"]
        elif vh >= 5: status, why = "void", ["void Moon most of the business day"]
        elif el < 180 and not merc_rx and vh < 2 and (good_asp or mh in (2,10,11)):
            status = "green"
            why = [f"Moon {g[2]} {g[1]}" for g in good_asp[:1]] + ([f"Moon in your {mh}"] if mh in (2,10,11) else [])
        days.append(dict(date=d.isoformat(), elong=el, moon_house=mh, moon_sign=ms, status=status, why=why,
                         merc_rx=merc_rx, ven_rx=ven_rx, mars_rx=mars_rx, voc_hours=round(vh,1)))
        d += timedelta(days=1)

    find = ctx.find_phase
    lun = []
    for kind, t in (("New Moon",0),("Full Moon",180)):
        j = JD0
        while True:
            x = find(j, t)
            if x > JD1: break
            ml = lon("Moon", x)
            e = [k for k,ej in ecl if abs(ej-x) < 0.3]
            lun.append(dict(kind=kind, dt=fromjd(x).isoformat(), deg=fmt(ml), sign=sign(ml), house=house(ml),
                            eclipse=(("Solar" if kind=="New Moon" else "Lunar")+" Eclipse") if e else None,
                            opp_house=house((ml+180)%360)))
            j = x + 20
    lun.sort(key=lambda e: e["dt"])

    return dict(**ctx.window(), blueprint=blueprint, natal={k: fmt(v) for k, v in natal.items()}, prof=prof,
                events=[{k: v for k, v in e.items() if k != "jd"} for e in events], days=days, lunations=lun)
