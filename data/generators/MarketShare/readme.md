# Market Sharing Problem Generator Parameters

## Parameters

### n_companies

- **Description**: The number of companies/suppliers in the market sharing problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 2 to 100

### n_markets

- **Description**: The number of markets/customers to be served.
- **Type**: Integer
- **Default**: `4`
- **Reasonable Range**: 1 to 1000

### n_products

- **Description**: The number of different products to be supplied.
- **Type**: Integer
- **Default**: `2`
- **Reasonable Range**: 1 to 100

### demand_range

- **Description**: A tuple specifying the minimum and maximum demand values for each market-product pair.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 30)`
- **Reasonable Range**:
  - `min_demand`: 1 to 1000
  - `max_demand`: `min_demand` to 10000

### cost_range

- **Description**: A tuple specifying the minimum and maximum unit costs for companies supplying products to markets.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_cost`: 1 to 100
  - `max_cost`: `min_cost` to 1000

### revenue_range

- **Description**: A tuple specifying the minimum and maximum unit revenues for companies selling products in markets.
- **Type**: Tuple of two integers `(min_revenue, max_revenue)`
- **Default**: `(8, 15)`
- **Reasonable Range**:
  - `min_revenue`: Must be greater than corresponding cost
  - `max_revenue`: `min_revenue` to 2000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer

## Additional Notes

- Revenue values are automatically generated to be at least 1 unit higher than corresponding costs
- Revenue range minimum should always be higher than cost range maximum to ensure profitability
- Problem size and computational complexity increases with number of companies, markets and products
