#!/usr/bin/env python3
"""Builds small_places.sqlite: every GeoNames populated place (feature class P)
that is NOT already in cities500.txt, so tiny towns like Adak, Alaska
(population ~330) can still be found as birthplaces.

The big-city index stays in memory (fast, ranked); this file is read from
disk with SQLite, so the extra ~4 million places cost almost no RAM.

Usage: build_small_places.py DATA_DIR
  reads  DATA_DIR/allCountries.zip, cities500.txt, admin1CodesASCII.txt, countryInfo.txt
  writes DATA_DIR/small_places.sqlite
"""

from __future__ import annotations

import io
import os
import sqlite3
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sr11calc.places import _fold  # noqa: E402  (same folding as the search)

# Feature codes left out: sections of a bigger city (neighbourhoods), and
# abandoned or destroyed places.
SKIP_CODES = {"PPLX", "PPLQ", "PPLW"}


def main(data_dir: str) -> None:
    d = Path(data_dir)
    countries = {}
    with open(d / "countryInfo.txt", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            c = line.rstrip("\n").split("\t")
            countries[c[0]] = c[4]
    admin1 = {}
    with open(d / "admin1CodesASCII.txt", encoding="utf-8") as f:
        for line in f:
            c = line.rstrip("\n").split("\t")
            if len(c) >= 2:
                admin1[c[0]] = c[1]
    big = set()
    for name in ("cities500.txt", "cities1000.txt"):
        p = d / name
        if p.exists():
            with open(p, encoding="utf-8") as f:
                for line in f:
                    big.add(line.split("\t", 1)[0])
            break

    out = d / "small_places.sqlite"
    tmp = d / "small_places.sqlite.tmp"
    if tmp.exists():
        tmp.unlink()
    db = sqlite3.connect(tmp)
    db.executescript(
        """
        PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;
        CREATE TABLE place(id INTEGER PRIMARY KEY, name TEXT, admin1_code TEXT, admin2_code TEXT,
                           cc TEXT, lat REAL, lon REAL, tz TEXT, pop INTEGER);
        CREATE TABLE pkey(k TEXT, region TEXT, pop INTEGER, id INTEGER);
        """
    )
    n = 0
    rows, keys = [], []
    with zipfile.ZipFile(d / "allCountries.zip") as z:
        with z.open("allCountries.txt") as raw:
            for line in io.TextIOWrapper(raw, encoding="utf-8"):
                c = line.rstrip("\n").split("\t")
                if len(c) < 18 or c[6] != "P" or c[7] in SKIP_CODES or not c[17] or c[0] in big:
                    continue
                gid, cc = int(c[0]), c[8]
                pop = int(c[14] or 0)
                region = f"{cc}.{c[10]}"
                rows.append((gid, c[1], c[10], c[11], cc, float(c[4]), float(c[5]), c[17], pop))
                for k in {_fold(c[1]), _fold(c[2])}:
                    if len(k) >= 2:
                        keys.append((k, region, pop, gid))
                n += 1
                if len(rows) >= 50000:
                    db.executemany("INSERT INTO place VALUES (?,?,?,?,?,?,?,?,?)", rows)
                    db.executemany("INSERT INTO pkey VALUES (?,?,?,?)", keys)
                    rows, keys = [], []
    db.executemany("INSERT INTO place VALUES (?,?,?,?,?,?,?,?,?)", rows)
    db.executemany("INSERT INTO pkey VALUES (?,?,?,?)", keys)
    # Indexes are built once at the end (a sort), far faster than keeping
    # them up to date during millions of inserts.
    # Covering index: a search is answered from the index alone, and only
    # the 60 best matches are then looked up in the place table.
    db.execute("CREATE INDEX pkey_k ON pkey(k, region, pop, id)")
    db.commit()
    db.close()
    os.replace(tmp, out)
    print(f"small_places.sqlite: {n} extra populated places")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/geonames")
