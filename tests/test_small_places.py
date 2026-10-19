"""Small-town birthplaces (below the cities500 cut-off) must be searchable."""

import io
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from sr11calc.places import PlaceIndex  # noqa: E402
import build_small_places  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "geonames"


def row(gid, name, ascii_, lat, lon, fclass, fcode, cc, a1, pop, tz):
    return "\t".join([str(gid), name, ascii_, "", str(lat), str(lon), fclass, fcode, cc, "", a1, "", "", "",
                      str(pop), "", "", tz, "2024-01-01"]) + "\n"


class SmallPlacesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp())
        for f in ("countryInfo.txt", "cities1000.txt"):
            shutil.copy(FIX / f, cls.dir / f)
        admin = (FIX / "admin1CodesASCII.txt").read_text(encoding="utf-8")
        admin += "US.AK\tAlaska\tAlaska\t5879092\nTR.72\tMardin\tMardin\t304794\n"
        (cls.dir / "admin1CodesASCII.txt").write_text(admin, encoding="utf-8")
        all_rows = (FIX / "cities1000.txt").read_text(encoding="utf-8")  # big cities appear in allCountries too
        all_rows += row(5878818, "Adak", "Adak", 51.88, -176.65, "P", "PPL", "US", "AK", 332, "America/Adak")
        all_rows += row(325390, "Adak", "Adak", 37.3, 40.7, "P", "PPL", "TR", "72", 455, "Europe/Istanbul")
        all_rows += row(999001, "Adak Island", "Adak Island", 51.8, -176.6, "T", "ISL", "US", "AK", 0, "America/Adak")
        all_rows += row(999002, "Old Adak", "Old Adak", 51.8, -176.6, "P", "PPLQ", "US", "AK", 0, "America/Adak")
        all_rows += row(999003, "Kotzebue Section", "Kotzebue Section", 66.9, -162.6, "P", "PPLX", "US", "AK", 0, "America/Nome")
        all_rows += row(999004, "Tiny Ville", "Tiny Ville", 60.0, -150.0, "P", "PPL", "US", "AK", 0, "America/Anchorage")
        buf = io.BytesIO()
        with zipfile.ZipFile(cls.dir / "allCountries.zip", "w") as z:
            z.writestr("allCountries.txt", all_rows)
        build_small_places.main(str(cls.dir))
        cls.idx = PlaceIndex(cls.dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir)

    def test_counts(self):
        self.assertTrue(self.idx.loaded)
        self.assertEqual(self.idx.small_count, 3)  # two Adaks + Tiny Ville; big cities, islands, PPLQ/PPLX skipped

    def test_adak_found(self):
        labels = [r["label"] for r in self.idx.search("Adak")]
        self.assertIn("Adak, Alaska, United States", labels)

    def test_adak_with_state(self):
        for q in ("Adak, Alaska", "Adak AK", "adak alaska"):
            res = self.idx.search(q)
            self.assertEqual([r["id"] for r in res], [5878818], q)
            self.assertEqual(res[0]["tz"], "America/Adak")

    def test_get_small_place(self):
        p = self.idx.get(5878818)
        self.assertEqual(p["admin1"], "Alaska")
        self.assertEqual(p["admin1_code"], "AK")
        self.assertAlmostEqual(p["lat"], 51.88)

    def test_big_city_still_first(self):
        self.assertEqual(self.idx.search("London")[0]["id"], 2643743)
        self.assertEqual(len({r["id"] for r in self.idx.search("Lon")}), len(self.idx.search("Lon")))

    def test_no_duplicates(self):
        res = self.idx.search("Adak")
        self.assertEqual(len(res), len({r["id"] for r in res}))

    def test_without_small_file(self):
        d = Path(tempfile.mkdtemp())
        for f in ("countryInfo.txt", "cities1000.txt", "admin1CodesASCII.txt"):
            shutil.copy(FIX / f, d / f)
        idx = PlaceIndex(d)
        self.assertEqual(idx.small_count, 0)
        self.assertEqual(idx.search("Adak"), [])
        self.assertIsNone(idx.get(5878818))
        self.assertEqual(idx.search("London")[0]["id"], 2643743)
        shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
