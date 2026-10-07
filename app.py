"""Sage Reality 11 Birth Chart — calculation service (HTTP layer).

Only the WordPress server talks to this service. Every request except
/v1/health must carry the shared secret in the ``X-SR11-Key`` header; the
secret lives in WordPress's settings (server side) and in this service's
SR11_API_KEY environment variable — never in browser code.

Privacy: request bodies are never logged or stored. Run under gunicorn with
access logging disabled (see gunicorn.conf.py) so place searches are not
written to logs either. No caching of chart results.
"""

from __future__ import annotations

import hmac
import os
import threading
import time

from flask import Flask, jsonify, request

from sr11calc import asteroids, engine, timeconv, yearahead, yearahead_render
from sr11calc.places import PlaceIndex
from sr11calc.service import InputError, build_chart, parse_request

API_KEY = os.environ.get("SR11_API_KEY", "")
GLOBAL_LIMIT_PER_MIN = int(os.environ.get("SR11_GLOBAL_LIMIT_PER_MIN", "600"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024  # chart requests are tiny
places = PlaceIndex()

_lock = threading.Lock()
_window = [0.0, 0]


def _global_rate_ok() -> bool:
    """Coarse service-wide ceiling. Per-visitor limits are enforced by
    WordPress; this protects the service if the shared key ever leaks."""
    now = time.monotonic()
    with _lock:
        if now - _window[0] >= 60:
            _window[0], _window[1] = now, 0
        _window[1] += 1
        return _window[1] <= GLOBAL_LIMIT_PER_MIN


def _error(code: str, message: str, http: int = 400, **extra):
    return jsonify({"status": "error", "code": code, "message": message, **extra}), http


@app.before_request
def _auth():
    if request.path == "/v1/health":
        return None
    if not API_KEY:
        return _error("service_misconfigured", "Calculation service has no API key configured.", 503)
    supplied = request.headers.get("X-SR11-Key", "")
    if not hmac.compare_digest(supplied.encode(), API_KEY.encode()):
        return _error("unauthorized", "Unauthorized.", 401)
    if not _global_rate_ok():
        return _error("rate_limited", "The chart service is busy. Please try again in a minute.", 429)
    return None


@app.after_request
def _headers(resp):
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


@app.get("/v1/health")
def health():
    st = engine.ephemeris_status()
    return jsonify({
        "status": "ok" if st["ready"] and places.loaded else "degraded",
        "engine": engine.engine_info(),
        "ephemeris_ready": st["ready"],
        "ephemeris_files": st["files"],
        "places_loaded": places.loaded,
        "places_count": len(places.places),
        "tzdb": timeconv.tzdb_version(),
        "asteroid_names": len(asteroids._names()[0]),
        "optional_points": engine.OPTIONAL_POINT_IDS,
    })


@app.get("/v1/places")
def search_places():
    q = (request.args.get("q") or "").strip()[:80]
    if len(q) < 2:
        return jsonify({"status": "ok", "results": []})
    if not places.loaded:
        return _error("location_lookup_failed", "Birthplace search is unavailable. Please use the manual location option.", 503)
    return jsonify({"status": "ok", "results": places.search(q), "attribution": "Place data © GeoNames (CC BY 4.0)"})


@app.get("/v1/asteroids")
def search_asteroids():
    q = (request.args.get("q") or "").strip()[:60]
    return jsonify({"status": "ok", "results": asteroids.search(q),
                    "attribution": "Names: IAU Minor Planet Center. Positions: NASA/JPL Horizons."})


@app.get("/v1/timezones")
def timezones():
    return jsonify({"status": "ok", "zones": timeconv.timezone_list(), "tzdb": timeconv.tzdb_version()})


@app.get("/v1/house-systems")
def house_systems():
    return jsonify({"status": "ok", "default": engine.DEFAULT_HOUSE_SYSTEM,
                    "systems": [{"id": k, "name": v} for k, v in engine.HOUSE_SYSTEMS.items()]})


@app.post("/v1/chart")
def chart():
    body = request.get_json(silent=True)
    try:
        req = parse_request(body, places)
    except InputError as e:
        return _error(e.code, e.message, 422)
    try:
        result = build_chart(req)
    except Exception:  # never leak internals or input into logs/responses
        app.logger.error("chart calculation failed (input withheld)")
        return _error("calculation_failed", "The chart could not be calculated. Please try again.", 500)
    http = {"ok": 200, "ambiguous": 409, "nonexistent": 422, "needs_confirmation": 409}.get(result["status"], 422)
    return jsonify(result), http


@app.post("/v1/year-ahead")
def year_ahead():
    """Your 2027 personal year-ahead reading. Same body as /v1/chart plus an optional
    "name". Placidus houses and the True Node are always used. Returns the reading as
    structured data plus a ready-to-print HTML document."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return _error("invalid_input", "Malformed request.", 422)
    body = {**body, "house_system": "P", "node": "true", "points": [], "asteroids": [], "aspects": []}
    body.pop("orbs", None)
    name = str(body.get("name") or "").strip()[:60] or "Friend"
    try:
        req = parse_request(body, places)
    except InputError as e:
        return _error(e.code, e.message, 422)
    try:
        chart_out = build_chart(req)
        if chart_out["status"] != "ok":
            http = {"ambiguous": 409, "nonexistent": 422, "needs_confirmation": 409}.get(chart_out["status"], 422)
            return jsonify(chart_out), http
        t = req["time"]
        btime = t.strftime("%I:%M %p").lstrip("0") if (t and req["time_known"]) else ""
        reading = yearahead.build_reading(chart_out, req["date"], name, req["time_known"],
                                          req["place"].get("label", ""), btime)
        want_pdf = body.get("format") == "pdf"
        doc = None if want_pdf else yearahead_render.render_single_html(reading)
        pdf = yearahead_render.render_pdf(reading) if want_pdf else None
    except Exception:  # never leak internals or input into logs/responses
        app.logger.error("year-ahead calculation failed (input withheld)")
        return _error("calculation_failed", "The reading could not be created. Please try again.", 500)
    out = {"status": "ok", "product": "your-2027", "reading": reading}
    if pdf is not None:
        import base64
        out["pdf_base64"] = base64.b64encode(pdf).decode("ascii")
        out["filename"] = "Your-2027-Reading-" + "".join(c for c in name if c.isalnum() or c in "-_")[:40] + ".pdf"
    else:
        out["html"] = doc
    return jsonify(out)


if __name__ == "__main__":  # local development only
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8080")))
