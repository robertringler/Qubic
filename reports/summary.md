# QuASIM Benchmark Report

## Environment

- **Commit**: `ee8da844`
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
| autonomous_systems | cpu | fp32 | 0.011 | 0.012 | 88447.05 |
| quasim_runtime | cpu | fp32 | 38.594 | 38.885 | 25.87 |
| pressure_poisson | cpu | fp32 | 44.430 | 44.697 | 22.46 |

## Resource Usage

No memory data available.

## Key Findings

- **Fastest Kernel**: `autonomous_systems` (0.011 ms p50)
- **Highest Throughput**: `autonomous_systems` (88447.05 ops/s)

## Recommendations

- **Precision Testing**: Consider testing additional precisions (FP16, FP8) for speed vs. accuracy trade-offs.
