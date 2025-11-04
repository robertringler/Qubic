# Certification CI/CD Pipeline

## Overview

The QuASIM Certification CI/CD Pipeline ensures continuous validation of certification requirements for aerospace and defense applications. It automates the execution of certification tests, validates compliance metrics, and archives artifacts for audit purposes.

## Standards Compliance

The pipeline enforces compliance with:

- **DO-178C Level A**: Software Considerations in Airborne Systems and Equipment Certification
- **ECSS-Q-ST-80C Rev. 2**: European Space Agency Software Product Assurance
- **NASA E-HBK-4008**: NASA Engineering Handbook for Software Safety

## Pipeline Architecture

### Workflow Triggers

The certification pipeline runs on:

1. **Pull Requests**: Validates changes before merging to main/master
2. **Main Branch Pushes**: Continuous validation of production branch
3. **Releases**: Creates comprehensive certification artifact bundles

### Jobs

#### 1. Certification Test Suite

**Purpose**: Generate and validate all certification artifacts

**Steps**:
1. Generate certification artifacts using `generate_quasim_jsons.py`
   - Monte-Carlo simulation results (1024 trajectories)
   - Seed determinism audit logs
   - MC/DC coverage matrices
   - Certification Data Package (CDP) metadata

2. Run comprehensive certification validation suite (`test_quasim_validator.py`)
   - 13 certification tests covering all requirements
   - Deterministic replay validation
   - Fidelity metrics validation
   - Trotter convergence checks
   - Schema compliance verification

3. Run QuASIM validation suite (`validation_suite.py`)
   - Bloch vector consistency checks
   - Purity monotonicity validation
   - Shot noise analysis

4. Generate test reports (HTML + JSON format)

5. Upload artifacts with 90-day retention

**Artifacts Generated**:
- `montecarlo_campaigns/MC_Results_1024.json`
- `montecarlo_campaigns/coverage_matrix.csv`
- `seed_management/seed_audit.log`
- `cdp_artifacts/CDP_v1.0.json`
- `reports/certification-report.json`
- `reports/certification-report.html`

#### 2. Validation Gates

**Purpose**: Enforce certification requirements with fail-fast gates

These gates **block merges** if validation criteria are not met:

##### Gate 1: Monte-Carlo Fidelity

**Requirement**: Mean fidelity ≥ 0.97 ± 0.005

**Validation**:
- Checks mean fidelity from 1024 Monte-Carlo trajectories
- Validates acceptance criteria are met
- Ensures convergence rate ≥ 98%

**Failure Conditions**:
- Mean fidelity below 0.965 or above 0.975
- Convergence rate below 98%

##### Gate 2: MC/DC Coverage (DO-178C §6.4.4)

**Requirement**: 100% Modified Condition/Decision Coverage

**Validation**:
- Verifies all test conditions are covered
- Checks coverage matrix completeness
- Ensures traceability for each condition

**Failure Conditions**:
- Any condition without coverage
- Coverage rate < 100%

##### Gate 3: Anomaly Check

**Requirement**: Zero open anomalies at CDP freeze

**Validation**:
- Checks certification package for open anomalies
- Verifies verification status is READY_FOR_AUDIT
- Validates package integrity

**Failure Conditions**:
- Open anomalies > 0
- Verification status not compliant

##### Gate 4: Package Integrity

**Requirement**: All verification evidence items present

**Validation**:
- Checks for required evidence items (E-01 through E-04)
- Verifies evidence status (Verified or Submitted)
- Validates artifact references

**Failure Conditions**:
- Missing required evidence items
- Unverified critical evidence

#### 3. Archive Release Artifacts (`archive-release-artifacts`)

**Purpose**: Create comprehensive certification bundles for releases

**Triggered**: Only on release publications

**Steps**:
1. Download all certification artifacts and test reports
2. Create release bundle with manifest
3. Generate tar.gz archive
4. Upload with 365-day retention
5. Attach to GitHub release automatically

**Bundle Contents**:
- All certification artifacts
- Test reports (HTML + JSON)
- Manifest with standards compliance info
- Release metadata (version, commit SHA, timestamp)

**File Naming**: `QuASIM-CDP-{version}.tar.gz`

#### 4. Certification Report

**Purpose**: Provide visibility into certification validation results

**Triggered**: Only on pull requests

**Steps**:
1. Parse certification artifacts
2. Extract key metrics and status
3. Post detailed comment to PR with:
   - Monte-Carlo fidelity results
   - MC/DC coverage statistics
   - Anomaly check status
   - Certification package metadata
   - Pass/fail status for all gates

## Usage

### Running Certification Tests Locally

```bash
# Install dependencies
pip install pytest qutip numpy scipy pytest-json-report pytest-html

# Generate certification artifacts
python generate_quasim_jsons.py

# Run certification validation suite
pytest test_quasim_validator.py -v

# Run QuASIM validation suite
pytest validation_suite.py -v
```

### Manual Validation Gates

