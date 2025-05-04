## Parameters

### n_widths

- **Description**: The number of widths to be cut in the Cutting Stock problem.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 100

### roll_width

- **Description**: The width of the raw rolls available for cutting.
- **Type**: Integer
- **Default**: `100`
- **Reasonable Range**: 1 to 10,000

### orders_range

- **Description**: A tuple specifying the minimum and maximum number of orders for each width.
- **Type**: Tuple of two integers `(min_orders, max_orders)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_orders`: 1 to 10,000
  - `max_orders`: `min_orders` to 10,000

### num_patterns

- **Description**: The number of cutting patterns to be considered in the problem.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 1 to 1,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer

## Notes

- **Widths**: The widths are generated as integers starting from `1` to `n_widths`.
- **Orders**: The number of orders for each width is randomly generated within the specified `orders_range`.
- **Patterns**: The patterns are generated as `pattern_0`, `pattern_1`, ..., `pattern_{num_patterns-1}`.
- **Rolls per Pattern**: The number of rolls of each width in a pattern is randomly generated between `0` and `5`.
- **Constraints**:
  - The total number of rolls cut for each width must meet the orders (`Orders[i]`).
  - The total width of rolls in each pattern must not exceed the raw roll width (`roll_width`).
- **Objective**: Minimize the total number of raw rolls cut.
