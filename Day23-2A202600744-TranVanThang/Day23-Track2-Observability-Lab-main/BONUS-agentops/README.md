# BONUS — AgentOps: Quan Sát & SLI Cho Agent (B3, +10 pts)

> Maps to **deck §13 (Agent Observability)** + **§14 (Harness, Loop & Flywheel)** + **§19 (AgentOps Deepdive)**.
>
> Vận hành đúng thứ **bạn đã xây** trong chương trình: agent ReAct nhiều bước, dùng tool (Day 3 e-commerce agent, Day 9 multi-agent). **Zero-key**, dùng lại OTel + **Jaeger** + deps có sẵn của lab.

## Vì sao agent cần loại quan sát khác

Một `HTTP 200` có thể che giấu một agent **lặp 12 bước, gọi sai tool, đốt $5**. Request-observability không thấy điều đó — phải đo **trajectory** (quỹ đạo), không phải request. Đó là AgentOps.

## Bạn build gì

`agent_run.py` (cho sẵn — đọc, chạy, rồi *mở rộng*) chạy một mock agent qua vài task và:

1. **Emit OTel-GenAI spans** (`gen_ai.operation.name = invoke_agent / execute_tool`, `gen_ai.tool.name`) tới **OTel Collector → Jaeger** đang chạy sẵn → bạn thấy **cây span** của một quỹ đạo agent (parent `invoke_agent` + child `execute_tool`).
2. **Tính Agent SLIs** (deck §13/§14): `success_rate`, `avg_steps_per_task`, `tool_error_rate`, `cost_per_task_usd`, `loops_detected`.
3. **Phát hiện failure modes**: loop/no-progress, tool-error, task-failed (một task cố tình bị tiêm vòng lặp + một task có tool 503).
4. Ghi `agentops-report.json`.

```
invoke_agent (task)
 ├─ execute_tool search
 ├─ execute_tool get_price
 └─ execute_tool place_order   ✓ success
```

## Chạy

```bash
make up          # Jaeger (16686) + OTel Collector đã có trong stack
make agentops    # spans -> Jaeger (service: day23-agent); SLIs -> agentops-report.json
# hoặc không cần stack (SLIs vẫn tính, span export tự bỏ qua):
python3 BONUS-agentops/agent_run.py
```

Kỳ vọng: `success_rate` ~0.67, `loops_detected` = 1, task 3 có `failure_modes=[loop/no-progress, task-failed]`.

## Deliverable (chấm điểm)

| Có | Điểm |
|---|---|
| `agentops-report.json` commit trong `submission/` + **screenshot cây span trong Jaeger** (service `day23-agent`) | +5 |
| **Mở rộng** một trong: (a) thay mock bằng **agent thật của bạn** (Day 3/9) và instrument OTel-GenAI spans; (b) đẩy agent SLIs thành Prometheus metric + 1 panel Grafana (loop rate / cost-per-task / tool-error); (c) thêm 1 failure mode mới (vd wrong-tool, hallucinated-tool-arg) + test; (d) `--real-llm` policy với model free/local | +5 |

REFLECTION (mục AgentOps): vì sao **`pass^k` ≠ `pass@k`** (deck §19) lại quan trọng cho agent của bạn, và **SLI nào** bạn sẽ alert đầu tiên.

## Đi xa hơn (deck §14/§19, không bắt buộc)

- **Span standards**: thử cả OTel-GenAI và **OpenInference** (Arize Phoenix); nhiều SDK dual-emit.
- **MCP**: nếu agent dùng MCP, mỗi `tools/call` là **cặp span** client+server — nối bằng trace-context.
- **Reliability**: durable execution + HITL cho hành động không đảo ngược; pin model version chống prompt-drift.
- **Harness & flywheel (§14)**: emit harness signals (`context_util` %, `compaction_count`, `stop_reason` distribution), đo **time-horizon** mỗi task (autonomy duration), và **observe→skill**: tìm 1 sub-trajectory lặp nhiều lần trong trace → đóng gói thành 'skill'/tool.
