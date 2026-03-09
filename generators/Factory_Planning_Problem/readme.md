## Parameters

### n_periods
- **Description**: The number of planning periods (months) in the planning horizon.
- **Type**: Integer
- **Default**: `6`
- **Reasonable Range**: 3 to 24 months

### n_products
- **Description**: Range for the number of different products to be manufactured.
- **Type**: Tuple of two integers `(min_products, max_products)`
- **Default**: `(3, 5)`
- **Reasonable Range**:
  - `min_products`: 2 to 20
  - `max_products`: `min_products` to 50
  - Small problems: 3-5
  - Medium problems: 5-15
  - Large problems: 15-50

### n_machines
- **Description**: Dictionary specifying the number of each type of machine available.
- **Type**: Dictionary `{machine_type: quantity}`
- **Default**: `{"grinder": 4, "drill": 2, "borer": 1}`
- **Reasonable Range**: 1 to 10 machines per type
- **Note**: Represents the installed machine capacity

### profit_range
- **Description**: Range for profit per unit of each product.
- **Type**: Tuple of two integers `(min_profit, max_profit)`
- **Default**: `(150, 300)`
- **Reasonable Range**:
  - `min_profit`: 50 to 500
  - `max_profit`: `min_profit` to 2000
- **Note**: Represents revenue minus variable costs

### holding_cost
- **Description**: Cost per unit per period for storing inventory.
- **Type**: Integer or Float
- **Default**: `20`
- **Reasonable Range**: 5 to 100
- **Note**: Should be significantly lower than product profits

### machine_time_range
- **Description**: Range for processing time required on each machine per unit.
- **Type**: Tuple of two integers `(min_time, max_time)`
- **Default**: `(1, 3)`
- **Reasonable Range**:
  - `min_time`: 0.5 to 5
  - `max_time`: `min_time` to 10
- **Unit**: Hours per unit

### machine_hours
- **Description**: Available working hours per machine per period.
- **Type**: Integer
- **Default**: `160`
- **Reasonable Range**: 80 to 720
- **Note**: Typically based on shift patterns (e.g., 160 hours = 20 days × 8 hours)

### max_inventory
- **Description**: Maximum storage capacity per product type.
- **Type**: Integer
- **Default**: `100`
- **Reasonable Range**: 50 to 1000
- **Note**: Represents warehouse space constraints

### sales_limit_range
- **Description**: Range for maximum sales per product per period.
- **Type**: Tuple of two integers `(min_sales, max_sales)`
- **Default**: `(30, 80)`
- **Reasonable Range**:
  - `min_sales`: 10 to 100
  - `max_sales`: `min_sales` to 500
- **Note**: Represents market demand constraints

### target_inventory_ratio
- **Description**: Ratio for calculating end-of-horizon inventory targets.
- **Type**: Float between 0 and 1
- **Default**: `0.3`
- **Reasonable Range**: 0.1 to 0.5
- **Note**: Applied to max_inventory to set final period targets

### seed
- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer
- **Usage**: Set for reproducible testing and validation