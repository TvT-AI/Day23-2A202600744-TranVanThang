# 01 — Instrument a FastAPI AI service

A mock LLM inference service that emits **all 6 OTel signals**: metrics, traces, logs, plus simulated GPU gauges. The app is the load target for tracks 02-04.

## What's instrumented

- **Prometheus metrics** at `/metrics`:
  - `inference_requests_total{model,status}` — Counter (RED: rate + errors)
  - `inference_latency_seconds_bucket{model}` — Histogram (RED: duration)
  - `inference_active_gauge` — Gauge (USE: in-flight requests)
  - `gpu_utilization_percent` — Gauge (USE: GPU util — simulated)
  - `inference_tokens_total{model,direction}` — Counter (AI 4th pillar)
  - `inference_quality_score{model}` — Gauge (eval-as-metric stub)

- **OpenTelemetry traces** via OTLP gRPC → otel-collector:4317
  - Auto-instrumentation: FastAPI handler spans + outbound `requests` calls
  - Manual spans: `embed-text`, `vector-search`, `generate-tokens` (deck §7)

- **Structured JSON logs** via `structlog` → stdout → **Grafana Alloy** / OTel Collector → Loki
  - Every log line carries `trace_id`, `span_id`, `model`, `request_id`

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | Liveness — used by Compose health-check |
| `POST /predict` | Mock LLM inference (deterministic random latency) |
| `GET /metrics` | Prometheus exposition |

## Run standalone (without the full stack)

```bash
cd app
pip install -r ../../requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
# In another shell:
curl localhost:8000/metrics | head -40
```

## Submission checkpoint (20 pts)

- 5 pts: `/metrics` exposes all 6 metric families above
- 5 pts: spans visible in Jaeger UI for `POST /predict`
- 5 pts: log line in Loki contains `trace_id` matching the request
- 5 pts: `inference_active_gauge` rises during load and returns to 0 after
