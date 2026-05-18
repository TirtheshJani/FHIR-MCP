#!/usr/bin/env bash
set -euo pipefail
OUT_DIR="${1:-./examples/synthea_raw}"
mkdir -p "$OUT_DIR"
if [ ! -f synthea-with-dependencies.jar ]; then
  curl -L -o synthea-with-dependencies.jar \
    https://github.com/synthetichealth/synthea/releases/latest/download/synthea-with-dependencies.jar
fi
java -jar synthea-with-dependencies.jar \
  -p 100 \
  --exporter.fhir.export true \
  --exporter.fhir.version R4 \
  --generate.only_alive_patients true \
  --exporter.baseDirectory "$OUT_DIR" \
  --generate.demographics.default_file geography/demographics.csv \
  Massachusetts
