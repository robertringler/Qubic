#!/usr/bin/env python
"""CLI interface for QCMG simulations."""

from __future__ import annotations

import argparse
import json
import sys

from quasim.sim import QCMGParameters, QuantacosmorphysigeneticField


def main():
    """Run QCMG simulation from command line."""
    parser = argparse.ArgumentParser(
        description="Run Quantacosmomorphysigenetic Field simulation"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of evolution iterations (default: 100)",
    )
    parser.add_argument(
        "--grid-size",
        type=int,
        default=64,
        help="Grid size (default: 64)",
    )
    parser.add_argument(
        "--dt",
        type=float,
        default=0.01,
        help="Time step (default: 0.01)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="gaussian",
        choices=["gaussian", "soliton", "random"],
        help="Initialization mode (default: gaussian)",
    )
    parser.add_argument(
        "--coupling-strength",
        type=float,
        default=0.1,
        help="Coupling strength (default: 0.1)",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (default: None)",
    )
    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="Export results to JSON file (default: None)",
    )
    
    args = parser.parse_args()
    
    # Create parameters
    params = QCMGParameters(
        grid_size=args.grid_size,
        dt=args.dt,
        coupling_strength=args.coupling_strength,
        random_seed=args.random_seed,
    )
    
    # Initialize field
    print(f"Initializing QCMG field (mode={args.mode})...")
    field = QuantacosmorphysigeneticField(params)
    field.initialize(mode=args.mode)
    
    # Run simulation
    print(f"Running {args.iterations} iterations...")
    for i in range(args.iterations):
        state = field.evolve()
        
        if (i + 1) % 10 == 0:
            print(
                f"  Step {i + 1:4d}: "
                f"C={state.coherence:.4f}, "
                f"S={state.entropy:.4f}, "
                f"E={state.energy:.4f}"
            )
    
    # Final state
    final_state = field.get_state()
    print("\nFinal state:")
    print(f"  Time:      {final_state.time:.4f}")
    print(f"  Coherence: {final_state.coherence:.4f}")
    print(f"  Entropy:   {final_state.entropy:.4f}")
    print(f"  Energy:    {final_state.energy:.4f}")
    
    # Export if requested
    if args.export:
        print(f"\nExporting to {args.export}...")
        export_data = field.export_state()
        
        # Convert numpy arrays to lists for JSON serialization
        export_data["final_state"] = {
            "time": final_state.time,
            "coherence": final_state.coherence,
            "entropy": final_state.entropy,
            "energy": final_state.energy,
            "state": {
                "phi_m_real": final_state.phi_m.real.tolist(),
                "phi_m_imag": final_state.phi_m.imag.tolist(),
                "phi_i_real": final_state.phi_i.real.tolist(),
                "phi_i_imag": final_state.phi_i.imag.tolist(),
            },
        }
        
        with open(args.export, "w") as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Results saved to {args.export}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
