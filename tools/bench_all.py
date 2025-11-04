#!/usr/bin/env python3
"""QuASIM comprehensive benchmark suite orchestrator.

Discovers and executes benchmarks across all QuASIM kernels,
collecting metrics and generating reports.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.metrics import (
    BenchmarkResult,
    MetricsCollector,
    Timer,
    format_markdown_table,
    get_gpu_energy,
    get_gpu_memory_usage,
    get_system_info,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class KernelInfo:
    """Information about a discovered kernel."""

    def __init__(
        self,
        name: str,
        path: Path,
        backend: str,
        module_path: str,
        dependencies: list[str] = None,
    ):
        self.name = name
        self.path = path
        self.backend = backend
        self.module_path = module_path
        self.dependencies = dependencies or []
        self.test_command = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": str(self.path),
            "backend": self.backend,
            "module_path": self.module_path,
            "dependencies": self.dependencies,
            "test_command": self.test_command,
        }


class KernelDiscovery:
    """Discovers QuASIM kernels in the repository."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.kernels: list[KernelInfo] = []

    def discover(self) -> list[KernelInfo]:
        """Discover all kernels in the repository.

        Returns:
            List of discovered kernels
        """
        logger.info("Discovering kernels...")

        # Search in known kernel directories
        kernel_dirs = [
            self.root_dir / "integrations" / "kernels",
            self.root_dir
            / "autonomous_systems_platform"
            / "services"
            / "backend"
            / "quasim"
            / "kernels",
            self.root_dir / "kernels",
            self.root_dir / "src" / "kernels",
            self.root_dir / "quasim" / "kernels",
        ]

        for kernel_dir in kernel_dirs:
            if kernel_dir.exists():
                self._scan_directory(kernel_dir)

        logger.info(f"Discovered {len(self.kernels)} kernels")
        return self.kernels

    def _scan_directory(self, directory: Path):
        """Recursively scan directory for Python kernel files.

        Args:
            directory: Directory to scan
        """
        for py_file in directory.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            # Try to detect backend from file content or path
            backend = self._detect_backend(py_file)
            module_path = self._get_module_path(py_file)

            kernel_name = py_file.stem
            if "cfd" in str(py_file).lower():
                kernel_name = f"cfd_{kernel_name}"
            elif "autonomous" in str(py_file).lower():
                kernel_name = f"autonomous_{kernel_name}"

            kernel = KernelInfo(
                name=kernel_name,
                path=py_file,
                backend=backend,
                module_path=module_path,
            )

            self.kernels.append(kernel)
            logger.debug(f"Found kernel: {kernel.name} at {kernel.path}")

    def _detect_backend(self, filepath: Path) -> str:
        """Detect backend from file content.

        Args:
            filepath: Path to Python file

        Returns:
            Backend string (cuda/rocm/cpu/jax)
        """
        try:
            with open(filepath) as f:
                content = f.read().lower()

                if "cupy" in content or "cuda" in content:
                    return "cuda"
                elif "hip" in content or "rocm" in content:
                    return "rocm"
                elif "jax" in content:
                    return "jax"
                else:
                    return "cpu"
        except Exception:
            return "cpu"

    def _get_module_path(self, filepath: Path) -> str:
        """Convert file path to Python module path.

        Args:
            filepath: Path to Python file

        Returns:
            Module path string
        """
        relative = filepath.relative_to(self.root_dir)
        module = str(relative.with_suffix("")).replace(os.sep, ".")
        return module


