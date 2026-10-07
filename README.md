# SR11 Chart Service

The calculation service behind the Sage Reality 11 birth chart calculator at [sagereality11.com](https://sagereality11.com). It turns a birth date, time and place into planetary positions, house cusps, angles and major aspects. It does not draw charts or write interpretations.

This source code is published under the GNU Affero General Public License v3 (see `LICENSE`), as required by the Swiss Ephemeris licence used for the calculations.

## What it calculates

* Sun through Pluto, True North Node, South Node (North Node + 180°), Chiron
* Tropical zodiac, geocentric apparent positions, True Node
* Houses: Placidus (default), Whole Sign, Equal, Koch, Porphyry, Regiomontanus, Campanus, Alcabitius, Topocentric
* Ascendant, Descendant, Midheaven, IC
* Major aspects (conjunction, sextile, square, trine, opposition) with configurable orbs
* Untimed charts: local-noon positions, plus which placements and aspects could change across the day
* Optional: Mean Node instead of True Node; Black Moon Lilith (Mean and True); Ceres, Pallas, Juno, Vesta;
  Part of Fortune and Part of Spirit (day/night formulas by sect); Vertex and Anti-Vertex;
  the golden ratio aspect (137.5°); up to five more asteroids by number or name

Local birth times are converted to UTC with the IANA time zone database, including historical daylight saving rules. Ambiguous and skipped clock times are reported instead of guessed.

## API

All endpoints except `/v1/health` require the header `X-SR11-Key` matching the `SR11_API_KEY` environment variable.

| Method | Path | Purpose |
|---|---|---|
| GET | `/v1/health` | engine version, ephemeris and place-data status |
| GET | `/v1/places?q=paris` | birthplace search (GeoNames) |
| GET | `/v1/asteroids?q=eros` | asteroid search by name or number |
| GET | `/v1/timezones` | IANA time zone list |
| GET | `/v1/house-systems` | supported house systems |
| POST | `/v1/chart` | calculate a chart |
| POST | `/v1/year-ahead` | "Your 2027" personal year-ahead reading (same body as `/v1/chart` plus `name`; returns the reading as data and a printable HTML document) |

Example request body for `/v1/chart`:

```json
{ "year": 1990, "month": 5, "day": 17, "hour": 14, "minute": 30,
  "location": { "mode": "place", "place_id": 5128581 },
  "house_system": "P" }
```

## Run it

```bash
docker build -t sr11-chart-service .
docker run -e SR11_API_KEY=change-me -p 8080:8080 sr11-chart-service
```

The Docker build downloads the Swiss Ephemeris data files (1800–2399) and GeoNames place data. No birth data is stored or logged.

## Tests

```bash
pip install -r requirements.txt
./scripts/fetch_ephemeris.sh ephe
python -m unittest discover -s tests -v
```

## Credits and licences

* Calculations: Swiss Ephemeris, used under the AGPL-3.0.
* Place data: © GeoNames, CC BY 4.0.
* Asteroids beyond Ceres, Pallas, Juno and Vesta: positions from NASA/JPL Horizons, which receives only the
  asteroid number and the UTC instant. Asteroid names: IAU Minor Planet Center list.
* Time zones: IANA tz database.
* Flask and gunicorn under their own licences.

Copyright © 2026 Sage Reality 11. Licensed under the GNU Affero General Public License v3.0.
