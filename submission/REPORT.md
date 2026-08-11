# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nhóm Day 13 Observability
- Repository URL: https://github.com/sampham-AIstudy/Day13-K3-Observability.git
- Commit SHA cuối: 8e40287
- Danh sách thành viên và vai trò:
  1. Tô Minh Đức (MSSV: 2A202601043) — Tracing & Prompt Versioning
  2. Phạm Văn Sâm (MSSV: 2A202601837) — Logging & PII, System Integration
  3. Nguyễn Đỗ Khải Hoàn (MSSV: 2A202601379) — Dashboard, SLO & Alert Rules
  4. Nguyễn Văn Duy (MSSV: 2A202601537) — Incident Investigation & Challenge
  5. Vương Trần Hoàn (MSSV: 2A202601481) — Testing, Quality Assurance & Evidence
  6. Lê Thành Vinh (MSSV: 2A202601945) — Documentation & Code Review

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100 / 100** (Estimated Score; minh chứng tại [submission/evidence/09-log-validation.png](submission/evidence/09-log-validation.png))
- Tổng số traces: **20+ traces** thực tế đã ghi nhận trực tiếp trên Langfuse Cloud UI ([submission/evidence/05-langfuse-traces.png](submission/evidence/05-langfuse-traces.png))
- Số PII leak còn lại: **0** (Hoàn toàn làm sạch PII Email, SĐT, CCCD, Thẻ tín dụng)
- Link/đường dẫn dashboard: [submission/evidence/10-dashboard.png](submission/evidence/10-dashboard.png) và [submission/evidence/dashboard.html](submission/evidence/dashboard.html)

## 3. Logging và tracing

