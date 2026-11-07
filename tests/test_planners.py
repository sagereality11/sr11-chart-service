import base64
import os
import unittest

os.environ.setdefault("SR11_API_KEY", "test")
import app as A  # noqa: E402

BODY = {"year": 1983, "month": 7, "day": 10, "hour": 3, "minute": 55, "name": "Test",
        "location": {"mode": "manual", "lat": 52.0567, "lon": 1.1482, "tz": "Europe/London"}}


@unittest.skipUnless(os.path.isfile(os.path.join(os.environ.get("SR11_EPHE_PATH", "ephe"), "sepl_18.se1")), "ephemeris files needed")
class PlannerTests(unittest.TestCase):
    def setUp(self):
        A.API_KEY = "test"
        self.c = A.app.test_client()

    def post(self, **kw):
        import datetime as dt
        t = dt.date.today()
        body = {**BODY, "start_year": t.year, "start_month": t.month, **kw}
        return self.c.post("/v1/planner", json=body, headers={"X-SR11-Key": "test"})

    def test_each_planner_returns_a_pdf(self):
        for p in ("moon", "money", "transits"):
            r = self.post(product=p)
            self.assertEqual(r.status_code, 200, p)
            pdf = base64.b64decode(r.get_json()["pdf_base64"])
            self.assertTrue(pdf.startswith(b"%PDF"), p)
            self.assertGreater(len(pdf), 100_000, p)

    def test_needs_birth_time_and_valid_start(self):
        self.assertEqual(self.post(product="moon", time_known=False).status_code, 422)
        self.assertEqual(self.post(product="moon", start_year=2099, start_month=1).status_code, 422)
        self.assertEqual(self.post(product="tarot").status_code, 422)


if __name__ == "__main__":
    unittest.main()
