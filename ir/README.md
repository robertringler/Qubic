# Intermediate Representation (IR)

MLIR-based intermediate representation for QuASIM kernels enabling multi-backend code generation.

## Features

- **MLIR Integration**: Leverage MLIR infrastructure
- **Custom Dialects**: QuASIM-specific operations
- **Multi-Backend**: Target CUDA, HIP, Metal, CPU
- **Optimization Passes**: Kernel fusion, layout optimization

## Usage

```python
from ir import IRBuilder, Dialect

builder = IRBuilder()
module = builder.create_module("my_kernel")

# Define operations
func = module.define_function("matmul", inputs=["A", "B"], output="C")
func.add_operation("tensor.contract", ["A", "B"], result="C")

# Apply optimization passes
module.apply_passes(["fusion", "layout-opt", "vectorize"])

# Lower to target backend
cuda_code = module.lower_to("cuda")
```