- Evidence correlation ID: Định dạng `req-<8-char-hex>` (như `req-56997088`, `req-0d81ad4f`, `req-3aeae714`); minh chứng ở [submission/evidence/03-correlation-id.png](submission/evidence/03-correlation-id.png) và [data/logs.jsonl](data/logs.jsonl)
- Evidence PII redaction: Minh chứng tại [submission/evidence/04-pii-redaction.png](submission/evidence/04-pii-redaction.png); các payload đã được làm sạch tự động thành `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]` và `[REDACTED_CREDIT_CARD]`
- Evidence trace waterfall: Minh chứng tại [submission/evidence/05-langfuse-traces.png](submission/evidence/05-langfuse-traces.png)
- Giải thích một span đáng chú ý: Span `retrieve` (RAG Retrieval) bị chậm khoảng 2.5s khi kích hoạt incident `rag_slow`, khiến tổng latency nhảy từ ~150ms lên hơn 2.6s, dễ dàng phát hiện trên Dashboard và khoanh vùng trên Trace.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: Version 1 / label `baseline` & `production`
- Version/label candidate: Version 2 / label `candidate`
- Trace ID của mỗi version: Minh chứng tại [submission/evidence/07-prompt-versions.png](submission/evidence/07-prompt-versions.png), [submission/evidence/06b-trace-metadata.png](submission/evidence/06b-trace-metadata.png) và [submission/evidence/07b-trace-candidate-v2.png](submission/evidence/07b-trace-candidate-v2.png)
- Bằng chứng đổi label hoặc rollback: Chuyển nhãn `production` sang v2 tại [submission/evidence/08a-production-v2.png](submission/evidence/08a-production-v2.png) và rollback về v1 tại [submission/evidence/08b-production-rollback-v1.png](submission/evidence/08b-production-rollback-v1.png) và [submission/evidence/08c-rollback-trace-v1.png](submission/evidence/08c-rollback-trace-v1.png)

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: **PASS / HỢP LỆ**; validator xác nhận đủ 6/6 panel theo contract trong [config/dashboard.yaml](config/dashboard.yaml)
- Evidence dashboard: [submission/evidence/10-dashboard.png](submission/evidence/10-dashboard.png) và [submission/evidence/dashboard.html](submission/evidence/dashboard.html)
- SLO đã chọn và lý do: `latency_p95_ms <= 3000ms` (phản ánh trực tiếp sự cố `rag_slow`), `error_rate_pct <= 2.0%` (đảm bảo độ tin cậy API) và `quality_score_avg >= 0.75` (đảm bảo chất lượng phản hồi)
- Alert rules và runbook: Rule `HighLatencyP95`, `HighErrorRate`, `LowQualityScore` trong [config/alert_rules.yaml](config/alert_rules.yaml); hướng dẫn xử lý sự cố chi tiết nằm trong [docs/alerts.md](docs/alerts.md)

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1` (Cohort K3)
- Triệu chứng từ metrics: Latency P95/P99 của feature `refund` tăng đột biến từ ~150ms lên gần **2.650ms - 13.300ms** khi incident `rag_slow` được bật (minh chứng tại [submission/evidence/12-challenge.png](submission/evidence/12-challenge.png))
- Trace ID liên quan: `req-94196f05`, `req-05295c96`, `req-e99037f7`, `req-6283bee7`, `req-a1e47283`
- Log line/correlation ID liên quan: Dòng log `incident_enabled` tại correlation ID `req-64f46977` / `req-4e103e52` cho scenario `rag_slow`
- Root cause: Incident `rag_slow` kích hoạt độ trễ giả lập 2.5s trong [app/mock_rag.py](app/mock_rag.py), khiến bước RAG Retrieval bị nghẽn và kéo tổng latency vượt quá ngưỡng `latency_threshold_ms: 2000ms`
- Fix action: Tắt incident bằng lệnh `py scripts/inject_incident.py --scenario rag_slow --disable` và tối ưu hóa index/cache cho tầng RAG Search
- Preventive measure: Cấu hình Alert Rule `HighLatencyP95` (P95 > 3000ms) để tự động phát hiện nghẽn tầng RAG và giữ nguyên PII redaction để bảo vệ dữ liệu log

## 7. Đóng góp cá nhân

| Thành viên | MSSV | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|---|
| Tô Minh Đức | 2A202601043 | Tích hợp Langfuse Tracing, Prompt Management (`v1/v2`, `labels`, `rollback`) | `Main branch` | Hiểu rõ cách giám sát LLM Tracing, Prompt Versioning và Rollback trên Langfuse |
| Phạm Văn Sâm | 2A202601837 | Triển khai Structured Logging (`structlog`), PII Scrubbing (`pii.py`) và Middleware `correlation_id` | `Main branch` | Nắm vững kỹ thuật khử PII (Regex + Presidio) và Correlation ID propagation |
| Nguyễn Đỗ Khải Hoàn | 2A202601379 | Thiết kế Dashboard 6 Panel (`dashboard.py`), SLO và Alert Rules (`alert_rules.yaml`) | `Main branch` | Nắm vững cách xây dựng Dashboard Observability và thiết lập Symptom-based Alert Rules |
| Nguyễn Văn Duy | 2A202601537 | Xây dựng kịch bản điều tra Incident Challenge và kiểm thử luồng Metrics $\rightarrow$ Traces $\rightarrow$ Logs | `Main branch` | Nắm vững phương pháp khoanh vùng và truy tìm Root Cause sự cố hệ thống AI |
| Vương Trần Hoàn | 2A202601481 | Kiểm thử Public Tests (`pytest`), Validator Scripts và tổng hợp bằng chứng Evidence images | `Main branch` | Nắm vững kỹ thuật kiểm thử tự động và thu thập bằng chứng nghiệm thu kỹ thuật |
| Lê Thành Vinh | 2A202601945 | Xây dựng tài liệu Runbook (`alerts.md`), tổng hợp Báo cáo `REPORT.md` và kiểm duyệt Code | `Main branch` | Nắm vững quy trình viết Runbook xử lý sự cố và báo cáo kỹ thuật tiêu chuẩn |
