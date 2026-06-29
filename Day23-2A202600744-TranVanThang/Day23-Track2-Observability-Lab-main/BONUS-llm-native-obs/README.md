# BONUS — LLM-Native Observability with Langfuse (B2, +10 pts)

> Maps to **deck §11 (LLM-obs platform matrix)** + **§13 (Agent Observability, OTel gen_ai.* / MCP spans)**. Goal: self-host **Langfuse** and capture **one LangChain LLM trace** with token + cost + latency on a single record (a "wide event", deck §9).
>
> Why Langfuse: OSS (MIT), **self-hostable**, **OTel-native** (SDK **v4** is built on the OTel client), ClickHouse-backed. (2026 fact: **ClickHouse acquired Langfuse** in Jan 2026 — it stays OSS/self-host.) Phoenix and Comet Opik are equally valid OSS picks; the deck's matrix compares all three.

## What you'll build

```
LangChain app ──OTel/Langfuse SDK v4──▶  Langfuse (ClickHouse + Postgres + Redis + MinIO)  ──▶  trace w/ gen_ai.* attrs
```

You will see one chat span with: model, `input_tokens` / `output_tokens`, `cost_usd`, latency, and (optionally) tool calls — the LLM-native fields RED can't capture.

## Steps

1. **Self-host Langfuse** (separate Compose — Langfuse needs ClickHouse + Postgres + Redis + MinIO, so keep it out of the core 7-service stack):

```bash
git clone https://github.com/langfuse/langfuse
cd langfuse && docker compose up -d          # UI on http://localhost:3000
# create a project → copy LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY
```

2. **Instrument a minimal LangChain call** (`trace_llm.py` — you write this, ~15 lines):

```python
# pip install langfuse langchain-openai   (or any provider)
from langfuse import Langfuse, observe
from langfuse.openai import openai   # drop-in: auto-captures gen_ai.* spans
import os

# keys from step 1 (or via env LANGFUSE_PUBLIC_KEY / _SECRET_KEY / _HOST)
@observe()
def ask(q):
    r = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": q}])
    return r.choices[0].message.content

print(ask("Một câu về observability."))
# trace (model, tokens, cost, latency) appears in Langfuse UI
```

3. Open `http://localhost:3000` → **Tracing** → confirm your trace shows model, token usage, cost, and latency on one record.

## No API key? (zero-key path)

- Point `langfuse.openai` at a **local** OpenAI-compatible server (llama.cpp / Ollama / vLLM from Day 20) via `base_url` + a dummy key — Langfuse still captures the gen_ai.* span.
- Or use the **OTel route**: any app already emitting OTel `gen_ai.*` spans (deck §7/§13) can export to Langfuse's OTLP endpoint (`/api/public/otel`) — "instrument once, swap backend".

## Deliverable (B2)

- `submission/screenshots/langfuse-trace.png` — one LangChain/LLM trace in Langfuse showing **model + token usage + cost + latency**.
- 2–3 sentences in `submission/REFLECTION.md`: which LLM-native signal (token cost / latency split / tool-call) RED-only monitoring would have **missed**.

## Going further (deck §13)

- **Online eval-as-metric**: add a Langfuse score (faithfulness / judge-LLM) on a 10% sample → export to Prometheus as a gauge → alert on drops (deck §10 eval-as-metric + judge-recall trap).
- **Agent + MCP spans**: if you run an agent, capture the OTel `invoke_agent` / `execute_tool` span tree (and MCP client+server dual spans, semconv v1.42).
