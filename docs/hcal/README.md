# HCAL - Hardware Control Abstraction Layer

## Overview

HCAL (Hardware Control Abstraction Layer) provides a unified interface for controlling and monitoring physical hardware devices in quantum computing and simulation environments. It abstracts the complexity of hardware interactions and provides policy-based control mechanisms.

## Features

- **Device Discovery**: Automatically discover and enumerate available hardware devices
- **Policy Enforcement**: Define and enforce hardware access policies based on environment
- **Backend Abstraction**: Support multiple compute backends (CPU, CUDA, ROCm)
- **Resource Management**: Track and limit resource usage
- **CLI Tools**: Command-line utilities for device management

## Architecture

### Components

1. **Device Manager** (`quasim.hcal.device`)
   - Device discovery and enumeration
   - Device lifecycle management
   - Status monitoring

2. **Policy Validator** (`quasim.hcal.policy`)
   - Policy configuration loading
   - Backend validation
   - Resource limit enforcement

3. **CLI Interface** (`quasim.hcal.cli`)
   - `quasim-hcal discover`: List available devices
   - `quasim-hcal validate-policy`: Validate policy files

## Installation

```bash
pip install -e .
```

## Usage

### Device Discovery

```python
from quasim.hcal.device import DeviceManager

manager = DeviceManager()
devices = manager.discover()

for device in devices:
    print(f"{device.name} ({device.id}): {device.status}")
```

### Policy Validation

```python
from pathlib import Path
from quasim.hcal.policy import PolicyValidator

validator = PolicyValidator.from_file(Path("configs/hcal/policy.example.yaml"))

# Check if a backend is allowed
if validator.validate_backend("cuda"):
    print("CUDA backend is allowed")

# Check resource limits
if validator.check_limits("max_qubits", 15):
    print("Within qubit limit")
```

### CLI Usage

```bash
# Discover devices
quasim-hcal discover

# Discover devices (JSON output)
quasim-hcal discover --json

# Validate policy file
quasim-hcal validate-policy configs/hcal/policy.example.yaml
```

## Configuration

Policy configuration files are YAML-based and must include:

- `environment`: Environment type (DEV, LAB, PROD)
- `allowed_backends`: List of permitted compute backends
- `limits`: Resource limits (max_qubits, max_circuits, etc.)

Example policy file:

```yaml
environment: DEV
allowed_backends:
  - cpu
  - cuda
limits:
  max_qubits: 20
  max_circuits: 100
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/hcal/ -v

# Run with coverage
pytest tests/hcal/ --cov=quasim.hcal --cov-report=term

# Run only non-hardware tests
pytest tests/hcal/ -m "not requires_hardware"
```

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use Ruff for linting and formatting

### Linting

```bash
# Check code style
ruff check quasim/hcal/ tests/hcal/

# Format code
ruff format quasim/hcal/ tests/hcal/

# Type checking
mypy quasim/hcal/ --ignore-missing-imports
```

## Safety Considerations

See [Safety-and-Compliance.md](./Safety-and-Compliance.md) for detailed safety guidelines and compliance requirements.

## License

Copyright © 2024 QuASIM Project
