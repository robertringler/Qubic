# Neuromorphic & Cognitive Simulation

Event-driven spiking neural networks with biologically-inspired learning mechanisms.

## Features

- **Spiking Neurons**: Event-driven Leaky Integrate-and-Fire (LIF) models
- **STDP Learning**: Spike-timing-dependent plasticity
- **Time Quantization**: Efficient discrete-time simulation
- **Membrane Potential Caching**: Fast state management
- **Energy Efficiency**: Sparse event-driven computation

## Neuron Models

### Leaky Integrate-and-Fire (LIF)
```python
from neuromorphic import LIFNeuron, Network

neuron = LIFNeuron(
    tau_membrane=20.0,  # ms
    threshold=-50.0,    # mV
    reset=-70.0,        # mV
    refractory_period=2.0  # ms
)
```

### Adaptive Exponential (AdEx)
```python
from neuromorphic import AdExNeuron

neuron = AdExNeuron(
    tau_membrane=20.0,
    adaptation_time=100.0,
    spike_slope=2.0
)
```

## Network Construction

```python
from neuromorphic import Network, STDPSynapse

# Create network
net = Network(dt=0.1)  # 0.1 ms time step

# Add populations
input_pop = net.add_population(
    size=784,
    neuron_type="lif",
    name="input"
)

hidden_pop = net.add_population(
    size=200,
    neuron_type="lif",
    name="hidden"
)

output_pop = net.add_population(
    size=10,
    neuron_type="lif",
    name="output"
)

# Connect with STDP synapses
net.connect(
    source=input_pop,
    target=hidden_pop,
    synapse=STDPSynapse(
        weight_init="uniform",
        weight_range=(0.0, 1.0),
        learning_rate=0.001,
        tau_plus=20.0,
        tau_minus=20.0
    )
)
```

## STDP Learning

```python
from neuromorphic import STDPRule

# Configure STDP parameters
stdp = STDPRule(
    tau_plus=20.0,   # Pre-before-post time constant (ms)
    tau_minus=20.0,  # Post-before-pre time constant (ms)
    a_plus=0.01,     # Potentiation amplitude
    a_minus=0.01,    # Depression amplitude
    weight_min=0.0,
    weight_max=1.0
)

# Apply to synapses
network.set_learning_rule(stdp)
```

## Event-Driven Simulation

```python
from neuromorphic import EventDrivenSimulator

simulator = EventDrivenSimulator(
    network=net,
    time_quantization=0.1  # ms
)

# Simulate with spike input
spike_train = [
    {"time": 10.0, "neuron_id": 5},
    {"time": 15.0, "neuron_id": 12},
    {"time": 20.0, "neuron_id": 5},
]

results = simulator.run(
    duration=1000.0,  # ms
    input_spikes=spike_train,
    record_voltages=True,
    record_spikes=True
)

# Analyze results
print(f"Total spikes: {len(results.spike_times)}")
print(f"Average firing rate: {results.mean_firing_rate} Hz")
```

## Benchmarking

```python
from neuromorphic import benchmark_energy_efficiency

# Compare spiking vs. dense networks
benchmark = benchmark_energy_efficiency(
    spiking_network=net,
    dense_baseline="mlp_784_200_10",
    dataset="mnist",
    duration=1000.0
)

print(f"Spiking network energy: {benchmark['spiking_energy_j']} J")
print(f"Dense network energy: {benchmark['dense_energy_j']} J")
print(f"Energy reduction: {benchmark['energy_reduction_percent']}%")
print(f"Accuracy: {benchmark['spiking_accuracy']}% vs {benchmark['dense_accuracy']}%")
```

## Visualization

```python
from neuromorphic import SpikeRasterPlot, MembraneVoltagePlot

# Spike raster plot
raster = SpikeRasterPlot(results.spike_times)
raster.plot(time_range=(0, 100))
raster.save("outputs/spike_raster.png")

# Membrane voltage traces
voltage_plot = MembraneVoltagePlot(results.voltages)
voltage_plot.plot_neurons([0, 10, 50])
voltage_plot.save("outputs/voltages.png")
```

## Applications

- **Pattern Recognition**: Low-power classification
- **Temporal Processing**: Audio and video analysis
- **Robotics**: Sensorimotor control
- **Brain-Computer Interfaces**: Neural signal processing
- **Edge AI**: Ultra-low-power inference

## Performance

- **Event-driven**: 10-100× faster than time-stepped for sparse activity
- **Energy**: 100-1000× lower power vs. standard ANNs
- **Latency**: Sub-millisecond response times
- **Scalability**: Millions of neurons on single GPU

## Dependencies

- numpy >= 1.24
- torch >= 2.3 (optional, for GPU acceleration)
- matplotlib >= 3.8 (for visualization)
