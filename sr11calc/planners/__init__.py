"""Personalized twelve-month planners: Moon Cycles, Money & Business, and Transits."""

from __future__ import annotations

import datetime as dt
import threading

from . import common, moon_calc, money_calc, transit_calc, render_moon, render_money, render_transits

PRODUCTS = {
    "moon": (moon_calc.compute, render_moon.render, "Moon-Cycles-Planner"),
    "money": (money_calc.compute, render_money.render, "Money-Business-Planner"),
    "transits": (transit_calc.compute, render_transits.render, "Transits-Planner"),
}
_render_lock = threading.Lock()  # ReportLab font caches are shared; draw one planner at a time


def build(product: str, chart: dict, birth_date: dt.date, tz_name: str, city_label: str,
          start_year: int, start_month: int, name: str, with_calendar: bool = False) -> dict:
    """Returns {"pdf", "filename"} and, with with_calendar, {"ics", "ics_filename"}."""
    from . import ics
    compute, render, stem = PRODUCTS[product]
    ctx = common.Ctx(chart, birth_date, tz_name, start_year, start_month)
    data = compute(ctx)
    tzl = common.tz_label(tz_name, city_label)
    with _render_lock:
        pdf = render(data, name, tzl)
    safe = "".join(ch for ch in name if ch.isalnum() or ch in "-_")[:40]
    base = f"{stem}-{safe}" if safe and name != "Friend" else stem
    out = {"pdf": pdf, "filename": base + ".pdf"}
    if with_calendar:
        out["ics"] = ics.BUILDERS[product](data, name, tzl)
        out["ics_filename"] = base.replace("Planner", "Calendar") + ".ics"
    return out
