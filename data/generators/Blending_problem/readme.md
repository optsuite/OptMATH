## Parameters

### n_alloys
- **Description**: The number of alloys available for purchase.
- **Type**: Tuple of two integers `(min_alloys, max_alloys)`
- **Default**: `(8, 8)`
- **Reasonable Range**: 2 to 100

### n_elements
- **Description**: The number of elements to be considered in the blend.
- **Type**: Tuple of two integers `(min_elements, max_elements)`
- **Default**: `(3, 3)`
- **Reasonable Range**: 1 to 20

### percentage_range
- **Description**: Range for the percentage composition of elements in alloys.
- **Type**: Tuple of two floats `(min_percentage, max_percentage)`
- **Default**: `(0.35, 0.65)`
- **Reasonable Range**: 
  - `min_percentage`: 0.0 to 0.5
  - `max_percentage`: `min_percentage` to 1.0

### cost_range
- **Description**: Range for the cost per unit of alloys.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(100, 1000)`
- **Reasonable Range**:
  - `min_cost`: 1 to 10,000
  - `max_cost`: `min_cost` to 100,000

### desired_percentages
- **Description**: List of desired percentages for each element in final blend.
- **Type**: List of floats
- **Default**: `[]` (randomly generated within feasible range)
- **Reasonable Range**: Each value between 0.0 and 1.0

### seed
- **Description**: Random seed for reproducible problem generation.
- **Type**: Integer (optional)
- **Default**: `None`
- **Reasonable Range**: Any valid integer