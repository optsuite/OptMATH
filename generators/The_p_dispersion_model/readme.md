## Parameters

### n_nodes

- **Description**: The number of candidate nodes (locations) to include in the p-dispersion problem.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 2 to 1000

### p

- **Description**: The number of facilities to select from the candidate nodes.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 2 to `n_nodes`

### distance_range

- **Description**: A tuple specifying the minimum and maximum distances between any two nodes.
- **Type**: Tuple of two integers `(min_distance, max_distance)`
- **Default**: `(1, 100)`
- **Reasonable Range**:
  - `min_distance`: 1 to 10,000
  - `max_distance`: `min_distance` to 10,000

### M

- **Description**: A sufficiently large number (big-M) used in the constraints to enforce the minimum distance condition.
- **Type**: Float
- **Default**: `1e6`
- **Reasonable Range**: Any value larger than the maximum possible distance between nodes.

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer