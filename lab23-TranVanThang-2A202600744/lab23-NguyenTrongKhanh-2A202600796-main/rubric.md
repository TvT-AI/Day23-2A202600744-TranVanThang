# Day 23 Lab Rubric

**Core: 100 points · Bonus: 30 points (additive, not gating)**

Grader runs `make verify` from a clean clone. Exit code 0 = all core checkpoints pass.

---

## Core (100 pts)

| # | Track | Pts | Checkpoint | How verified |
|---|---|---|---|---|
| 1 | 00-setup       | 5  | `setup-report.json` committed     | file exists in `submission/` or `00-setup/` |
| 2 | 01 instrument  | 5  | `/metrics` exposes `inference_requests_total` | curl + grep |
| 3 | 01 instrument  | 5  | `/metrics` exposes `inference_latency_seconds_bucket` | curl + grep |
| 4 | 01 instrument  | 5  | `/metrics` exposes `inference_active_gauge` (rises during load, returns to 0) | screenshot |
| 5 | 01 instrument  | 5  | `inference_quality_score` and `inference_tokens_total` present (4th-pillar) | curl + grep |
| 6 | 02 dashboards  | 5  | 3 Day-23 dashboards loaded automatically | Grafana API search |
| 7 | 02 dashboards  | 5  | Overview dashboard 6 panels render with data after load | screenshot |
| 8 | 02 dashboards  | 5  | SLO burn-rate dashboard populates burn rates                 | screenshot |
| 9 | 02 dashboards  | 5  | Cost-and-tokens dashboard shows non-zero $/hr estimate       | screenshot |
| 10 | 02 alerts     | 5  | `make alert` triggers `ServiceDown` in Alertmanager     | screenshot |
| 11 | 02 alerts     | 5  | Slack receives both fire AND resolve messages           | screenshot |
| 12 | 03 tracing    | 5  | Jaeger UI shows trace for `POST /predict` w/ 3 child spans | screenshot |
| 13 | 03 tracing    | 5  | Span attributes follow GenAI semantic conventions       | screenshot of attrs panel |
| 14 | 03 tracing    | 5  | tail-sampling: forced-error trace retained, healthy trace dropped (math in REFLECTION) | REFLECTION text |
| 15 | 03 logs       | 5  | At least one structured JSON log line with `trace_id` (paste in REFLECTION) | REFLECTION text |
| 16 | 04 drift      | 5  | `drift-summary.json` exists & shows ≥1 feature with `drift: yes` | file content |
| 17 | 04 drift      | 5  | Evidently HTML report renders                           | screenshot |
| 18 | 04 drift      | 5  | REFLECTION explains which test (PSI/KL/KS/MMD) fits which feature type | REFLECTION text |
| 19 | 05 integ      | 5  | At least 1 prior-day source connected (real or stub)    | screenshot of cross-day dashboard |
| 20 | 05 integ      | 5  | Cross-day dashboard renders with all 6 panels (data or "No Data") | screenshot |
| 21 | reflection    | 5  | REFLECTION.md exists, sections 1-5 filled               | length + spot-check |
| 22 | reflection    | 10 | "The single change that mattered most" paragraph (graded for substance, not length) | grader read |

---

## Bonus (20 pts, optional, additive)

| # | Bonus | Pts | Checkpoint |
|---|---|---|---|
| B1 | BONUS-ebpf-profiling | +10 | Pyroscope flame graph for `day23-app` Python process (Linux/WSL only) |
| B2 | BONUS-llm-native-obs | +10 | Langfuse self-hosted, capture 1 LangChain LLM trace |
| B3 | BONUS-agentops | +10 | `agentops-report.json` + Jaeger span-tree screenshot (`day23-agent`) **+** one extension (instrument your own agent / SLIs→Grafana / new failure mode / `--real-llm`); REFLECTION on pass^k vs pass@k |

---

## Failing checkpoints

If `make verify` exits non-zero:

1. Check Compose stack health: `make smoke`
2. Check the specific failing line in `verify.py` output
3. Common issues:
   - Grafana not yet provisioned dashboards (wait 30s after first `up`)
   - Slack webhook unset or wrong URL → no fire/resolve evidence
   - Drift script not run yet → no `drift-summary.json`
   - REFLECTION.md too short (< 500 chars) → re-fill

---

## Grading philosophy

We grade your **report**, not your absolute numbers. P99 latency on M1 vs RTX 4090 is wildly different — what matters is that you measured it, dashboarded it, alerted on it, and can explain what you'd change.