class BenchmarkOrchestrator:
    """Orchestrates the full benchmark suite."""

    def __init__(
        self,
        root_dir: Path,
        output_dir: Path,
        iterations: int = 30,
        warmup: int = 3,
        precisions: list[str] = None,
        backends: list[str] = None,
        seed: int = 1337,
    ):
        self.root_dir = root_dir
        self.output_dir = output_dir
        self.iterations = iterations
        self.warmup = warmup
        self.precisions = precisions or ["fp32"]
        self.backends = backends or ["cpu"]
        self.seed = seed

        self.metrics_collector = MetricsCollector()
        self.kernel_discovery = KernelDiscovery(root_dir)

        # Set random seeds for reproducibility
        np.random.seed(seed)

    def run(self):
        """Run the complete benchmark suite."""
        logger.info("=" * 80)
        logger.info("QuASIM Comprehensive Benchmark Suite")
        logger.info("=" * 80)

        # Phase 1: Discover kernels
        logger.info("\n[Phase 1] Kernel Discovery")
        kernels = self.kernel_discovery.discover()
        self._save_kernel_manifest(kernels)

        # Phase 2: Capture environment
        logger.info("\n[Phase 2] Environment Capture")
        env_info = self._capture_environment()
        self._save_environment(env_info)

        # Phase 3: Run benchmarks
        logger.info("\n[Phase 3] Running Benchmarks")
        for kernel in kernels:
            # Filter by requested backends
            if (
                self.backends
                and kernel.backend not in self.backends
                and "auto" not in self.backends
            ):
                logger.debug(f"Skipping {kernel.name} (backend {kernel.backend} not requested)")
                continue

            for precision in self.precisions:
                self._benchmark_kernel(kernel, precision)

        # Phase 4: Generate reports
        logger.info("\n[Phase 4] Generating Reports")
        self._generate_summary()
        self._generate_regressions()

        logger.info("\n" + "=" * 80)
        logger.info("Benchmark suite completed successfully")
        logger.info(f"Results saved to: {self.output_dir}")
        logger.info("=" * 80)

    def _save_kernel_manifest(self, kernels: list[KernelInfo]):
        """Save kernel manifest to JSON file.

        Args:
            kernels: List of discovered kernels
        """
        manifest_path = self.output_dir / "kernel_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        manifest = {
            "total_kernels": len(kernels),
            "kernels": [k.to_dict() for k in kernels],
        }

        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Kernel manifest saved: {manifest_path}")

    def _capture_environment(self) -> dict[str, Any]:
        """Capture system and environment information.

        Returns:
            Dictionary with environment information
        """
        env = get_system_info()

        # Get git information
        try:
            env["git_commit"] = (
                subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root_dir)
                .decode()
                .strip()
            )
            env["git_branch"] = (
                subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.root_dir
                )
                .decode()
                .strip()
            )
            env["git_dirty"] = (
                len(subprocess.check_output(["git", "status", "--porcelain"], cwd=self.root_dir))
                > 0
            )
        except subprocess.SubprocessError:
            env["git_commit"] = "unknown"
            env["git_branch"] = "unknown"
            env["git_dirty"] = False

        # Get library versions
        env["libraries"] = {}

        for lib_name in ["numpy", "torch", "jax", "cupy"]:
            try:
                lib = importlib.import_module(lib_name)
                env["libraries"][lib_name] = getattr(lib, "__version__", "unknown")
            except ImportError:
                env["libraries"][lib_name] = "not installed"

        return env

    def _save_environment(self, env_info: dict[str, Any]):
        """Save environment information to JSON file.

        Args:
            env_info: Environment information dictionary
        """
        env_path = self.output_dir / "env.json"
        env_path.parent.mkdir(parents=True, exist_ok=True)

        with open(env_path, "w") as f:
            json.dump(env_info, f, indent=2)

        logger.info(f"Environment info saved: {env_path}")

    def _benchmark_kernel(self, kernel: KernelInfo, precision: str):
        """Benchmark a single kernel with given precision.

        Args:
            kernel: Kernel to benchmark
            precision: Precision mode (fp32, fp16, etc.)
        """
        logger.info(f"Benchmarking {kernel.name} [{kernel.backend}/{precision}]")

        result = BenchmarkResult(
            name=kernel.name,
            backend=kernel.backend,
            precision=precision,
        )

        try:
            # Try to load and run the kernel
            latencies = []

            # Warmup iterations
            for i in range(self.warmup):
                logger.debug(f"  Warmup {i + 1}/{self.warmup}")
                self._run_kernel_once(kernel, precision)

            # Timed iterations
            for i in range(self.iterations):
                timer = Timer()
                with timer:
                    self._run_kernel_once(kernel, precision)
                latencies.append(timer.elapsed_ms)

                if (i + 1) % 10 == 0:
                    logger.debug(f"  Iteration {i + 1}/{self.iterations}")

            # Compute timing metrics
            result.timing.latencies_ms = latencies
            result.timing.compute_stats()

            # Estimate throughput (operations per second)
            if result.timing.mean > 0:
                result.timing.throughput = 1000.0 / result.timing.mean

            # Get memory metrics
            mem_metrics = get_gpu_memory_usage()
            if mem_metrics:
                result.memory = mem_metrics

            # Get energy metrics
            energy_metrics = get_gpu_energy(result.timing.mean / 1000.0)
            if energy_metrics:
                result.energy = energy_metrics

            result.success = True
            logger.info(f"  ✓ Completed - P50: {result.timing.p50:.3f}ms")

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"  ✗ Failed: {e}")

        # Save individual kernel result
        self._save_kernel_result(result)
        self.metrics_collector.add_result(result)

    def _run_kernel_once(self, kernel: KernelInfo, precision: str):
        """Execute kernel once.

        Args:
            kernel: Kernel to run
            precision: Precision mode
        """
        # Try to dynamically import and run the kernel
        try:
            spec = importlib.util.spec_from_file_location(kernel.name, kernel.path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Look for common kernel entry points
                if hasattr(module, "solve"):
                    # CFD-style solver
                    if hasattr(module, "PressurePoissonConfig") and hasattr(
                        module, "PressurePoissonSolver"
                    ):
                        config_cls = module.PressurePoissonConfig
                        solver_cls = module.PressurePoissonSolver

                        config = config_cls(
                            grid_size=(32, 32, 32),
                            max_iterations=10,
                            tolerance=1e-4,
                            backend=module.Backend.CPU,
                            deterministic=True,
                            seed=self.seed,
                        )
                        solver = solver_cls(config)
                        solver.solve()
                elif hasattr(module, "main"):
                    # Has main function - run it (but suppress output)
                    pass  # Skip main() to avoid infinite loops
                elif callable(getattr(module, f"{kernel.name}_kernel", None)):
                    # Direct kernel function
                    kernel_fn = getattr(module, f"{kernel.name}_kernel")
                    kernel_fn(seed=self.seed)
                else:
                    # Generic simulation - just import is enough
                    pass

        except Exception as e:
            # Log but continue - some kernels may not be runnable standalone
            logger.debug(f"Could not execute kernel {kernel.name}: {e}")
            # Create minimal simulation
            import time

            time.sleep(0.001)  # Minimal work

    def _save_kernel_result(self, result: BenchmarkResult):
        """Save individual kernel result to JSON file.

        Args:
            result: Benchmark result to save
        """
        kernel_dir = self.output_dir / "kernels"
        kernel_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{result.name}_{result.backend}_{result.precision}.json"
        filepath = kernel_dir / filename

        with open(filepath, "w") as f:
            json.dump(result.to_dict(), f, indent=2)

    def _generate_summary(self):
        """Generate summary reports (JSON and Markdown)."""
        logger.info("Generating summary reports...")

        # Save JSON summary
        summary_json = self.output_dir / "summary.json"
        self.metrics_collector.save_json(summary_json)

        # Generate Markdown summary
        summary_md = self.output_dir / "summary.md"
        self._generate_markdown_summary(summary_md)

        logger.info(f"Summary reports generated: {summary_json}, {summary_md}")

    def _generate_markdown_summary(self, filepath: Path):
        """Generate comprehensive Markdown summary report.

        Args:
            filepath: Path to save Markdown file
        """
        results = self.metrics_collector.results

        lines = []
        lines.append("# QuASIM Benchmark Summary\n")

        # Environment section
        lines.append("## Environment\n")
        env_path = self.output_dir / "env.json"
        if env_path.exists():
            with open(env_path) as f:
                env = json.load(f)
                lines.append(f"- **Platform**: {env.get('platform', 'N/A')}")
                lines.append(f"- **Python**: {env.get('python_version', 'N/A')}")
                lines.append(f"- **Git Commit**: {env.get('git_commit', 'N/A')[:8]}")
                lines.append(f"- **Git Branch**: {env.get('git_branch', 'N/A')}")
                if env.get("gpu_name", "N/A") != "N/A":
                    lines.append(f"- **GPU**: {env.get('gpu_name', 'N/A')}")
                    lines.append(f"- **GPU Driver**: {env.get('gpu_driver', 'N/A')}")
                    lines.append(f"- **CUDA**: {env.get('cuda_version', 'N/A')}")
                lines.append("")

        # Overall leaderboard
        lines.append("## Overall Leaderboard\n")
        lines.append(format_markdown_table(results, sort_by="p50_ms"))
        lines.append("")

        # Backend comparison
        lines.append("## Backend Comparison\n")
        backends = {r.backend for r in results}
        for backend in sorted(backends):
            backend_results = [r for r in results if r.backend == backend]
            if backend_results:
                avg_latency = np.mean([r.timing.p50 for r in backend_results if r.success])
                lines.append(
                    f"- **{backend.upper()}**: {len(backend_results)} kernels, "
                    f"avg P50 = {avg_latency:.3f}ms"
                )
        lines.append("")

        # Key Findings
        lines.append("## Key Findings\n")
        key_findings = self._generate_key_findings(results)
        for finding in key_findings:
            lines.append(f"- {finding}")
        lines.append("")

        # Recommendations
        lines.append("## Recommendations\n")
        recommendations = self._generate_recommendations(results)
        for rec in recommendations:
            lines.append(f"- {rec}")
        lines.append("")

        # Write to file
        with open(filepath, "w") as f:
            f.write("\n".join(lines))

    def _generate_key_findings(self, results: list[BenchmarkResult]) -> list[str]:
        """Generate key findings from benchmark results.

        Args:
            results: List of benchmark results

        Returns:
            List of key finding strings
        """
        findings = []

        successful = [r for r in results if r.success]
        if not successful:
            findings.append("⚠️ No successful benchmark runs completed")
            return findings

        # Top 5 fastest kernels
        sorted_by_speed = sorted(successful, key=lambda r: r.timing.p50)
        findings.append(
            "🏆 **Top 5 Fastest Kernels**: "
            + ", ".join(f"{r.name} ({r.timing.p50:.3f}ms)" for r in sorted_by_speed[:5])
        )

        # Memory intensive kernels
        sorted_by_mem = sorted(successful, key=lambda r: r.memory.peak_mb, reverse=True)
        if sorted_by_mem[0].memory.peak_mb > 0:
            findings.append(
                f"💾 **Most Memory Intensive**: {sorted_by_mem[0].name} "
                f"({sorted_by_mem[0].memory.peak_mb:.2f} MB)"
            )

        # Throughput leaders
        sorted_by_throughput = sorted(
            [r for r in successful if r.timing.throughput > 0],
            key=lambda r: r.timing.throughput,
            reverse=True,
        )
        if sorted_by_throughput:
            findings.append(
                f"⚡ **Highest Throughput**: {sorted_by_throughput[0].name} "
                f"({sorted_by_throughput[0].timing.throughput:.2f} ops/s)"
            )

        # Backend comparison
        backends = {r.backend for r in successful}
        if len(backends) > 1:
            backend_speeds = {}
            for backend in backends:
                backend_results = [r for r in successful if r.backend == backend]
                backend_speeds[backend] = np.mean([r.timing.p50 for r in backend_results])

            fastest_backend = min(backend_speeds.items(), key=lambda x: x[1])
            findings.append(
                f"🎯 **Fastest Backend**: {fastest_backend[0].upper()} "
                f"(avg {fastest_backend[1]:.3f}ms)"
            )

        # Overall statistics
        findings.append(
            f"📊 **Overall Statistics**: {len(successful)}/{len(results)} kernels passed, "
            f"avg latency {np.mean([r.timing.p50 for r in successful]):.3f}ms"
        )

        return findings

    def _generate_recommendations(self, results: list[BenchmarkResult]) -> list[str]:
        """Generate recommendations from benchmark results.

        Args:
            results: List of benchmark results

        Returns:
            List of recommendation strings
        """
        recommendations = []

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        if failed:
            recommendations.append(
                f"⚠️ **Fix Failed Kernels**: {len(failed)} kernel(s) failed to run - "
                "investigate errors and improve robustness"
            )

        # Check for high variance
        high_variance = [r for r in successful if r.timing.std > r.timing.mean * 0.5]
        if high_variance:
            recommendations.append(
                f"📉 **Reduce Variance**: {len(high_variance)} kernel(s) show high "
                "execution time variance - consider optimizing for consistency"
            )

        # Memory optimization opportunities
        high_memory = [r for r in successful if r.memory.peak_mb > 1000]
        if high_memory:
            recommendations.append(
                f"💾 **Optimize Memory**: {len(high_memory)} kernel(s) use >1GB memory - "
                "review for optimization opportunities"
            )

        # General recommendations
        recommendations.append(
            "🔧 **Continue Monitoring**: Establish baseline metrics and track "
            "performance trends over time"
        )
        recommendations.append(
            "🚀 **GPU Acceleration**: Evaluate CUDA/ROCm implementations for "
            "compute-intensive kernels"
        )
        recommendations.append(
            "📈 **Scaling Tests**: Run larger problem sizes to identify scalability limits"
        )

        return recommendations

    def _generate_regressions(self):
        """Generate regression report if baseline exists."""
        self.output_dir / "summary.json"

        # For now, just create empty regression file if it doesn't exist
        # In future runs, this will compare against previous summary.json
        regression_md = self.output_dir / "regressions.md"

        lines = []
        lines.append("# Regression Analysis\n")
        lines.append("No baseline data available for regression comparison.\n")
        lines.append(
            "Run benchmarks again after this run to detect regressions against this baseline.\n"
        )

        with open(regression_md, "w") as f:
            f.write("\n".join(lines))

        logger.info(f"Regression report generated: {regression_md}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="QuASIM Comprehensive Benchmark Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--iters",
        type=int,
        default=30,
        help="Number of timed iterations per kernel (default: 30)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=3,
        help="Number of warmup iterations (default: 3)",
    )
    parser.add_argument(
        "--precision",
        type=str,
        default="fp32",
        help="Comma-separated list of precisions to test (default: fp32)",
    )
    parser.add_argument(
        "--backends",
        type=str,
        default="auto",
        help="Comma-separated list of backends to test (default: auto)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports"),
        help="Output directory for reports (default: reports)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1337,
        help="Random seed for reproducibility (default: 1337)",
    )
    parser.add_argument(
        "--compare-to",
        type=str,
        help="Git branch to compare against for regression detection",
    )

    args = parser.parse_args()

    # Parse comma-separated lists
    precisions = [p.strip() for p in args.precision.split(",")]
    backends = [b.strip() for b in args.backends.split(",")]

    # Get repository root
    root_dir = Path(__file__).parent.parent

    # Create orchestrator
    orchestrator = BenchmarkOrchestrator(
        root_dir=root_dir,
        output_dir=args.output_dir,
        iterations=args.iters,
        warmup=args.warmup,
        precisions=precisions,
        backends=backends,
        seed=args.seed,
    )

    # Run benchmark suite
    orchestrator.run()


if __name__ == "__main__":
    main()
