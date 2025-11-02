"""Distributed execution module for QuASIM.

Provides distributed tensor execution using Ray + JAX with support
for CUDA and HIP/ROCm backends across multi-region GPU clusters.
"""

from __future__ import annotations

from .executor import DistributedExecutor
from .scheduler import TaskScheduler

__all__ = ["DistributedExecutor", "TaskScheduler"]
