"""QUBIC Unified Visualization Subsystem.

This module provides a production-ready visualization system for simulation results,
including tire simulations, quantum circuits, XENON bio-mechanisms, and generic mesh/field data.

Components:
    - core: Data models, camera, and lighting
    - adapters: Simulation-specific data adapters (tire, quantum, mesh, XENON)
    - backends: Rendering backends (matplotlib, headless, GPU)
    - pipelines: Visualization pipelines (static, timeseries, streaming)
    - exporters: Export functionality (image, video, interactive)
    - examples: Runnable examples
    - cli: Command-line interface
    - qubic_viz: High-level unified visualization API

Usage:
    from qubic.visualization import QubicVisualizer, VizConfig
    
    viz = QubicVisualizer()
    viz.visualize_mechanism(nodes, edges, output_path="output.png")
"""

__version__ = "0.1.0"

from qubic.visualization.qubic_viz import QubicVisualizer, VizConfig

__all__ = [
    "QubicVisualizer",
    "VizConfig",
]
