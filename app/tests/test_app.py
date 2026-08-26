import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app  # noqa: E402


def test_index():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.get_json()["service"] == "reliability-api"


def test_healthz():
    client = app.test_client()
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "alive"


def test_readyz_default_is_ready():
    client = app.test_client()
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ready"


def test_toggle_ready_flips_readiness():
    client = app.test_client()
    toggled = client.post("/toggle-ready").get_json()
    resp = client.get("/readyz")
    if toggled["ok"] is False:
        assert resp.status_code == 503
    else:
        assert resp.status_code == 200
    # flip it back so test order doesn't matter
    client.post("/toggle-ready")


def test_metrics_endpoint_exposes_prometheus_format():
    client = app.test_client()
    client.get("/")  # generate at least one request metric
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"http_requests_total" in resp.data
