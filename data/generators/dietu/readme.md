## Parameters

### n_foods

- **Description**: The number of foods to include in the diet problem.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 1 to 100

### n_nutrients

- **Description**: The number of nutrients to include in the diet problem.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 50

### cost_range

- **Description**: A tuple specifying the minimum and maximum costs for the foods' costs.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 100)`
- **Reasonable Range**:
  - `min_cost`: 1 to 1,000
  - `max_cost`: `min_cost` to 1,000

### nutrient_amount_range

- **Description**: A tuple specifying the minimum and maximum amounts for the nutrient amounts in foods.
- **Type**: Tuple of two integers `(min_amount, max_amount)`
- **Default**: `(1, 50)`
- **Reasonable Range**:
  - `min_amount`: 1 to 1,000
  - `max_amount`: `min_amount` to 1,000

### min_requirement_range

- **Description**: A tuple specifying the minimum and maximum values for the minimum nutrient requirements.
- **Type**: Tuple of two integers `(min_req, max_req)`
- **Default**: `(100, 200)`
- **Reasonable Range**:
  - `min_req`: 1 to 10,000
  - `max_req`: `min_req` to 10,000

### max_requirement_range

- **Description**: A tuple specifying the minimum and maximum values for the maximum nutrient requirements.
- **Type**: Tuple of two integers `(min_req, max_req)`
- **Default**: `(300, 400)`
- **Reasonable Range**:
  - `min_req`: 1 to 10,000
  - `max_req`: `min_req` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer