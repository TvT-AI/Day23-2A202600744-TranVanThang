"""Stub scraper for Day 19's Qdrant vector store.

If DAY19_QDRANT_URL is set, just confirms the /metrics endpoint is reachable.
Otherwise, runs a stub HTTP server that emits fake Qdrant-shaped metrics so
the cross-day dashboard panel still renders.
"""
from __future__ import annotations

import os
import time

import requests
from prometheus_client import Counter, Gauge, start_http_server


def real_scrape(url: str) -> None:
    while True:
        try:
            r = requests.get(url, timeout=2)
            print(f"day19 qdrant /metrics: {r.status_code} ({len(r.content)} bytes)")
        except requests.exceptions.RequestException as e:
            print(f"day19 qdrant unreachable: {e}")
        time.sleep(15)


def stub_emit() -> None:
    qdrant_collections = Gauge("day19_qdrant_collections", "Stub: Qdrant collection count")
    qdrant_search_total = Counter("day19_qdrant_search_total", "Stub: Qdrant search calls")
    start_http_server(9101)
    print("Stub Day 19 metrics on :9101 (add to prometheus.yml as 'day19-stub')")
    qdrant_collections.set(3)
    while True:
        qdrant_search_total.inc()
        time.sleep(1)


def main() -> int:
    url = os.getenv("DAY19_QDRANT_URL", "")
    if url:
        real_scrape(url)
    else:
        stub_emit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
