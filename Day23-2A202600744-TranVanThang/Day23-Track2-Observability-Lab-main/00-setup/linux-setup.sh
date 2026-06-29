#!/usr/bin/env bash
## Linux pre-flight check.

set -euo pipefail

echo "Checking Linux lab prerequisites..."

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker not installed."
  echo "  Ubuntu/Debian: https://docs.docker.com/engine/install/ubuntu/"
  exit 1
fi

# Group membership check (avoids sudo for every docker command)
if ! groups | grep -q docker; then
  echo "WARNING: \$USER is not in the 'docker' group."
  echo "  Fix:  sudo usermod -aG docker \$USER  &&  newgrp docker"
fi

# systemd service active?
if ! systemctl is-active --quiet docker 2>/dev/null; then
  echo "WARNING: docker service not active."
  echo "  Start:  sudo systemctl start docker  &&  sudo systemctl enable docker"
fi

# Compose v2?
if ! docker compose version >/dev/null 2>&1; then
  echo "ERROR: Compose v2 plugin not installed."
  echo "  Install: https://docs.docker.com/compose/install/linux/"
  exit 1
fi

echo "Linux setup OK."
