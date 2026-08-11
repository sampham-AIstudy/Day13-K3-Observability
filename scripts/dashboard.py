from __future__ import annotations

import argparse
import html
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from statistics import mean
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_records(path: Path = LOG_PATH, minutes: int = 60) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        timestamp = _timestamp(record.get("ts"))
        if timestamp is not None and timestamp >= cutoff:
            records.append(record)
    return records


def percentile(values: list[float], percentage: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round(percentage / 100 * len(ordered) + 0.5) - 1))
    return ordered[index]


def calculate(records: list[dict[str, Any]], minutes: int = 60) -> dict[str, Any]:
    received = [item for item in records if item.get("event") == "request_received"]
    responses = [item for item in records if item.get("event") == "response_sent"]
    failures = [item for item in records if item.get("event") == "request_failed"]
    latencies = [float(item["latency_ms"]) for item in responses if isinstance(item.get("latency_ms"), (int, float))]
    qualities = [float(item["quality_score"]) for item in responses if isinstance(item.get("quality_score"), (int, float))]
    errors = Counter(str(item.get("error_type", "unknown")) for item in failures)
    request_count = len(received)
    traffic_by_minute = Counter(
        timestamp.replace(second=0, microsecond=0)
        for item in received
        if (timestamp := _timestamp(item.get("ts"))) is not None
    )
    active_minute_rate = (
        sum(traffic_by_minute.values()) / len(traffic_by_minute)
        if traffic_by_minute
        else 0.0
    )
    return {
        "p50": percentile(latencies, 50),
        "p95": percentile(latencies, 95),
        "p99": percentile(latencies, 99),
        "requests": request_count,
        "rate": active_minute_rate,
        "error_rate": len(failures) / request_count * 100 if request_count else 0.0,
        "errors": dict(errors),
        "cost": sum(float(item.get("cost_usd", 0)) for item in responses),
        "tokens_in": sum(int(item.get("tokens_in", 0)) for item in responses),
        "tokens_out": sum(int(item.get("tokens_out", 0)) for item in responses),
        "quality": mean(qualities) if qualities else 0.0,
    }


def render_dashboard(records: list[dict[str, Any]]) -> str:
    values = calculate(records)
    error_breakdown = ", ".join(f"{html.escape(name)}: {count}" for name, count in values["errors"].items()) or "No errors"
    cards = [
        ("Latency percentiles", f'P50 {values["p50"]:.0f} · P95 {values["p95"]:.0f} · P99 {values["p99"]:.0f}', "ms", "P95 ≤ 3000 ms", values["p95"] <= 3000),
        ("Request traffic", f'{values["requests"]} total · {values["rate"]:.2f}/min', "requests/min", "Rate ≥ 1 req/min", values["rate"] >= 1),
        ("Error rate and breakdown", f'{values["error_rate"]:.2f}% · {error_breakdown}', "percent", "Error rate ≤ 2%", values["error_rate"] <= 2),
        ("Cost over time", f'${values["cost"]:.6f}', "USD", "Total ≤ $2.50", values["cost"] <= 2.5),
        ("Input and output tokens", f'Input {values["tokens_in"]:,} · Output {values["tokens_out"]:,}', "tokens", "Total per field ≤ 50,000", max(values["tokens_in"], values["tokens_out"]) <= 50_000),
        ("Quality proxy", f'{values["quality"]:.3f}', "score 0–1", "Mean ≥ 0.75", values["quality"] >= 0.75),
    ]
    rendered_cards = "".join(
        f'<section class="card"><div class="status {"ok" if passed else "bad"}"></div>'
        f'<h2>{html.escape(title)}</h2><div class="value">{value}</div>'
        f'<div class="unit">{html.escape(unit)}</div><div class="threshold">SLO: {html.escape(threshold)}</div></section>'
        for title, value, unit, threshold, passed in cards
    )
    generated = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="30">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Day 13 AI Observability</title>
<style>
:root{{--bg:#0b1020;--card:#151c30;--text:#edf2ff;--muted:#95a2c3;--ok:#40d68b;--bad:#ff6b78}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:15px system-ui,sans-serif}}
main{{max-width:1180px;margin:auto;padding:38px 24px}} header{{display:flex;justify-content:space-between;align-items:end;margin-bottom:24px}}
h1{{margin:0;font-size:29px}} .meta,.unit,.threshold{{color:var(--muted)}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}}
.card{{position:relative;display:flex;flex-direction:column;background:var(--card);border:1px solid #26304a;border-radius:14px;padding:22px;min-height:220px}}
.card h2{{font-size:16px;margin:0 0 28px}} .value{{font-size:24px;font-weight:700;line-height:1.35}} .unit{{margin-top:5px}}
.threshold{{margin-top:auto;border-top:1px solid #26304a;padding-top:10px}}
.status{{position:absolute;right:18px;top:18px;width:10px;height:10px;border-radius:50%}} .ok{{background:var(--ok)}} .bad{{background:var(--bad)}}
@media(max-width:650px){{header{{display:block}}.meta{{margin-top:8px}}}}
</style></head><body><main><header><div><h1>Day 13 AI Observability</h1><div class="meta">Source: data/logs.jsonl</div></div>
<div class="meta">Last 60 minutes · refresh 30s · {generated}</div></header><div class="grid">{rendered_cards}</div></main></body></html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        payload = render_dashboard(load_records()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the Day 13 dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Dashboard: http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
