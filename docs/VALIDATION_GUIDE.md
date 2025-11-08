# QuASIM Validation Guide

This guide documents the validation envelope for the QuASIM platform. It is designed to align
with aerospace certification requirements and the verification artifacts shipped as part of the
QuASIM Full Package Builder workflow.

## Validation Objectives

1. **Safety-Critical Determinism** – Ensure Monte Carlo campaign replay tolerance remains below
   1µs for deterministic certification use cases.
2. **Regulatory Compliance** – Maintain DO-178C Level A, DO-254, and DO-330 alignment across
   software, hardware, and tooling components.
3. **Model Fidelity** – Enforce <2% RMSE against telemetry baselines captured in
   `validation_suite.py` and `live_emulation_for_ci_validation.py`.
4. **Security Hardening** – Validate that runtime posture adheres to NIST 800-53 and CMMC Level 2
   controls using automated scans in `.github/workflows/pr-defense-compliance.yml`.

## Core Test Suites

| Suite | Scope | Trigger |
| --- | --- | --- |
| `validation_suite.py` | Full Monte Carlo validation with flight telemetry | Pull requests, nightly CI |
| `live_emulation_for_ci_validation.py` | Hardware-in-the-loop emulation for GPU/FPGA backends | Nightly CI |
| `tests/` | Unit and integration regression suites | Pull requests |
| `ci/` | Container build, linting, and compliance gates | Pull requests |

Each suite publishes results to the QuASIM observability stack. Failures block releases until
triaged by the compliance automation team.

## Evidence Capture

Validation artifacts are exported to `reports/validation` with signed SBOMs, code coverage reports,
and certification attestations. These outputs are bundled by the release workflow into the
`quasim-closure-repo.zip` artifact for downstream auditors.

## Change Control

All validation configuration changes must:

- Pass gated reviews from the compliance and certification code owners.
- Update the `CHANGELOG.md` and `COMPLIANCE_STATUS_CHECKLIST.md` entries.
- Maintain traceability back to Jira tickets or customer validation requests.

## Contact

For exceptions or audit escalations, contact the Certification Office at
`certification@quasim.dev` or review the escalation matrix in `SECURITY_SUMMARY.md`.
