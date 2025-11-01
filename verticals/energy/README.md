# Energy Systems and Smart-Grid Vertical

Fusion plasma simulation, smart-grid control, and renewable energy system optimization.

## Features

- **Plasma Field Solver**: MHD simulation for tokamak fusion reactors
- **Grid Balancing**: Real-time smart-grid load balancing with RL
- **Renewable Forecasting**: Solar and wind power generation prediction
- **Battery Optimization**: Energy storage system optimization
- **Thermal Management**: Power plant thermal dynamics and control

## Kernels

### plasma_field_solver
Magnetohydrodynamics (MHD) solver for tokamak plasma confinement simulations with adaptive time-stepping.

### grid_balancing
Hybrid PID + reinforcement learning controller for dynamic load balancing in smart grids.

### renewable_forecasting
Time-series forecasting models for solar irradiance and wind speed prediction.

### battery_optimization
Battery energy storage system (BESS) optimization with degradation modeling and lifetime prediction.

### thermal_management
Coupled thermal-hydraulic simulation for power generation systems.

## Getting Started

```python
from verticals.energy import plasma_field_solver, grid_balancing

# Plasma simulation
plasma_state = plasma_field_solver.simulate(
    geometry="examples/iter_tokamak.mesh",
    magnetic_field=5.3,  # Tesla
    plasma_current=15e6,  # Amperes
    duration=10.0  # seconds
)

# Smart-grid control
control_actions = grid_balancing.optimize(
    grid_state="examples/grid_snapshot.json",
    demand_forecast="datasets/load_forecast.parquet",
    renewable_generation="datasets/solar_wind.parquet"
)
```

## Benchmarks

Run benchmarks with:
```bash
python verticals/energy/benchmarks/plasma_convergence_bench.py
python verticals/energy/benchmarks/grid_response_bench.py
```

## Datasets

- **plasma_diagnostics**: HDF5 format ITER experimental data (300 GB)
- **grid_telemetry**: Parquet format smart meter streams (150 GB)

See `manifest.yaml` for complete dataset specifications.

## Examples

Explore Jupyter notebooks in `notebooks/`:
- `fusion_plasma.ipynb`: Tokamak plasma equilibrium calculation
- `grid_optimization.ipynb`: Multi-objective grid operation optimization
- `renewable_integration.ipynb`: Solar/wind integration strategies
- `battery_lifetime.ipynb`: Battery degradation modeling

## Performance Targets

- Plasma solver: 2.0× speedup in time-to-solution
- Grid response: 2.5× faster control latency
- Energy efficiency: Real-time telemetry via NVML/ROCm

## Outputs

- Plasma equilibrium visualizations
- Grid state dashboards with real-time metrics
- Energy flow diagrams

## Dependencies

See `manifest.yaml` for complete dependency list. Key requirements:
- Python ≥3.11
- CUDA ≥12.0
- PyTorch ≥2.3
- Gymnasium ≥0.29 (for RL)
- NVML support
