# AutoTune

Automatic kernel parameter tuning and optimization.

## Features

- **Grid Search**: Exhaustive parameter exploration
- **Bayesian Optimization**: Efficient search with Gaussian processes
- **Genetic Algorithms**: Evolutionary optimization
- **Learned Tuning**: ML-based parameter prediction

## Usage

```python
from autotune import Tuner, SearchSpace

# Define search space
space = SearchSpace({
    "block_size": [64, 128, 256],
    "tile_size": [16, 32, 64],
    "num_threads": [1, 2, 4, 8]
})

# Create tuner
tuner = Tuner(
    kernel=my_kernel,
    search_space=space,
    objective="minimize_latency"
)

# Find optimal parameters
best_params = tuner.optimize(max_trials=100)
print(f"Best parameters: {best_params}")
```
