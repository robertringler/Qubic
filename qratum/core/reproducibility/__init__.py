"""QRATUM Reproducibility Framework.

Provides enterprise-grade deterministic reproducibility infrastructure with:
- Cryptographic seed verification
- Multi-framework synchronization
- Drift detection and alerting
- Execution replay capabilities
- DO-178C Level A compliance

Certificate: QRATUM-DETERMINISM-20251216-V1
"""

from .determinism import (
    DeterminismLevel,
    DeterministicContext,
    DriftDetector,
    ExecutionSnapshot,
    ReplayEngine,
    SeedAuthority,
    SeedState,
    deterministic_execution,
    get_seed_authority,
)
from .global_seed import GLOBAL_SEED, get_global_seed
from .manager import ReproducibilityManager

__all__ = [
    # Legacy exports
    "GLOBAL_SEED",
    "get_global_seed",
    "ReproducibilityManager",
    # Enhanced determinism framework
    "DeterminismLevel",
    "DeterministicContext",
    "DriftDetector",
    "ExecutionSnapshot",
    "ReplayEngine",
    "SeedAuthority",
    "SeedState",
    "deterministic_execution",
    "get_seed_authority",
]
