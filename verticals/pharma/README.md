# Pharmaceutical Simulation Vertical

GPU-accelerated molecular dynamics, drug docking, and pharmacokinetics simulation for pharmaceutical research and drug discovery.

## Features

- **Molecular Dynamics**: Protein folding simulation with GPU acceleration
- **Docking Simulation**: Ligand-protein interaction modeling with quantum corrections
- **Pharmacokinetics**: ADME/Tox prediction using neural ordinary differential equations

## Kernels

### molecular_dynamics
High-performance molecular dynamics engine optimized for protein folding simulations. Supports multiple precision modes (fp16/32/64) and GPU backends.

### docking_simulation
Virtual screening and ligand-protein docking with quantum-enhanced scoring functions for improved accuracy.

### pharmacokinetics
Neural ODE-based ADME/Tox prediction pipeline for rapid drug candidate evaluation.

## Getting Started

```python
from verticals.pharma import molecular_dynamics, docking_simulation

# Run protein folding simulation
result = molecular_dynamics.simulate(
    protein_pdb="examples/1abc.pdb",
    timesteps=10000,
    precision="fp32"
)

# Virtual screening
hits = docking_simulation.screen(
    receptor="examples/target.pdb",
    library="datasets/compounds.sdf",
    top_n=100
)
```

## Benchmarks

Run benchmarks with:
```bash
python verticals/pharma/benchmarks/protein_folding_bench.py
python verticals/pharma/benchmarks/virtual_screening_bench.py
```

## Datasets

- **protein_structures**: PDB format protein structures (50 GB)
- **compound_library**: SDF format chemical compounds from ChEMBL (10 GB)

See `manifest.yaml` for complete dataset specifications.

## Examples

Explore Jupyter notebooks in `notebooks/`:
- `protein_folding_tutorial.ipynb`: Step-by-step protein folding workflow
- `drug_screening.ipynb`: Virtual screening pipeline demonstration
- `pk_prediction.ipynb`: Pharmacokinetic property prediction

## Performance Targets

- Protein folding: 2.0× speedup vs. baseline
- Virtual screening: 3.0× throughput improvement
- Energy efficiency: ≤30% reduction in power consumption

## Dependencies

See `manifest.yaml` for complete dependency list. Key requirements:
- Python ≥3.11
- CUDA ≥12.0
- PyTorch ≥2.3
- RDKit ≥2023.3
- BioPython ≥1.81
