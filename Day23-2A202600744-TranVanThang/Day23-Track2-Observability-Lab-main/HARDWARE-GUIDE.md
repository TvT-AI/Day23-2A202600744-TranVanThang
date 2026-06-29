# Hardware Guide — Day 23 Lab

The lab runs **7 containers** simultaneously. Most laptops can handle it, but pre-flight checks save a lot of "why isn't anything working" debugging.

## Minimum requirements

| Resource | Min | Recommended |
|---|---|---|
| RAM (free, after OS + browser) | 4 GB | 8 GB |
| Docker Desktop memory limit (Mac/Win) | 4 GB | 6 GB |
| Disk space | 10 GB | 20 GB |
| CPU | 4 cores | 8 cores |

## Per-platform notes

### macOS (Apple Silicon — M1/M2/M3)

- All 7 images publish `linux/arm64` natively. No emulation needed.
- Docker Desktop default memory limit is **2 GB** — increase via Settings → Resources → Memory ≥ **6 GB**.
- File watcher: `make logs` may consume CPU; switch off when idle.

### macOS (Intel)

- Same as above. Most images run faster on Intel actually (no emulation overhead for pre-built x86 layers).
- Docker Desktop is heavier on Intel — close other apps.

### Linux

- No memory limit by default — uses host RAM directly.
- Confirm `docker` group membership: `groups | grep docker`. If absent: `sudo usermod -aG docker $USER && newgrp docker`.
- Docker Compose v2 plugin: `docker compose version` — if missing, install via `apt-get install docker-compose-plugin`.

### Windows + WSL2

- **Run `make` commands from a WSL2 shell**, not PowerShell native. PowerShell doesn't have `make`, and Compose v2 path resolution has quirks.
- WSL2 must be enabled: `wsl --status` should show `Default Version: 2`.
- Docker Desktop must have **WSL2 integration** enabled for your distro.

## Resource budget

Approximate steady-state per service (after `make up`, no load):

| Service | RAM | CPU |
|---|---|---|
| app (FastAPI)            | 80 MB  | <1% |
| prometheus               | 200 MB | 1-3% |
| alertmanager             | 60 MB  | <1% |
| grafana                  | 250 MB | 1-2% |
| loki                     | 150 MB | 1% |
| jaeger                   | 200 MB | <1% |
| otel-collector           | 100 MB | 1% |
| **Total steady-state**   | **~1 GB** | **~5-10%** of one core |

Under `make load` (10 concurrent users):

| Service | RAM | CPU |
|---|---|---|
| app                      | 200 MB | 30-60% |
| prometheus               | 250 MB | 5% |
| otel-collector           | 200 MB | 5-10% (tail-sampling buffer) |
| **Total under load**     | **~1.5 GB** | **~50%** of one core |

If you have only 4 GB free RAM:
- Skip `BONUS-ebpf-profiling/` (Pyroscope adds ~300 MB)
- Skip `BONUS-llm-native-obs/` (Langfuse + Postgres adds ~600 MB)
- Reduce locust concurrency: `locust -u 5 -r 1 ...`

## What if I don't have Docker?

The drift detection track (`04-drift-detection/`) **runs in Colab** — see `04-drift-detection/colab/`. The other 4 tracks need Docker.

We considered a "Lite" path (no Docker), but observability is fundamentally a multi-process distributed-systems story — Prometheus + Grafana + Loki + Jaeger as 5 daemons via Homebrew/apt is *more* fragile than `docker compose up`.

## Common failures

| Symptom | Cause | Fix |
|---|---|---|
| `make smoke` fails on grafana       | Provisioning not yet complete         | Wait 30s, retry |
| `make alert` doesn't fire            | Alert needs ~90s of failure dwell     | Be patient (or shorten `for: 1m` in alert rules for the demo) |
| Slack receives nothing               | Webhook URL invalid                   | `curl -X POST $SLACK_WEBHOOK_URL -d '{"text":"test"}'` |
| Out of memory                        | Docker Desktop limit too low          | Settings → Resources → Memory ≥ 6 GB |
| Port already bound                   | Another process holds 3000/9090/etc.  | `lsof -i :3000` to find offender |
