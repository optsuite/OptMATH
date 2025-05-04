## Parameters

### n_origins

- **Description**: The number of origins (supply points) in the multi-commodity transportation problem.
- **Type**: Integer
- **Default**: `(2, 2)` (a tuple specifying a fixed number of origins)
- **Reasonable Range**: 1 to 100

### n_destinations

- **Description**: The number of destinations (demand points) in the multi-commodity transportation problem.
- **Type**: Integer
- **Default**: `(2, 2)` (a tuple specifying a fixed number of destinations)
- **Reasonable Range**: 1 to 100

### n_products

- **Description**: The number of products (commodities) to be transported in the multi-commodity transportation problem.
- **Type**: Integer
- **Default**: `(2, 2)` (a tuple specifying a fixed number of products)
- **Reasonable Range**: 1 to 100

### supply_range

- **Description**: A tuple specifying the minimum and maximum supply values for each product at each origin.
- **Type**: Tuple of two integers `(min_supply, max_supply)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_supply`: 1 to 10,000
  - `max_supply`: `min_supply` to 10,000

### demand_range

- **Description**: A tuple specifying the minimum and maximum demand values for each product at each destination.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### limit_range

- **Description**: A tuple specifying the minimum and maximum transportation limits for each origin-destination pair.
- **Type**: Tuple of two integers `(min_limit, max_limit)`
- **Default**: `(50, 200)`
- **Reasonable Range**:
  - `min_limit`: 1 to 10,000
  - `max_limit`: `min_limit` to 10,000

### shipping_cost_range

- **Description**: A tuple specifying the minimum and maximum shipping costs for transporting one unit of a product from an origin to a destination.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_cost`: 1 to 10,000
  - `max_cost`: `min_cost` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer