try:
    from prometheus_client import Counter, Histogram, generate_latest
    from prometheus_client import CONTENT_TYPE_LATEST
except ImportError:  # pragma: no cover - optional dependency.
    Counter = Histogram = None
    generate_latest = None
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"


if Counter and Histogram:
    http_requests_total = Counter(
        "smartstay_http_requests_total",
        "Total HTTP requests.",
        ["method", "path", "status_code"],
    )
    http_request_duration_seconds = Histogram(
        "smartstay_http_request_duration_seconds",
        "HTTP request duration in seconds.",
        ["method", "path"],
    )
    agent_requests_total = Counter(
        "smartstay_agent_requests_total",
        "Total agent route requests.",
        ["agent", "intent", "next_action"],
    )
else:
    http_requests_total = None
    http_request_duration_seconds = None
    agent_requests_total = None


def metrics_response() -> tuple[bytes, str]:
    if generate_latest is None:
        return b"# prometheus_client is not installed\n", CONTENT_TYPE_LATEST
    return generate_latest(), CONTENT_TYPE_LATEST
