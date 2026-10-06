"""Local civil time -> UTC, using the IANA time zone database (tzdb).

Python's ``zoneinfo`` applies the full historical tzdb rules (standard time
changes and daylight saving time) for the given zone and date, so a 1955 birth
in Chicago uses 1955 rules, not today's offset.

Outcomes of ``resolve_local_time``:

* ``ok``            exactly one valid UTC instant
* ``ambiguous``     the wall time happened twice (clocks went back). The caller
                    must re-submit with ``fold`` 0 (earlier, first occurrence)
                    or 1 (later, second occurrence).
* ``nonexistent``   the wall time was skipped (clocks went forward). The
                    visitor must correct the time; we never shift it silently.
* ``needs_confirmation``  the tzdb only has Local Mean Time (LMT) for this
                    place and date — i.e. no standardized zone existed or no
                    record is available. The visitor must either accept the
                    LMT value tzdb provides or enter a manual UTC offset.

Reliability notes are attached for dates before 1970; the tzdb maintainers
document that pre-1970 data is less reliable than modern data.

Calendar: dates are interpreted as Gregorian (proleptic), which is what
nearly all modern birth records use. Births recorded in the Julian calendar
(e.g. Russia before 1918) must be converted by the visitor first.
"""

from __future__ import annotations

import datetime as dt
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

MIN_DATE = dt.date(1800, 1, 1)
MAX_DATE = dt.date(2399, 12, 31)
RELIABLE_TZ_FROM = 1970


class TimeInputError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@lru_cache(maxsize=1)
def tzdb_version() -> str:
    """Best-effort tzdb release identifier (e.g. '2026c')."""
    candidates = []
    try:  # the 'tzdata' PyPI package, if installed and used
        import tzdata  # type: ignore
        candidates.append(Path(tzdata.__file__).parent / "zoneinfo" / "tzdata.zi")
        ver = getattr(tzdata, "IANA_VERSION", None)
        if ver:
            return str(ver)
    except Exception:
        pass
    candidates.append(Path("/usr/share/zoneinfo/tzdata.zi"))
    for p in candidates:
        try:
            first = p.read_text(encoding="utf-8").splitlines()[0]
            if first.startswith("# version"):
                return first.split()[-1]
        except Exception:
            continue
    return "unknown"


@lru_cache(maxsize=1)
def timezone_list() -> list[str]:
    zones = sorted(
        z for z in available_timezones()
        if "/" in z and not z.startswith(("Etc/", "SystemV/", "posix/", "right/"))
    )
    return zones


