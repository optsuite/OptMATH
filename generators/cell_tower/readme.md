## Parameters

### n_towers

- **Description**: The number of potential tower sites to include in the cell tower problem.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 1 to 100

### n_regions

- **Description**: The number of regions to be covered by the cell towers.
- **Type**: Integer
- **Default**: `20`
- **Reasonable Range**: 1 to 500

### cost_range

- **Description**: A tuple specifying the minimum and maximum costs for building a tower at a potential site.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(10, 1000)`
- **Reasonable Range**:
  - `min_cost`: 1 to 10,000
  - `max_cost`: `min_cost` to 10,000

### population_range

- **Description**: A tuple specifying the minimum and maximum populations for the regions.
- **Type**: Tuple of two integers `(min_population, max_population)`
- **Default**: `(100, 10,000)`
- **Reasonable Range**:
  - `min_population`: 1 to 100,000
  - `max_population`: `min_population` to 100,000

### budget_ratio

- **Description**: The ratio of the budget to the total cost of building all towers. Determines how much of the total cost can be spent.
- **Type**: Float between 0 and 1
- **Default**: `0.7`
- **Reasonable Range**: 0.1 to 1.0

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer