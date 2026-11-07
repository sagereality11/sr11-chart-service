"""Moon Cycles Planner data: every New and Full Moon, eclipse, quarter Moon and daily phase."""

from __future__ import annotations

import datetime as dt
from datetime import timedelta

from .common import Ctx, fmt, sign

CONTACT_POINTS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
                  "North Node", "Ascendant", "Midheaven", "Descendant", "IC"]


def _d(a, b):
    return abs(((a - b + 180) % 360) - 180)


def compute(ctx: Ctx) -> dict:
    natal = {k: ctx.natal[k] for k in CONTACT_POINTS if k in ctx.natal}
    ecl = ctx.eclipses()
    events = []
    for kind, target in (("New Moon", 0), ("Full Moon", 180)):
        j = ctx.J0
        while True:
            t = ctx.find_phase(j, target)
            if t > ctx.J1:
                break
            mlon = ctx.lon("Moon", t)
            slon = ctx.lon("Sun", t)
            e = [x for x in ecl if abs(x[1] - t) < 0.3 and ((x[0] == "solar") == (kind == "New Moon"))]
            contacts = [(k, "conjunct", round(_d(mlon, v), 1)) for k, v in natal.items() if _d(mlon, v) <= 3]
            axis = []
            if e:
                for k, v in natal.items():
                    o = min(_d(mlon, v), 180 - _d(mlon, v))
                    if o <= 8:
                        axis.append((k, "on" if _d(mlon, v) <= 90 else "opposite", round(o, 1)))
                axis.sort(key=lambda a: a[2])
            events.append(dict(
                kind=kind, dt=ctx.fromjd(t).isoformat(), deg=fmt(mlon), sign=sign(mlon), house=ctx.house(mlon),
                sun_deg=fmt(slon), sun_house=ctx.house(slon),
                eclipse=(e[0][2] + (" Solar" if kind == "New Moon" else " Lunar") + " Eclipse") if e else None,
                contacts=contacts, opp_house=ctx.house((mlon + 180) % 360), opp_sign=sign((mlon + 180) % 360),
                axis=axis))
            j = t + 20
    events.sort(key=lambda x: x["dt"])

    quarters = []
    for kind, target in (("First Quarter", 90), ("Last Quarter", 270)):
        j = ctx.J0
        while True:
            t = ctx.find_phase(j, target)
            if t > ctx.J1:
                break
            mlon = ctx.lon("Moon", t)
            quarters.append(dict(kind=kind, dt=ctx.fromjd(t).isoformat(), deg=fmt(mlon), sign=sign(mlon),
                                 house=ctx.house(mlon)))
            j = t + 20
    quarters.sort(key=lambda x: x["dt"])

    days = []
    d = ctx.start.date()
    while d < ctx.end.date():
        jj = ctx.tojd(dt.datetime(d.year, d.month, d.day, 12, tzinfo=ctx.tz))
        mlon = ctx.lon("Moon", jj)
        days.append(dict(date=d.isoformat(), elong=ctx.elong(jj), sign=sign(mlon), house=ctx.house(mlon)))
        d += timedelta(days=1)

    return dict(**ctx.window(), events=events, quarters=quarters, days=days,
                natal={k: fmt(v) for k, v in natal.items()})
