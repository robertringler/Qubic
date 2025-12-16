"""Advanced Molecular Dynamics Lab.

A production-grade, interactive 3D molecular visualization and simulation lab
featuring:
- 3Dmol.js integration for web-based molecular viewing
- PDB file loading and parsing (Protein Data Bank)
- Interactive molecular docking simulation
- VR-ready WebXR support
- Haptic feedback simulation
- Real-time molecular dynamics simulation

This module provides both Python backend services and web-based frontend
components for a complete molecular dynamics research environment.
"""

from .core.molecular_viewer import MolecularViewer, ViewerConfig
from .core.pdb_loader import PDBLoader, PDBStructure
from .core.docking_engine import DockingEngine, DockingConfig, DockingResult
from .core.md_simulator import MDSimulator, MDConfig, SimulationState
from .webxr.vr_controller import VRController, VRConfig
from .webxr.haptic_engine import HapticEngine, HapticConfig, HapticFeedback
from .web.server import MolecularLabServer

__all__ = [
    # Core components
    "MolecularViewer",
    "ViewerConfig",
    "PDBLoader",
    "PDBStructure",
    "DockingEngine",
    "DockingConfig",
    "DockingResult",
    "MDSimulator",
    "MDConfig",
    "SimulationState",
    # WebXR components
    "VRController",
    "VRConfig",
    "HapticEngine",
    "HapticConfig",
    "HapticFeedback",
    # Web server
    "MolecularLabServer",
]

__version__ = "1.0.0"
