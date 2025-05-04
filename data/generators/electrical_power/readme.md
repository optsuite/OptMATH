## Parameters

### n_generator_types

- **Description**: The number of generator types to include in the electrical power problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 10

### n_time_periods

- **Description**: The number of time periods (e.g., hours) to consider in the problem.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 24

### demand_range

- **Description**: A tuple specifying the minimum and maximum demand for each time period.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(100, 500)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### min_output_range

- **Description**: A tuple specifying the minimum and maximum power output for each generator type when it is on.
- **Type**: Tuple of two integers `(min_output, max_output)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_output`: 1 to 1,000
  - `max_output`: `min_output` to 1,000

### max_output_range

- **Description**: A tuple specifying the minimum and maximum power output for each generator type when it is on.
- **Type**: Tuple of two integers `(min_output, max_output)`
- **Default**: `(100, 200)`
- **Reasonable Range**:
  - `min_output`: 1 to 10,000
  - `max_output`: `min_output` to 10,000

### base_cost_range

- **Description**: A tuple specifying the minimum and maximum base operating cost for each generator type.
- **Type**: Tuple of two integers `(min_base_cost, max_base_cost)`
- **Default**: `(50, 100)`
- **Reasonable Range**:
  - `min_base_cost`: 1 to 10,000
  - `max_base_cost`: `min_base_cost` to 10,000

### per_mw_cost_range

- **Description**: A tuple specifying the minimum and maximum cost per megawatt (MW) generated for each generator type.
- **Type**: Tuple of two integers `(min_per_mw_cost, max_per_mw_cost)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_per_mw_cost`: 1 to 1,000
  - `max_per_mw_cost`: `min_per_mw_cost` to 1,000

### startup_cost_range

- **Description**: A tuple specifying the minimum and maximum startup cost for each generator type.
- **Type**: Tuple of two integers `(min_startup_cost, max_startup_cost)`
- **Default**: `(200, 500)`
- **Reasonable Range**:
  - `min_startup_cost`: 1 to 10,000
  - `max_startup_cost`: `min_startup_cost` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer