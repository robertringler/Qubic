#!/usr/bin/env python3
"""Metrics collection and formatting utilities for QuASIM benchmarks.

Provides standardized metric collection for:
- Timing (latency, throughput)
- Memory usage
- Energy consumption
- Statistical analysis (percentiles)
- JSON and Markdown formatting
"""

from __future__ import annotations

import json
import platform
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class TimingMetrics:
    """Container for timing metrics."""

    latencies_ms: list[float] = field(default_factory=list)
    throughput: float = 0.0
    p50: float = 0.0
    p90: float = 0.0
    p99: float = 0.0
    mean: float = 0.0
    std: float = 0.0
    min: float = 0.0
    max: float = 0.0

    def compute_stats(self):
        """Compute statistical metrics from latency samples."""
        if not self.latencies_ms:
            return

        self.latencies_ms.sort()
        self.p50 = float(np.percentile(self.latencies_ms, 50))
        self.p90 = float(np.percentile(self.latencies_ms, 90))
        self.p99 = float(np.percentile(self.latencies_ms, 99))
        self.mean = float(np.mean(self.latencies_ms))
        self.std = float(np.std(self.latencies_ms))
        self.min = float(min(self.latencies_ms))
        self.max = float(max(self.latencies_ms))

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "p50_ms": self.p50,
            "p90_ms": self.p90,
            "p99_ms": self.p99,
            "mean_ms": self.mean,
            "std_ms": self.std,
            "min_ms": self.min,
            "max_ms": self.max,
            "throughput": self.throughput,
        }


@dataclass
class MemoryMetrics:
    """Container for memory metrics."""

    peak_mb: float = 0.0
    allocated_mb: float = 0.0
    reserved_mb: float = 0.0

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "peak_mb": self.peak_mb,
            "allocated_mb": self.allocated_mb,
            "reserved_mb": self.reserved_mb,
        }


@dataclass
class EnergyMetrics:
    """Container for energy metrics."""

    energy_j: float = 0.0
    avg_power_w: float = 0.0
    duration_s: float = 0.0

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "energy_j": self.energy_j,
            "avg_power_w": self.avg_power_w,
            "duration_s": self.duration_s,
        }


@dataclass
class AccuracyMetrics:
    """Container for accuracy metrics."""

    rmse: float = 0.0
    mae: float = 0.0
    ulps: float = 0.0
    numerical_error: float = 0.0

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "rmse": self.rmse,
            "mae": self.mae,
            "ulps": self.ulps,
            "numerical_error": self.numerical_error,
        }


@dataclass
class BenchmarkResult:
    """Complete benchmark result for a single kernel."""

    name: str
    backend: str
    precision: str
    timing: TimingMetrics = field(default_factory=TimingMetrics)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    energy: EnergyMetrics = field(default_factory=EnergyMetrics)
    accuracy: AccuracyMetrics = field(default_factory=AccuracyMetrics)
    config: dict[str, Any] = field(default_factory=dict)
    failures: int = 0
    determinism_std: float = 0.0
    success: bool = True
    error_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "backend": self.backend,
            "precision": self.precision,
            "timing": self.timing.to_dict(),
            "memory": self.memory.to_dict(),
            "energy": self.energy.to_dict(),
            "accuracy": self.accuracy.to_dict(),
            "config": self.config,
            "failures": self.failures,
            "determinism_std": self.determinism_std,
            "success": self.success,
            "error_message": self.error_message,
        }


class MetricsCollector:
    """Collects and aggregates benchmark metrics."""

    def __init__(self):
        self.results: list[BenchmarkResult] = []

    def add_result(self, result: BenchmarkResult):
        """Add a benchmark result."""
        self.results.append(result)

    def save_json(self, filepath: Path):
        """Save results to JSON file."""
        data = {
            "results": [r.to_dict() for r in self.results],
            "summary": self.get_summary(),
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def get_summary(self) -> dict[str, Any]:
        """Get summary statistics."""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        return {
            "total_benchmarks": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "avg_latency_ms": (
                float(np.mean([r.timing.p50 for r in successful])) if successful else 0.0
            ),
            "total_failures": sum(r.failures for r in self.results),
        }


class Timer:
    """Context manager for timing code execution."""

    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0
        self.elapsed_ms = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed_ms = (self.end_time - self.start_time) * 1000.0


def get_gpu_memory_usage() -> MemoryMetrics | None:
    """Get current GPU memory usage.

    Returns:
        MemoryMetrics if GPU is available, None otherwise
    """
    metrics = MemoryMetrics()

    # Try PyTorch CUDA
    try:
        import torch

        if torch.cuda.is_available():
            metrics.peak_mb = torch.cuda.max_memory_allocated() / (1024**2)
            metrics.allocated_mb = torch.cuda.memory_allocated() / (1024**2)
            metrics.reserved_mb = torch.cuda.memory_reserved() / (1024**2)
            return metrics
    except ImportError:
        pass

    # Try CuPy
    try:
        import cupy as cp

        mempool = cp.get_default_memory_pool()
        metrics.allocated_mb = mempool.used_bytes() / (1024**2)
        metrics.peak_mb = mempool.total_bytes() / (1024**2)
        return metrics
    except ImportError:
        pass

    return None


def get_gpu_energy(duration_s: float) -> EnergyMetrics | None:
    """Estimate GPU energy consumption using nvidia-smi.

    Args:
        duration_s: Duration of measurement in seconds

    Returns:
        EnergyMetrics if successful, None otherwise
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            power_w = float(result.stdout.strip().split("\n")[0])
            energy_j = power_w * duration_s

            metrics = EnergyMetrics()
            metrics.avg_power_w = power_w
            metrics.duration_s = duration_s
            metrics.energy_j = energy_j
            return metrics
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError, FileNotFoundError):
        pass

    return None


def format_markdown_table(results: list[BenchmarkResult], sort_by: str = "p50_ms") -> str:
    """Format benchmark results as a Markdown table.

    Args:
        results: List of benchmark results
        sort_by: Field to sort by

    Returns:
        Markdown table string
    """
    if not results:
        return "No results available.\n"

    # Sort results
    results_sorted = sorted(results, key=lambda r: r.timing.p50) if sort_by == "p50_ms" else results

    # Build table
    lines = []
    lines.append(
        "| Kernel | Backend | Precision | P50 (ms) | P90 (ms) | P99 (ms) | Throughput | Peak Mem (MB) | Status |"
    )
    lines.append(
        "|--------|---------|-----------|----------|----------|----------|------------|---------------|--------|"
    )

    for result in results_sorted:
        status = "✅ Pass" if result.success else "❌ Fail"
        throughput = f"{result.timing.throughput:.2f}" if result.timing.throughput > 0 else "N/A"
        lines.append(
            f"| {result.name} | {result.backend} | {result.precision} | "
            f"{result.timing.p50:.3f} | {result.timing.p90:.3f} | {result.timing.p99:.3f} | "
            f"{throughput} | {result.memory.peak_mb:.2f} | {status} |"
        )

    return "\n".join(lines)


def get_system_info() -> dict[str, Any]:
    """Collect system information.

    Returns:
        Dictionary with system information
    """
    info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
    }

    # Try to get GPU info
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if lines:
                parts = lines[0].split(",")
                info["gpu_name"] = parts[0].strip() if len(parts) > 0 else "Unknown"
                info["gpu_driver"] = parts[1].strip() if len(parts) > 1 else "Unknown"
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        info["gpu_name"] = "N/A"
        info["gpu_driver"] = "N/A"

    # Try to get CUDA version
    try:
        result = subprocess.run(["nvcc", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "release" in line.lower():
                    info["cuda_version"] = line.split("release")[-1].strip().split(",")[0]
                    break
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        info["cuda_version"] = "N/A"

    return info


def compute_regression(
    current: BenchmarkResult, baseline: BenchmarkResult, threshold: float = 0.10
) -> dict[str, Any] | None:
    """Detect regression between current and baseline results.

    Args:
        current: Current benchmark result
        baseline: Baseline benchmark result
        threshold: Threshold for regression (default 10%)

    Returns:
        Dictionary with regression details if detected, None otherwise
    """
    if not baseline.success or not current.success:
        return None

    latency_change = (current.timing.p50 - baseline.timing.p50) / baseline.timing.p50
    accuracy_change = abs(current.accuracy.rmse - baseline.accuracy.rmse)

    is_regression = False
    details = []

    if latency_change > threshold:
        is_regression = True
        details.append(
            f"Latency regression: {latency_change * 100:.1f}% slower "
            f"({baseline.timing.p50:.3f}ms → {current.timing.p50:.3f}ms)"
        )

    if accuracy_change > 1e-3:
        is_regression = True
        details.append(
            f"Accuracy drift: RMSE changed by {accuracy_change:.2e} "
            f"({baseline.accuracy.rmse:.2e} → {current.accuracy.rmse:.2e})"
        )

    if is_regression:
        return {
            "kernel": current.name,
            "backend": current.backend,
            "precision": current.precision,
            "latency_change_pct": latency_change * 100,
            "accuracy_change": accuracy_change,
            "details": details,
        }

    return None
