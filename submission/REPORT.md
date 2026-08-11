# Báo cáo Day 13 Observability

## 1. Thông tin bài làm

- Tên nhóm: Nhóm Day 13 Observability
- Repository URL: `https://github.com/sampham-AIstudy/Day13-K3-Observability.git`
- Commit SHA cuối: `eb6cb32`
- Danh sách thành viên và vai trò:
  1. Phạm Văn Sâm (MSSV: 2A202601837) — Logging & PII, System Integration
  2. Tô Minh Đức (MSSV: 2A202601043) — Tracing & Prompt Versioning
  3. Nguyễn Đỗ Khải Hoàn (MSSV: 2A202601379) — Dashboard, SLO & Alert Rules
  4. Nguyễn Văn Duy (MSSV: 2A202601537) — Incident Investigation & Challenge
  5. Vương Trần Hoàn (MSSV: 2A202601481) — Testing, Quality Assurance & Evidence
  6. Lê Thành Vinh (MSSV: 2A202601945) — Documentation & Code Review

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100 / 100** (Tất cả 4 tiêu chí JSON Schema, Correlation ID, Log Enrichment, PII Scrubbing đều PASSED).
- Tổng số traces: **21+ Traces** ghi nhận trực tiếp trên Langfuse Cloud UI (`https://us.cloud.langfuse.com`).
- Số PII leak còn lại: **0** (Hoàn toàn làm sạch PII Email, SĐT, CCCD, Thẻ tín dụng, Passport và Địa chỉ).
- Link/đường dẫn dashboard: `submission/evidence/dashboard.html`

## 3. Logging và tracing

- Evidence correlation ID: Định dạng `req-<8-char-hex>` (Ví dụ: `req-327be679`, `req-6139b2bd`, `req-aa6fb950`) xuất hiện đồng bộ ở cả HTTP Response Header (`x-request-id`), `structlog` contextvars và file `data/logs.jsonl`.
- Evidence PII redaction: Các mẫu thông tin nhạy cảm như Email (`student@vinuni.edu.vn`), SĐT (`0901234567`), Thẻ tín dụng được làm sạch tự động bằng processor `scrub_event` thành `[REDACTED_EMAIL]`, `[REDACTED_PHONE_VN]`, `[REDACTED_CREDIT_CARD]`.
- Evidence trace waterfall: Span gốc `agent.run` lồng các sub-spans: `RAG Retrieval`, `Prompt Resolution`, `LLM Generation` (`claude-sonnet-4-5`).
- Giải thích một span đáng chú ý: Span `generation` (LLM Call) ghi nhận TTFT, Token Input (35 tokens), Token Output (152 tokens), Latency (150ms) và Cost ($0.002385).

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: Version 1 (`labels: ["production", "baseline"]`)
- Version/label candidate: Version 2 (`labels: ["candidate"]`)
- Trace ID của mỗi version: 
  - Version 1 (`production`): Trace ghi nhận `prompt_version="1"`, `prompt_source="langfuse"`, `prompt_label="production"`.
  - Version 2 (`candidate`): Trace ghi nhận `prompt_version="2"`, `prompt_source="langfuse"`, `prompt_label="candidate"`.
- Bằng chứng đổi label hoặc rollback: Thực hiện lệnh chuyển label `production` về Version 1 thành công trên Langfuse SDK, metadata trace xác nhận rollback về `prompt_version="1"`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: **HỢP LỆ: 6/6 panel có trong dashboard contract**.
- Evidence dashboard: File HTML báo cáo 6 panel tại `submission/evidence/dashboard.html`.
- SLO đã chọn và lý do:
  - `latency_p95_ms <= 3000ms` (Đảm bảo phản hồi nhanh cho trải nghiệm người dùng).
  - `error_rate_pct <= 2.0%` (Giữ cho API hoạt động ổn định và tin cậy).
  - `quality_score_avg >= 0.75` (Đảm bảo câu trả lời đủ thông tin và chính xác).
- Alert rules và runbook: Cập nhật 3 rules trong `config/alert_rules.yaml` (`HighLatencyP95`, `HighErrorRate`, `LowQualityScore`) kết nối trực tiếp với tài liệu `docs/alerts.md`.

## 6. Điều tra challenge

*(Lưu ý: Phần này sẽ thực hiện ngay sau khi Lab Coach release file `config/challenge.json` chính thức)*

- Challenge ID: (Chờ Lab Coach release file)
- Triệu chứng từ metrics: (Chờ Lab Coach release file)
- Trace ID liên quan: (Chờ Lab Coach release file)
- Log line/correlation ID liên quan: (Chờ Lab Coach release file)
- Root cause: (Chờ Lab Coach release file)
- Fix action: (Chờ Lab Coach release file)
- Preventive measure: (Chờ Lab Coach release file)

## 7. Đóng góp cá nhân

| Thành viên | MSSV | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|---|
| Phạm Văn Sâm | 2A202601837 | Triển khai Structured Logging (`structlog`), PII Scrubbing (`pii.py`) và Middleware `correlation_id` | `Main branch` | Nắm vững kỹ thuật khử PII (Regex + Presidio) và Correlation ID propagation |
| Tô Minh Đức | 2A202601043 | Tích hợp Langfuse Tracing, Prompt Management (`v1/v2`, `labels`, `rollback`) | `Main branch` | Hiểu rõ cách giám sát LLM Tracing, Prompt Versioning và Rollback trên Langfuse |
| Nguyễn Đỗ Khải Hoàn | 2A202601379 | Thiết kế Dashboard 6 Panel (`dashboard_app.py`), SLO và Alert Rules (`alert_rules.yaml`) | `Main branch` | Nắm vững cách xây dựng Dashboard Observability và thiết lập Symptom-based Alert Rules |
| Nguyễn Văn Duy | 2A202601537 | Xây dựng kịch bản điều tra Incident Challenge và kiểm thử luồng Metrics $\rightarrow$ Traces $\rightarrow$ Logs | `Main branch` | Nắm vững phương pháp khoanh vùng và truy tìm Root Cause sự cố hệ thống AI |
| Vương Trần Hoàn | 2A202601481 | Kiểm thử Public Tests (`pytest`), Validator Scripts và tổng hợp bằng chứng Evidence HTML | `Main branch` | Nắm vững kỹ thuật kiểm thử tự động và thu thập bằng chứng nghiệm thu kỹ thuật |
| Lê Thành Vinh | 2A202601945 | Xây dựng tài liệu Runbook (`alerts.md`), tổng hợp Báo cáo `REPORT.md` và kiểm duyệt Code | `Main branch` | Nắm vững quy trình viết Runbook xử lý sự cố và báo cáo kỹ thuật tiêu chuẩn |
