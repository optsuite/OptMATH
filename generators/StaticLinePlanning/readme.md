## Parameters

### n_nodes

- **Description**: Number of nodes in the network
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 5 to 100

### n_lines

- **Description**: Number of potential transit lines
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 2 to 50

### n_od_pairs

- **Description**: Number of origin-destination pairs to be served
- **Type**: Integer
- **Default**: `15`
- **Reasonable Range**: 1 to n_nodes * (n_nodes-1)

### fixed_cost_range

- **Description**: Range for fixed costs of opening transit lines
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1000, 5000)`
- **Reasonable Range**:
  - `min_cost`: 100 to 10,000
  - `max_cost`: `min_cost` to 100,000

### operational_cost_range

- **Description**: Range for operational costs per unit of service
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(100, 500)`
- **Reasonable Range**:
  - `min_cost`: 10 to 1,000
  - `max_cost`: `min_cost` to 10,000

### capacity_range

- **Description**: Range for vehicle capacity
- **Type**: Tuple of two integers `(min_capacity, max_capacity)`
- **Default**: `(100, 200)`
- **Reasonable Range**:
  - `min_capacity`: 50 to 500
  - `max_capacity`: `min_capacity` to 1,000

### demand_range

- **Description**: Range for demand between OD pairs
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_demand`: 1 to 100
  - `max_demand`: `min_demand` to 500

### penalty_range

- **Description**: Range for penalty costs of unmet demand
- **Type**: Tuple of two integers `(min_penalty, max_penalty)`
- **Default**: `(500, 1000)`
- **Reasonable Range**:
  - `min_penalty`: 100 to 5,000
  - `max_penalty`: `min_penalty` to 10,000

### trip_time_range

- **Description**: Range for one-way trip time in minutes
- **Type**: Tuple of two integers `(min_time, max_time)`
- **Default**: `(60, 180)`
- **Reasonable Range**:
  - `min_time`: 30 to 120
  - `max_time`: `min_time` to 360

### density

- **Description**: Network connectivity density, representing the probability of connection between nodes
- **Type**: Float between 0 and 1
- **Default**: `0.3`
- **Reasonable Range**: 0.1 to 0.8

### seed

- **Description**: Random seed for reproducibility of the generated problem instance
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer
