# QuASIM Intellectual Property Register

The IP register tracks production-grade components and patent-aligned assets that are bundled in
the QuASIM Full Package release. This registry provides traceability for legal review and ensures
licensing artifacts accompany all distributed binaries.

## Registered Assets

| ID | Component | Description | IP Type | Status |
| --- | --- | --- | --- | --- |
| IP-001 | `quantum_search/` | Adaptive Grover extensions for telemetry anomaly detection | Patent pending | Cleared |
| IP-002 | `runtime/` | Deterministic hybrid runtime with GPU failover orchestration | Trade secret | Cleared |
| IP-003 | `sdk/` | Python SDK for mission profile design and compliance reporting | Copyright | Cleared |
| IP-004 | `telemetry_api/` | Secure ingestion pipeline for classified data flows | Patent pending | Export controlled |
| IP-005 | `montecarlo_campaigns/` | Reproducible campaign templates with certification evidence | Trade secret | Cleared |

## Obligations

- Maintain SPDX headers in all distributed source files (`make lint-headers`).
- Update `PATENT_INVENTIONS.json` when IP catalog changes occur.
- Coordinate with legal before publishing derived research papers or datasets.

## Export Control

Export classification is maintained in `SECURITY.md`. The release workflow tags artifacts with
ECCN annotations when uploaded to GitHub releases.
