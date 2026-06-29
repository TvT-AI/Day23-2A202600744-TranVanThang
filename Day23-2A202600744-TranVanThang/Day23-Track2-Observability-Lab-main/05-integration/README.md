# 05 — Integration with Days 16-22

Day 23 is the **integrative day** for Phase 2 Track 2. This track wires the observability stack to artifacts from prior days.

## What gets monitored from where

| Source day | What | How |
|---|---|---|
| 16 cloud infra | EC2/EKS hosts | `node_exporter` scrape (configure target in `prometheus.yml`) |
| 17 data pipeline | Airflow DAG | `airflow_dag_run_duration` via `statsd_exporter` |
| 18 lakehouse | Spark / Delta | Spark UI metrics → Prometheus |
| 19 vector store | Qdrant | scrape `host.docker.internal:6333/metrics` |
| 20 model serving | llama.cpp | scrape `host.docker.internal:8080/metrics` |
| 21 (skipped) | — | not yet authored as of 2026-05 |
| 22 alignment | DPO model | push `dpo_eval_pass_rate` gauge via `monitor-day22-alignment.py` |

## Run

If you have prior days running locally:

```bash
# In .env:
DAY19_QDRANT_URL=http://host.docker.internal:6333
DAY20_LLAMACPP_METRICS_URL=http://host.docker.internal:8080/metrics

# Then enable the prometheus.yml job stanzas (uncomment the blocks)
make restart
```

If you don't have prior days running, the integration scripts will **stub** the metrics so the cross-day dashboard still renders.

## Cross-day dashboard

`full-stack-dashboard.json` shows one panel per source day. Designed to fail-soft — panels with no data show "No Data" rather than breaking.

## Submission checkpoint (15 pts)

- 5 pts: at least 1 prior-day source actually scraped (or stub script running)
- 5 pts: cross-day dashboard renders with all 6 panels (data or "No Data")
- 5 pts: REFLECTION.md describes which prior-day metric was hardest to expose
