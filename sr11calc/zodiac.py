"""Zodiac maths and display rounding.

Internal values keep full floating-point precision. Rounding happens only in
``split_longitude`` for display.

Display rounding convention (documented, tested):
    Longitudes are rounded to the nearest arc-minute, BUT the sign is always
    the sign of the unrounded longitude. A body at 29°59'45" Aries therefore
    displays as 29°59' Aries, not 0°00' Taurus. This is the same idea as the
    Swiss Ephemeris SE_SPLIT_DEG_KEEP_SIGN option and prevents a display that
    contradicts the body's real sign.
"""

from __future__ import annotations

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_IDS = [s.lower() for s in SIGNS]


def norm360(x: float) -> float:
    """Normalize an angle to [0, 360)."""
    v = x % 360.0
    # Guard against -0.0 and the float edge case where x % 360 == 360.0
    if v >= 360.0 or v < 0.0:
        v = 0.0
    return v + 0.0


def sign_index(lon: float) -> int:
    return int(norm360(lon) // 30.0)


def split_longitude(lon: float) -> dict:
    """Return sign / degree / minute for display, keeping the true sign."""
    lon = norm360(lon)
    sidx = int(lon // 30.0)
    within = lon - sidx * 30.0              # 0 <= within < 30
    total_min = round(within * 60.0)        # nearest arc-minute
    if total_min >= 30 * 60:                # would round into the next sign
        total_min = 30 * 60 - 1             # keep sign: show 29°59'
    deg, minute = divmod(total_min, 60)
    sec_exact = (within * 3600.0)
    return {
        "lon": lon,
        "sign_index": sidx,
        "sign": SIGNS[sidx],
        "sign_id": SIGN_IDS[sidx],
        "deg": int(deg),
        "min": int(minute),
        "within_sign": within,
        "display": f"{int(deg)}°{int(minute):02d}' {SIGNS[sidx]}",
        "seconds_in_sign": sec_exact,
    }


def angular_separation(a: float, b: float) -> float:
    """Smallest separation between two longitudes, in [0, 180]."""
    d = abs(a - b) % 360.0
    return 360.0 - d if d > 180.0 else d
