#!/usr/bin/env sh
# Downloads GeoNames place data (CC BY 4.0, https://www.geonames.org/) into ./data/geonames
set -eu
DEST="${1:-data/geonames}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DEST"
cd "$DEST"
curl -fsSL https://download.geonames.org/export/dump/cities500.zip -o cities500.zip
unzip -o -q cities500.zip && rm cities500.zip
curl -fsSL https://download.geonames.org/export/dump/admin1CodesASCII.txt -o admin1CodesASCII.txt
curl -fsSL https://download.geonames.org/export/dump/countryInfo.txt -o countryInfo.txt
# Every populated place, however small (Adak, Alaska has about 330 people),
# goes into an on-disk SQLite index so it costs almost no memory.
curl -fsSL https://download.geonames.org/export/dump/allCountries.zip -o allCountries.zip
python3 "$HERE/build_small_places.py" .
rm allCountries.zip
echo "GeoNames data ready in $DEST"
