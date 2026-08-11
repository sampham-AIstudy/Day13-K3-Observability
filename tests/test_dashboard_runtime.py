from datetime import datetime, timezone

from scripts.dashboard import calculate, percentile, render_dashboard


def test_dashboard_calculations_and_contract_labels() -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    records = [
        {"event": "request_received", "ts": timestamp},
        {"event": "request_received", "ts": timestamp},
        {"event": "request_failed", "error_type": "TimeoutError"},
        {
            "event": "response_sent",
            "latency_ms": 100,
            "cost_usd": 0.01,
            "tokens_in": 10,
            "tokens_out": 20,
            "quality_score": 0.8,
        },
    ]
    values = calculate(records)
    assert values["error_rate"] == 50
    assert values["rate"] == 2
    assert values["tokens_in"] == 10
    page = render_dashboard(records)
    assert "Latency percentiles" in page
    assert "Request traffic" in page
    assert "Error rate and breakdown" in page
    assert "Cost over time" in page
    assert "Input and output tokens" in page
    assert "Quality proxy" in page


def test_percentile_empty() -> None:
    assert percentile([], 95) == 0
