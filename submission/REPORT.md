# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K3 - Observability Team
- Repository URL: https://github.com/sampham-AIstudy/Day13-K3-Observability.git
- Commit SHA cuối: cd84f4f
- Thành viên và vai trò: Hoàn — triển khai logging/tracing/PII, prompt versioning, dashboard validation và viết báo cáo.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (Estimated Score)
- Tổng số traces: 10+ trace thực tế đã ghi nhận cho prompt versioning và incident investigation
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: [submission/evidence/10-dashboard.png](submission/evidence/10-dashboard.png)

## 3. Logging và tracing

- Evidence correlation ID: req-56997088, req-0d81ad4f, req-3aeae714; minh chứng ở [submission/evidence/03-correlation-id.png](submission/evidence/03-correlation-id.png) và [data/logs.jsonl](data/logs.jsonl)
- Evidence PII redaction: [submission/evidence/04-pii-redaction.png](submission/evidence/04-pii-redaction.png); các payload đã được scrub thành [REDACTED_EMAIL], [REDACTED_PHONE_VN] và [REDACTED_CREDIT_CARD]
- Evidence trace waterfall: [submission/evidence/05-langfuse-traces.png](submission/evidence/05-langfuse-traces.png)
- Giải thích một span đáng chú ý: span `retrieve` bị chặn khoảng 2,5 giây khi incident `rag_slow` được bật, khiến latency tăng vượt ngưỡng và dễ bị phát hiện trên dashboard.

## 4. Prompt versioning

- Prompt name: day13-chat
- Version/label baseline: v1 / label `baseline`
- Version/label candidate: v2 / label `candidate`
- Trace ID của mỗi version: được ghi trong các evidence screenshot của prompt versioning: [submission/evidence/07-prompt-versions.png](submission/evidence/07-prompt-versions.png) và [submission/evidence/07b-trace-candidate-v2.png](submission/evidence/07b-trace-candidate-v2.png)
- Bằng chứng đổi label hoặc rollback: production được chuyển sang v2 ở [submission/evidence/08a-production-v2.png](submission/evidence/08a-production-v2.png) và rollback về v1 ở [submission/evidence/08b-production-rollback-v1.png](submission/evidence/08b-production-rollback-v1.png)

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: PASS; validator xác nhận đủ 6/6 panel theo contract
- Evidence dashboard: [submission/evidence/10-dashboard.png](submission/evidence/10-dashboard.png) và [config/dashboard.yaml](config/dashboard.yaml)
- SLO đã chọn và lý do: SLO `latency_p95_ms <= 3000 ms` vì đây là chỉ số trực tiếp phản ánh incident `rag_slow`; khi latency tăng, cảnh báo sẽ rõ ràng và dễ liên kết với trace/logs
- Alert rules và runbook: rule `HighLatencyP95` trong [config/alert_rules.yaml](config/alert_rules.yaml); runbook ở [docs/alerts.md](docs/alerts.md) hướng dẫn kiểm tra dashboard, mở trace liên quan, tra correlation ID và xác nhận incident status trước khi can thiệp

## 6. Điều tra challenge

- Challenge ID: day13-k3-observability-v1
- Triệu chứng từ metrics: latency p95/p99 tăng đột biến từ khoảng 150 ms lên gần 2.650 ms khi incident `rag_slow` được bật, trong khi traffic và quality vẫn ổn định
- Trace ID liên quan: trace cho request bị ảnh hưởng được minh họa trong [submission/evidence/12-challenge.png](submission/evidence/12-challenge.png)
- Log line/correlation ID liên quan: sự kiện `incident_enabled` ở correlation ID `req-4e103e52`, và request bị ảnh hưởng `req-56997088`/`req-0d81ad4f`
- Root cause: incident `rag_slow` kích hoạt một sleep 2,5 giây trong [app/mock_rag.py](app/mock_rag.py), làm retrieval path chậm và kéo latency vượt ngưỡng
- Fix action: tắt incident hoặc giới hạn sleep chỉ ở môi trường test/non-production, đồng thời giữ alert/trace/log để việc điều tra nhanh và có thể rollback an toàn
- Preventive measure: thêm guardrail cho incident flag, theo dõi SLO/alert liên tục và giữ PII redaction trước khi ghi log để tránh rò dữ liệu

## 7. Đóng góp cá nhân

| Thành viên | Phần việc                                                                                                | Commit/PR            | Điều đã học                                                                                     |
| ---------- | -------------------------------------------------------------------------------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------- |
| Hoàn    | Triển khai logging/tracing, PII redaction, prompt versioning, dashboard validation và hoàn thiện báo cáo | commit cuối: cd84f4f | Hiểu cách kết nối metrics → traces → logs và dùng correlation ID để điều tra incident nhanh hơn |
