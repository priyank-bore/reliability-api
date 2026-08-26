import os
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")

# In-memory flag used only to demo readiness-probe / alerting behavior.
# A real service would check its actual dependencies here (DB, cache, downstream API).
_READY_STATE = {"ok": True}

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)


@app.before_request
def _start_timer():
    request.start_time = time.time()


@app.after_request
def _record_metrics(response):
    latency = time.time() - getattr(request, "start_time", time.time())
    endpoint = request.path
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    REQUEST_COUNT.labels(
        method=request.method, endpoint=endpoint, status=response.status_code
    ).inc()
    return response


@app.route("/")
def index():
    return jsonify({"service": "reliability-api", "version": APP_VERSION})


@app.route("/healthz")
def healthz():
    """Liveness probe: is the process itself alive?"""
    return jsonify({"status": "alive"}), 200


@app.route("/readyz")
def readyz():
    """Readiness probe: is the service ready to receive traffic?"""
    if _READY_STATE["ok"]:
        return jsonify({"status": "ready"}), 200
    return jsonify({"status": "not ready"}), 503


@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/toggle-ready", methods=["POST"])
def toggle_ready():
    """
    Demo-only endpoint: flips readiness state so you can watch Kubernetes
    pull the pod out of the Service endpoints list, and watch the
    /metrics error-rate climb, without actually crashing the process.
    """
    _READY_STATE["ok"] = not _READY_STATE["ok"]
    return jsonify(_READY_STATE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
