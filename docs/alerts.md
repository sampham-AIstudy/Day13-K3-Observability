# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: HighLatencyP95
- Severity: warning
- SLI/SLO liên quan: `latency_p95_ms <= 3000`.
- Điều kiện và thời gian duy trì: P95 lớn hơn 3000 ms liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: ít nhất 5% request phản hồi chậm, trải nghiệm chat bị gián đoạn.
- Ba bước kiểm tra đầu tiên: xác định cửa sổ tăng latency trên dashboard; mở trace chậm trong cửa sổ đó; dùng correlation ID tìm log và span gây chậm.
- Mitigation tạm thời: giảm concurrency, tắt incident/feature gây chậm hoặc chuyển sang dependency dự phòng.
- Owner: observability-team.

## Alert 2

- Tên: HighErrorRate
- Severity: critical
- SLI/SLO liên quan: `error_rate_pct <= 2`.
- Điều kiện và thời gian duy trì: error rate lớn hơn 2% liên tục trong 5 phút.
- Ảnh hưởng tới người dùng: request chat thất bại hoặc nhận HTTP 500.
- Ba bước kiểm tra đầu tiên: xem error breakdown; mở trace lỗi mới nhất; đối chiếu `error_type` và correlation ID trong log.
- Mitigation tạm thời: rollback thay đổi gần nhất, tắt feature lỗi hoặc định tuyến sang đường xử lý fallback.
- Owner: api-team.

## Alert 3

- Tên: LowQualityScore
- Severity: warning
- SLI/SLO liên quan: `quality_score_avg >= 0.75`.
- Điều kiện và thời gian duy trì: quality score trung bình dưới 0.75 liên tục trong 10 phút.
- Ảnh hưởng tới người dùng: câu trả lời thiếu liên quan hoặc thiếu ngữ cảnh dù API vẫn phản hồi thành công.
- Ba bước kiểm tra đầu tiên: xác định thời điểm quality giảm; so sánh trace theo prompt version và feature; kiểm tra retrieval docs và output trong phạm vi dữ liệu đã redact.
- Mitigation tạm thời: rollback label `production` về prompt ổn định gần nhất và kiểm tra lại cùng bộ input.
- Owner: ai-team.
