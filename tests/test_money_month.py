"""Monthly Money Forecast: API smoke tests."""
import base64
import os
import unittest

os.environ.setdefault("SR11_API_KEY", "testkey")
import app as appmod  # noqa: E402


class TestMoneyMonthAPI(unittest.TestCase):
    def setUp(self):
        appmod.API_KEY = "testkey"
        self.c = appmod.app.test_client()
        import datetime as dt
        t = dt.date.today()
        self.y, self.m = t.year, t.month

    def post(self, **kw):
        body = {"year": 1983, "month": 7, "day": 10, "hour": 3, "minute": 55, "name": "Tiff",
                "location": {"mode": "manual", "lat": 52.0592, "lon": 1.1555, "tz": "Europe/London", "label": "Ipswich"},
                "forecast_year": self.y, "forecast_month": self.m, "forecast_tz": "America/New_York"}
        body.update(kw)
        return self.c.post("/v1/money-month", json=body, headers={"X-SR11-Key": "testkey"})

    def test_pdf(self):
        r = self.post(with_html=True)
        self.assertEqual(r.status_code, 200, r.get_json())
        j = r.get_json()
        self.assertTrue(base64.b64decode(j["pdf_base64"]).startswith(b"%PDF"))
        self.assertIn("Monthly-Money-Forecast-Tiff-", j["filename"])
        self.assertIn('table class="cal"', j["html"])

    def test_untimed(self):
        r = self.post(time_known=False, hour=None, minute=None)
        self.assertEqual(r.status_code, 200, r.get_json())

    def test_month_range(self):
        r = self.post(forecast_year=self.y + 2)
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()
