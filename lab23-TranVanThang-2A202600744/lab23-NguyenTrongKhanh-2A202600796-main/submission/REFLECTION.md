# Day 23 Lab Reflection

**Student:** Nguyễn Trọng Khánh

**Submission date:** 2026-06-29

**Lab repo URL:** https://github.com/Honeybrew25/lab23-NguyenTrongKhanh-2A202600796

---

## 1. Hardware + setup output

`python 00-setup/verify-docker.py` produced:

```text
Docker:        OK  (29.5.3)
Compose v2:    OK  (5.1.4)
RAM available: 15.34 GB (OK)
Ports free:    OK
Report written: 00-setup/setup-report.json
```

The committed JSON report records `docker.ok`, `compose_v2.ok`, `ram_ok`, and
`all_ports_free` as `true`. Two unrelated local containers later occupied ports
3000 and 8000, so my untracked `.env` uses 3001 and 8001; the committed Compose
file retains rubric-compatible defaults through `${GRAFANA_PORT:-3000}` and
`${APP_PORT:-8000}`.

---

## 2. Track 02 — Dashboards & Alerts

### Dashboard evidence

- Overview: `submission/screenshots/dashboard-overview.png`
- Active gauge under load: `submission/screenshots/active-gauge.png`
- SLO burn rate: `submission/screenshots/slo-burn-rate.png`
- Cost and tokens: `submission/screenshots/cost-and-tokens.png`

During a 10-user run with 10% injected errors, Prometheus reported about 19.3
requests/s, P99 latency 0.248 s, 634 tokens/s, active requests = 2–3, estimated
cost = $1.76/hour, and 5-minute burn rate = 18.26. The non-zero cost panel is
computed from separate input/output token counters rather than request count.

### Alert fire + resolve

| When | What | Evidence |
|---|---|---|
| 11:29:34 ICT | stopped `day23-app` | `alertmanager-firing.png` |
| 11:30:52 ICT | `ServiceDown` became firing/active | Prometheus + Alertmanager APIs and `slack-firing.png` |
| 11:32:00 ICT | restored `day23-app` | container healthy |
| 11:33 ICT | `ServiceDown` resolved and disappeared | Alertmanager API and `slack-resolved.png` |

`send_resolved: true` is enabled for both Slack receivers. The real webhook
returned `ok`; the firing and resolved lifecycle completed with zero
Alertmanager notification errors. The webhook remains only in the untracked
`.env`, while the repository contains a safe placeholder.

### One thing that surprised me

A dashboard can look healthy while the error budget is being consumed very
quickly. The service still had sub-250 ms P99 latency, yet a roughly 10% error
ratio produced an 18× burn rate against a 99.5% SLO. Multi-window burn-rate
alerts therefore communicate operational urgency much better than a raw red
error-rate line.

---

## 3. Track 03 — Tracing & Logs

### Trace evidence

`submission/screenshots/jaeger-trace.png` shows trace
`40740f2359579c07bc3375f24293fe7c`: one `POST /predict` root with the three
children `embed-text`, `vector-search`, and `generate-tokens`. The attributes
panel includes `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.system`,
`gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, and
`gen_ai.response.finish_reasons`.

### Log line correlated to a trace

```json
{"model":"llama3-mock","input_tokens":4,"output_tokens":54,"quality":0.667,"duration_seconds":0.2431,"trace_id":"99a7461f2975fe4406ee84a6268777b0","event":"prediction served","level":"info","timestamp":"2026-06-29T04:09:50.761428Z"}
```

The `trace_id` is emitted in the response and structured JSON log, so an
operator can query the same identifier in Jaeger. The core lab obtains this
line from `docker logs day23-app`; Loki is healthy but the starter's seven-core-
service topology has no log shipper.

### Tail-sampling math

After the trace-context fix, the service produces approximately one trace per
request, or about 20 traces/s during this run. With healthy traffic, the 1%
policy retains `20 × 0.01 = 0.2 traces/s`, about 12/minute. At error fraction
`e = 0.10`, the composite OR policy retains all errors plus 1% of healthy
traffic: `e + (1-e)×0.01 = 0.10 + 0.90×0.01 = 0.109`, or about 10.9% overall.

The controlled error trace `4a423fa260595ecc6349f3940d419014` was retained,
while healthy trace `1f67cc23b6971d368ac78418ff81a3d0` was absent after the
30-second decision window. Collector counters also showed error-policy samples
and probabilistic samples independently, confirming that the policies are
combined by OR rather than chained filters.

---

## 4. Track 04 — Drift Detection

The full report is `04-drift-detection/reports/drift-report.html`. Summary:

```json
{
  "prompt_length": {"psi": 3.461, "kl": 1.7982, "ks_stat": 0.702, "ks_pvalue": 0.0, "drift": "yes"},
  "embedding_norm": {"psi": 0.0187, "kl": 0.0324, "ks_stat": 0.052, "ks_pvalue": 0.133853, "drift": "no"},
  "response_length": {"psi": 0.0162, "kl": 0.0178, "ks_stat": 0.056, "ks_pvalue": 0.086899, "drift": "no"},
  "response_quality": {"psi": 8.8486, "kl": 13.5011, "ks_stat": 0.941, "ks_pvalue": 0.0, "drift": "yes"}
}
```

For `prompt_length`, I would use PSI with fixed business-readable buckets: it
is stable for monitoring volume and its thresholds map cleanly to alerting. For
the scalar `embedding_norm`, KS is the direct non-parametric univariate test;
for the original embedding vectors I would use MMD because a norm can hide a
directional distribution shift. For `response_length`, KS avoids arbitrary bin
boundaries, while PSI remains useful as the dashboard statistic. For bounded
`response_quality`, I would use KS for detection and KL only when the quality
histogram is carefully smoothed; KL is asymmetric and zero-probability bins can
otherwise dominate. In short: PSI is operationally interpretable, KS is strong
for scalar continuous features, KL compares normalized distributions, and MMD
is the better choice for high-dimensional embeddings.

---

## 5. Track 05 — Cross-Day Integration

Day 19 is connected reproducibly as a Compose-managed Qdrant-shaped stub and is
scraped by Prometheus as `day19-stub`; `day19_qdrant_collections` returned 3.
Grafana provisions the Cross-Day dashboard separately and renders all six Day
16/17/18/19/20/22 panels, allowing absent sources to fail soft as “No data”.

The hardest prior-day metric would be Day 22's `dpo_eval_pass_rate`. Unlike
Qdrant's always-on `/metrics`, pass rate only exists after an evaluation job, so
it needs a durable push/recording step, run identity, model-version labels, and
staleness handling. A bare gauge without those lifecycle details can look valid
long after the evaluated model has changed.

---

## 6. The single change that mattered most

The most important change was making `POST /predict` a **current root span**.
The starter created a span with `start_span()` but never attached it to the
current context, so the three stages appeared as four unrelated one-span
traces. Metrics said the service was working, but a trace could not explain
where one request spent its time. Wrapping the request with
`start_as_current_span()` immediately produced one causal tree with the exact
critical path from embedding to retrieval to generation.

This also made tail sampling semantically correct. A forced 503 now marks the
root span as `ERROR`, so the collector's keep-errors policy retains the entire
request, not an isolated fragment. This connects the deck's tracing and
sampling concepts: instrumentation is useful only when context propagation
preserves causality, and sampling decisions are useful only when they operate
on that complete causal unit.
