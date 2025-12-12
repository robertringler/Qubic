"""Tire simulation domain for QuASIM.

This module provides comprehensive tire simulation capabilities including:
- Material modeling (compounds, viscoelasticity, thermomechanics)
- Structural design (tread geometry, internal structure)
- Environmental conditions (temperature, surfaces, weather)
- Performance analysis (traction, wear, thermal response, rolling resistance)
- Quantum-enhanced optimization for multi-variable interactions
"""

from .materials import (
    CompoundType,
    MaterialProperties,
    TireCompound,
)
from .geometry import (
    TreadDesign,
    TireGeometry,
    TireStructure,
)
from .environment import (
    EnvironmentalConditions,
    RoadSurface,
    WeatherCondition,
)
from .simulation import (
    TireSimulation,
    TireSimulationResult,
    PerformanceMetrics,
)
from .generator import (
    TireScenarioGenerator,
    generate_tire_library,
)

__all__ = [
    "CompoundType",
    "MaterialProperties",
    "TireCompound",
    "TreadDesign",
    "TireGeometry",
    "TireStructure",
    "EnvironmentalConditions",
    "RoadSurface",
    "WeatherCondition",
    "TireSimulation",
    "TireSimulationResult",
    "PerformanceMetrics",
    "TireScenarioGenerator",
    "generate_tire_library",
]
