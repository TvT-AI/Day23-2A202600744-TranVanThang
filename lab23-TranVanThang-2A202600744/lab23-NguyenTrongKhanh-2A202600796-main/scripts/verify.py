"""Rubric gate. Exit 0 only if all submission checkpoints pass.

Run: python3 scripts/verify.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

LAB = Path(__file__).resolve().parent.parent
SUBMISSION = LAB / "submission"


def load_local_env() -> None:
    """Load simple KEY=VALUE entries without adding another dependency."""
    env_file = LAB / ".env"
    if not env_file.exists():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_local_env()
APP_PORT = os.getenv("APP_PORT", "8000")
GRAFANA_PORT = os.getenv("GRAFANA_PORT", "3000")
APP_URL = f"http://localhost:{APP_PORT}"
GRAFANA_URL = f"http://localhost:{GRAFANA_PORT}"


def check(label: str, ok: bool, detail: str = "") -> bool:
    icon = "[PASS]" if ok else "[FAIL]"
    line = f"{icon} {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    return ok


def http_ok(url: str, timeout: float = 3.0) -> bool:
    try:
        return requests.get(url, timeout=timeout).status_code == 200
    except requests.exceptions.RequestException:
        return False


def main() -> int:
    results: list[bool] = []

    # 00-setup
    setup_report = LAB / "00-setup" / "setup-report.json"
    results.append(check(
        "00-setup: setup-report.json committed",
        setup_report.exists(),
        f"path={setup_report}",
    ))

    # 01-instrument-fastapi
    results.append(check(
        "01: app /healthz reachable",
        http_ok(f"{APP_URL}/healthz"),
    ))

    metric_text = ""
    try:
        metric_response = requests.get(f"{APP_URL}/metrics", timeout=3)
        if metric_response.status_code == 200:
            metric_text = metric_response.text
    except requests.exceptions.RequestException:
        pass

    required_metrics = (
        "inference_requests_total",
        "inference_latency_seconds_bucket",
        "inference_active_gauge",
        "inference_quality_score",
        "inference_tokens_total",
        "gpu_utilization_percent",
    )
    results.append(check(
        "01: /metrics exposes all 6 required metric families",
        all(metric in metric_text for metric in required_metrics),
        "missing=" + ",".join(metric for metric in required_metrics if metric not in metric_text),
    ))

    # 02-prometheus-grafana
    results.append(check("02: Prometheus reachable", http_ok("http://localhost:9090/-/healthy")))
    results.append(check("02: Grafana reachable", http_ok(f"{GRAFANA_URL}/api/health")))
    results.append(check("02: Alertmanager reachable", http_ok("http://localhost:9093/-/healthy")))

    # Verify dashboards loaded (Grafana API)
    try:
        r = requests.get(
            f"{GRAFANA_URL}/api/search?query=Day%2023",
            auth=("admin", "admin"),
            timeout=3,
        )
        dashboards = r.json() if r.status_code == 200 else []
        dashboard_uids = {
            item.get("uid") for item in dashboards if item.get("type") == "dash-db"
        }
    except Exception:
        dashboard_uids = set()
    required_dashboard_uids = {
        "day23-ai-overview",
        "day23-cost-tokens",
        "day23-slo",
        "day23-cross-day",
    }
    results.append(check(
        "02: 3 core dashboards + Cross-Day dashboard loaded",
        required_dashboard_uids <= dashboard_uids,
        f"found={len(dashboard_uids)}",
    ))

    integration_ok = False
    try:
        response = requests.get(
            "http://localhost:9090/api/v1/query",
            params={"query": "day19_qdrant_collections"},
            timeout=3,
        )
        integration_ok = bool(response.json().get("data", {}).get("result", []))
    except (requests.exceptions.RequestException, ValueError):
        pass
    results.append(check("05: Day 19 integration metric has data", integration_ok))

    # 03-tracing-and-logs
    results.append(check("03: Jaeger UI reachable", http_ok("http://localhost:16686/")))
    results.append(check("03: Loki ready", http_ok("http://localhost:3100/ready")))
    results.append(check("03: OTel Collector self-metrics reachable", http_ok("http://localhost:8888/metrics")))

    # 04-drift-detection
    drift_summary = LAB / "04-drift-detection" / "reports" / "drift-summary.json"
    drift_ok = False
    if drift_summary.exists():
        try:
            data = json.loads(drift_summary.read_text(encoding="utf-8"))
            drift_ok = any(m.get("drift") == "yes" for m in data.values())
        except json.JSONDecodeError:
            pass
    results.append(check("04: drift-summary.json shows at least one drifted feature", drift_ok))
    drift_html = LAB / "04-drift-detection" / "reports" / "drift-report.html"
    results.append(check(
        "04: Evidently HTML report exists and is non-trivial",
        drift_html.exists() and drift_html.stat().st_size > 10_000,
    ))

    # Submission
    reflection = SUBMISSION / "REFLECTION.md"
    reflection_text = reflection.read_text(encoding="utf-8") if reflection.exists() else ""
    reflection_sections = all(f"## {number}." in reflection_text for number in range(1, 7))
    results.append(check(
        "submission: REFLECTION.md sections 1-6 are filled",
        len(reflection_text) > 500 and reflection_sections,
    ))
    results.append(check(
        "submission: single-change paragraph is present",
        "The single change that mattered most" in reflection_text
        and len(reflection_text.split("## 6.", 1)[-1].strip()) > 300,
    ))

    required_screenshots = (
        "dashboard-overview.png",
        "active-gauge.png",
        "slo-burn-rate.png",
        "cost-and-tokens.png",
        "alertmanager-firing.png",
        "slack-firing.png",
        "slack-resolved.png",
        "jaeger-trace.png",
        "jaeger-attributes.png",
        "drift-report.png",
        "cross-day-dashboard.png",
    )
    screenshot_dir = SUBMISSION / "screenshots"
    for name in required_screenshots:
        screenshot = screenshot_dir / name
        results.append(check(
            f"submission screenshot: {name}",
            screenshot.exists() and screenshot.stat().st_size > 10_000,
        ))

    print()
    passed = sum(results)
    total = len(results)
    print(f"Result: {passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
