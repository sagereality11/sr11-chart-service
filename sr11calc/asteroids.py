"""Any numbered asteroid, by number or name.

Positions come from NASA/JPL Horizons (https://ssd.jpl.nasa.gov/api/horizons.api),
the reference source for minor-planet orbits. Swiss Ephemeris itself is built
from integrations of the same kind of orbital data; for Ceres at
2000-01-01 17:00 UT the two agree to 0.1 arc-second (see tests).

Settings sent to Horizons (documented, fixed):
  EPHEM_TYPE=OBSERVER, CENTER=500@399 (geocentre), TIME_TYPE=UT,
  QUANTITIES=31 (observer ecliptic longitude/latitude of date, apparent),
  ANG_FORMAT=DEG, EXTRA_PREC=YES.
Three instants are requested (birth time and ±12 hours) so longitudinal speed,
and therefore retrograde status, is measured rather than assumed.

What Horizons receives: only the asteroid number and the UTC instant. No name,
birthplace or other personal detail is sent. Nothing is cached or logged.

Numbers 1-4 (Ceres, Pallas, Juno, Vesta) and 2060 (Chiron) are answered from
the Swiss Ephemeris files instead, so they always match the main chart.

Name search uses the IAU Minor Planet Center list of named minor planets,
shipped with Swiss Ephemeris (asteroid_names.tsv).
"""

from __future__ import annotations

import json
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path

HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
TIMEOUT = 12
MAX_PER_CHART = 5
MAX_NUMBER = 2_000_000
SWISS_EQUIVALENT = {1: "ceres", 2: "pallas", 3: "juno", 4: "vesta", 2060: "chiron"}


class AsteroidError(RuntimeError):
    def __init__(self, number: int, message: str):
        super().__init__(message)
        self.number = number
        self.message = message


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).casefold().strip()


@lru_cache(maxsize=1)
def _names() -> tuple[dict, list]:
    by_number, rows = {}, []
    path = Path(__file__).with_name("asteroid_names.tsv")
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or "\t" not in line:
                continue
            n, name = line.rstrip("\n").split("\t", 1)
            n = int(n)
            by_number[n] = name
            rows.append((_fold(name), n, name))
    return by_number, rows


def name_of(number: int) -> str | None:
    return _names()[0].get(number)


def search(query: str, limit: int = 10) -> list[dict]:
    """Find asteroids by number ("1181") or name ("lilith", "eros")."""
    q = query.strip().lstrip("(").rstrip(")").strip()
    if not q:
        return []
    if q.isdigit():
        n = int(q)
        if 1 <= n <= MAX_NUMBER:
            nm = name_of(n)
            return [{"number": n, "name": nm, "label": f"{n} {nm}" if nm else f"Asteroid {n} (unnamed)"}]
        return []
    fq = _fold(q)
    if len(fq) < 2:
        return []
    _, rows = _names()
    exact = [r for r in rows if r[0] == fq]
    prefix = [r for r in rows if r[0].startswith(fq) and r[0] != fq]
    hits = sorted(exact, key=lambda r: r[1]) + sorted(prefix, key=lambda r: r[1])
    return [{"number": n, "name": name, "label": f"{n} {name}"} for _, n, name in hits[:limit]]


def short_label(number: int) -> str:
    """Up to 6 characters for the wheel: the name, or the number if unnamed."""
    nm = name_of(number)
    return (nm[:6] if nm else str(number))


def _query(number: int, jds: list[float]) -> tuple[list[tuple[float, float]], str]:
    params = {
        "format": "json",
        "COMMAND": f"'{number};'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'OBSERVER'",
        "CENTER": "'500@399'",
        "TLIST": "'" + " ".join(f"{j:.9f}" for j in jds) + "'",
        "TLIST_TYPE": "'JD'",
        "TIME_TYPE": "'UT'",
        "QUANTITIES": "'31'",
        "ANG_FORMAT": "'DEG'",
        "EXTRA_PREC": "'YES'",
        "CSV_FORMAT": "'NO'",
    }
    url = HORIZONS_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "SR11-chart-service/0.2 (sagereality11.com)"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            payload = json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise AsteroidError(number, "The asteroid service (NASA/JPL Horizons) could not be reached. Please try again later.") from e
    text = payload.get("result", "")
    if "$$SOE" not in text:
        if "No matches found" in text or "no such" in text.lower():
            raise AsteroidError(number, f"Asteroid {number} was not found in the JPL Horizons database.")
        raise AsteroidError(number, f"JPL Horizons could not calculate asteroid {number} for this date.")
    body = text.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    rows = []
    for line in body.strip().splitlines():
        nums = []
        for tok in line.split():
            try:
                nums.append(float(tok))
            except ValueError:
                pass
        if len(nums) >= 2:
            rows.append((nums[-2], nums[-1]))
    if len(rows) != len(jds):
        raise AsteroidError(number, f"JPL Horizons returned an incomplete answer for asteroid {number}.")
    source = ""
    for line in text.splitlines():
        if "Target body name" in line:
            source = " ".join(line.split(":", 1)[1].split())
            break
    return rows, source


def positions(numbers: list[int], jd_ut: float) -> tuple[list[dict], list[dict]]:
    """Return (points, omitted) for asteroid numbers not covered by Swiss
    Ephemeris. Each point: id, name, label, lon, lat, speed (deg/day)."""
    numbers = [n for n in dict.fromkeys(numbers) if n not in SWISS_EQUIVALENT][:MAX_PER_CHART]
    jds = [jd_ut - 0.5, jd_ut, jd_ut + 0.5]

    def one(n):
        try:
            rows, source = _query(n, jds)
        except AsteroidError as e:
            return None, {"id": f"ast_{n}", "name": f"Asteroid {n}", "reason": e.message}
        (l0, _), (lon, lat), (l2, _) = rows
        speed = ((l2 - l0 + 540.0) % 360.0) - 180.0      # degrees per day, wrap-safe
        nm = name_of(n)
        return {"id": f"ast_{n}", "number": n, "name": f"{n} {nm}" if nm else f"Asteroid {n}",
                "label": short_label(n), "lon": lon, "lat": lat, "speed": speed,
                "source": f"JPL Horizons: {source}" if source else "JPL Horizons"}, None

    pts, omitted = [], []
    if not numbers:
        return pts, omitted
    with ThreadPoolExecutor(max_workers=min(5, len(numbers))) as ex:
        for p, o in ex.map(one, numbers):
            (pts if p else omitted).append(p or o)
    return pts, omitted
