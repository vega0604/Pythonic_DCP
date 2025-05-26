# PDCP - Pythonic DCP Wrapper

PDCP is a Python package that provides a more Pythonic interface to the DCP Python SDK (Bifrost2). It simplifies the interaction with DCP services by providing a clean, type-hinted interface for job management and computation.

## Features

- **Type-Safe Configuration**: Full type hints using TypedDict for job configuration
- **Event Handling**: Flexible event subscription system for job monitoring
- **Job Chaining**: Basic workflow management through job chaining
- **Compute Groups**: Support for DCP compute group management
- **Streaming Slices**: Optional streaming support for job slices

## Requirements
PDCP requires a python version between [3.10, 4.0) and the latest node version.

You also need to have your keystore files located in your home directory as shown below for dcp to identify you.

```
└── %USERPROFILE%/.dcp
    ├── default.keystore
    └── id.keystore
```

## Installation

```bash
pip install pdcp
```

## Quick Start

```python
from pdcp import Job, dcp
from pdcp.custom_types import JobConfig

# Define your work function
def work(x, a):
    dcp.progress()
    return x * a

# Configure your job
config: JobConfig = {   
    "name": "test",
    "work_function": work,
    "slices": [1, 2, 3],
    "constant_params": [3],
    "compute_groups": [{"joinKey": "group_name", "joinSecret": "secret"}]
}

# Create and configure the job
job = Job(config)

# Subscribe to job events
job.subscribe_to({
    "readystatechange": print,
    "accepted": lambda _: print(f'accepted: {job.id}'),
    "result": lambda e: print(f'result: {e.result}'),
    "status": lambda e: print(f'status: {e.runStatus}')
})

# Execute the job
job.dispatch()
results = job.get_results()
print(results)
```

## Job Configuration

The `JobConfig` TypedDict provides a type-safe way to configure jobs:

```python
class JobConfig(TypedDict):
    name: str                                           # Name of the job
    work_function: callable                             # Function to be executed
    slices: NotRequired[list]                           # Input data slices
    stream_slices: NotRequired[bool]                    # Enable/disable slice streaming
    constant_params: NotRequired[list[any]]             # Constant parameters for work function
    compute_groups: NotRequired[list[ComputeGroup]]     # DCP compute groups
    job_dependencies: NotRequired[list[str]]            # Required local dependencies
```

## Event Handling

Jobs support various events that can be subscribed to:

```python
from pdcp.types import EventHandler

events: EventHandler = {
    "readystatechange": handler,    # Job state changes
    "accepted": handler,            # Job accepted by DCP
    "result": handler,              # New result available
    "complete": handler,            # Job completed
    "console": handler,             # Console output
    "status": handler               # Status updates
}

job.subscribe_to(events)
```

## Job Chaining

Basic job chaining is supported through the `chain` method:

```python
# Create and chain jobs
job1 = Job(config1)
job2 = job1.chain(config2)

job1.dispatch()
```

## Compute Groups

Support for DCP compute groups:

```python
config: JobConfig = {
    "name": "my_job",
    "work_function": work,
    "compute_groups": [
        {
            "joinKey": "group_name",
            "joinSecret": "secret"
        }
    ]
}
```

## Streaming Slices

Enable streaming slices for continuous data processing:

```python
config: JobConfig = {
    "name": "streaming_job",
    "work_function": work,
    "stream_slices": True,  # Enable streaming
    "slices": initial_slices
}

job = Job(config)
# Add more slices later
job.add_slices(new_slices)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
