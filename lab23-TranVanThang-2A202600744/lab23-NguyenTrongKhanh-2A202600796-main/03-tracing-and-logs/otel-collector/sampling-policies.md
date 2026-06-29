# Tail-Sampling Policy Math

The lab's collector keeps:

| Policy | Keep rate | Why |
|---|---|---|
| `keep-errors` (status_code = ERROR) | 100% | Errors are rare and high-information; never drop. |
| `keep-slow` (latency > 2s) | 100% | P99 outliers are the reason you'd want a trace. |
| `probabilistic-1pct` | 1% | Healthy baseline for capacity planning. |

## Sampled count formula

For a service producing `N` traces / sec:

```
sampled = N × (P(error) × 1.0 + P(slow ∧ ¬error) × 1.0 + P(healthy) × 0.01)
```

For typical web traffic (1% errors, 1% slow, 98% healthy):

```
sampled = N × (0.01 + 0.01 + 0.98 × 0.01)
        = N × 0.0298
        ≈ 3% retention
```

Cost reduction: **~97%** vs. retain-everything.

## Buffer cost

Tail-sampling requires the collector to **hold every span until the trace is complete**:

- `decision_wait: 30s` — wait this long before deciding
- `num_traces: 50000` — circular buffer cap
- Memory: ~100 bytes/span × 50K traces × ~10 spans/trace ≈ **50 MB RAM**

Scale headroom: this lab handles up to ~1500 traces / sec before the buffer overflows
(buffer holds 30s of traffic, so 50K / 30 = 1666). For higher rates: increase
`num_traces` or move to head-sampling at the edge.

## Anti-patterns

- **Tail-sample without `keep-errors` policy.** You lose the traces you most need.
- **Probabilistic 0.01% across the board.** Below ~1% you stop seeing tail latency reliably.
- **Tail-sampling at scale > 10K spans/sec on one collector.** Use a hashmod load-balancer in front to ensure all spans of a trace land on the same collector instance.
