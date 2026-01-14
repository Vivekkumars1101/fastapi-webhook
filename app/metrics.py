from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# Define the metrics
HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["path", "status"])
WEBHOOK_OUTCOMES = Counter("webhook_requests_total", "Webhook processing results", ["result"])
LATENCY = Histogram("request_latency_ms", "Latency in milliseconds")

def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)