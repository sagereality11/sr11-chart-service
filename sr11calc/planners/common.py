"""Shared setup for the personalized planners (Moon Cycles, Money & Business, Transits).

A planner covers twelve full calendar months starting on the 1st of the month the buyer
chooses. Natal positions come from the regular chart pipeline (Placidus, True Node); dates
and times are shown in the time zone of the buyer's current city.
"""

from __future__ import annotations

import datetime as dt
from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from .. import engine

FL = swe.FLG_SWIEPH | swe.FLG_SPEED
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
         "Capricorn", "Aquarius", "Pisces"]
RULER = dict(Aries="Mars", Taurus="Venus", Gemini="Mercury", Cancer="Moon", Leo="Sun", Virgo="Mercury",
             Libra="Venus", Scorpio="Mars", Sagittarius="Jupiter", Capricorn="Saturn", Aquarius="Saturn",
             Pisces="Jupiter")
PIDS = dict(Sun=swe.SUN, Moon=swe.MOON, Mercury=swe.MERCURY, Venus=swe.VENUS, Mars=swe.MARS,
            Jupiter=swe.JUPITER, Saturn=swe.SATURN, Uranus=swe.URANUS, Neptune=swe.NEPTUNE, Pluto=swe.PLUTO)
PLANETS = list(PIDS)

US_ZONES = {
    "America/New_York": "Eastern Time", "America/Detroit": "Eastern Time", "America/Indiana/Indianapolis": "Eastern Time",
    "America/Kentucky/Louisville": "Eastern Time", "America/Chicago": "Central Time", "America/Indiana/Knox": "Central Time",
    "America/Denver": "Mountain Time", "America/Boise": "Mountain Time", "America/Phoenix": "Arizona Time",
    "America/Los_Angeles": "Pacific Time", "America/Anchorage": "Alaska Time", "Pacific/Honolulu": "Hawaii Time",
    "America/Toronto": "Eastern Time", "America/Vancouver": "Pacific Time", "Europe/London": "UK time",
}


def fmt(lon: float) -> str:
    s = int(lon // 30) % 12
    d = lon % 30
    m = int(round((d % 1) * 60))
    deg = int(d)
    if m == 60:
        deg, m = deg + 1, 0
    return f"{deg}°{m:02d}' {SIGNS[s]}"


def sign(lon: float) -> str:
    return SIGNS[int(lon // 30) % 12]


def tz_label(tz_name: str, city_label: str = "") -> str:
    if tz_name in US_ZONES:
        return US_ZONES[tz_name]
    city = (city_label or "").split(",")[0].strip()
    return f"{city} time" if city else "local time"


class Ctx:
    """Everything a planner calculation needs about the buyer and the twelve months."""

    def __init__(self, chart: dict, birth_date: dt.date, tz_name: str, start_year: int, start_month: int):
        engine._require_ephemeris()
        self.birth = birth_date
        self.tz = ZoneInfo(tz_name)
        self.natal = {}
        for b in chart["bodies"]:
            if b["name"] in PIDS:
                self.natal[b["name"]] = b["lon"]
            elif b.get("id") in ("true_node", "north_node", "node") or b["name"] in ("North Node", "True Node"):
                self.natal["North Node"] = b["lon"]
        ang = chart["houses"]["angles"]
        self.natal["Ascendant"] = ang["asc"]["lon"]
        self.natal["Midheaven"] = ang["mc"]["lon"]
        self.natal["Descendant"] = ang["dsc"]["lon"]
        self.natal["IC"] = ang["ic"]["lon"]
        self.cusps = [c["lon"] for c in chart["houses"]["cusps"]]
        self.asc_sign = int(self.natal["Ascendant"] // 30)
        self.start = dt.datetime(start_year, start_month, 1, tzinfo=self.tz)
        ey, em = start_year + (start_month + 11) // 12, (start_month + 11) % 12 + 1
        self.end = dt.datetime(ey, em, 1, tzinfo=self.tz)
        self.J0, self.J1 = self.tojd(self.start), self.tojd(self.end)

    def house(self, lon: float) -> int:
        c = self.cusps
        for i in range(12):
            a, b = c[i], c[(i + 1) % 12]
            if (lon - a) % 360 < (b - a) % 360:
                return i + 1
        return 12

    def tojd(self, d: dt.datetime) -> float:
        u = d.astimezone(timezone.utc)
        return swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60 + u.second / 3600)

    def fromjd(self, jd: float) -> dt.datetime:
        y, m, d, h = swe.revjul(jd)
        return (dt.datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=h)).astimezone(self.tz)

    def pos(self, p: str, jd: float):
        r = swe.calc_ut(jd, PIDS[p], FL)[0]
        return r[0], r[3]

    def lon(self, p: str, jd: float) -> float:
        return swe.calc_ut(jd, PIDS[p], FL)[0][0]

    def elong(self, jd: float) -> float:
        return (self.lon("Moon", jd) - self.lon("Sun", jd)) % 360

    def find_phase(self, jd0: float, target: float) -> float:
        f = lambda j: ((self.elong(j) - target + 180) % 360) - 180
        j = jd0
        while not (f(j) < 0 <= f(j + 0.5)):
            j += 0.5
        lo, hi = j, j + 0.5
        for _ in range(40):
            mid = (lo + hi) / 2
            if f(mid) < 0:
                lo = mid
            else:
                hi = mid
        return lo

    def eclipses(self):
        """[(kind 'solar'|'lunar', jd, type)] within the window."""
        out = []
        j = self.J0 - 1
        while True:
            r = swe.sol_eclipse_when_glob(j, swe.FLG_SWIEPH)
            if r[1][0] > self.J1:
                break
            t = r[0]
            typ = ("Total" if t & swe.ECL_TOTAL else "Annular" if t & swe.ECL_ANNULAR
                   else "Hybrid" if t & swe.ECL_ANNULAR_TOTAL else "Partial")
            out.append(("solar", r[1][0], typ))
            j = r[1][0] + 1
        j = self.J0 - 1
        while True:
            r = swe.lun_eclipse_when(j, swe.FLG_SWIEPH)
            if r[1][0] > self.J1:
                break
            t = r[0]
            typ = "Total" if t & swe.ECL_TOTAL else "Partial" if t & swe.ECL_PARTIAL else "Penumbral"
            out.append(("lunar", r[1][0], typ))
            j = r[1][0] + 1
        return out

    def profections(self):
        out = []
        sy = self.start.year
        for yr in (sy - 1, sy, sy + 1):
            try:
                b = dt.datetime(yr, self.birth.month, self.birth.day, tzinfo=self.tz)
                nx = dt.datetime(yr + 1, self.birth.month, self.birth.day, tzinfo=self.tz)
            except ValueError:  # Feb 29 birthdays
                b = dt.datetime(yr, 3, 1, tzinfo=self.tz)
                nx = dt.datetime(yr + 1, 3, 1, tzinfo=self.tz)
            if nx <= self.start or b >= self.end:
                continue
            age = yr - self.birth.year
            h = age % 12 + 1
            sg = SIGNS[(self.asc_sign + h - 1) % 12]
            lord = RULER[sg]
            out.append(dict(age=age, house=h, sign=sg, lord=lord, lord_sign=sign(self.natal[lord]),
                            lord_house=self.house(self.natal[lord]), frm=max(b, self.start).date().isoformat(),
                            to=(min(nx, self.end) - timedelta(days=1)).date().isoformat(),
                            bday=b.date().isoformat()))
        return out

    def window(self) -> dict:
        return dict(start=self.start.date().isoformat(), end=(self.end.date() - timedelta(days=1)).isoformat())
