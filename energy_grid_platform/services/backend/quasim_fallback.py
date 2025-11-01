from __future__ import annotations

import jax.numpy as jnp

def kernel(key, payload):  # pragma: no cover
    scale = payload.get("scale", 1.0)
    vector = jnp.linspace(0, 1, 8) * scale
    return {"vector": vector, "mean": vector.mean()}

