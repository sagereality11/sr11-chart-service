#!/usr/bin/env sh
# Downloads the Swiss Ephemeris data files covering 1800-2399 into ./ephe
#   sepl_18.se1  planets      semo_18.se1  Moon      seas_18.se1  main asteroids incl. Chiron
# Source: the official Swiss Ephemeris repository by Astrodienst (github.com/aloistr/swisseph).
set -eu
DEST="${1:-ephe}"
BASE="https://raw.githubusercontent.com/aloistr/swisseph/master/ephe"
mkdir -p "$DEST"
for f in sepl_18.se1 semo_18.se1 seas_18.se1; do
  curl -fsSL "$BASE/$f" -o "$DEST/$f"
  echo "fetched $f"
done
