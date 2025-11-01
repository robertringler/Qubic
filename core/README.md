# QuASIM Core Framework

Shared foundation modules providing common functionality across all verticals.

## Components

- **kernel_base**: Base classes for all simulation kernels
- **precision**: Precision management (fp8, fp16, fp32, fp64)
- **backend**: Hardware backend abstraction (CUDA, HIP, Metal, CPU)
- **telemetry**: Performance monitoring and energy tracking
- **config**: Configuration management and validation

## Usage

```python
from core import KernelBase, PrecisionMode, Backend

class MyKernel(KernelBase):
    def __init__(self):
        super().__init__(
            precision=PrecisionMode.FP32,
            backend=Backend.CUDA
        )
    
    def execute(self, inputs):
        # Kernel implementation
        pass
```

## Design Principles

- **Modularity**: All components are independently usable
- **Extensibility**: Easy to add new backends and precision modes
- **Performance**: Minimal overhead, zero-cost abstractions
- **Type Safety**: Full type hints and runtime validation
