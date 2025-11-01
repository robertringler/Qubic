from __future__ import annotations

import jax.numpy as jnp

def quantum_benchmarks_kernel(key, payload):
    scale = payload.get("scale", 1.0)
    base = jnp.sin(jnp.linspace(0, 3.14, 16) * scale)
    return {"series": base, "max": base.max(), "min": base.min()}

