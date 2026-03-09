## Parameters

### n_products
- **Description**: The number of products to include in the lot-sizing problem.
- **Type**: Tuple of two integers `(min_products, max_products)`
- **Default**: `(2, 2)`
- **Reasonable Range**: 1 to 100 products

### n_periods
- **Description**: The number of time periods in the planning horizon.
- **Type**: Tuple of two integers `(min_periods, max_periods)`
- **Default**: `(6, 6)`
- **Reasonable Range**: 1 to 52 (weekly planning for a year)

### setup_cost_range
- **Description**: A tuple specifying the minimum and maximum setup costs for production runs.
- **Type**: Tuple of two integers `(min_setup, max_setup)`
- **Default**: `(1000, 2000)`
- **Reasonable Range**:
  - `min_setup`: 100 to 10,000
  - `max_setup`: `min_setup` to 50,000

### production_cost_range
- **Description**: A tuple specifying the minimum and maximum unit production costs.
- **Type**: Tuple of two integers `(min_prod_cost, max_prod_cost)`
- **Default**: `(40, 50)`
- **Reasonable Range**:
  - `min_prod_cost`: 1 to 1,000
  - `max_prod_cost`: `min_prod_cost` to 5,000

### holding_cost_range
- **Description**: A tuple specifying the minimum and maximum unit holding costs per period.
- **Type**: Tuple of two integers `(min_hold_cost, max_hold_cost)`
- **Default**: `(4, 5)`
- **Reasonable Range**:
  - `min_hold_cost`: 0.1 to 100
  - `max_hold_cost`: `min_hold_cost` to 500

### capacity_range
- **Description**: A tuple specifying the minimum and maximum production capacity per period.
- **Type**: Tuple of two integers `(min_capacity, max_capacity)`
- **Default**: `(800, 800)`
- **Reasonable Range**:
  - `min_capacity`: 100 to 10,000
  - `max_capacity`: `min_capacity` to 50,000

### demand_range
- **Description**: A tuple specifying the minimum and maximum demand per product per period.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(50, 100)`
- **Reasonable Range**:
  - `min_demand`: 1 to 1,000
  - `max_demand`: `min_demand` to 5,000

### resource_usage_range
- **Description**: A tuple specifying the minimum and maximum resource usage per unit of production.
- **Type**: Tuple of two floats `(min_usage, max_usage)`
- **Default**: `(1.5, 2.0)`
- **Reasonable Range**:
  - `min_usage`: 0.1 to 10.0
  - `max_usage`: `min_usage` to 20.0

### seed
- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer
