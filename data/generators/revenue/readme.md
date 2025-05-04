## Parameters

### n_flight_legs

- **Description**: The number of flight legs (one-way non-stop flights) to include in the revenue maximization problem.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 1 to 100

### n_packages

- **Description**: The number of flight packages (itineraries) to include in the revenue maximization problem.
- **Type**: Integer
- **Default**: `20`
- **Reasonable Range**: 1 to 500

### demand_range

- **Description**: A tuple specifying the minimum and maximum estimated demand for each package.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(1, 50)`
- **Reasonable Range**:
  - `min_demand`: 1 to 1,000
  - `max_demand`: `min_demand` to 1,000

### revenue_range

- **Description**: A tuple specifying the minimum and maximum revenue for each package.
- **Type**: Tuple of two integers `(min_revenue, max_revenue)`
- **Default**: `(100, 1,000)`
- **Reasonable Range**:
  - `min_revenue`: 1 to 10,000
  - `max_revenue`: `min_revenue` to 10,000

### available_seats_range

- **Description**: A tuple specifying the minimum and maximum available seats for each flight leg.
- **Type**: Tuple of two integers `(min_seats, max_seats)`
- **Default**: `(50, 200)`
- **Reasonable Range**:
  - `min_seats`: 1 to 10,000
  - `max_seats`: `min_seats` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer