"""Locust load harness with three scenarios.

Run modes:
  locust -f locustfile.py --headless -u 10 -r 2  -t 60s --host http://localhost:8000   # baseline
  locust -f locustfile.py --headless -u 50 -r 10 -t 60s --host http://localhost:8000   # spike
  ERROR_RATE=0.2 locust -f locustfile.py ...                                            # sustained error
"""
from __future__ import annotations

import os
import random

from locust import HttpUser, between, task

ERROR_RATE = float(os.getenv("ERROR_RATE", "0.0"))

PROMPTS = [
    "Explain SLO burn-rate alerting in two sentences.",
    "What is cardinality and why does it matter?",
    "Recommend an observability stack for a 10-engineer startup.",
    "Translate to Vietnamese: 'Production model degradation is invisible without observability.'",
    "Hello.",
]


class InferenceUser(HttpUser):
    wait_time = between(0.1, 0.6)

    @task(10)
    def predict(self):
        prompt = random.choice(PROMPTS)
        force_fail = random.random() < ERROR_RATE
        with self.client.post(
            "/predict",
            json={"prompt": prompt, "model": "llama3-mock", "fail": force_fail},
            catch_response=True,
            name="POST /predict",
        ) as resp:
            if force_fail and resp.status_code == 503:
                resp.success()  # expected
            elif resp.status_code != 200:
                resp.failure(f"unexpected {resp.status_code}")
