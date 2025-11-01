# Async Execution

Asynchronous kernel execution and distributed task management.

## Features

- **Non-Blocking Execution**: Async kernel launches
- **Task Queues**: Priority-based scheduling
- **Distributed Execution**: Multi-GPU, multi-node
- **Stream Management**: CUDA/HIP stream abstraction

## Usage

```python
from async_exec import AsyncExecutor, Task

executor = AsyncExecutor(
    devices=["cuda:0", "cuda:1"],
    max_concurrent=4
)

# Submit async tasks
task1 = executor.submit(kernel1, data1)
task2 = executor.submit(kernel2, data2)

# Wait for results
result1 = task1.wait()
result2 = task2.wait()
```
