"""REST and gRPC API module for QuASIM.

Provides remote simulation orchestration via FastAPI endpoints
and gRPC services for high-performance communication.
"""

from __future__ import annotations

from .server import create_app

__all__ = ["create_app"]
