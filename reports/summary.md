# QuASIM Benchmark Report

## Environment

- **Commit**: `a5f5b35a`
- **Branch**: `copilot/execute-quasim-benchmark-suite-again`
- **Dirty**: True

- **OS**: Linux
- **Python**: 3.12.3


## Summary

- **Total Kernels**: 3
- **Successful**: 3
- **Failed**: 0

## Performance Leaderboard

| Kernel | Backend | Precision | p50 (ms) | p90 (ms) | Throughput (ops/s) |
| --- | --- | --- | --- | --- | --- |
| autonomous_systems | jax | fp32 | 0.011 | 0.011 | 92373.35 |
| pressure_poisson | cuda | fp32 | 44.499 | 45.144 | 22.42 |
| quasim_runtime | cpu | fp32 | 115.596 | 115.981 | 8.65 |

## Resource Usage

No memory data available.

## Key Findings

- **Fastest Kernel**: `autonomous_systems` (0.011 ms p50)
- **Highest Throughput**: `autonomous_systems` (92373.35 ops/s)
- **Backends Tested**: cpu, cuda, jax

## Recommendations

- **Precision Testing**: Consider testing additional precisions (FP16, FP8) for speed vs. accuracy trade-offs.
