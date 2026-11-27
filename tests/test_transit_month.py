"""Monthly Transit Forecast and Shared Soul Journey: API smoke tests."""
import json
import os
import re
import unittest

os.environ.setdefault("SR11_API_KEY", "testkey")
import app as appmod  # noqa: E402


class TestTransitMonthAPI(unittest.TestCase):
    def setUp(self):
        appmod.API_KEY = "testkey"
        self.c = appmod.app.test_client()
        import datetime as dt
        t = dt.date.today()
        self.y, self.m = t.year, t.month

    def body(self, **kw):
        b = {"year": 1983, "month": 7, "day": 10, "hour": 3, "minute": 55, "name": "Tiff", "pronoun": "she",
             "location": {"mode": "manual", "lat": 52.0592, "lon": 1.1555, "tz": "Europe/London", "label": "Ipswich, England"},
             "forecast_year": self.y, "forecast_month": self.m, "forecast_tz": "America/New_York"}
        b.update(kw)
        return b

    def post(self, b):
        return self.c.post("/v1/transit-month", json=b, headers={"X-SR11-Key": "testkey"})

    def check(self, r):
        self.assertEqual(r.status_code, 200, r.get_json())
        j = r.get_json()
        txt = json.dumps(j["reading"], ensure_ascii=False)
        for bad in ("None", "undefined", "nan,", "{N}", "{np}", "{ess}"):
            self.assertNotIn(bad, txt)
        self.assertGreater(len(j["reading"]["parts"]), 6)
        return j

    def test_solo(self):
        j = self.check(self.post(self.body()))
        self.assertEqual(j["product"], "transit-month")
        self.assertIn("Monthly-Transit-Forecast-Tiff-", j["filename"])
        self.assertIn("3:55 am in Ipswich, England", j["reading"]["birthLabel"])

    def test_mean_node_untimed(self):
        j = self.check(self.post(self.body(node="mean", time_known=False, hour=None, minute=None)))
        self.assertEqual(j["node"], "mean")
        self.assertIn("Mean Node", " ".join(j["reading"]["method"]))

    def test_pair(self):
        partner = {"year": 2003, "month": 2, "day": 10, "hour": 6, "minute": 27, "name": "James", "pronoun": "he",
                   "location": {"mode": "manual", "lat": 41.1544, "lon": -96.0422, "tz": "America/Chicago", "label": "Papillion, Nebraska"}}
        j = self.check(self.post(self.body(partner=partner, relationship="mother_son")))
        self.assertEqual(j["product"], "transit-month-pair")
        self.assertTrue(j["reading"]["pair"])
        self.assertIn("Shared-Soul-Journey-Tiff-James-", j["filename"])

    def test_month_range(self):
        self.assertEqual(self.post(self.body(forecast_year=self.y + 2)).status_code, 422)


if __name__ == "__main__":
    unittest.main()
