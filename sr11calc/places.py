"""Offline birthplace search using GeoNames data.

Data files (downloaded once at deploy time by scripts/fetch_geonames.sh,
GeoNames data is CC BY 4.0 — attribution is shown under the form):

  cities1000.txt        every populated place with population >= 1,000
                        (about 150,000 places) incl. lat, lon and IANA zone
  admin1CodesASCII.txt  state / province / region names
  countryInfo.txt       country names

Nothing is sent to a third party while a visitor types: searches run against
this local copy. Smaller villages may be missing; the form's manual-location
option covers them.
"""

from __future__ import annotations

import os
import unicodedata
from pathlib import Path

DATA_DIR = Path(os.environ.get("SR11_GEONAMES_DIR", str(Path(__file__).resolve().parent.parent / "data" / "geonames")))
MAX_RESULTS = 10


# Common abbreviations are expanded on both sides, so "St. Louis", "St Louis"
# and "Saint Louis" all match, as do "Mt Pleasant" and "Mount Pleasant".
_ABBREV = {"st": "saint", "ste": "sainte", "mt": "mount", "ft": "fort", "pt": "point"}


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    words = s.casefold().replace("-", " ").replace("'", "").replace(".", " ").split()
    return " ".join(_ABBREV.get(w, w) for w in words)


class PlaceIndex:
    def __init__(self, data_dir: Path | str = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.places: dict[int, dict] = {}
        self.by_prefix: dict[str, list[int]] = {}
        self.loaded = False
        self.error = None
        try:
            self._load()
            self.loaded = True
        except FileNotFoundError as e:
            self.error = f"GeoNames data not found: {e.filename}"

    def _load(self):
        countries = {}
        with open(self.data_dir / "countryInfo.txt", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue
                c = line.rstrip("\n").split("\t")
                countries[c[0]] = c[4]
        admin1 = {}
        with open(self.data_dir / "admin1CodesASCII.txt", encoding="utf-8") as f:
            for line in f:
                c = line.rstrip("\n").split("\t")
                if len(c) >= 2:
                    admin1[c[0]] = c[1]
        with open(self.data_dir / "cities1000.txt", encoding="utf-8") as f:
            for line in f:
                c = line.rstrip("\n").split("\t")
                if len(c) < 18 or not c[17]:
                    continue
                gid = int(c[0])
                cc = c[8]
                p = {
                    "id": gid,
                    "name": c[1],
                    "admin1": admin1.get(f"{cc}.{c[10]}", ""),
                    "country": countries.get(cc, cc),
                    "country_code": cc,
                    "lat": float(c[4]),
                    "lon": float(c[5]),
                    "tz": c[17],
                    "population": int(c[14] or 0),
                }
                p["_keys"] = {_fold(c[1]), _fold(c[2])}
                p["_ctx"] = _fold(" ".join([p["admin1"], p["country"], cc, c[10] if cc == "US" else ""]))
                self.places[gid] = p
                for k in p["_keys"]:
                    if len(k) >= 2:
                        self.by_prefix.setdefault(k[:2], []).append(gid)
        for lst in self.by_prefix.values():
            lst.sort(key=lambda g: -self.places[g]["population"])

    @staticmethod
    def public(p: dict) -> dict:
        out = {k: v for k, v in p.items() if not k.startswith("_")}
        parts = [p["name"]] + ([p["admin1"]] if p["admin1"] else []) + [p["country"]]
        out["label"] = ", ".join(parts)
        return out

    def get(self, gid: int) -> dict | None:
        p = self.places.get(gid)
        return self.public(p) if p else None

    def _find(self, city: str, ctx: list[str]) -> list[dict]:
        """Places whose name starts with ``city`` and whose region/country
        words start with every ``ctx`` token (so "ky" matches Kentucky's
        code, "neb" matches Nebraska, "united" matches United States)."""
        out = []
        for gid in self.by_prefix.get(city[:2], []):
            p = self.places[gid]
            if not any(k.startswith(city) for k in p["_keys"]):
                continue
            if ctx:
                words = p["_ctx"].split()
                if not all(any(w.startswith(t) for w in words) for t in ctx):
                    continue
            out.append(p)
            if len(out) >= 60:
                break
        return out

    def search(self, query: str, limit: int = MAX_RESULTS) -> list[dict]:
        """Accepts "Papillion", "Papillion, Nebraska", "Papillion Nebraska",
        "Lebanon KY" or "Paris, Texas, United States".

        With commas, the first part is the place name and the rest narrows
        it down. Without commas, the longest leading run of words that matches
        a place name is the name and any remaining words narrow it down, so
        multi-word names like "Saint Louis Missouri" also work."""
        if not self.loaded:
            return []
        q = query.strip()
        if "," in q:
            parts = [_fold(x) for x in q.split(",")]
            attempts = [(parts[0], " ".join(x for x in parts[1:] if x).split())]
        else:
            words = _fold(q).split()
            attempts = [(" ".join(words[:k]), words[k:]) for k in range(len(words), 0, -1)]
        for city, ctx in attempts:
            if len(city) < 2:
                continue
            out = self._find(city, ctx)
            if out:
                # Exact name matches first, then population.
                out.sort(key=lambda p: (city not in p["_keys"], -p["population"]))
                return [self.public(p) for p in out[:limit]]
        return []
