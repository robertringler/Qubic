import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

os.environ.setdefault("QUASIM_KERNEL_SEED", "0")
os.environ.setdefault("JAX_PLATFORM_NAME", "cpu")

from services.backend.app import app, counts, times, execute_kernel


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_execute_kernel_deterministic():
    payload = {"scale": 1.0}
    first = execute_kernel(payload)
    second = execute_kernel(payload)
    assert first["result"] == second["result"]


def test_metrics_and_kernel_endpoint(client):
    before = list(times["/autonomous_systems/kernel"])
    response = client.post("/kernel", json={"scale": 0.5})
    assert response.status_code == 200
    data = response.get_json()
    assert data["vertical"] == "autonomous_systems"
    assert "result" in data
    assert len(times["/autonomous_systems/kernel"]) == len(before) + 1
    metrics = client.get("/metrics")
    assert metrics.status_code == 200

