"""Stub scraper for Day 20's llama.cpp inference server.

llama.cpp's HTTP server doesn't natively expose Prometheus metrics — Day 20's
lab patched in basic counters via a sidecar. This script either tails that
sidecar (DAY20_LLAMACPP_METRICS_URL) or emits stub metrics shaped like what
Day 20 would emit.
"""
from __future__ import annotations

import os
import random
import time

import requests
from prometheus_client import Counter, Gauge, start_http_server


def real_scrape(url: str) -> None:
    while True:
        try:
            r = requests.get(url, timeout=2)
            print(f"day20 llama.cpp /metrics: {r.status_code} ({len(r.content)} bytes)")
        except requests.exceptions.RequestException as e:
            print(f"day20 llama.cpp unreachable: {e}")
        time.sleep(15)


def stub_emit() -> None:
    tps = Gauge("day20_llamacpp_tokens_per_second", "Stub: tokens/sec")
    queue = Gauge("day20_llamacpp_queue_depth", "Stub: in-flight requests")
    completions = Counter("day20_llamacpp_completions_total", "Stub: total completions")
    start_http_server(9102)
    print("Stub Day 20 metrics on :9102 (add to prometheus.yml as 'day20-stub')")
    while True:
        tps.set(20 + random.gauss(0, 3))
        queue.set(max(0, int(random.gauss(2, 1))))
        completions.inc()
        time.sleep(1)


def main() -> int:
    url = os.getenv("DAY20_LLAMACPP_METRICS_URL", "")
    if url:
        real_scrape(url)
    else:
        stub_emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
