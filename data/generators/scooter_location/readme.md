## Parameters

### n_demand_points

- **Description**: The number of demand points (e.g., public transportation hubs, malls, residential complexes) in the scooter location problem.
- **Type**: Integer
- **Default**: `(5, 10)` (randomly selected between 5 and 10)
- **Reasonable Range**: 1 to 100

### n_candidate_locations

- **Description**: The number of candidate locations where scooters can be placed (e.g., based on security, space availability, and accessibility).
- **Type**: Integer
- **Default**: `(3, 5)` (randomly selected between 3 and 5)
- **Reasonable Range**: 1 to 50

### demand_range

- **Description**: A tuple specifying the minimum and maximum estimated demand for each demand point.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### distance_range

- **Description**: A tuple specifying the minimum and maximum distance/travel time between demand points and candidate locations.
- **Type**: Tuple of two integers `(min_distance, max_distance)`
- **Default**: `(1, 20)`
- **Reasonable Range**:
  - `min_distance`: 1 to 100
  - `max_distance`: `min_distance` to 100

### num_available_scooters

- **Description**: The number of scooters already available for redistribution.
- **Type**: Integer
- **Default**: `50`
- **Reasonable Range**: 0 to 10,000

### max_selected_locations

- **Description**: The maximum number of candidate locations that can be selected for placing scooters.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 50

### new_max

- **Description**: The maximum number of new scooters that can be added to the system.
- **Type**: Integer
- **Default**: `30`
- **Reasonable Range**: 0 to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer