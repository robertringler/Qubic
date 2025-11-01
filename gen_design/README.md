# Generative Engineering Design

AI-powered automatic structure generation for materials, circuits, and aerodynamic surfaces.

## Features

- **Diffusion Models**: Denoising diffusion for 3D structure generation
- **Transformer Models**: Sequence-based design optimization
- **Differentiable Solvers**: Gradient-based optimization via differentiable physics
- **CAD Export**: Direct output to industry-standard formats

## Capabilities

### Materials Design
- Crystal structure generation
- Molecular design for drug discovery
- Composite material optimization
- Metamaterial topology

### Circuit Design
- Analog circuit topology generation
- PCB layout optimization
- Antenna design
- RF component optimization

### Aerodynamic Surfaces
- Airfoil shape optimization
- Wing geometry generation
- Turbine blade design
- Heat sink topology

## Usage

```python
from gen_design import DiffusionDesigner, TransformerDesigner

# Diffusion-based material generation
designer = DiffusionDesigner(
    domain="materials",
    model="stable_diffusion_3d",
    guidance_scale=7.5
)

structures = designer.generate(
    prompt="high-strength aluminum alloy with low density",
    num_samples=10,
    constraints={
        "density_max": 2.8,  # g/cm³
        "yield_strength_min": 400  # MPa
    }
)

# Export to CAD
for i, structure in enumerate(structures):
    structure.export_step(f"outputs/designs/structure_{i}.step")
    structure.export_mesh(f"outputs/designs/structure_{i}.stl")

# Transformer-based circuit design
circuit_designer = TransformerDesigner(
    domain="circuits",
    model="gpt_circuit"
)

circuit = circuit_designer.generate(
    specifications={
        "type": "low_noise_amplifier",
        "frequency": "5GHz",
        "gain": "20dB",
        "noise_figure_max": "1.5dB"
    }
)
```

## Gradient-Based Optimization

```python
from gen_design import DifferentiableSolver

# Couple generative model to differentiable solver
solver = DifferentiableSolver(
    physics="aerodynamics",
    objective="minimize_drag"
)

# Generate initial design
initial_design = designer.generate(
    prompt="transonic airfoil",
    num_samples=1
)[0]

# Optimize using gradients
optimized_design = solver.optimize(
    initial_design=initial_design,
    constraints={
        "lift_coefficient": 1.2,
        "mach_number": 0.85
    },
    iterations=100
)

optimized_design.export_step("outputs/designs/optimized_airfoil.step")
```

## Output Formats

- **CAD**: STEP, IGES, Parasolid
- **Mesh**: STL, OBJ, PLY
- **Analysis**: ABAQUS, ANSYS, OpenFOAM inputs
- **Manufacturing**: G-code, CNC toolpaths

## Model Zoo

Pre-trained models available:
- `materials_v1`: Material structure generation
- `circuits_v1`: Analog circuit topology
- `aerodynamics_v1`: Airfoil and wing shapes
- `thermal_v1`: Heat sink and cooling structures

## Performance

- Generation time: 1-10 seconds per design on A100
- Batch generation: 100+ designs in parallel
- Optimization: 100 iterations in 5-30 minutes
- Export: Real-time CAD/mesh generation

## Dependencies

- torch >= 2.3
- diffusers >= 0.24
- transformers >= 4.36
- trimesh >= 4.0
- cadquery >= 2.3
