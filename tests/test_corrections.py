"""Historical time zone corrections added Nov 2026 (statutes and official records).

Run:  python -m unittest tests.test_corrections -v
Place dicts are built by hand (state, county FIPS, zone) so no GeoNames data is needed.
"""

import datetime as dt
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("SR11_GEONAMES_DIR", str(HERE / "fixtures" / "geonames"))
os.environ.setdefault("SR11_API_KEY", "test-key-not-secret")
sys.path.insert(0, str(HERE.parent))

from sr11calc.service import resolve_time  # noqa: E402


def place(state, county, tz):
    return {"country_code": "US", "admin1_code": state, "admin2_code": county, "tz": tz}


def conv(p, y, m, d, hh=12, mm=0):
    req = {"record_offset": False, "utc_offset_minutes": None, "place": p, "tz": p["tz"]}
    r = resolve_time(req, dt.date(y, m, d), dt.time(hh, mm), None, False)
    assert r["status"] == "ok", r
    return r["time"]["utc_offset"], r["time"]["tz_abbrev"], r.get("reliability")


CHARLOTTE = place("NC", "119", "America/New_York")
MILWAUKEE = place("WI", "079", "America/Chicago")
SEATTLE = place("WA", "033", "America/Los_Angeles")
PORTLAND_OR = place("OR", "051", "America/Los_Angeles")
ONTARIO_OR = place("OR", "045", "America/Boise")
RICHMOND_VA = place("VA", "760", "America/New_York")
ARLINGTON_VA = place("VA", "013", "America/New_York")
CHARLESTON_WV = place("WV", "039", "America/New_York")
MINNEAPOLIS = place("MN", "053", "America/Chicago")
ST_PAUL = place("MN", "123", "America/Chicago")
WASHINGTON_DC = place("DC", "001", "America/New_York")
ANCHORAGE = place("AK", "020", "America/Anchorage")
JUNEAU = place("AK", "110", "America/Juneau")
KNOXVILLE = place("TN", "093", "America/New_York")
ATLANTA = place("GA", "121", "America/New_York")
PONCHATOULA = place("LA", "105", "America/Chicago")


class NewCorrections(unittest.TestCase):
    def test_north_carolina_no_dst_1946_1965(self):
        self.assertEqual(conv(CHARLOTTE, 1955, 7, 15)[:2], ("UTC-05:00", "EST"))
        self.assertEqual(conv(CHARLOTTE, 1966, 7, 15)[1], "EDT")          # tzdb from 1966

    def test_wisconsin_no_dst_until_1957(self):
        self.assertEqual(conv(MILWAUKEE, 1950, 7, 15)[:2], ("UTC-06:00", "CST"))
        self.assertEqual(conv(MILWAUKEE, 1960, 7, 15)[1], "CDT")

    def test_washington_no_dst_1953_1960(self):
        self.assertEqual(conv(SEATTLE, 1957, 7, 15)[:2], ("UTC-08:00", "PST"))
        self.assertEqual(conv(SEATTLE, 1962, 7, 15)[1], "PDT")

    def test_oregon_dst_ends_last_saturday_september(self):
        self.assertEqual(conv(PORTLAND_OR, 1964, 7, 15)[:2], ("UTC-07:00", "PDT"))
        self.assertEqual(conv(PORTLAND_OR, 1964, 9, 26, 1, 0)[1], "PDT")   # Sat 26 Sep, before 2 am
        self.assertEqual(conv(PORTLAND_OR, 1964, 9, 26, 12, 0)[:2], ("UTC-08:00", "PST"))
        self.assertEqual(conv(PORTLAND_OR, 1964, 10, 15)[1], "PST")
        self.assertNotEqual(conv(ONTARIO_OR, 1964, 10, 15)[2], "corrected")               # Mountain-zone county untouched

    def test_virginia_short_seasons(self):
        self.assertEqual(conv(RICHMOND_VA, 1962, 5, 15)[:2], ("UTC-05:00", "EST"))
        self.assertEqual(conv(RICHMOND_VA, 1962, 7, 15)[:2], ("UTC-04:00", "EDT"))
        self.assertEqual(conv(RICHMOND_VA, 1962, 9, 20)[1], "EST")
        self.assertEqual(conv(RICHMOND_VA, 1965, 6, 1)[1], "EST")          # starts Sun 6 June 1965
        self.assertEqual(conv(RICHMOND_VA, 1965, 6, 7)[1], "EDT")
        self.assertEqual(conv(RICHMOND_VA, 1965, 9, 5, 12)[1], "EST")      # Sunday before Labor Day
        self.assertNotEqual(conv(ARLINGTON_VA, 1962, 9, 20)[2], "corrected")              # 10th District: tzdb

    def test_west_virginia_ends_fourth_sunday_september(self):
        self.assertEqual(conv(CHARLESTON_WV, 1963, 7, 15)[1], "EDT")
        self.assertEqual(conv(CHARLESTON_WV, 1963, 10, 1)[:2], ("UTC-05:00", "EST"))

    def test_minnesota_may_to_september(self):
        self.assertEqual(conv(MINNEAPOLIS, 1962, 5, 10)[:2], ("UTC-06:00", "CST"))
        self.assertEqual(conv(MINNEAPOLIS, 1962, 7, 15)[1], "CDT")
        self.assertEqual(conv(MINNEAPOLIS, 1962, 9, 4, 1)[1], "CDT")       # Tue after Labor Day, 1 am
        self.assertEqual(conv(MINNEAPOLIS, 1962, 9, 20)[1], "CST")
        self.assertNotEqual(conv(ST_PAUL, 1965, 7, 15)[2], "corrected")                   # 1965 St. Paul left to tzdb
        self.assertEqual(conv(ST_PAUL, 1964, 9, 20)[1], "CST")

    def test_dc_dst_capped_at_september(self):
        self.assertEqual(conv(WASHINGTON_DC, 1955, 7, 15)[1], "EDT")
        self.assertEqual(conv(WASHINGTON_DC, 1955, 10, 10)[:2], ("UTC-05:00", "EST"))

    def test_alaska_1968_dst(self):
        self.assertEqual(conv(ANCHORAGE, 1968, 7, 15)[:2], ("UTC-09:00", "AHDT"))
        self.assertEqual(conv(ANCHORAGE, 1968, 1, 15)[0], "UTC-10:00")
        self.assertEqual(conv(JUNEAU, 1968, 7, 15)[:2], ("UTC-07:00", "PDT"))
        self.assertEqual(conv(JUNEAU, 1968, 11, 15)[0], "UTC-08:00")

    def test_knoxville_central_and_central_war_time(self):
        self.assertEqual(conv(KNOXVILLE, 1938, 7, 15)[:2], ("UTC-06:00", "CST"))
        self.assertEqual(conv(KNOXVILLE, 1943, 7, 15)[:2], ("UTC-05:00", "CWT"))
        self.assertEqual(conv(KNOXVILLE, 1946, 1, 15)[:2], ("UTC-06:00", "CST"))
        self.assertNotEqual(conv(KNOXVILLE, 1946, 5, 15)[2], "corrected")

    def test_atlanta_central_before_march_1941(self):
        self.assertEqual(conv(ATLANTA, 1940, 7, 15)[:2], ("UTC-06:00", "CST"))
        self.assertEqual(conv(ATLANTA, 1941, 4, 1)[0], "UTC-05:00")

    def test_louisiana_untouched(self):
        self.assertEqual(conv(PONCHATOULA, 1960, 7, 15)[:2], ("UTC-05:00", "CDT"))
        self.assertEqual(conv(PONCHATOULA, 1982, 10, 28)[:2], ("UTC-05:00", "CDT"))


if __name__ == "__main__":
    unittest.main()
