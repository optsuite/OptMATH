## Parameters

### n_people

- **Description**: The number of people available for project assignments.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 1 to 100

### n_projects

- **Description**: The number of projects to be assigned.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 1 to 100

### supply_range

- **Description**: A tuple specifying the minimum and maximum available hours for each person.
- **Type**: Tuple of two integers `(min_supply, max_supply)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_supply`: 1 to 1000
  - `max_supply`: `min_supply` to 1000

### demand_range

- **Description**: A tuple specifying the minimum and maximum required hours for each project.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_demand`: 1 to 1000
  - `max_demand`: `min_demand` to 1000

### cost_range

- **Description**: A tuple specifying the minimum and maximum cost per hour of work for each person on each project.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_cost`: 1 to 1000
  - `max_cost`: `min_cost` to 1000

### limit_range

- **Description**: A tuple specifying the minimum and maximum limit on the number of hours each person can contribute to each project.
- **Type**: Tuple of two integers `(min_limit, max_limit)`
- **Default**: `(1, 20)`
- **Reasonable Range**:
  - `min_limit`: 1 to 1000
  - `max_limit`: `min_limit` to 1000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer