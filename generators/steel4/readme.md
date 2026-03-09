## Parameters

### n_products

- **Description**: The number of products to include in the production planning problem.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 1 to 100

### n_stages

- **Description**: The number of stages in the production process.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 20

### rate_range

- **Description**: A tuple specifying the minimum and maximum production rates (tons per hour) for each product in each stage.
- **Type**: Tuple of two integers `(min_rate, max_rate)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_rate`: 1 to 100
  - `max_rate`: `min_rate` to 100

### available_range

- **Description**: A tuple specifying the minimum and maximum available hours per week for each stage.
- **Type**: Tuple of two integers `(min_available, max_available)`
- **Default**: `(40, 80)`
- **Reasonable Range**:
  - `min_available`: 1 to 168 (hours in a week)
  - `max_available`: `min_available` to 168

### profit_range

- **Description**: A tuple specifying the minimum and maximum profit per ton for each product.
- **Type**: Tuple of two integers `(min_profit, max_profit)`
- **Default**: `(100, 500)`
- **Reasonable Range**:
  - `min_profit`: 1 to 10,000
  - `max_profit`: `min_profit` to 10,000

### commit_range

- **Description**: A tuple specifying the minimum and maximum production commitments (tons) for each product.
- **Type**: Tuple of two integers `(min_commit, max_commit)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_commit`: 1 to 1,000
  - `max_commit`: `min_commit` to 1,000

### market_range

- **Description**: A tuple specifying the minimum and maximum market demands (tons) for each product.
- **Type**: Tuple of two integers `(min_market, max_market)`
- **Default**: `(100, 200)`
- **Reasonable Range**:
  - `min_market`: 1 to 10,000
  - `max_market`: `min_market` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer