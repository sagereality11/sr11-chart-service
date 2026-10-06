#!/usr/bin/env sh
# Downloads GeoNames place data (CC BY 4.0, https://www.geonames.org/) into ./data/geonames
set -eu
DEST="${1:-data/geonames}"
mkdir -p "$DEST"
cd "$DEST"
curl -fsSL https://download.geonames.org/export/dump/cities1000.zip -o cities1000.zip
unzip -o -q cities1000.zip && rm cities1000.zip
curl -fsSL https://download.geonames.org/export/dump/admin1CodesASCII.txt -o admin1CodesASCII.txt
curl -fsSL https://download.geonames.org/export/dump/countryInfo.txt -o countryInfo.txt
echo "GeoNames data ready in $DEST"
