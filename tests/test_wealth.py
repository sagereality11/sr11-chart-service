"""Your Birth Chart's Wealth Story: calculations, voice rules and rendering."""
import datetime as dt
import random
import re
import unittest

from sr11calc import wealth, wealth_reading
from sr11calc.service import build_chart, parse_request

TIFF = dict(year=1983, month=7, day=10, hour=3, minute=55,
            location={"mode": "manual", "lat": 52.0592, "lon": 1.1555, "tz": "Europe/London", "label": "Ipswich, England"})
TODAY = dt.date(2026, 10, 19)


def reading_for(body, name="Tiff"):
    req = parse_request({**body, "house_system": "P", "points": ["fortune"]})
    chart = build_chart(req)
    a = wealth.analyze(chart, req["date"], TODAY)
    return a, wealth_reading.build_reading(a, name, {})


def text_of(r):
    return " ".join(p for s in r["sections"] for p in s["paragraphs"])


class TestTiffChart(unittest.TestCase):
    """Her own chart, checked against astro.com / Astro Gold."""

    @classmethod
    def setUpClass(cls):
        cls.a, cls.r = reading_for(TIFF)

    def test_rulers_and_roles(self):
        self.assertEqual(self.a["rulers"][2], "moon")
        self.assertEqual(self.a["rulers"][10], "jupiter")
        self.assertEqual(set(self.a["roles"]["moon"]), {"asc", "second", "fortune", "assets"})
        self.assertTrue(self.a["night"])

    def test_lots(self):
        P = self.a["planets"]
        self.assertEqual((P["fortune"]["sign"], P["fortune"]["deg"], P["fortune"]["house"]), ("Cancer", 10, 1))
        self.assertEqual((P["assets"]["sign"], P["assets"]["deg"]), ("Cancer", 14))

    def test_condition(self):
        P = self.a["planets"]
        self.assertEqual(P["moon"]["dignity"], "domicile")
        self.assertEqual(P["moon"]["solar"], "combust")
        self.assertEqual(P["mars"]["dignity"], "fall")
        self.assertEqual(P["saturn"]["dignity"], "exaltation")
        self.assertEqual(self.a["moon_phase"], "balsamic")

    def test_regulus_on_venus_and_ic(self):
        pts = {(s["star"], s["point"]) for s in self.a["stars"]}
        self.assertIn(("Regulus", "venus"), pts)
        self.assertIn(("Regulus", "ic"), pts)

    def test_profection(self):
        self.assertEqual((self.a["profection"]["house"], self.a["profection"]["lord"]), (8, "saturn"))

    def test_saturn_squares_fortune(self):
        self.assertTrue(any(h["planet"] == "saturn" and h["target"] == "fortune" and h["aspect"] == 90
                            for h in self.a["transits"]))

    def test_sections(self):
        heads = [s["heading"] for s in self.r["sections"] if s["level"] == 1]
        self.assertEqual(heads[0], "Where Your Wealth Story Begins")
        self.assertEqual(heads[-2:], ["Final Thoughts", "Where to Go From Here"])
        self.assertIn("Your Midheaven and Career Path", heads)


class TestVoiceRules(unittest.TestCase):
    def test_many_charts(self):
        rnd = random.Random(11)
        cities = [(40.71, -74.0, "America/New_York"), (51.5, -0.12, "Europe/London"), (-33.87, 151.2, "Australia/Sydney"),
                  (19.07, 72.88, "Asia/Kolkata"), (35.68, 139.69, "Asia/Tokyo")]
        for _ in range(12):
            lat, lon, tz = rnd.choice(cities)
            body = dict(year=rnd.randint(1950, 2005), month=rnd.randint(1, 12), day=rnd.randint(1, 28),
                        hour=rnd.randint(0, 23), minute=rnd.randint(0, 59),
                        location={"mode": "manual", "lat": lat, "lon": lon, "tz": tz})
            _, r = reading_for(body, "Sam")
            t = text_of(r)
            self.assertNotIn("—", t)
            self.assertLessEqual(t.count(":"), 1)
            self.assertNotRegex(t, r"[{}]|\bNone\b|[.!?] [a-z]")
            sents = [s for s in re.split(r"(?<=[.!?])\s+", t) if len(s) > 20]
            self.assertEqual(len(sents), len(set(sents)), "a sentence repeats")
            for s in r["sections"]:
                self.assertTrue(s["paragraphs"], s["heading"])


if __name__ == "__main__":
    unittest.main()