def _fmt_offset(td: dt.timedelta) -> str:
    total = int(td.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    out = f"UTC{sign}{h:02d}:{m:02d}"
    if s:
        out += f":{s:02d}"
    return out


def validate_date(year: int, month: int, day: int) -> dt.date:
    try:
        d = dt.date(year, month, day)
    except ValueError:
        raise TimeInputError("invalid_date", "That date does not exist. Please check the day, month and year.")
    if d < MIN_DATE or d > MAX_DATE:
        raise TimeInputError(
            "unsupported_date",
            f"Supported birth dates are {MIN_DATE.isoformat()} through {MAX_DATE.isoformat()} "
            "(the range covered by the installed Swiss Ephemeris files).",
        )
    return d


def _describe(local: dt.datetime, utc: dt.datetime, zone_label: str, source: str) -> dict:
    off = local.utcoffset()
    dst = local.dst()
    return {
        "local_iso": local.replace(tzinfo=None).isoformat(timespec="seconds"),
        "utc_iso": utc.replace(tzinfo=None).isoformat(timespec="seconds") + "Z",
        "utc_date_differs": utc.date() != local.date(),
        "utc_offset_seconds": int(off.total_seconds()),
        "utc_offset": _fmt_offset(off),
        "dst_active": bool(dst and dst.total_seconds() != 0) if dst is not None else None,
        "tz_abbrev": local.tzname(),
        "zone": zone_label,
        "source": source,
    }


def resolve_local_time(
    date: dt.date,
    time: dt.time,
    tz_name: str | None = None,
    utc_offset_minutes: int | None = None,
    fold: int | None = None,
    accept_lmt: bool = False,
) -> dict:
    """Convert a local wall-clock birth time to UTC. See module docstring."""
    naive = dt.datetime.combine(date, time)
    notes: list[str] = []

    if utc_offset_minutes is not None:
        if not -16 * 60 <= utc_offset_minutes <= 16 * 60:
            raise TimeInputError("invalid_offset", "UTC offset must be between -16:00 and +16:00.")
        tz = dt.timezone(dt.timedelta(minutes=utc_offset_minutes))
        local = naive.replace(tzinfo=tz)
        utc = local.astimezone(dt.timezone.utc)
        res = _describe(local, utc, _fmt_offset(tz.utcoffset(None)), "manual UTC offset entered by visitor")
        res["dst_active"] = None
        notes.append("A manual UTC offset was used. Daylight saving time is NOT applied automatically; "
                     "the offset you entered must already include it.")
        return {"status": "ok", "time": res, "notes": notes, "reliability": "manual"}

    if not tz_name:
        raise TimeInputError("missing_timezone", "A time zone is required.")
    try:
        zone = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError):
        raise TimeInputError("invalid_timezone", "Unknown time zone identifier.")

    a = naive.replace(tzinfo=zone, fold=0)
    b = naive.replace(tzinfo=zone, fold=1)

    def roundtrips(x: dt.datetime) -> bool:
        back = x.astimezone(dt.timezone.utc).astimezone(zone)
        return back.replace(tzinfo=None) == naive

    ok_a, ok_b = roundtrips(a), roundtrips(b)
    source = f"IANA tzdb {tzdb_version()} ({tz_name})"

    if not ok_a and not ok_b:
        before = a.utcoffset()
        after = b.utcoffset()
        return {
            "status": "nonexistent",
            "message": (
                f"{naive.strftime('%H:%M')} on {date.isoformat()} did not exist in {tz_name}: "
                f"clocks jumped forward (from {_fmt_offset(before)} to {_fmt_offset(after)}) and skipped this time. "
                "Please double-check the birth time on the birth record."
            ),
            "zone": tz_name,
        }

    if ok_a and ok_b and a.utcoffset() != b.utcoffset():
        if fold not in (0, 1):
            opts = []
            for f, x in ((0, a), (1, b)):
                u = x.astimezone(dt.timezone.utc)
                opts.append({
                    "fold": f,
                    "label": ("First occurrence" if f == 0 else "Second occurrence")
                             + f" ({x.tzname()}, {_fmt_offset(x.utcoffset())})",
                    "utc_iso": u.replace(tzinfo=None).isoformat(timespec="seconds") + "Z",
                    "tz_abbrev": x.tzname(),
                    "utc_offset": _fmt_offset(x.utcoffset()),
                })
            return {
                "status": "ambiguous",
                "message": (
                    f"{naive.strftime('%H:%M')} on {date.isoformat()} happened twice in {tz_name} because clocks "
                    "were set back. Please choose which one matches the birth record."
                ),
                "options": opts,
                "zone": tz_name,
            }
        chosen = a if fold == 0 else b
        notes.append(f"Ambiguous local time resolved by visitor choice: {'first' if fold == 0 else 'second'} occurrence.")
    else:
        chosen = a if ok_a else b

    utc = chosen.astimezone(dt.timezone.utc)
    res = _describe(chosen, utc, tz_name, source)

    reliability = "normal"
    if (chosen.tzname() or "").upper() == "LMT":
        if not accept_lmt:
            return {
                "status": "needs_confirmation",
                "code": "lmt",
                "message": (
                    f"The time zone database has no standard time zone for {tz_name} on {date.isoformat()}; "
                    f"it only provides Local Mean Time ({_fmt_offset(chosen.utcoffset())}). "
                    "Use this Local Mean Time value, or enter the UTC offset recorded for the birth."
                ),
                "lmt_offset": _fmt_offset(chosen.utcoffset()),
                "zone": tz_name,
            }
        reliability = "lmt"
        notes.append("Local Mean Time (LMT) from the tzdb was used at the visitor's request.")
    elif date.year < RELIABLE_TZ_FROM:
        reliability = "pre1970"
        notes.append(
            "This birth is before 1970. The tzdb records historical clock changes, but its maintainers note "
            "that pre-1970 data can be less reliable, especially outside major cities. If the birth record "
            "states a different time zone or 'war time', use the manual UTC offset option."
        )
    return {"status": "ok", "time": res, "notes": notes, "reliability": reliability}
