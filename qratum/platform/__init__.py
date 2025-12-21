"""
QRATUM Platform Core Infrastructure

Provides the foundational components for deterministic, auditable execution:
- PlatformIntent: Immutable computation requests
- PlatformContract: Authorized, signed execution contracts
- MerkleEventChain: Thread-safe, cryptographically-verified event log
- PlatformOrchestrator: Routes intents to appropriate vertical modules
"""

from .core import (
    PlatformIntent,
    PlatformContract,
    Event,
    FATAL_INVARIANTS,
)
from .event_chain import MerkleEventChain
from .orchestrator import PlatformOrchestrator
from .substrates import ComputeSubstrate, SubstrateSelector

__all__ = [
    "PlatformIntent",
    "PlatformContract",
    "Event",
    "FATAL_INVARIANTS",
    "MerkleEventChain",
    "PlatformOrchestrator",
    "ComputeSubstrate",
    "SubstrateSelector",
]
