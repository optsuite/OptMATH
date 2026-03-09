## Parameters

### n_jobs
- **Description**: Range for the number of jobs to be scheduled in the flow shop.
- **Type**: Tuple of two integers `(min_jobs, max_jobs)` or single Integer
- **Default**: `(3, 5)`
- **Reasonable Range**: 
  - Small instances: 3 to 10 jobs
  - Medium instances: 10 to 20 jobs
  - Large instances: 20 to 50 jobs
- **Note**: Affects problem complexity exponentially

### n_machines
- **Description**: Number of machines in the production line sequence.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 2 to 15 machines
- **Note**: Represents the number of processing stages

### processing_time_range
- **Description**: Range for processing times of jobs on each machine.
- **Type**: Tuple of two integers `(min_time, max_time)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_time`: 1 to 20
  - `max_time`: `min_time` to 50
- **Unit**: Time units (e.g., hours)

### seed
- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer
- **Usage**: Set for reproducible testing and validation