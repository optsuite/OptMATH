## Parameters

### n_crops

- **Description**: The number of crops to include in the farm planning problem.
- **Type**: Tuple of two integers `(min_crops, max_crops)`
- **Default**: `(3, 3)`
- **Reasonable Range**: 1 to 100

### n_months

- **Description**: The number of months to consider in the farm planning problem.
- **Type**: Tuple of two integers `(min_months, max_months)`
- **Default**: `(12, 12)`
- **Reasonable Range**: 1 to 12

### n_consumption_bundles

- **Description**: The number of consumption bundles to include in the farm planning problem.
- **Type**: Tuple of two integers `(min_bundles, max_bundles)`
- **Default**: `(2, 2)`
- **Reasonable Range**: 1 to 10

### yield_range

- **Description**: A tuple specifying the minimum and maximum yield for each crop (in tons per hectare).
- **Type**: Tuple of two integers `(min_yield, max_yield)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_yield`: 1 to 100
  - `max_yield`: `min_yield` to 100

### price_range

- **Description**: A tuple specifying the minimum and maximum price for each crop (in dollars per ton).
- **Type**: Tuple of two integers `(min_price, max_price)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_price`: 1 to 10,000
  - `max_price`: `min_price` to 10,000

### land_available

- **Description**: The total land available for planting (in hectares).
- **Type**: Integer
- **Default**: `100`
- **Reasonable Range**: 1 to 10,000

### labor_required_range

- **Description**: A tuple specifying the minimum and maximum labor required per hectare for each crop (in man-hours).
- **Type**: Tuple of two integers `(min_labor, max_labor)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_labor`: 1 to 100
  - `max_labor`: `min_labor` to 100

### water_requirement_range

- **Description**: A tuple specifying the minimum and maximum water requirement per hectare for each crop (in cubic kilometers).
- **Type**: Tuple of two floats `(min_water, max_water)`
- **Default**: `(0.1, 1.0)`
- **Reasonable Range**:
  - `min_water`: 0.01 to 10.0
  - `max_water`: `min_water` to 10.0

### water_limit

- **Description**: The maximum amount of water available per month (in cubic kilometers).
- **Type**: Float
- **Default**: `50`
- **Reasonable Range**: 1 to 1,000

### annual_water_available

- **Description**: The total annual amount of water available (in cubic kilometers).
- **Type**: Float
- **Default**: `500`
- **Reasonable Range**: 1 to 10,000

### wage_rates

- **Description**: A dictionary specifying wage rates for family, permanent, and temporary labor (in dollars).
- **Type**: Dictionary with keys `"family"`, `"permanent"`, and `"temporary"`
- **Default**:
  ```python
  {
      "family": 10000,
      "permanent": 15000,
      "temporary": 10
  }
  ```
- **Reasonable Range**:
  - `family`: 1,000 to 100,000
  - `permanent`: 1,000 to 100,000
  - `temporary`: 1 to 100

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer