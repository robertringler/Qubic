"""Example: Cross-vertical integration demonstrating unified QuASIM architecture."""
from __future__ import annotations

import numpy as np
from core import Config, PrecisionMode, Backend
from quantum_bridge import QuantumBridge, QuantumJobConfig
from neuromorphic import Network, STDPSynapse
from operators import FourierNeuralOperator
from dashboard import DashboardServer, Plot3D, ColorMap


def example_quantum_finance_integration():
    """
    Demonstrate quantum-classical hybrid for financial risk calculation.
    
    Combines classical Monte Carlo with quantum optimization
    via the quantum_bridge module.
    """
    print("\n" + "="*60)
    print("Quantum-Finance Integration Example")
    print("="*60)
    
    from verticals.finance.examples.monte_carlo_pricing import MonteCarloOptionPricer
    
    # Classical pricing
    pricer = MonteCarloOptionPricer()
    classical_result = pricer.execute(
        spot=100.0, strike=100.0, rate=0.05,
        volatility=0.2, maturity=1.0, n_paths=10_000
    )
    
    # Quantum enhancement (simulated)
    quantum_bridge = QuantumBridge()
    quantum_result = quantum_bridge.monte_carlo_quantum(
        classical_samples=[classical_result],
        quantum_subroutine=lambda x: x,
        merge_strategy="weighted_average"
    )
    
    print(f"Classical option price: ${classical_result['price']:.4f}")
    print(f"Quantum-enhanced result: {quantum_result}")
    print(f"✓ Successfully integrated quantum and finance verticals\n")


def example_neuromorphic_edge_deployment():
    """
    Demonstrate neuromorphic network compilation for edge deployment.
    
    Shows integration between neuromorphic module and edge_runtime.
    """
    print("="*60)
    print("Neuromorphic-Edge Integration Example")
    print("="*60)
    
    from edge_runtime import KernelCompiler, Target
    
    # Create spiking neural network
    net = Network(dt=0.1)
    input_pop = net.add_population(size=28, neuron_type="lif", name="input")
    output_pop = net.add_population(size=10, neuron_type="lif", name="output")
    
    net.connect(
        source=input_pop,
        target=output_pop,
        synapse=STDPSynapse(learning_rate=0.001)
    )
    
    print(f"Created SNN with {len(net._populations)} populations")
    
    # Compile for edge deployment
    compiler = KernelCompiler(target=Target.ARM_CORTEX_A72)
    edge_binary = compiler.compile(
        kernel=net,
        output_format="elf",
        enable_profiling=True
    )
    
    print(f"✓ Compiled neuromorphic network for ARM target\n")


def example_pde_operators_aerospace():
    """
    Demonstrate Neural PDE operators for aerospace CFD.
    
    Shows integration of operators module with aerospace vertical.
    """
    print("="*60)
    print("PDE Operators-Aerospace Integration Example")
    print("="*60)
    
    # Create Fourier Neural Operator for fluid flow
    fno = FourierNeuralOperator(
        modes=(12, 12),
        width=64,
        n_layers=4
    )
    
    # Simulate training on velocity fields
    velocity_fields = np.random.rand(100, 64, 64, 2)  # (batch, H, W, channels)
    target_fields = velocity_fields * 1.01  # Next timestep
    
    training_stats = fno.train(
        input_data=velocity_fields,
        target_data=target_fields,
        epochs=10
    )
    
    print(f"Trained FNO for CFD: {training_stats}")
    
    # Apply to aerospace simulation
    initial_flow = np.random.rand(64, 64, 2)
    predicted_flow = fno.forward(initial_flow)
    print(f"Predicted flow field shape: {predicted_flow.shape}, mean: {np.mean(predicted_flow):.4f}")
    print(f"✓ Applied neural PDE operator to aerospace flow field\n")


def example_federated_multi_vertical():
    """
    Demonstrate federated learning across multiple verticals.
    
    Shows how different institutions can collaborate without sharing data.
    """
    print("="*60)
    print("Federated Multi-Vertical Example")
    print("="*60)
    
    from federated import FederatedService, FederatedClient, PrivacyConfig
    
    # Start federated coordinator
    service = FederatedService(
        privacy_config=PrivacyConfig(epsilon=1.0, delta=1e-5),
        blockchain_enabled=True
    )
    
    # Register multiple verticals as tenants
    service.register_tenant("pharma_lab_1", {"institution": "University A"})
    service.register_tenant("finance_firm_1", {"institution": "Bank B"})
    service.register_tenant("aerospace_co_1", {"institution": "Company C"})
    
    print(f"✓ Registered {len(service._tenants)} tenants across verticals")
    print(f"  Privacy budget: ε={service.privacy_config.epsilon}")
    print(f"  Blockchain enabled: {service.blockchain_enabled}\n")


def example_visualization_dashboard():
    """
    Demonstrate 3D visualization dashboard for multiple verticals.
    
    Shows unified visualization across different simulation types.
    """
    print("="*60)
    print("Visualization Dashboard Example")
    print("="*60)
    
    # Create dashboard server
    server = DashboardServer(port=8050, enable_3d=True)
    
    # Register all verticals
    verticals = ["pharma", "aerospace", "finance", "telecom", "energy", "defense"]
    for vertical in verticals:
        server.register_vertical(vertical, vertical.capitalize())
    
    # Create 3D visualization
    plot = Plot3D(title="Multi-Vertical Simulation States")
    
    # Add sample volume data
    volume_data = np.random.rand(32, 32, 32)
    plot.add_volume(volume_data, colormap=ColorMap.VIRIDIS, opacity=0.7)
    plot.add_isosurface(value=0.5, color="red")
    
    print(f"✓ Dashboard configured for {len(verticals)} verticals")
    print(f"  3D visualization ready\n")


def main():
    """Run all cross-vertical integration examples."""
    print("\n" + "╔" + "═"*58 + "╗")
    print("║" + " "*15 + "QuASIM Phase IV Integration" + " "*15 + "║")
    print("╚" + "═"*58 + "╝")
    
    # Run integration examples
    example_quantum_finance_integration()
    example_neuromorphic_edge_deployment()
    example_pde_operators_aerospace()
    example_federated_multi_vertical()
    example_visualization_dashboard()
    
    print("="*60)
    print("Summary: All Cross-Vertical Integrations Successful!")
    print("="*60)
    print("\nPhase IV demonstrates:")
    print("  ✓ Quantum-classical hybrid workflows")
    print("  ✓ Neuromorphic to edge deployment pipeline")
    print("  ✓ Neural PDE operators for scientific computing")
    print("  ✓ Federated multi-tenant collaboration")
    print("  ✓ Unified 3D visualization across verticals")
    print("\nQuASIM is ready for full-stack simulation ecosystems!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
