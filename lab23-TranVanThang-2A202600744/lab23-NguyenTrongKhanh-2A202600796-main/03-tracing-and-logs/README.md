# 03 — Distributed Tracing + Logs

OTel Collector with **tail-sampling**, Jaeger backend, Loki for logs.

## What's wired

- `app` → OTLP/gRPC (4317) → `otel-collector` → Jaeger (traces)
- `app` stdout JSON → `otel-collector` filelog receiver → Loki (logs)
- Grafana datasource for Loki has a **derived field** that auto-extracts
  `trace_id` from log lines and links to Jaeger — click a log → jump to its trace.

## Sampling policy

The collector is configured with a **composite tail-sampling policy**:

1. Keep 100% of traces with `status_code == ERROR`
2. Keep 100% of traces with span duration `> 2s`
3. Keep 1% of healthy traces (random)

Buffer: 30s decision window, ~10K spans memory.

See `otel-collector/sampling-policies.md` for the math.

## Submission checkpoint (20 pts)

- 5 pts: end-to-end trace screenshot from Jaeger for `POST /predict`
- 5 pts: span flame graph shows `embed-text → vector-search → generate-tokens`
- 5 pts: log line in Loki contains `trace_id`, click correlates to Jaeger
- 5 pts: tail-sampling policy verified (kill app once → all error traces kept)
