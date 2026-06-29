# BONUS — eBPF Continuous Profiling (B1, +10 pts)

> **Linux / WSL2 only** (eBPF needs a Linux kernel ≥ 5.8 with `CAP_BPF`). Not runnable on native macOS/Windows Docker Desktop — use a Linux VM or WSL2.
>
> Maps to **deck §9 (eBPF, Continuous Profiling & Observability 2.0)**. Goal: get a **flame graph** of the `day23-app` Python process **without changing app code** — the "4th signal" the deck introduces.

## What you'll build

Add **Grafana Pyroscope** + the eBPF profiler to the existing stack and view a CPU flame graph of the FastAPI app under load.

```
day23-app (Python)  ──eBPF (whole-system, zero-code)──▶  Pyroscope  ──▶  Grafana (Flame Graph + Traces↔Profiles)
```

Two zero-code paths (pick one):

- **Grafana Alloy `pyroscope.ebpf`** — Alloy discovers processes and profiles them via eBPF. Deck-aligned (Alloy replaced Promtail/Agent; Beyla→OBI is the OTel sibling).
- **Pyroscope `ebpf` agent** standalone — same idea, fewer moving parts.

## Steps

1. Drop this into `docker-compose.override.yml` at the repo root (Compose auto-merges it):

```yaml
services:
  pyroscope:
    image: grafana/pyroscope:1.14.0      # Pyroscope 2.0 line (diskless, OTLP profiles)
    ports: ["4040:4040"]
    networks: [obs]

  alloy:
    image: grafana/alloy:v1.10.0
    privileged: true                      # eBPF needs this
    pid: "host"                           # see all host processes
    volumes:
      - ./BONUS-ebpf-profiling/alloy-ebpf.river:/etc/alloy/config.river:ro
    command: ["run", "/etc/alloy/config.river"]
    networks: [obs]
```

2. `alloy-ebpf.river` (zero-code eBPF profiling of the app container):

```river
discovery.process "all" { }

pyroscope.ebpf "default" {
  forward_to = [pyroscope.write.local.receiver]
  targets    = discovery.process.all.targets
}

pyroscope.write "local" {
  endpoint { url = "http://pyroscope:4040" }
}
```

3. Add a **Pyroscope datasource** in Grafana (`Connections → Add data source → Grafana Pyroscope`, URL `http://pyroscope:4040`).

4. Generate load and watch the flame graph:

```bash
make up           # core stack
docker compose up -d pyroscope alloy
make load         # 60s locust load
# Grafana → Explore → Pyroscope → service "day23-app" → Flame Graph
```

## Deliverable (B1)

- `submission/screenshots/flamegraph.png` — a CPU flame graph of `day23-app` under load, with the hot path visible (tokenizer / inference loop / serialization).
- 2–3 sentences in `submission/REFLECTION.md`: which function dominated CPU, and one optimization the flame graph suggests.

## Going further (deck §9)

- **Span profiles**: wire `trace_id`/`span_id` so a slow Jaeger span links straight to its flame graph (Grafana *Traces → Profiles*).
- **GPU hot-path**: on a GPU box, try `parca-agent` CUDA profiling (CUPTI→eBPF) — the first OSS always-on GPU profiler.
- **OBI (ex-Beyla)**: swap `pyroscope.ebpf` for OBI to *also* get zero-code RED metrics + traces from the kernel.

> Status note (2026-06): OTel **Profiles** signal is still **Public Alpha** — great for labs, not yet for critical production. Pin versions and re-check component READMEs.
