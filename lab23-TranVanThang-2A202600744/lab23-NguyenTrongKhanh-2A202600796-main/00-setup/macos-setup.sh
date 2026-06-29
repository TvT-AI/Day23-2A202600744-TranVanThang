#!/usr/bin/env bash
## macOS pre-flight check.

set -euo pipefail

echo "Checking macOS lab prerequisites..."

if ! pgrep -q Docker; then
  echo "ERROR: Docker Desktop is not running."
  echo "  Start it from Applications, wait ~30s, then re-run."
  exit 1
fi

# Check Docker Desktop memory limit (recommendation, not hard fail)
mem_bytes=$(docker info --format '{{.MemTotal}}' 2>/dev/null || echo 0)
mem_gb=$((mem_bytes / 1024 / 1024 / 1024))
if [ "$mem_gb" -lt 4 ]; then
  echo "WARNING: Docker Desktop has only ${mem_gb} GB allocated."
  echo "  Increase via: Docker Desktop > Settings > Resources > Memory >= 6 GB"
fi

# Apple Silicon? Note that some images may run under emulation.
if [ "$(uname -m)" = "arm64" ]; then
  echo "INFO: Apple Silicon detected. All images in this lab support arm64 natively."
fi

echo "macOS setup OK."
