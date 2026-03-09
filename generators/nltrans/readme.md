## Parameters

### n_origins

- **Description**: The number of origins in the transportation problem.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 100

### n_destinations

- **Description**: The number of destinations in the transportation problem.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 100

### supply_range

- **Description**: A tuple specifying the minimum and maximum supply values for the origins.
- **Type**: Tuple of two integers `(min_supply, max_supply)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_supply`: 1 to 10,000
  - `max_supply`: `min_supply` to 10,000

### demand_range

- **Description**: A tuple specifying the minimum and maximum demand values for the destinations.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### rate_range

- **Description**: A tuple specifying the minimum and maximum shipping rates from origins to destinations.
- **Type**: Tuple of two integers `(min_rate, max_rate)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_rate`: 1 to 1,000
  - `max_rate`: `min_rate` to 1,000

### limit_range

- **Description**: A tuple specifying the minimum and maximum limits on the number of units that can be shipped from an origin to a destination.
- **Type**: Tuple of two integers `(min_limit, max_limit)`
- **Default**: `(5, 20)`
- **Reasonable Range**:
  - `min_limit`: 1 to 10,000
  - `max_limit`: `min_limit` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer