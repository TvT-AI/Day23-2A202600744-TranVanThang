# Verified runtime evidence

Collected on 2026-06-29 (Asia/Bangkok) from the running Compose stack.

| Check | Observed result |
|---|---|
| Compose | app, Prometheus, Grafana, Alertmanager, Loki, Jaeger, OTel Collector and Day 19 stub running |
| Prometheus targets | `inference-api`, `day19-stub`, `otel-collector`, `prometheus` all `up` |
| Grafana provisioning | four dashboards plus the `AICB Day 23` folder returned by `/api/search` |
| Load | ~19.3 RPS, P99 ~0.248 s, active gauge 2–3 |
| AI metrics | ~634 tokens/s; estimated cost ~$1.76/hour |
| SLO | 5m burn 18.26; 1h burn 19.40; `SLOFastBurn` firing |
| Integration | `day19_qdrant_collections = 3` |
| Nested trace | `40740f2359579c07bc3375f24293fe7c`, 4 spans |
| Tail sampling | error `4a423fa260595ecc6349f3940d419014` retained; healthy `1f67cc23b6971d368ac78418ff81a3d0` dropped |
| ServiceDown | fired at 11:30:52 ICT; resolved after restore; zero Slack notification errors |
| Slack webhook | direct connectivity test returned `ok`; secret kept only in `.env` |
| Drift | `prompt_length` PSI 3.461 and `response_quality` PSI 8.8486 |

Machine-readable setup and drift evidence live in `00-setup/setup-report.json`
and `04-drift-detection/reports/drift-summary.json`; the full Evidently report
is `04-drift-detection/reports/drift-report.html`.
