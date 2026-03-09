## Parameters

### n_facilities
- **Description**: The number of potential facility locations to consider.
- **Type**: Tuple of two integers `(min_facilities, max_facilities)`
- **Default**: `(3, 3)`
- **Reasonable Range**: 2 to 100

### n_customers
- **Description**: The number of customers to be served.
- **Type**: Tuple of two integers `(min_customers, max_customers)`
- **Default**: `(3, 3)`
- **Reasonable Range**: 2 to 1000

### fixed_cost_range
- **Description**: A tuple specifying the minimum and maximum fixed costs for opening facilities.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(80000, 120000)`
- **Reasonable Range**:
  - `min_cost`: 10,000 to 1,000,000
  - `max_cost`: `min_cost` to 2,000,000

### transport_cost_range
- **Description**: A tuple specifying the minimum and maximum transportation costs between customers and facilities.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_cost`: 1 to 1,000
  - `max_cost`: `min_cost` to 5,000

### demand_range
- **Description**: A tuple specifying the minimum and maximum demand values for customers.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(300, 500)`
- **Reasonable Range**:
  - `min_demand`: 1 to 1,000
  - `max_demand`: `min_demand` to 10,000

### capacity_range
- **Description**: A tuple specifying the minimum and maximum capacity values for facilities.
- **Type**: Tuple of two integers `(min_capacity, max_capacity)`
- **Default**: `(800, 1200)`
- **Reasonable Range**:
  - `min_capacity`: 500 to 5,000
  - `max_capacity`: `min_capacity` to 50,000

### seed
- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer