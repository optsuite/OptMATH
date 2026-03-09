# Aircraft Assignment Problem Generator Parameters

## Parameters

### n_aircraft

- **Description**: The number of aircraft types to include in the assignment problem.
- **Type**: Tuple of two integers `(min_aircraft, max_aircraft)`
- **Default**: `(2, 5)`
- **Reasonable Range**:
  - `min_aircraft`: 1 to 20
  - `max_aircraft`: `min_aircraft` to 50

### n_routes

- **Description**: The number of routes to consider in the assignment problem.
- **Type**: Tuple of two integers `(min_routes, max_routes)`
- **Default**: `(3, 8)`
- **Reasonable Range**:
  - `min_routes`: 1 to 30
  - `max_routes`: `min_routes` to 100

### availability_range

- **Description**: A tuple specifying the minimum and maximum number of available aircraft for each type.
- **Type**: Tuple of two integers `(min_available, max_available)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_available`: 1 to 10
  - `max_available`: `min_available` to 50

### demand_range

- **Description**: A tuple specifying the minimum and maximum passenger demand for each route.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(100, 500)`
- **Reasonable Range**:
  - `min_demand`: 50 to 1000
  - `max_demand`: `min_demand` to 5000

### capabilities_range

- **Description**: A tuple specifying the minimum and maximum passenger capacity of each aircraft type for each route.
- **Type**: Tuple of two integers `(min_capacity, max_capacity)`
- **Default**: `(50, 200)`
- **Reasonable Range**:
  - `min_capacity`: 30 to 500
  - `max_capacity`: `min_capacity` to 1000

### cost_range

- **Description**: A tuple specifying the minimum and maximum cost of assigning an aircraft to a route.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1000, 5000)`
- **Reasonable Range**:
  - `min_cost`: 500 to 10000
  - `max_cost`: `min_cost` to 50000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer

## Notes

- All parameters can be customized when initializing the generator
- The ranges for aircraft types and routes should be chosen to ensure feasible solutions exist
- The capabilities range should be set considering the typical demand range to allow for realistic solutions
- Cost ranges should reflect realistic operational costs in the airline industry
