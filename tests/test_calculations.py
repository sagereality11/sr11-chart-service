"""Reproducible calculation tests (no rendering involved).

Run:  python -m unittest discover -s tests -v
Uses the small GeoNames fixture in tests/fixtures/geonames.
All birth data below is SAMPLE data chosen to exercise edge cases.
"""

import datetime as dt
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("SR11_GEONAMES_DIR", str(HERE / "fixtures" / "geonames"))
os.environ.setdefault("SR11_API_KEY", "test-key-not-secret")
sys.path.insert(0, str(HERE.parent))

import swisseph as swe  # noqa: E402

from sr11calc import engine, timeconv  # noqa: E402
from sr11calc.aspects import DEFAULT_ORBS, find_aspects  # noqa: E402
from sr11calc.places import PlaceIndex  # noqa: E402
from sr11calc.service import InputError, build_chart, parse_request  # noqa: E402
from sr11calc.zodiac import split_longitude  # noqa: E402

PLACES = PlaceIndex()
NYC, LONDON, SYDNEY, TROMSO, DELHI, LONGYEARBYEN = 5128581, 2643743, 2147714, 3133895, 1261481, 2729907


def chart(y, m, d, hh=None, mm=None, place=NYC, hsys="P", **extra):
    body = {"year": y, "month": m, "day": d, "location": {"mode": "place", "place_id": place},
            "house_system": hsys}
    if hh is None:
        body["time_known"] = False
    else:
        body.update(hour=hh, minute=mm)
    body.update(extra)
    return build_chart(parse_request(body, PLACES))


def ang_diff(a, b):
    return abs(((a - b + 180) % 360) - 180)


class HouseSystems(unittest.TestCase):
    def test_house_system_change_keeps_positions_and_angles(self):
        base = chart(1990, 5, 17, 14, 30, hsys="P")
        for code in engine.HOUSE_SYSTEMS:
            other = chart(1990, 5, 17, 14, 30, hsys=code)
            self.assertEqual(other["status"], "ok", code)
            for b0, b1 in zip(base["bodies"], other["bodies"]):
                self.assertEqual(b0["lon"], b1["lon"], f"{code} {b0['id']}")
            for k in ("asc", "mc", "dsc", "ic"):
                self.assertEqual(base["houses"]["angles"][k]["lon"], other["houses"]["angles"][k]["lon"], code)

    def test_whole_sign_cusps_start_at_zero_of_asc_sign(self):
        c = chart(1990, 5, 17, 14, 30, hsys="W")
        asc_sign = int(c["houses"]["angles"]["asc"]["lon"] // 30)
        for i, cusp in enumerate(c["houses"]["cusps"]):
            self.assertAlmostEqual(cusp["lon"], ((asc_sign + i) % 12) * 30.0, places=9)
        # The real Ascendant is kept distinct from the 1st cusp label.
        self.assertNotAlmostEqual(c["houses"]["angles"]["asc"]["lon"], c["houses"]["cusps"][0]["lon"], places=3)

    def test_equal_cusps_start_at_exact_ascendant(self):
        c = chart(1990, 5, 17, 14, 30, hsys="E")
        asc = c["houses"]["angles"]["asc"]["lon"]
        for i, cusp in enumerate(c["houses"]["cusps"]):
            self.assertLess(ang_diff(cusp["lon"], asc + 30 * i), 1e-9)

    def test_placidus_houses_are_unequal(self):
        c = chart(1990, 5, 17, 14, 30, hsys="P")
        cusps = [x["lon"] for x in c["houses"]["cusps"]]
        widths = [(cusps[(i + 1) % 12] - cusps[i]) % 360 for i in range(12)]
        self.assertAlmostEqual(sum(widths), 360.0, places=9)
        self.assertGreater(max(widths) - min(widths), 5.0)
        # Placidus cusp 1 = Ascendant and cusp 10 = Midheaven.
        self.assertLess(ang_diff(cusps[0], c["houses"]["angles"]["asc"]["lon"]), 1e-9)
        self.assertLess(ang_diff(cusps[9], c["houses"]["angles"]["mc"]["lon"]), 1e-9)

    def test_high_latitude_reports_unavailable_systems(self):
        c = chart(1990, 12, 21, 12, 0, place=TROMSO, hsys="P")
        self.assertEqual(c["status"], "error")
        self.assertEqual(c["code"], "house_system_unavailable")
        self.assertNotIn("P", c["available"])
        self.assertIn("W", c["available"])
        ok = chart(1990, 12, 21, 12, 0, place=TROMSO, hsys="W")
        self.assertEqual(ok["status"], "ok")
        self.assertEqual(ok["houses"]["system"], "W")  # no silent switch

    def test_svalbard(self):
        c = chart(2000, 6, 21, 12, 0, place=LONGYEARBYEN, hsys="K")
        self.assertEqual(c["code"], "house_system_unavailable")
        self.assertEqual(chart(2000, 6, 21, 12, 0, place=LONGYEARBYEN, hsys="O")["status"], "ok")

    def test_house_assignment_wraps_zero_aries_and_cusp_boundary(self):
        cusps = [350.0] + [350.0 + 30 * i - 360 for i in range(1, 12)]  # cusp 1 at 350, cusp 2 at 20 ...
        self.assertEqual(engine.house_of(355.0, cusps), 1)
        self.assertEqual(engine.house_of(0.0, cusps), 1)
        self.assertEqual(engine.house_of(19.999999, cusps), 1)
        self.assertEqual(engine.house_of(20.0, cusps), 2)   # exactly on cusp 2 -> house 2
        self.assertEqual(engine.house_of(349.9999999, cusps), 12)

    def test_planet_exactly_on_a_real_cusp(self):
        c = chart(1990, 5, 17, 14, 30, hsys="P")
        cusps = [x["lon"] for x in c["houses"]["cusps"]]
        for i, cl in enumerate(cusps):
            self.assertEqual(engine.house_of(cl, cusps), i + 1)

    def test_intercepted_signs_reported(self):
        # High-ish latitude Placidus chart typically has interceptions.
        c = chart(1990, 12, 21, 3, 0, place=LONDON, hsys="P")
        h = c["houses"]
        self.assertEqual(len(h["intercepted_signs"]), len(h["repeated_cusp_signs"]))
        self.assertGreater(len(h["intercepted_signs"]), 0)


class TimeConversion(unittest.TestCase):
    def test_utc_changes_calendar_date(self):
        c = chart(2000, 1, 1, 23, 30)  # New York, UTC-5
        self.assertEqual(c["time"]["utc_iso"], "2000-01-02T04:30:00Z")
        self.assertTrue(c["time"]["utc_date_differs"])
        s = chart(2000, 1, 1, 0, 30, place=SYDNEY)  # UTC+11 (summer)
        self.assertEqual(s["time"]["utc_iso"], "1999-12-31T13:30:00Z")

    def test_leap_days(self):
        self.assertEqual(chart(2000, 2, 29, 12, 0)["status"], "ok")
        for y in (1900, 2001):
            with self.assertRaises(InputError):
                chart(y, 2, 29, 12, 0)

    def test_dst_ambiguous_requires_choice(self):
        c = chart(2021, 11, 7, 1, 30)
        self.assertEqual(c["status"], "ambiguous")
        self.assertEqual([o["fold"] for o in c["options"]], [0, 1])
        a = chart(2021, 11, 7, 1, 30, fold=0)
        b = chart(2021, 11, 7, 1, 30, fold=1)
        self.assertEqual(a["time"]["utc_iso"], "2021-11-07T05:30:00Z")
        self.assertEqual(b["time"]["utc_iso"], "2021-11-07T06:30:00Z")

    def test_dst_nonexistent_is_rejected(self):
        c = chart(2021, 3, 14, 2, 30)
        self.assertEqual(c["status"], "nonexistent")
        self.assertNotIn("bodies", c)

    def test_historical_british_standard_time_and_double_summer_time(self):
        # 1968-1971 the UK stayed on UTC+1 all year ("British Standard Time").
        self.assertEqual(chart(1970, 1, 15, 12, 0, place=LONDON)["time"]["utc_offset"], "UTC+01:00")
        # Today's January offset would be UTC+0 — prove we are not using it.
        self.assertEqual(chart(2020, 1, 15, 12, 0, place=LONDON)["time"]["utc_offset"], "UTC+00:00")
        # WWII British Double Summer Time: UTC+2.
        self.assertEqual(chart(1944, 6, 1, 12, 0, place=LONDON)["time"]["utc_offset"], "UTC+02:00")

    def test_pre_1970_warning(self):
        c = chart(1944, 6, 1, 12, 0, place=LONDON)
        self.assertEqual(c["time"]["reliability"], "pre1970")
        self.assertTrue(any("1970" in w for w in c["warnings"]))

    def test_lmt_requires_confirmation(self):
        c = chart(1850, 6, 1, 12, 0)
        self.assertEqual(c["status"], "needs_confirmation")
        ok = chart(1850, 6, 1, 12, 0, accept_lmt=True)
        self.assertEqual(ok["status"], "ok")
        self.assertEqual(ok["time"]["reliability"], "lmt")

    def test_manual_offset_and_zone(self):
        body = {"year": 1985, "month": 3, "day": 2, "hour": 8, "minute": 15, "house_system": "P",
                "location": {"mode": "manual", "lat": 52.0567, "lon": 1.1482, "utc_offset_minutes": 0}}
        c = build_chart(parse_request(body, PLACES))
        self.assertEqual(c["time"]["utc_iso"], "1985-03-02T08:15:00Z")
        body["location"] = {"mode": "manual", "lat": 52.0567, "lon": 1.1482}
        with self.assertRaises(InputError):
            parse_request(body, PLACES)
        body["location"] = {"mode": "manual", "lat": 95, "lon": 1, "tz": "Europe/London"}
        with self.assertRaises(InputError):
            parse_request(body, PLACES)

    def test_unsupported_dates(self):
        for y in (1799, 2400):
            with self.assertRaises(InputError) as cm:
                chart(y, 6, 1, 12, 0)
            self.assertEqual(cm.exception.code, "unsupported_date")


class Bodies(unittest.TestCase):
    def test_south_node_exactly_opposite(self):
        c = chart(1990, 5, 17, 14, 30)
        b = {x["id"]: x for x in c["bodies"]}
        self.assertAlmostEqual((b["south_node"]["lon"] - b["north_node"]["lon"]) % 360, 180.0, places=10)
        self.assertTrue(0 <= b["south_node"]["lon"] < 360)

    def test_retrograde_follows_speed_sign(self):
        for d in ((2000, 1, 1), (1990, 5, 17), (2023, 8, 30)):
            c = chart(*d, 12, 0)
            for b in c["bodies"]:
                self.assertEqual(b["retrograde"], b["speed"] < 0, b["id"])

    def test_true_node_is_not_always_retrograde(self):
        # The true node's speed changes sign; scan a month and expect both.
        signs = set()
        for day in range(1, 29):
            c = chart(2000, 2, day, 12, 0)
            nn = next(b for b in c["bodies"] if b["id"] == "north_node")
            signs.add(nn["retrograde"])
        self.assertEqual(signs, {True, False})

    def test_chiron_present_with_files(self):
        c = chart(1990, 5, 17, 14, 30)
        self.assertIn("chiron", [b["id"] for b in c["bodies"]])

    def test_stellium_1962(self):
        c = chart(1962, 2, 4, 17, 0, place=DELHI)
        aq = [b["id"] for b in c["bodies"] if b["sign"] == "Aquarius"]
        for body in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"):
            self.assertIn(body, aq)

    def test_reference_values_j2000(self):
        # Independent cross-check: Swiss Ephemeris documentation / almanac value
        # for the Sun on 2000-01-01 17:00 UT is 280.581° (10°34'53" Capricorn, shown 10°34').
        c = chart(2000, 1, 1, 12, 0)
        sun = next(b for b in c["bodies"] if b["id"] == "sun")
        self.assertEqual((sun["sign"], sun["deg"], sun["min"]), ("Capricorn", 10, 34))
        self.assertAlmostEqual(c["time"]["delta_t_seconds"], 63.8, delta=0.5)


class Rounding(unittest.TestCase):
    def test_rounding_never_changes_sign(self):
        r = split_longitude(29.99999)
        self.assertEqual((r["sign"], r["deg"], r["min"]), ("Aries", 29, 59))
        r = split_longitude(359.99999)
        self.assertEqual((r["sign"], r["deg"], r["min"]), ("Pisces", 29, 59))
        r = split_longitude(360.0)
        self.assertEqual((r["sign"], r["deg"], r["min"]), ("Aries", 0, 0))

    def test_minutes_are_truncated_like_astro_com(self):
        r = split_longitude(45 + 12.6 / 60)
        self.assertEqual((r["sign"], r["deg"], r["min"]), ("Taurus", 15, 12))
        r = split_longitude(45 + 59.6 / 60)  # 15°59.6' -> 15°59'
        self.assertEqual((r["deg"], r["min"]), (15, 59))
        r = split_longitude(96 + 18 / 60 + 46.4 / 3600)  # 6°18'46" Cancer -> 6°18'
        self.assertEqual((r["deg"], r["min"]), (6, 18))

    def test_sample_ipswich_1983_with_astro_gold_coordinates(self):
        # Sample check against Astro Gold atlas coordinates 52N04, 1E10.
        body = {"year": 1983, "month": 7, "day": 10, "hour": 3, "minute": 55, "house_system": "P",
                "location": {"mode": "manual", "lat": 52 + 4 / 60, "lon": 1 + 10 / 60, "tz": "Europe/London"}}
        c = build_chart(parse_request(body, PLACES))
        self.assertEqual(c["time"]["utc_iso"], "1983-07-10T02:55:00Z")  # BST
        sun = next(b for b in c["bodies"] if b["id"] == "sun")
        self.assertEqual((sun["sign"], sun["deg"], sun["min"]), ("Cancer", 17, 18))
        asc = c["houses"]["angles"]["asc"]
        self.assertEqual((asc["sign"], asc["deg"], asc["min"]), ("Cancer", 5, 29))


class Aspects(unittest.TestCase):
    def pts(self, *lons):
        return [{"id": f"p{i}", "lon": lon, "category": "planet"} for i, lon in enumerate(lons)]

    def test_wraparound_conjunction(self):
        a = find_aspects(self.pts(359.0, 1.0), DEFAULT_ORBS)
        self.assertEqual(a[0]["type"], "conjunction")
        self.assertAlmostEqual(a[0]["separation"], 2.0)

    def test_trine_and_orb(self):
        a = find_aspects(self.pts(10.0, 250.0), DEFAULT_ORBS)
        self.assertEqual(a[0]["type"], "trine")
        self.assertAlmostEqual(a[0]["orb"], 0.0)

    def test_out_of_orb(self):
        self.assertEqual(find_aspects(self.pts(0.0, 97.0), DEFAULT_ORBS), [])  # square orb 6

    def test_mixed_category_average(self):
        pts = [{"id": "sun", "lon": 0.0, "category": "luminary"}, {"id": "mars", "lon": 8.4, "category": "planet"}]
        a = find_aspects(pts, DEFAULT_ORBS)
        self.assertEqual(a[0]["allowed_orb"], 8.5)


class Untimed(unittest.TestCase):
    def test_untimed_has_no_houses_or_angles(self):
        c = chart(2000, 1, 1)
        self.assertFalse(c["timed"])
        self.assertIsNone(c["houses"])
        self.assertNotIn("house", c["bodies"][0])
        self.assertIn("untimed", c)
        self.assertTrue(all(a["a"] not in ("asc", "mc") and a["b"] not in ("asc", "mc") for a in c["aspects"]))
        self.assertTrue(c["time"]["local_iso"].endswith("12:00:00"))

    def test_moon_sign_change_flagged(self):
        # 2000-01-02: the Moon leaves Scorpio during the New York day.
        c = chart(2000, 1, 2)
        self.assertTrue(c["untimed"]["moon"]["sign_changes"])
        self.assertIn("moon", [x["id"] for x in c["untimed"]["sign_changes"]])


class MissingEphemeris(unittest.TestCase):
    def test_missing_files_refuse_to_calculate(self):
        old = engine.EPHE_PATH
        with tempfile.TemporaryDirectory() as empty:
            try:
                engine.EPHE_PATH = empty
                swe.close()
                swe.set_ephe_path(empty)
                c = chart(1990, 5, 17, 14, 30)
                self.assertEqual(c["status"], "error")
                self.assertEqual(c["code"], "ephemeris_missing")
            finally:
                engine.EPHE_PATH = old
                swe.close()
                swe.set_ephe_path(old)
                engine._tls.path = None

    def test_worker_threads_use_ephemeris_files(self):
        # Regression: Swiss Ephemeris settings are per thread.
        import threading
        out = {}
        t = threading.Thread(target=lambda: out.setdefault("c", chart(1990, 5, 17, 14, 30)))
        t.start(); t.join()
        self.assertEqual(out["c"]["status"], "ok")


class Api(unittest.TestCase):
    def setUp(self):
        import app as app_module
        self.client = app_module.app.test_client()

    def test_auth_required(self):
        self.assertEqual(self.client.get("/v1/places?q=lon").status_code, 401)
        self.assertEqual(self.client.get("/v1/health").status_code, 200)

    def test_chart_endpoint(self):
        r = self.client.post("/v1/chart", json={"year": 1990, "month": 5, "day": 17, "hour": 14, "minute": 30,
                                                "location": {"mode": "place", "place_id": NYC}, "house_system": "K"},
                             headers={"X-SR11-Key": "test-key-not-secret"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["houses"]["system"], "K")
        self.assertEqual(r.headers["Cache-Control"], "no-store")

    def test_invalid_input(self):
        r = self.client.post("/v1/chart", json={"year": "abc"}, headers={"X-SR11-Key": "test-key-not-secret"})
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()
