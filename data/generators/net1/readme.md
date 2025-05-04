## Parameters

### n_cities

- **Description**: The number of cities in the network flow problem.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 2 to 100

### supply_range

- **Description**: A tuple specifying the minimum and maximum supply values for each city.
- **Type**: Tuple of two integers `(min_supply, max_supply)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_supply`: 1 to 10,000
  - `max_supply`: `min_supply` to 10,000

### demand_range

- **Description**: A tuple specifying the minimum and maximum demand values for each city.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### shipping_cost_range

- **Description**: A tuple specifying the minimum and maximum shipping costs for each link between cities.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_cost`: 1 to 1,000
  - `max_cost`: `min_cost` to 1,000

### capacity_range

- **Description**: A tuple specifying the minimum and maximum capacities for each link between cities.
- **Type**: Tuple of two integers `(min_capacity, max_capacity)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_capacity`: 1 to 10,000
  - `max_capacity`: `min_capacity` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer