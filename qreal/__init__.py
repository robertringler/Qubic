"""Reality adapters bringing external data into Q-Stack deterministically."""
from qreal.base_adapter import BaseAdapter, AdapterOutput
from qreal.market_adapter import MarketAdapter
from qreal.telemetry_adapter import TelemetryAdapter
from qreal.grid_adapter import GridAdapter
from qreal.transport_adapter import TransportAdapter
from qreal.science_adapter import ScienceAdapter
from qreal.provenance import ProvenanceRecord, compute_provenance
from qreal.normalizers import NormalizationChain

__all__ = [
    "BaseAdapter",
    "AdapterOutput",
    "MarketAdapter",
    "TelemetryAdapter",
    "GridAdapter",
    "TransportAdapter",
    "ScienceAdapter",
    "ProvenanceRecord",
    "compute_provenance",
    "NormalizationChain",
]
