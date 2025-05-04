# Supply Chain Network Design Problem Parameters

## Parameters

### n_nodes

- **Description**: The total number of nodes in the network (including suppliers, customers, and intermediate nodes).
- **Type**: Integer
- **Default**: `20`
- **Reasonable Range**: 5 to 100

### cap_range

- **Description**: A tuple specifying the minimum and maximum capacity for arcs between nodes.
- **Type**: Tuple of two integers `(min_capacity, max_capacity)`
- **Default**: `(50, 200)`
- **Reasonable Range**:
  - `min_capacity`: 10 to 1,000
  - `max_capacity`: `min_capacity` to 10,000

### fixed_cost_range

- **Description**: A tuple specifying the minimum and maximum fixed costs for using arcs.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1000, 5000)`
- **Reasonable Range**:
  - `min_cost`: 100 to 10,000
  - `max_cost`: `min_cost` to 100,000

### unit_cost_range

- **Description**: A tuple specifying the minimum and maximum unit transportation costs for arcs.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_cost`: 1 to 1,000
  - `max_cost`: `min_cost` to 5,000

### total_supply

- **Description**: The total amount of supply in the system (which equals total demand for balance).
- **Type**: Integer
- **Default**: `1000`
- **Reasonable Range**: 100 to 10,000

### n_suppliers

- **Description**: The number of supplier nodes in the network.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to `n_nodes/2`
- **Note**: Must be less than total number of nodes

### n_customers

- **Description**: The number of customer nodes in the network.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to `n_nodes/2`
- **Note**: Must be less than total number of nodes

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer

## Notes

1. The sum of `n_suppliers` and `n_customers` must be less than `n_nodes`
2. The total supply will be distributed among supplier nodes
3. The total demand (equal to total supply) will be distributed among customer nodes
4. All remaining nodes act as potential intermediate facilities
5. Arc capacities are generated to ensure feasibility of the problem
