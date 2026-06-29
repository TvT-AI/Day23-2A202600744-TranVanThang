# 02 — Prometheus, Grafana & Alertmanager

Scraping config, dashboards-as-code, and SLO burn-rate alerting.

## What's in here

```
prometheus/
├── prometheus.yml          # main scrape config
├── rules/
│   ├── slo-burn-rate.yml   # multi-window multi-burn-rate (deck §6)
│   └── ai-quality.yml      # latency, error rate, drift gauge alerts
alertmanager/
└── alertmanager.yml        # severity routing → Slack
grafana/
├── provisioning/datasources/prometheus.yml
├── provisioning/dashboards/dashboards.yml
└── dashboards/
    ├── ai-service-overview.json   # 6 panels: RPS / P50-95-99 / errors / GPU / tokens / cost
    ├── slo-burn-rate.json         # error budget remaining + burn rate panels
    └── cost-and-tokens.json       # token throughput + estimated cost
load-test/
└── locustfile.py           # baseline + spike + sustained-error scenarios
```

## What students do

1. Open <http://localhost:3000> (admin/admin) — confirm 3 dashboards loaded
2. `make load` — run Locust at 10 concurrent users for 60s
3. Watch RPS panel rise, P99 stay below 500ms
4. `make alert` — kill the app container; watch:
   - `HighInferenceLatency` and `ServiceDown` fire in <http://localhost:9093>
   - Slack webhook receives the message (if configured)
   - Alert resolves automatically after the app is restored
5. Take screenshots for `submission/`

## Submission checkpoint (25 pts)

- 5 pts: 3 dashboards loaded automatically (no manual import)
- 5 pts: 6 essential panels render with non-zero data after `make load`
- 5 pts: SLO burn-rate panel populates after ~15 min of load
- 5 pts: at least 2 alert rules fire AND resolve in Alertmanager during `make alert`
- 5 pts: Slack receives both fire + resolve messages (screenshot)
