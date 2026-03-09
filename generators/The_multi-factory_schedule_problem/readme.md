## Parameters

### n_factories

- **Description**: The number of factories to include in the multi-factory schedule problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 100

### n_months

- **Description**: The number of months to include in the multi-factory schedule problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 12

### fixed_cost_range

- **Description**: A tuple specifying the minimum and maximum fixed costs for running a factory during a month.
- **Type**: Tuple of two integers `(min_fixed_cost, max_fixed_cost)`
- **Default**: `(100, 500)`
- **Reasonable Range**:
  - `min_fixed_cost`: 1 to 10,000
  - `max_fixed_cost`: `min_fixed_cost` to 10,000

### min_production_range

- **Description**: A tuple specifying the minimum and maximum production levels for each factory.
- **Type**: Tuple of two integers `(min_production, max_production)`
- **Default**: `(10, 20)`
- **Reasonable Range**:
  - `min_production`: 1 to 10,000
  - `max_production`: `min_production` to 10,000

### max_production_range

- **Description**: A tuple specifying the maximum production levels for each factory.
- **Type**: Tuple of two integers `(min_max_production, max_max_production)`
- **Default**: `(50, 100)`
- **Reasonable Range**:
  - `min_max_production`: 1 to 10,000
  - `max_max_production`: `min_max_production` to 10,000

### unit_cost_range

- **Description**: A tuple specifying the minimum and maximum unit production costs for each factory.
- **Type**: Tuple of two integers `(min_unit_cost, max_unit_cost)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_unit_cost`: 1 to 10,000
  - `max_unit_cost`: `min_unit_cost` to 10,000

### demand_range

- **Description**: A tuple specifying the minimum and maximum demand for each month.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(100, 300)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer