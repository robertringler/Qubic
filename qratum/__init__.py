"""
QRATUM Ecosystem - Unified Brand Namespace

This module provides branded aliases to existing QuASIM/Qubic subsystems.
All underlying implementations remain unchanged - this is a pure alias layer.

Subsystem Mapping:
- QRATUM:NOVA    → quasim (Quantum-Accelerated Simulation Engine)
- QRATUM:VISOR   → qubic.visualization (Visualization Pipeline)
- QRATUM:QUANTIS → qunimbus (Distributed Quantum Compute)
- QRATUM:XENON   → xenon (Biological Intelligence Substrate)
- QRATUM:CORE_OS → qnx (Platform Operating System)
- QRATUM:CRYPTEX → qstack.security (Cryptography Layer)

Usage:
    # New QRATUM-branded imports (recommended for new code)
    from qratum import NOVA, VISOR, QUANTIS
    
    # Legacy imports still work (backward compatible)
    from quasim import QuASIM
    from qubic.visualization import VisualizationPipeline
"""

__version__ = "1.0.0-qratum-alpha"

# === QRATUM:NOVA - Quantum Simulation Engine ===
try:
    from quasim import QuASIM as NOVA
    from quasim import __version__ as _nova_version
    NOVA_AVAILABLE = True
except ImportError:
    NOVA = None
    NOVA_AVAILABLE = False
    _nova_version = "not-installed"

# === QRATUM:VISOR - Visualization & Analytics ===
try:
    from qubic.visualization import VisualizationPipeline as VISOR
    from qubic.visualization import __version__ as _visor_version
    VISOR_AVAILABLE = True
except ImportError:
    VISOR = None
    VISOR_AVAILABLE = False
    _visor_version = "not-installed"

# === QRATUM:QUANTIS - Distributed Orchestration ===
try:
    from qunimbus import QuNimbus as QUANTIS
    from qunimbus import __version__ as _quantis_version
    QUANTIS_AVAILABLE = True
except ImportError:
    QUANTIS = None
    QUANTIS_AVAILABLE = False
    _quantis_version = "not-installed"

# === QRATUM:XENON - Biological Intelligence ===
try:
    from xenon import XENON
    from xenon import __version__ as _xenon_version
    XENON_AVAILABLE = True
except ImportError:
    XENON = None
    XENON_AVAILABLE = False
    _xenon_version = "not-installed"

# === QRATUM:CORE_OS - Platform Runtime ===
try:
    from qnx import QNXSubstrate as CORE_OS
    from qnx import __version__ as _core_os_version
    CORE_OS_AVAILABLE = True
except ImportError:
    CORE_OS = None
    CORE_OS_AVAILABLE = False
    _core_os_version = "not-installed"

# === QRATUM:CRYPTEX - Security & Cryptography ===
try:
    from qstack.security import Cryptography as CRYPTEX
    from qstack.security import __version__ as _cryptex_version
    CRYPTEX_AVAILABLE = True
except (ImportError, AttributeError):
    try:
        from qstack import QStack as CRYPTEX
        _cryptex_version = "legacy"
        CRYPTEX_AVAILABLE = True
    except ImportError:
        CRYPTEX = None
        CRYPTEX_AVAILABLE = False
        _cryptex_version = "not-installed"

# === QRATUM:Q_IMAGE - Quantum Imaging ===
try:
    from q_image import QImage as Q_IMAGE
    from q_image import __version__ as _q_image_version
    Q_IMAGE_AVAILABLE = True
except ImportError:
    Q_IMAGE = None
    Q_IMAGE_AVAILABLE = False
    _q_image_version = "not-installed"

__all__ = [
    "NOVA",
    "VISOR",
    "QUANTIS",
    "XENON",
    "CORE_OS",
    "CRYPTEX",
    "Q_IMAGE",
    "get_subsystem_status",
]


def get_subsystem_status():
    """Return availability status of all QRATUM subsystems."""
    return {
        "NOVA": {"available": NOVA_AVAILABLE, "version": _nova_version},
        "VISOR": {"available": VISOR_AVAILABLE, "version": _visor_version},
        "QUANTIS": {"available": QUANTIS_AVAILABLE, "version": _quantis_version},
        "XENON": {"available": XENON_AVAILABLE, "version": _xenon_version},
        "CORE_OS": {"available": CORE_OS_AVAILABLE, "version": _core_os_version},
        "CRYPTEX": {"available": CRYPTEX_AVAILABLE, "version": _cryptex_version},
        "Q_IMAGE": {"available": Q_IMAGE_AVAILABLE, "version": _q_image_version},
    }
