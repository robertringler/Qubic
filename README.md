# GB10 QuASIM Reference Platform

The GB10 QuASIM reference repository delivers a cohesive hardware-software co-design stack for a synthetic Grace-Blackwell inspired superchip optimized for AI and quantum simulation workloads. The project demonstrates how an open research platform could expose heterogeneous compute resources through a unified runtime and SDK.

## ⚡ Phase II Enhancements

**NEW:** Phase II state-of-the-art enhancements now available! Featuring:
- 🧠 Neural kernel fusion with learned cost models
- 🔄 Cross-backend IR unification (MLIR/StableHLO → CUDA/HIP/Triton/JAX/PyTorch)
- 📊 Adaptive precision (FP8, INT4) with auto-fallback
- ⚡ Async execution pipelines with dependency tracking
- 🌐 Heterogeneous scheduling (CPU/GPU/NPU/TPU)
- 🔋 Energy-aware autotuning (GFLOPs/W optimization)
- ✅ Formal verification (determinism, gradient parity)
- 📈 Interactive Plotly dashboards with roofline models

See [`docs/phase2_features.md`](docs/phase2_features.md) for complete documentation.

## Repository Layout

```
rtl/                SystemVerilog and Chisel sources for the SoC
fw/                 Boot ROM, firmware, and board support libraries
drivers/            Linux kernel drivers for each subsystem
runtime/            libquasim runtime, Python bindings, and tooling
sdk/                Compiler frontend, ISA tools, and profiling utilities
tests/              Verification testbenches and software regression suites
quantum/            QuASIM accelerated kernels and visualization assets
scripts/            Build, lint, simulation, and CI orchestration scripts
docs/               Technical documentation and specifications
ci/                 Continuous integration workflows and container recipes
Makefile            Top-level convenience targets for developers
```

## Getting Started

1. Install build prerequisites (`cmake`, `ninja`, `gcc`, `clang`, `python3`, `verilator`, `openjdk`, `sbt`, and `pytest`).
2. Run `make setup` to configure the local toolchain mirrors and Python environment.
3. Use `make lint`, `make sim`, and `make cov` to exercise RTL quality gates.
4. Build and run the runtime tests with `make runtime` and `make test`.
5. Benchmark the QuASIM tensor simulator with `make bench` or invoke `python benchmarks/quasim_bench.py` directly for custom parameters.

### Phase II Quick Start

```python
from quasim import Phase2Config, Phase2Runtime

# Configure Phase II runtime
config = Phase2Config(
    simulation_precision="fp8",
    enable_fusion=True,
    enable_energy_monitoring=True,
    backend="cuda",
)

# Create runtime and simulate
runtime = Phase2Runtime(config)
circuit = [[1+0j, 0+0j], [0+0j, 1+0j]]
result = runtime.simulate(circuit)

# Generate performance dashboard
runtime.generate_dashboard("benchmarks.html")
```

Run the Phase II benchmark:
```bash
PYTHONPATH=runtime/python:quantum python3 benchmarks/phase2_benchmark.py \
    --qubits 16 --gates 200 --precision fp8 --backend cuda
```

The repository is intentionally modular—each layer can be evaluated independently while maintaining coherent interfaces. Refer to the documentation in `docs/` for in-depth architecture, firmware boot flows, and API references.

## Licensing

All source code and documentation in this repository is provided under the Apache 2.0 license unless otherwise noted. This project is intended for academic and research exploration of heterogeneous compute designs.