```bash
# Validate Monte-Carlo fidelity
python3 << 'EOF'
import json
with open("montecarlo_campaigns/MC_Results_1024.json") as f:
    data = json.load(f)
stats = data["statistics"]
assert stats["acceptance_criteria_met"], "Fidelity check failed"
assert stats["convergence_rate"] >= 0.98, "Convergence rate too low"
print("✅ Fidelity gate passed")
EOF

# Validate MC/DC coverage
python3 << 'EOF'
import csv
with open("montecarlo_campaigns/coverage_matrix.csv") as f:
    entries = list(csv.DictReader(f))
covered = sum(1 for e in entries if e["Coverage Achieved"] == "True")
assert covered == len(entries), "MC/DC coverage incomplete"
print("✅ Coverage gate passed")
EOF

# Validate anomaly check
python3 << 'EOF'
import json
with open("cdp_artifacts/CDP_v1.0.json") as f:
    package = json.load(f)["package"]
assert package["open_anomalies"] == 0, "Open anomalies detected"
print("✅ Anomaly gate passed")
EOF
```

### Understanding Test Reports

**HTML Report** (`reports/certification-report.html`):
- Visual test results with pass/fail indicators
- Test duration and performance metrics
- Detailed error messages for failures
- Self-contained (can be opened in browser)

**JSON Report** (`reports/certification-report.json`):
- Machine-readable test results
- Suitable for automated analysis
- Contains full test metadata
- Can be parsed by CI/CD tools

## Troubleshooting

### Common Failure Scenarios

#### Fidelity Gate Failure

**Symptom**: "Mean fidelity below threshold"

**Causes**:
- Noise parameters too high in simulation
- Insufficient trajectories for statistical significance
- Numerical instability in quantum simulation

**Resolution**:
1. Check noise parameters in `generate_quasim_jsons.py`
2. Increase number of trajectories (default: 1024)
3. Verify quantum simulation convergence

#### Coverage Gate Failure

**Symptom**: "MC/DC coverage incomplete"

**Causes**:
- Test vectors missing for some conditions
- Branch logic not exercised
- Traceability gaps

**Resolution**:
1. Review `coverage_matrix.csv` for uncovered conditions
2. Add test cases for missing branches
3. Ensure all decision outcomes are tested

#### Anomaly Gate Failure

**Symptom**: "Open anomalies detected"

**Causes**:
- Unresolved issues in certification package
- Pending verification items
- Documentation gaps

**Resolution**:
1. Review CDP artifacts for open items
2. Close or document all anomalies
3. Update verification status

### Debugging Failed Tests

```bash
# Run tests with verbose output
pytest test_quasim_validator.py -v --tb=long

# Run specific test class
pytest test_quasim_validator.py::TestFidelityMetrics -v

# Run with debugging on failure
pytest test_quasim_validator.py --pdb

# Generate detailed HTML report
pytest test_quasim_validator.py --html=debug-report.html --self-contained-html
```

## Maintenance

### Updating Certification Requirements

To update certification thresholds or requirements:

1. Modify thresholds in `test_quasim_validator.py`
2. Update validation gates in `.github/workflows/certification-cicd.yml`
3. Document changes in this file
4. Run full test suite to validate changes

### Adding New Validation Gates

1. Create validation logic in test suite
2. Add gate step in workflow file
3. Define failure conditions clearly
4. Update documentation

### Artifact Retention Policy

- **Test artifacts**: 30 days (workflow artifacts)
- **Certification artifacts**: 90 days (workflow artifacts)
- **Release bundles**: 365 days (workflow artifacts)
- **Release attachments**: Permanent (GitHub releases)

## Security Considerations

### Permissions

The workflow uses minimal required permissions:
- `contents: read` - Read repository code
- `pull-requests: write` - Post PR comments
- `checks: write` - Update check status

### Secrets

No secrets are required for basic operation. For release attachments, the workflow uses `GITHUB_TOKEN` which is automatically provided by GitHub Actions.

### Artifact Security

- Artifacts are stored in GitHub Actions with organizational access controls
- Release bundles are signed with commit SHA for integrity verification
- No sensitive data (credentials, keys) should be included in artifacts

## Performance

### Typical Run Times

- Certification test suite: ~5-10 seconds
- Validation gates: ~2-3 seconds
- Artifact archival: ~1-2 seconds
- Total pipeline: ~15-20 seconds

### Resource Requirements

- Runner: ubuntu-latest (2 vCPU, 7 GB RAM)
- Disk space: ~100 MB for artifacts
- Network: Minimal (package installation only)

## References

- [DO-178C Software Considerations](https://www.rtca.org/content/standards-guidance-materials)
- [ECSS-Q-ST-80C Software Product Assurance](https://ecss.nl/standard/ecss-q-st-80c-software-product-assurance/)
- [NASA E-HBK-4008 Software Safety](https://www.nasa.gov/reference/4008/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Support

For issues or questions about the certification pipeline:

1. Check existing GitHub issues
2. Review test output and logs
3. Consult this documentation
4. Open a new issue with:
   - Workflow run URL
   - Error messages
   - Expected vs actual behavior
