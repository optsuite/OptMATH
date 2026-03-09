## Parameters

### num_jobs

- **Description**: The number of total distinct jobs to be scheduled
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 1 to 1000

### num_machines

- **Description**: The number of  total distinct machines available for processing
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 1-1000

### operations_per_job

- **Description**: The **minimum** and **maximum** of operations each job must undergo. Typically, each job has one operation per machine..
- **Type**: Tuple of two integers `(min_weight, max_weight)`
- **Default**: `(2, 8)`
- **Reasonable Range**:
  - `min_weight`: 1
  - `max_weight`: `min_weight` to 100

### processing_time_range

- **Description**: The **minimum** and **maximum** of processing times for operations.
- **Type**: Tuple of two integers `(min_weight, max_weight)`
- **Default**: `(1, 10)`
- **Reasonable Range**: 
	- `min_weight`: 1
  - `max_weight`: `min_weight` to 1000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer