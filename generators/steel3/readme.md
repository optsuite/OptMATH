## Parameters

### n_products

- **Description**: The number of products to include in the production planning problem.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 100

### production_rate_range

- **Description**: A tuple specifying the minimum and maximum production rates for the products (in tons per hour).
- **Type**: Tuple of two integers `(min_rate, max_rate)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_rate`: 1 to 100
  - `max_rate`: `min_rate` to 100

### profit_range

- **Description**: A tuple specifying the minimum and maximum profit per ton for the products.
- **Type**: Tuple of two integers `(min_profit, max_profit)`
- **Default**: `(1, 100)`
- **Reasonable Range**:
  - `min_profit`: 1 to 10,000
  - `max_profit`: `min_profit` to 10,000

### min_sold_range

- **Description**: A tuple specifying the minimum and maximum tons of each product that must be sold.
- **Type**: Tuple of two integers `(min_sold, max_sold)`
- **Default**: `(1, 50)`
- **Reasonable Range**:
  - `min_sold`: 1 to 10,000
  - `max_sold`: `min_sold` to 10,000

### max_sold_range

- **Description**: A tuple specifying the minimum and maximum tons of each product that can be sold.
- **Type**: Tuple of two integers `(min_sold, max_sold)`
- **Default**: `(50, 100)`
- **Reasonable Range**:
  - `min_sold`: 1 to 10,000
  - `max_sold`: `min_sold` to 10,000

### available_hours

- **Description**: The total available production hours in a week.
- **Type**: Integer
- **Default**: `168` (168 hours in a week)
- **Reasonable Range**: 1 to 168

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer