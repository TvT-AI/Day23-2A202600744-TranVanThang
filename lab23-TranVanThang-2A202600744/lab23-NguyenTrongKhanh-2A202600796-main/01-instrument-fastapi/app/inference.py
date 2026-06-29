"""Mock LLM inference. Deterministic random latency + token counts.

Real LLMs aren't needed for the observability lab — we want predictable load
shapes so students can verify their dashboards/alerts behave correctly.
"""
from __future__ import annotations

import hashlib
import math
import random
import time


def _seeded_rng(prompt: str) -> random.Random:
    digest = hashlib.sha256(prompt.encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def simulate_inference(prompt: str, model: str) -> tuple[str, int, int, float]:
    """Returns (response_text, input_tokens, output_tokens, quality_score)."""
    rng = _seeded_rng(prompt + model)
    in_toks = max(4, len(prompt.split()))
    out_toks = rng.randint(8, 64)
    # Latency: log-normal distribution to mimic real LLM tail behavior
    base = 0.05 + abs(rng.gauss(0.15, 0.10))
    # 1% chance of a slow-tail (simulates GPU contention / cache miss)
    if rng.random() < 0.01:
        base += rng.uniform(0.5, 2.0)
    time.sleep(base)
    quality = max(0.0, min(1.0, rng.gauss(0.82, 0.05)))
    text = f"[mock] {model} replied to '{prompt[:32]}...' with {out_toks} tokens"
    return text, in_toks, out_toks, round(quality, 3)


def simulate_gpu_load() -> float:
    """Simulated GPU util that drifts smoothly between 30-95%."""
    t = time.time()
    base = 60 + 30 * math.sin(t / 30.0)
    return max(0.0, min(100.0, base + random.gauss(0, 3)))
