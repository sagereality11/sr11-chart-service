"""Your 2027 reading: runs end to end on a known chart and keeps Tiff's voice rules."""
import datetime as dt
import json
import re
import unittest

from sr11calc import engine, yearahead, yearahead_render


@unittest.skipUnless(engine.ephemeris_status()["ready"], "ephemeris files not installed")
class YearAheadTests(unittest.TestCase):
    def reading(self, timed=True):
        c = engine.chart_at(dt.datetime(1983, 7, 10, 2, 55, tzinfo=dt.timezone.utc), 52.0592, 1.1555,
                            "P" if timed else None, None)
        c["bodies"] = c["bodies"]
        return yearahead.build_reading(c, dt.date(1983, 7, 10), "Test", timed, "Ipswich, England", "3:55 AM")

    def test_known_chart(self):
        r = self.reading()
        self.assertEqual(r["subtitle"], "The Year of Expansion")          # 9th house profection at 44
        self.assertIn("Leo 3rd house", r["snapshot"]["Eclipse axis"])
        self.assertEqual(len(r["months"]), 12)
        self.assertEqual(len(r["power_months"]), 4)
        json.dumps(r)                                                      # serializable as-is

    def test_untimed(self):
        r = self.reading(timed=False)
        self.assertTrue(any("Birth Time" in s["heading"] for s in r["sections"]))

    def test_voice_rules(self):
        html = yearahead_render.render_single_html(self.reading())
        self.assertIsNone(re.search("—|–|…", html))           # no em/en dashes, no ellipsis glyph


if __name__ == "__main__":
    unittest.main()
