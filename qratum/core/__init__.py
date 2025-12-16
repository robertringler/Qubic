"""QRATUM Core Modules.

Production-grade quantum simulation primitives including:
- Circuit building and manipulation
- Gate operations and custom gates
- State vector representation
- Measurement and result analysis
- Density matrix operations
- Audit and compliance logging
- Validation framework
- Telemetry and observability
- Deterministic reproducibility

Classification: UNCLASSIFIED // CUI
"""

# Gates are imported as a module
from qratum.core import gates
from qratum.core.circuit import Circuit
from qratum.core.densitymatrix import DensityMatrix
from qratum.core.measurement import Measurement, Result
from qratum.core.simulator import SimulationError, SimulationMetadata, Simulator
from qratum.core.statevector import StateVector

# Lazy imports for optional modules to avoid circular imports
_audit = None
_telemetry = None
_validation = None
_reproducibility = None
_compliance = None


def get_audit():
    """Get audit module (lazy import)."""
    global _audit
    if _audit is None:
        from qratum.core import audit
        _audit = audit
    return _audit


def get_telemetry():
    """Get telemetry module (lazy import)."""
    global _telemetry
    if _telemetry is None:
        from qratum.core import telemetry
        _telemetry = telemetry
    return _telemetry


def get_validation():
    """Get validation module (lazy import)."""
    global _validation
    if _validation is None:
        from qratum.core import validation
        _validation = validation
    return _validation


def get_reproducibility():
    """Get reproducibility module (lazy import)."""
    global _reproducibility
    if _reproducibility is None:
        from qratum.core import reproducibility
        _reproducibility = reproducibility
    return _reproducibility


def get_compliance():
    """Get compliance module (lazy import)."""
    global _compliance
    if _compliance is None:
        from qratum.core import compliance
        _compliance = compliance
    return _compliance


__all__ = [
    # Core simulation
    "Circuit",
    "Simulator",
    "SimulationMetadata",
    "SimulationError",
    "StateVector",
    "Measurement",
    "Result",
    "DensityMatrix",
    "gates",
    # Module accessors
    "get_audit",
    "get_telemetry",
    "get_validation",
    "get_reproducibility",
    "get_compliance",
]
