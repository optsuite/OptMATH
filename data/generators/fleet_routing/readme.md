## Parameters

### n_locations

- **Description**: The number of locations/cities to include in the fleet routing problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 100

### n_planes

- **Description**: The number of plane types to include in the fleet routing problem.
- **Type**: Integer
- **Default**: `2`
- **Reasonable Range**: 1 to 50

### n_periods

- **Description**: The number of periods (time slots) to include in the fleet routing problem.
- **Type**: Integer
- **Default**: `2`
- **Reasonable Range**: 1 to 100

### capacity_range

- **Description**: A tuple specifying the minimum and maximum capacities for the planes.
- **Type**: Tuple of two integers `(min_capacity, max_capacity)`
- **Default**: `(50, 100)`
- **Reasonable Range**:
  - `min_capacity`: 1 to 10,000
  - `max_capacity`: `min_capacity` to 10,000

### cost_range

- **Description**: A tuple specifying the minimum and maximum costs for using the planes.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1000, 5000)`
- **Reasonable Range**:
  - `min_cost`: 1 to 1,000,000
  - `max_cost`: `min_cost` to 1,000,000

### available_planes_range

- **Description**: A tuple specifying the minimum and maximum number of available planes for each plane type.
- **Type**: Tuple of two integers `(min_available, max_available)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_available`: 1 to 100
  - `max_available`: `min_available` to 100

### demand_range

- **Description**: A tuple specifying the minimum and maximum number of passengers for each flight.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer