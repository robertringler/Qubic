"""QuASIM core framework - shared foundation modules."""
from __future__ import annotations

__all__ = ["KernelBase", "PrecisionMode", "Backend", "Config"]

from enum import Enum
from dataclasses import dataclass
from typing import Any


class PrecisionMode(Enum):
    """Numerical precision modes."""
    FP8 = "fp8"
    FP16 = "fp16"
    FP32 = "fp32"
    FP64 = "fp64"
    BF16 = "bf16"


class Backend(Enum):
    """Hardware backend types."""
    CPU = "cpu"
    CUDA = "cuda"
    HIP = "hip"
    METAL = "metal"
    QUANTUM = "quantum"
    EDGE = "edge"


@dataclass
class Config:
    """Base configuration for QuASIM kernels."""
    precision: PrecisionMode = PrecisionMode.FP32
    backend: Backend = Backend.CPU
    max_workspace_mb: int = 16384
    enable_telemetry: bool = True


class KernelBase:
    """Base class for all QuASIM simulation kernels."""
    
    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self._telemetry: dict[str, Any] = {}
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the kernel with given inputs."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    @property
    def telemetry(self) -> dict[str, Any]:
        """Return performance telemetry data."""
        return self._telemetry
    
    def reset_telemetry(self) -> None:
        """Reset telemetry counters."""
        self._telemetry.clear()
