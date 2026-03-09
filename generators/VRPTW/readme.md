## Parameters

### n_customers

- **Description**: The number of customers to include in the Capacitated Vehicle Routing Problem with Time Windows (CVRPTW). This does not include the depot.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 100

### demand_range

- **Description**: A tuple specifying the minimum and maximum demands for the customers' demands.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_demand`: 1 to 100
  - `max_demand`: `min_demand` to 100

### time_window_range

- **Description**: A tuple specifying the minimum and maximum values for the lower bound of the customers' time windows.
- **Type**: Tuple of two integers `(min_time, max_time)`
- **Default**: `(0, 100)`
- **Reasonable Range**:
  - `min_time`: 0 to 1000
  - `max_time`: `min_time` to 1000

### distance_range

- **Description**: A tuple specifying the minimum and maximum distances between customers (including the depot).
- **Type**: Tuple of two integers `(min_distance, max_distance)`
- **Default**: `(1, 50)`
- **Reasonable Range**:
  - `min_distance`: 1 to 1000
  - `max_distance`: `min_distance` to 1000

### service_time_range

- **Description**: A tuple specifying the minimum and maximum service times at each customer.
- **Type**: Tuple of two integers `(min_service_time, max_service_time)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_service_time`: 1 to 100
  - `max_service_time`: `min_service_time` to 100

### vehicle_capacity

- **Description**: The capacity of the vehicles used for routing. This is the maximum total demand that a vehicle can carry.
- **Type**: Integer
- **Default**: `50`
- **Reasonable Range**: 1 to 10,000

### M

- **Description**: A large constant used in the constraints to enforce logical conditions (e.g., ensuring schedule feasibility and load feasibility).
- **Type**: Integer
- **Default**: `1000`
- **Reasonable Range**: 100 to 1,000,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer