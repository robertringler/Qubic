# QuASIM Benchmarking Tools

Comprehensive benchmarking suite for QuASIM kernels with automated discovery, standardized metrics collection, and reproducible results.

## Overview

The benchmarking tools provide:
- **Automatic kernel discovery** across multiple paths
- **Standardized benchmarking protocol** with warmup and multiple iterations
- **Comprehensive metrics**: timing (p50/p90/p99), throughput, memory, energy
- **Multiple output formats**: JSON (machine-readable) and Markdown (human-readable)
- **Regression detection** by comparing against baseline results
- **CI/CD integration** via GitHub Actions

## Quick Start

### Local Execution

```bash
# Run full benchmark suite (30 iterations)
make bench

# Run quick benchmark (10 iterations)
make bench-quick

# Run with custom parameters
python tools/bench_all.py \
  --iters 30 \
  --warmup 3 \
  --precision fp32,fp16 \
  --backends cpu,cuda \
  --output-dir reports \
  --seed 1337 \
  --verbose
```

### CI/CD

The benchmark suite runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

Results are:
- Posted as PR comments (with regression alerts)
- Uploaded as artifacts
- Committed to `benchmarks/history/` on main branch
- Published to a GitHub issue

## Architecture

### Tools

#### `metrics.py`

Metrics collection utilities:
- `MetricsCollector`: Main class for collecting performance metrics
  - `time_execution()`: Timing with warmup and multiple iterations
  - `measure_memory()`: GPU/CPU memory usage tracking
  - `measure_energy()`: Energy consumption estimation (nvidia-smi/rocm-smi)
  - `compute_accuracy()`: Error metrics vs. reference
- `save_json()`, `load_json()`: JSON I/O
- `generate_markdown_table()`: Markdown table generation
- `get_system_info()`: Environment capture

#### `bench_all.py`

Main benchmark orchestrator:
- `KernelDiscovery`: Discovers kernels in configured paths
- `BenchmarkRunner`: Runs standardized benchmarks
- `ReportGenerator`: Generates JSON and Markdown reports

## Kernel Discovery

Kernels are discovered automatically in:
- `kernels/`
- `src/kernels/`
- `quasim/kernels/`
- `integrations/kernels/`
- `autonomous_systems_platform/services/backend/quasim/kernels/`

Each kernel is analyzed to determine:
- Name and path
- Backend (cuda/rocm/cpu/jax/pytorch)
- Dependencies
- Benchmark configuration (from `bench.yaml` if present)

## Benchmark Configuration

Optional `bench.yaml` in kernel directory:

```yaml
problem_size:
  grid_size: [64, 64, 64]
  max_iterations: 50
  tolerance: 1.0e-5

precisions:
  - fp32
  - fp16

backends:
  - cpu
  - cuda

tolerances:
  rmse: 1.0e-3
  relative_error: 1.0e-2

skip_conditions:
  - backend: cuda
    reason: "CUDA not available"
    check: "not torch.cuda.is_available()"
```

## Output Structure

```
reports/
├── env.json                      # Environment info (git, OS, GPU, libraries)
├── kernel_manifest.json          # Discovered kernels
├── kernels/
│   ├── autonomous_systems.json   # Per-kernel detailed results
│   ├── pressure_poisson.json
│   └── quasim_runtime.json
├── summary.json                  # Aggregate metrics
├── summary.md                    # Human-readable report
└── regressions.md                # Regression analysis (if baseline provided)
```

### Per-Kernel Report Format

```json
{
  "kernel_name": "autonomous_systems",
  "backend": "jax",
  "precision": "fp32",
  "problem_size": {"seed": 1337, "scale": 1.0},
  "timing": {
    "latency_ms_p50": 0.011,
    "latency_ms_p90": 0.011,
    "latency_ms_p99": 0.012,
    "latency_ms_mean": 0.011,
    "latency_ms_std": 0.0003,
    "throughput_ops_per_sec": 92373.35,
    "iterations": 30
  },
  "memory": {"peak_mb": 128.5, "allocated_mb": 64.2},
  "energy": {"energy_j": 0.015, "power_w": 150.0},
  "accuracy": {"rmse": 1e-6, "max_error": 2e-6},
  "success": true
}
```

## Summary Report Sections

1. **Environment**: Commit, OS, Python, CUDA versions
2. **Performance Leaderboard**: Ranked by p50 latency
3. **Resource Usage**: Memory and energy consumption
4. **Key Findings**: Top performers, anomalies
5. **Recommendations**: Optimization suggestions
6. **Regressions**: Performance deltas vs. baseline (if available)

## Adding New Kernels

1. **Place kernel** in a discovered path (e.g., `integrations/kernels/mykernel/`)

2. **Implement benchmark function**:
   ```python
   def run_benchmark(problem_size=1024, iterations=1):
       # Your kernel code
       return result
   ```

3. **Optional: Add configuration** (`bench.yaml`):
   ```yaml
   problem_size:
     size: 2048
   precisions: [fp32, fp16]
   backends: [cpu, cuda]
   ```

4. **Run benchmark**:
   ```bash
   make bench
   ```

The kernel will be automatically discovered and benchmarked!

## Regression Detection

Compare against a baseline:

```bash
python tools/bench_all.py \
  --compare-to main \
  --output-dir reports
```

This fetches the `summary.json` from the `main` branch and generates a `reports/regressions.md` file highlighting:
- Latency regressions (>10% threshold)
- Accuracy drift (>1e-3 threshold)

Thresholds are configurable in the code.

## Dependencies

**Required:**
- Python 3.8+
- numpy

**Optional:**
- PyYAML (for `bench.yaml` support)
- PyTorch (for CUDA/ROCm memory/energy metrics)
- JAX (for JAX backend benchmarks)

## CI/CD Workflow

The `.github/workflows/bench.yml` workflow:

1. **Matrix Strategy**: Tests multiple backend/precision combinations
2. **Artifact Upload**: Saves results for 30 days
3. **PR Comments**: Posts summary and regressions
4. **Issue Updates**: Creates/updates benchmark issue on main
5. **History Tracking**: Commits results to `benchmarks/history/`

## Troubleshooting

**Kernel not discovered:**
- Check if file is in a scanned path
- Ensure file is a `.py` file and not prefixed with `__` or `test_`
- Run with `--verbose` to see discovery logs

**Benchmark fails:**
- Check that required dependencies are installed
- Verify kernel has a callable benchmark function
- Add explicit `function_name` to kernel config if needed

**Energy measurement unavailable:**
- Install nvidia-smi (NVIDIA GPUs) or rocm-smi (AMD GPUs)
- Ensure tools are in PATH

## Examples

### Compare Multiple Precisions

```bash
python tools/bench_all.py \
  --precision fp32,fp16,fp8 \
  --output-dir reports/multi-precision
```

### Benchmark Specific Backend

```bash
python tools/bench_all.py \
  --backends cuda \
  --output-dir reports/cuda-only
```

### High-Iteration Run

```bash
python tools/bench_all.py \
  --iters 100 \
  --warmup 10 \
  --output-dir reports/high-iter
```

## Contributing

To extend the benchmarking tools:

1. Add new metrics to `MetricsCollector` in `metrics.py`
2. Add new report sections in `ReportGenerator` in `bench_all.py`
3. Update kernel discovery paths in `KernelDiscovery.KERNEL_PATHS`
4. Add new backend support in `_infer_backend()` and `_resolve_backend()`

## License

Part of the QuASIM project. See main repository LICENSE.
