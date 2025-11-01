from __future__ import annotations

import os
import time
from typing import Any, Dict

import jax
import jax.numpy as jnp
import numpy as np
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest

try:
    from quasim.kernels.drug_discovery import drug_discovery_kernel
except Exception:  # pragma: no cover
    from .quasim_fallback import kernel as drug_discovery_kernel  # type: ignore

app = Flask(__name__)

REQUEST_COUNT = Counter("drug_discovery_requests_total", "Total requests", ["endpoint"])
REQUEST_LATENCY = Histogram("drug_discovery_request_latency_seconds", "Latency", ["endpoint"])

counts: Dict[str, int] = {"/health": 0, "/metrics": 0, "/drug_discovery/kernel": 0}
times: Dict[str, list[float]] = {"/drug_discovery/kernel": []}

def _prepare_seed() -> int:
    seed_env = os.getenv("QUASIM_KERNEL_SEED", "0")
    try:
        return int(seed_env)
    except ValueError:
        return 0

def _to_native(value: Any) -> Any:
    if isinstance(value, jnp.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {k: _to_native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_native(v) for v in value]
    if hasattr(value, "tolist"):
        return value.tolist()
    if hasattr(value, "item"):
        return value.item()
    return value

def execute_kernel(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    seed = payload.get("seed", _prepare_seed())
    key = jax.random.PRNGKey(seed)
    result = drug_discovery_kernel(key=key, payload=payload)
    if hasattr(result, "block_until_ready"):
        result = jax.block_until_ready(result)
    response = _to_native(result)
    return {"vertical": "drug_discovery", "seed": seed, "result": response}

@app.route("/health", methods=["GET"])
def health() -> Any:
    counts["/health"] += 1
    REQUEST_COUNT.labels(endpoint="/health").inc()
    return jsonify({"status": "ok", "vertical": "drug_discovery"})

@app.route("/metrics", methods=["GET"])
def metrics() -> Any:
    counts["/metrics"] += 1
    REQUEST_COUNT.labels(endpoint="/metrics").inc()
    prometheus_metrics = generate_latest()
    return app.response_class(prometheus_metrics, mimetype="text/plain")

@app.route("/kernel", methods=["POST", "GET"])
def kernel_endpoint() -> Any:
    start = time.perf_counter()
    REQUEST_COUNT.labels(endpoint="/drug_discovery/kernel").inc()
    counts["/drug_discovery/kernel"] += 1
    payload = request.get_json(silent=True) or {}
    response = execute_kernel(payload)
    duration = time.perf_counter() - start
    times["/drug_discovery/kernel"].append(duration)
    REQUEST_LATENCY.labels(endpoint="/drug_discovery/kernel").observe(duration)
    return jsonify(response)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)

