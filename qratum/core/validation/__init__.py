"""QRATUM Validation Framework.

Provides comprehensive input/output validation, numerical stability analysis,
equivalence checking, and compliance validation for quantum simulation operations.

Designed for DO-178C Level A certification with complete requirements traceability.
"""

from .equivalence import EquivalenceValidator
from .numerical_stability import NumericalStabilityAnalyzer
from .validators import (
    CircuitSpec,
    CircuitValidator,
    ComplianceValidator,
    NumericValidator,
    StateVectorValidator,
    ValidationChain,
    ValidationError,
    ValidationLevel,
    ValidationResult,
    Validator,
    validate_circuit,
    validate_measurement,
    validate_statevector,
)

__all__ = [
    # Existing exports
    "NumericalStabilityAnalyzer",
    "EquivalenceValidator",
    # New validation framework
    "CircuitSpec",
    "CircuitValidator",
    "ComplianceValidator",
    "NumericValidator",
    "StateVectorValidator",
    "ValidationChain",
    "ValidationError",
    "ValidationLevel",
    "ValidationResult",
    "Validator",
    "validate_circuit",
    "validate_measurement",
    "validate_statevector",
]
