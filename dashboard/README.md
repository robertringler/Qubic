# Interactive 3D Visualization Dashboard

Advanced visualization dashboard with interactive 3D rendering for simulation states, attractor manifolds, and thermal maps.

## Features

- **3D Visualization**: Interactive 3D plots using Plotly and Three.js
- **Simulation States**: Real-time visualization of dynamic systems
- **Attractor Manifolds**: Phase space and state-space visualization
- **Thermal Maps**: Heat maps and temperature distributions
- **Flow Fields**: Vector field and streamline visualization
- **Performance Metrics**: Real-time telemetry dashboards

## Technologies

- **Plotly**: Interactive 2D/3D plotting
- **Three.js**: WebGL-based 3D rendering
- **Dash**: Web framework for Python dashboards
- **WebSocket**: Real-time data streaming

## Usage

### Start Dashboard Server

```python
from dashboard import DashboardServer

server = DashboardServer(
    port=8050,
    enable_3d=True,
    enable_realtime=True
)

server.register_vertical("pharma", "Pharmaceutical Simulations")
server.register_vertical("aerospace", "Aerospace CFD")
server.register_vertical("energy", "Plasma & Grid Control")

server.run()
# Dashboard available at http://localhost:8050
```

### 3D Visualization

```python
from dashboard import Plot3D, ColorMap

# Visualize 3D scalar field
plot = Plot3D(title="Plasma Temperature Distribution")
plot.add_volume(
    data=temperature_field,
    colormap=ColorMap.INFERNO,
    opacity=0.7
)
plot.add_isosurface(value=1000.0, color="red")
plot.show()
```

### Attractor Manifolds

```python
from dashboard import AttractorPlot

# Visualize Lorenz attractor or other dynamical systems
attractor = AttractorPlot(
    system="lorenz",
    initial_conditions=[1.0, 1.0, 1.0],
    timesteps=10000
)

attractor.plot_trajectory_3d()
attractor.plot_phase_space()
attractor.export_interactive("outputs/lorenz.html")
```

### Real-Time Monitoring

```python
from dashboard import RealtimeDashboard

dashboard = RealtimeDashboard(
    title="Smart Grid Monitor",
    update_interval_ms=100
)

# Add real-time metrics
dashboard.add_timeseries("Grid Load (MW)", max_points=1000)
dashboard.add_gauge("Frequency (Hz)", min=59.5, max=60.5, target=60.0)
dashboard.add_heatmap("Regional Demand", shape=(10, 10))

# Stream data
while True:
    dashboard.update({
        "Grid Load (MW)": get_current_load(),
        "Frequency (Hz)": get_grid_frequency(),
        "Regional Demand": get_demand_heatmap()
    })
    time.sleep(0.1)
```

### Thermal Maps

```python
from dashboard import ThermalMap

thermal = ThermalMap(
    geometry=wing_mesh,
    temperature_field=temperatures,
    colormap="jet"
)

thermal.add_contours(levels=10)
thermal.add_annotations([
    {"position": [0, 0, 0], "text": "Leading Edge"},
    {"position": [1, 0, 0], "text": "Trailing Edge"}
])

thermal.export_html("outputs/thermal_analysis.html")
```

### Flow Field Visualization

```python
from dashboard import FlowField

flow = FlowField(
    velocity_x=u_field,
    velocity_y=v_field,
    velocity_z=w_field,
    resolution=(64, 64, 64)
)

# Add streamlines from seed points
flow.add_streamlines(
    seed_points=[[0, 0, 0], [1, 1, 1]],
    integration_step=0.01
)

# Add vector glyphs
flow.add_vectors(
    sampling="uniform",
    scale=0.1,
    color_by_magnitude=True
)

flow.show()
```

## Dashboard Layouts

### Vertical-Specific Dashboards

Each vertical gets a custom dashboard:

```python
# Pharma dashboard - molecular structures and binding sites
pharma_dash = server.create_vertical_dashboard("pharma")
pharma_dash.add_molecule_viewer(pdb_file="protein.pdb")
pharma_dash.add_binding_site_heatmap()

# Aerospace dashboard - CFD results
aero_dash = server.create_vertical_dashboard("aerospace")
aero_dash.add_pressure_contours()
aero_dash.add_velocity_streamlines()
aero_dash.add_force_coefficients_timeseries()

# Energy dashboard - plasma equilibrium
energy_dash = server.create_vertical_dashboard("energy")
energy_dash.add_plasma_cross_section()
energy_dash.add_magnetic_field_lines()
energy_dash.add_confinement_metrics()
```

## Export Formats

- **HTML**: Self-contained interactive dashboards
- **PNG/SVG**: Static images for reports
- **MP4/WebM**: Video animations
- **JSON**: Data export for further analysis

## Example: Complete Dashboard

```python
from dashboard import DashboardServer, Plot3D, FlowField

server = DashboardServer(port=8050)

# Create multi-panel layout
layout = server.create_layout(rows=2, cols=2)

# Top-left: 3D temperature
layout.add_panel(
    row=0, col=0,
    plot=Plot3D(title="Temperature").add_volume(temp_data)
)

# Top-right: Flow streamlines
layout.add_panel(
    row=0, col=1,
    plot=FlowField(u, v, w).add_streamlines()
)

# Bottom-left: Time series
layout.add_panel(
    row=1, col=0,
    plot=server.create_timeseries(["Energy", "Power"])
)

# Bottom-right: Metrics table
layout.add_panel(
    row=1, col=1,
    component=server.create_metrics_table()
)

server.show_layout(layout)
```

## Dependencies

- plotly >= 5.18
- dash >= 2.14
- dash-vtk >= 0.0.9
- pyvista >= 0.42
- matplotlib >= 3.8
