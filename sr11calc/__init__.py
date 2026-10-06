"""Sage Reality 11 Birth Chart — calculation engine.

This package is deliberately independent of the chart wheel renderer and of
WordPress. It turns validated birth data into numbers (positions, houses,
aspects) and never draws anything.

Modules
-------
timeconv  local civil time -> UTC using the IANA time zone database
engine    Swiss Ephemeris positions, houses, angles, untimed-chart analysis
aspects   major-aspect detection with configurable orbs
places    offline GeoNames city search (lat, lon, IANA zone)
zodiac    sign maths and display rounding
"""

__version__ = "0.1.0-draft"
