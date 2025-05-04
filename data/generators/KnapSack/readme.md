## Parameters

### n_items

- **Description**: The number of items to include in the knapsack problem.
- **Type**: Integer
- **Default**: `50`
- **Reasonable Range**: 1 to 1000

### value_range

- **Description**: A tuple specifying the minimum and maximum values for the items' values.
- **Type**: Tuple of two integers `(min_value, max_value)`
- **Default**: `(1, 1000)`
- **Reasonable Range**:
  - `min_value`: 1 to 10,000
  - `max_value`: `min_value` to 10,000

### weight_range

- **Description**: A tuple specifying the minimum and maximum weights for the items' weights.
- **Type**: Tuple of two integers `(min_weight, max_weight)`
- **Default**: `(1, 500)`
- **Reasonable Range**:
  - `min_weight`: 1 to 10,000
  - `max_weight`: `min_weight` to 10,000

### capacity_ratio

- **Description**: The ratio of the knapsack capacity to the total weight of all items. Determines how full the knapsack can be relative to the total weight.
- **Type**: Float between 0 and 1
- **Default**: `0.7`
- **Reasonable Range**: 0.1 to 1.0

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer
