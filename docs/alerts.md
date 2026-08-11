# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: HighLatencyP95
- Severity: Critical
- SLI/SLO liên quan: `latency_p95_ms` (Mục tiêu <= 3000ms)
- Điều kiện và thời gian duy trì: P95 Latency > 3000ms kéo dài trên 5 phút
- Ảnh hưởng tới người dùng: Trải nghiệm tương tác với AI Agent bị chậm, phản hồi kéo dài quá 3 giây.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra Dashboard panel Latency P95 và P99 để xác định thời điểm bắt đầu chậm.
  2. Mở Langfuse Trace mới nhất của request bị chậm, kiểm tra xem latency nằm ở RAG (Vector DB) hay LLM Call.
  3. Kiểm tra log có cùng `correlation_id` để phát hiện lỗi timeout hoặc retry.
- Mitigation tạm thời: Chuyển sang fallback local prompt hoặc giảm `top_k` trong RAG search.
- Owner: OnCall-Engineer

## Alert 2

- Tên: HighErrorRate
- Severity: Critical
- SLI/SLO liên quan: `error_rate_pct` (Mục tiêu <= 2%)
- Điều kiện và thời gian duy trì: Tỷ lệ lỗi request > 2% kéo dài trên 5 phút
- Ảnh hưởng tới người dùng: Người dùng nhận phản hồi lỗi HTTP 500 hoặc thất bại khi gọi API.
- Ba bước kiểm tra đầu tiên:
  1. Xem Dashboard panel Errors để biết tỷ lệ phần trăm và loại lỗi chính (`error_type`).
  2. Tra cứu trong `data/logs.jsonl` các dòng log event `request_failed` để đọc stack trace / exception detail.
  3. Mở Trace trên Langfuse để xác định span bị lỗi (LLM API key hết hạn, network error hay code exception).
- Mitigation tạm thời: Khởi động lại dịch vụ hoặc chuyển lưu lượng sang backup LLM model.
- Owner: OnCall-Engineer

## Alert 3

- Tên: LowQualityScore
- Severity: Warning
- SLI/SLO liên quan: `quality_score_avg` (Mục tiêu >= 0.75)
- Điều kiện và thời gian duy trì: Quality Score trung bình < 0.75 kéo dài trên 10 phút
- Ảnh hưởng tới người dùng: Chất lượng câu trả lời của AI Agent bị giảm, thông tin trả về thiếu độ chính xác hoặc quá ngắn.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra Dashboard panel Quality Score và xem thông tin version Prompt đang chạy (`prompt_version`).
  2. Mở Trace trên Langfuse để so sánh prompt template v1 vs v2 và câu trả lời sinh ra.
  3. Kiểm tra xem có dữ liệu PII bị redact bất ngờ làm hỏng ngữ cảnh prompt hay không.
- Mitigation tạm thời: Rollback `LANGFUSE_PROMPT_LABEL` về phiên bản prompt ổn định trước đó (`baseline`/`v1`).
- Owner: AI-Engineer
