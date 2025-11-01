# Neural PDE Operators

Neural operators for solving partial differential equations using data-driven approaches.

## Operators

### Fourier Neural Operator (FNO)
Learns mappings between function spaces using Fourier transforms. Excellent for fluid dynamics, weather prediction, and multiscale physics.

### DeepONet
Deep operator networks that learn nonlinear operators from data. Suitable for parametric PDEs and inverse problems.

## Features

- **Symbolic DSL**: Specify differential equations in high-level notation
- **Adaptive Precision**: Dynamic precision switching for efficiency
- **Tile Streaming**: Handle large-scale simulations beyond GPU memory
- **Multi-Physics**: Coupled fluid-thermal-structural problems

## Usage

```python
from operators import FourierNeuralOperator, DeepONet

# Fourier Neural Operator for Navier-Stokes
fno = FourierNeuralOperator(
    modes=(12, 12),
    width=64,
    n_layers=4
)

# Train on simulation data
fno.train(
    input_data=velocity_fields,
    target_data=next_timestep_fields,
    epochs=100
)

# Predict future states
prediction = fno.forward(initial_conditions)

# DeepONet for parametric PDEs
deeponet = DeepONet(
    branch_net_layers=[128, 128, 128],
    trunk_net_layers=[128, 128, 128],
    output_dim=1
)
```

## Symbolic DSL Example

```python
from operators import SymbolicPDE, compile_kernel

# Define PDE symbolically
pde = SymbolicPDE("""
    ∂u/∂t + u·∇u = -∇p + ν∇²u  # Navier-Stokes
    ∇·u = 0                      # Incompressibility
""")

# Compile to optimized kernel
kernel = compile_kernel(pde, precision="fp32", backend="cuda")

# Execute
solution = kernel.solve(
    initial_conditions=u0,
    boundary_conditions=bc,
    timesteps=1000
)
```

## Applications

- **Fluid Dynamics**: Turbulent flow simulation
- **Plasma Physics**: Fusion reactor modeling
- **Materials Science**: Crystal growth and phase transitions
- **Climate Modeling**: Atmospheric and oceanic circulation
- **Electromagnetics**: Wave propagation

## Performance

- **Speedup**: 100-1000× over traditional PDE solvers for inference
- **Accuracy**: Sub-percent relative error on validation sets
- **Scalability**: Linear scaling to multi-GPU configurations
- **Memory**: Tile streaming enables TB-scale problems

## Dependencies

- torch >= 2.3
- jax >= 0.4.28
- numpy >= 1.24
- scipy >= 1.11
