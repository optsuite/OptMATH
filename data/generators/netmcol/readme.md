## Parameters

### n_cities

- **Description**: The number of cities in the multi-commodity network flow problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 2 to 100

### n_products

- **Description**: The number of products to be transported in the multi-commodity network flow problem.
- **Type**: Integer
- **Default**: `2`
- **Reasonable Range**: 1 to 50

### supply_range

- **Description**: A tuple specifying the minimum and maximum supply values for each product at each city.
- **Type**: Tuple of two integers `(min_supply, max_supply)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_supply`: 1 to 10,000
  - `max_supply`: `min_supply` to 10,000

### demand_range

- **Description**: A tuple specifying the minimum and maximum demand values for each product at each city.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### shipment_cost_range

- **Description**: A tuple specifying the minimum and maximum shipment costs for transporting one package of a product between two cities.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_cost`: 1 to 10,000
  - `max_cost`: `min_cost` to 10,000

### capacity_range

- **Description**: A tuple specifying the minimum and maximum capacities for transporting a product between two cities.
- **Type**: Tuple of two integers `(min_capacity, max_capacity)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_capacity`: 1 to 10,000
  - `max_capacity`: `min_capacity` to 10,000

### joint_capacity_ratio

- **Description**: The ratio of the joint capacity of a link to the total capacity of all products on that link. Determines how much of the total capacity can be used for all products combined.
- **Type**: Float between 0 and 1
- **Default**: `0.7`
- **Reasonable Range**: 0.1 to 1.0

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer