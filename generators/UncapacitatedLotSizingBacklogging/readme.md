## Parameters

### n_periods

- **Description**: The number of periods to include in the ULSB problem.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 100

### demand_range

- **Description**: A tuple specifying the minimum and maximum values for the demand in each period.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### fixed_cost_range

- **Description**: A tuple specifying the minimum and maximum values for the fixed ordering cost in each period.
- **Type**: Tuple of two integers `(min_fixed_cost, max_fixed_cost)`
- **Default**: `(50, 200)`
- **Reasonable Range**:
  - `min_fixed_cost`: 1 to 10,000
  - `max_fixed_cost`: `min_fixed_cost` to 10,000

### unit_order_cost_range

- **Description**: A tuple specifying the minimum and maximum values for the unit ordering cost in each period.
- **Type**: Tuple of two integers `(min_unit_order_cost, max_unit_order_cost)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_unit_order_cost`: 1 to 10,000
  - `max_unit_order_cost`: `min_unit_order_cost` to 10,000

### unit_holding_cost_range

- **Description**: A tuple specifying the minimum and maximum values for the unit holding cost in each period.
- **Type**: Tuple of two integers `(min_unit_holding_cost, max_unit_holding_cost)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_unit_holding_cost`: 1 to 10,000
  - `max_unit_holding_cost`: `min_unit_holding_cost` to 10,000

### unit_backlog_penalty_range

- **Description**: A tuple specifying the minimum and maximum values for the unit backlogging penalty in each period.
- **Type**: Tuple of two integers `(min_unit_backlog_penalty, max_unit_backlog_penalty)`
- **Default**: `(5, 20)`
- **Reasonable Range**:
  - `min_unit_backlog_penalty`: 1 to 10,000
  - `max_unit_backlog_penalty`: `min_unit_backlog_penalty` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer