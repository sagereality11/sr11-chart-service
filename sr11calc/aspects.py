"""Major aspects with configurable orbs.

Orbs are astrological choices, not astronomical facts. Every orb is
configurable from the WordPress settings page and sent to this service by the
WordPress server (never by the visitor's browser).

Orb model
---------
Each point belongs to one category: ``luminary`` (Sun, Moon), ``planet``
(Mercury through Pluto, and Chiron), ``node`` (North Node), ``angle``
(Ascendant, Midheaven) or ``extra`` (optional points: Black Moon Lilith,
Ceres, Pallas, Juno, Vesta, other asteroids, Parts of Fortune and Spirit,
Vertex). Each category has an orb per aspect type.

When two points of different categories meet, the orb used is the AVERAGE of
the two categories' orbs for that aspect type. Example with defaults: Sun
(luminary, conjunction 10°) conjunct Mars (planet, conjunction 7°) uses 8.5°.
This rule is symmetric and lets tight node/angle orbs pull a pair's orb down
without overriding the luminary allowance completely.

Points included in aspects: the ten planets, Chiron, the North Node, any
optional points chosen, and for timed charts the Ascendant and Midheaven. The
South Node, Anti-Vertex, Descendant and IC are excluded because every aspect to them mirrors an aspect to the North Node,
Ascendant or Midheaven and would only duplicate lines.

Applying / separating status is NOT calculated in this version, so it is never
labelled.
"""

from __future__ import annotations

from .zodiac import angular_separation

GOLDEN_ANGLE = 360.0 * (1.0 - 2.0 / (1.0 + 5.0 ** 0.5))   # 137.5078° = 360°/φ², the golden angle

ASPECTS = [
    {"id": "conjunction", "name": "Conjunction", "angle": 0.0},
    {"id": "sextile", "name": "Sextile", "angle": 60.0},
    {"id": "square", "name": "Square", "angle": 90.0},
    {"id": "trine", "name": "Trine", "angle": 120.0},
    {"id": "opposition", "name": "Opposition", "angle": 180.0},
]
# Optional aspects, only calculated when requested.
OPTIONAL_ASPECTS = {
    # Golden ratio aspect: the circle divided in the golden ratio. 360°/φ = 222.49°,
    # whose smaller separation is 137.51° (the "golden angle").
    "golden": {"id": "golden", "name": "Golden Ratio (137.5°)", "angle": GOLDEN_ANGLE},
}

DEFAULT_ORBS = {
    "luminary": {"conjunction": 10.0, "opposition": 10.0, "square": 8.0, "trine": 8.0, "sextile": 6.0, "golden": 2.0},
    "planet":   {"conjunction": 7.0,  "opposition": 7.0,  "square": 6.0, "trine": 6.0, "sextile": 4.0, "golden": 1.5},
    "node":     {"conjunction": 4.0,  "opposition": 4.0,  "square": 3.0, "trine": 3.0, "sextile": 2.0, "golden": 1.0},
    "angle":    {"conjunction": 6.0,  "opposition": 6.0,  "square": 5.0, "trine": 5.0, "sextile": 3.0, "golden": 1.0},
    # Optional points: Lilith, Ceres/Pallas/Juno/Vesta, other asteroids, Parts, Vertex.
    "extra":    {"conjunction": 3.0,  "opposition": 3.0,  "square": 2.0, "trine": 2.0, "sextile": 1.5, "golden": 1.0},
}

MAX_ORB = 15.0


def sanitize_orbs(raw) -> dict:
    """Merge a (possibly partial) orb table over the defaults, clamped 0..15."""
    out = {c: dict(v) for c, v in DEFAULT_ORBS.items()}
    if not isinstance(raw, dict):
        return out
    for cat, table in raw.items():
        if cat not in out or not isinstance(table, dict):
            continue
        for asp, val in table.items():
            if asp in out[cat]:
                try:
                    f = float(val)
                except (TypeError, ValueError):
                    continue
                if f == f:  # not NaN
                    out[cat][asp] = max(0.0, min(MAX_ORB, f))
    return out


def pair_orb(orbs: dict, cat_a: str, cat_b: str, aspect_id: str) -> float:
    return (orbs[cat_a][aspect_id] + orbs[cat_b][aspect_id]) / 2.0


def find_aspects(points: list[dict], orbs: dict, optional_types: list | None = None) -> list[dict]:
    """points: [{id, lon, category}]. Returns aspects sorted by tightness.

    Algorithm (as specified):
      1. absolute difference of longitudes
      2. normalize to [0, 360)
      3. smallest separation in [0, 180]
      4. |separation - exact aspect angle|
      5. keep if within the pair's orb
    If two aspect windows overlap (possible only with very wide orbs and the
    optional golden aspect, 17.5° from the trine), the tightest match wins.
    """
    found = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            p, q = points[i], points[j]
            sep = angular_separation(p["lon"], q["lon"])
            best = None
            for asp in ASPECTS + [OPTIONAL_ASPECTS[t] for t in (optional_types or []) if t in OPTIONAL_ASPECTS]:
                diff = abs(sep - asp["angle"])
                allowed = pair_orb(orbs, p["category"], q["category"], asp["id"])
                if diff <= allowed and (best is None or diff < best[1]):
                    best = (asp, diff, allowed)
            if best:
                asp, diff, allowed = best
                found.append({
                    "a": p["id"],
                    "b": q["id"],
                    "type": asp["id"],
                    "name": asp["name"],
                    "exact_angle": asp["angle"],
                    "separation": sep,
                    "orb": diff,
                    "allowed_orb": allowed,
                })
    found.sort(key=lambda x: x["orb"])
    return found
