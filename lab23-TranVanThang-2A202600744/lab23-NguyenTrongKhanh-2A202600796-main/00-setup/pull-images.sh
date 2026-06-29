#!/usr/bin/env bash
## Pre-pull all Docker images so the first `make up` doesn't take 10 minutes.
## Idempotent — re-running is safe.

set -euo pipefail

IMAGES=(
  "prom/prometheus:v2.55.0"
  "prom/alertmanager:v0.27.0"
  "grafana/grafana:11.3.0"
  "grafana/loki:3.3.0"
  "jaegertracing/all-in-one:1.62.0"
  "otel/opentelemetry-collector-contrib:0.114.0"
)

echo "Pre-pulling ${#IMAGES[@]} images (the FastAPI app builds locally)..."
for img in "${IMAGES[@]}"; do
  echo "  pulling: $img"
  docker pull --quiet "$img" >/dev/null
done

echo "All images cached."
