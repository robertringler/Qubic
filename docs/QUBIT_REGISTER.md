# QuASIM Hardware Qubit Register

The qubit register documents PTAQ-aligned hardware profiles consumed by the QuASIM runtime. These
entries map simulation workloads to supported accelerators and define lifecycle maintenance actions.

## Register Entries

| Register | Hardware Class | Capacity | Notes | Maintenance Cadence |
| --- | --- | --- | --- | --- |
| PTAQ-Alpha | Photonic tensor array qubits | 512 logical / 4,096 physical | Optimized for RL training workloads | Quarterly recalibration |
| PTAQ-Beta | Superconducting lattice | 256 logical / 2,048 physical | Supports cryogenic Monte Carlo loops | Bi-monthly cryo calibration |
| PTAQ-Gamma | NV-center hybrid | 128 logical / 1,024 physical | Field-deployable ruggedized package | Semi-annual field QA |

## Integration Notes

- Runtime bindings are configured via `runtime/hardware_registry.yaml`.
- Hardware acceptance tests live under `tests/hardware/` and are mirrored in the `notebooks/hardware`
  directory for engineering analysis.
- All hardware integrations require ECCN review before deployment.

## Support

Hardware escalations are managed by the Platform Hardware Office (`hardware@quasim.dev`). Include
serial numbers, calibration logs, and the affected mission profile when opening a ticket.
