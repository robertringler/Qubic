# QuASIM-Own Benchmark Results

Generated: 2026-01-02T03:27:15.003531

Total runs: 25

## Summary by Task and Model

### tabular-cls

| Model | Primary Metric | Secondary Metric | Latency (ms) | Stability | Deterministic |
|-------|---------------|------------------|--------------|-----------|---------------|
| logreg | 0.6600 ± 0.0000 | 0.6610 ± 0.0000 | 0.10 | 1.000 | ✅ |
| mlp | 0.8760 ± 0.0153 | 0.8763 ± 0.0154 | 0.17 | 0.983 | ❌ |
| rf | 0.7850 ± 0.0138 | 0.7850 ± 0.0140 | 4.41 | 0.982 | ❌ |
| slt | 0.7780 ± 0.0186 | 0.7779 ± 0.0185 | 7.09 | 0.976 | ❌ |

### text-cls

| Model | Primary Metric | Secondary Metric | Latency (ms) | Stability | Deterministic |
|-------|---------------|------------------|--------------|-----------|---------------|
| slt | 0.9910 ± 0.0020 | 0.9910 ± 0.0020 | 15.21 | 0.998 | ❌ |

## Reliability-per-Watt Ranking

Computed as: `(stability × primary_metric) / energy_proxy`

| Rank | Task | Model | Reliability-per-Watt |
|------|------|-------|---------------------|
| 1 | tabular-cls | logreg | 99.391504 |
| 2 | tabular-cls | mlp | 78.668964 |
| 3 | tabular-cls | rf | 2.690988 |
| 4 | tabular-cls | slt | 1.648780 |
| 5 | text-cls | slt | 1.000465 |
