## Parameters

### n_nutrients

- **Description**: The number of nutrients to include in the diet problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 100

### n_foods

- **Description**: The number of foods to include in the diet problem.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 1000

### cost_range

- **Description**: A tuple specifying the minimum and maximum costs for the foods' costs.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_cost`: 1 to 10,000
  - `max_cost`: `min_cost` to 10,000

### min_amount_range

- **Description**: A tuple specifying the minimum and maximum amounts for the minimum amount of each food that can be bought.
- **Type**: Tuple of two integers `(min_amount, max_amount)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_amount`: 1 to 10,000
  - `max_amount`: `min_amount` to 10,000

### max_amount_range

- **Description**: A tuple specifying the minimum and maximum amounts for the maximum amount of each food that can be bought.
- **Type**: Tuple of two integers `(min_amount, max_amount)`
- **Default**: `(10, 20)`
- **Reasonable Range**:
  - `min_amount`: 1 to 10,000
  - `max_amount`: `min_amount` to 10,000

### min_nutrient_range

- **Description**: A tuple specifying the minimum and maximum amounts for the minimum nutrient requirement.
- **Type**: Tuple of two integers `(min_nutrient, max_nutrient)`
- **Default**: `(10, 20)`
- **Reasonable Range**:
  - `min_nutrient`: 1 to 10,000
  - `max_nutrient`: `min_nutrient` to 10,000

### max_nutrient_range

- **Description**: A tuple specifying the minimum and maximum amounts for the maximum nutrient requirement.
- **Type**: Tuple of two integers `(min_nutrient, max_nutrient)`
- **Default**: `(50, 100)`
- **Reasonable Range**:
  - `min_nutrient`: 1 to 10,000
  - `max_nutrient`: `min_nutrient` to 10,000

### nutrient_amount_range

- **Description**: A tuple specifying the minimum and maximum amounts for the nutrient content in each food.
- **Type**: Tuple of two integers `(min_amount, max_amount)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_amount`: 1 to 10,000
  - `max_amount`: `min_amount` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer