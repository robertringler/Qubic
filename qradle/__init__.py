"""
QRADLE - Quantum-Resilient Auditable Deterministic Ledger Engine

The foundational execution layer for QRATUM platform providing:
- Deterministic execution with cryptographic proofs
- Merkle-chained audit trails
- Contract-based operations with rollback capability
- 8 Fatal Invariants enforcement
"""

__version__ = "1.0.0"

# Legacy module imports (from standalone files)
from qradle.engine import QRADLEEngine
from qradle.contract_types import Contract, ContractStatus, ContractExecution
from qradle.merkle import MerkleChain, MerkleNode
from qradle.invariants import FatalInvariants
from qradle.rollback import RollbackManager, Checkpoint

# Core engine imports (from core package)
from qradle.core.engine import DeterministicEngine, ExecutionContext, ExecutionResult
from qradle.core.invariants import FatalInvariants as CoreFatalInvariants
from qradle.core.invariants import InvariantViolation
from qradle.core.merkle import MerkleChain as CoreMerkleChain
from qradle.core.merkle import MerkleProof
from qradle.core.rollback import RollbackManager as CoreRollbackManager
from qradle.core.rollback import Checkpoint as CoreCheckpoint
from qradle.contracts.system import ContractExecutor, ContractValidator
from qradle.events.chain import EventChain, Event

# Unified exports with both legacy and new components
__all__ = [
    # Legacy engine
    "QRADLEEngine",
    "Contract",
    "ContractStatus",
    "ContractExecution",
    "MerkleChain",
    "MerkleNode",
    "FatalInvariants",
    "RollbackManager",
    "Checkpoint",
    # Core engine
    "DeterministicEngine",
    "ExecutionContext",
    "ExecutionResult",
    "CoreFatalInvariants",
    "InvariantViolation",
    "CoreMerkleChain",
    "MerkleProof",
    "CoreRollbackManager",
    "CoreCheckpoint",
    "ContractExecutor",
    "ContractValidator",
    "EventChain",
    "Event",
]
