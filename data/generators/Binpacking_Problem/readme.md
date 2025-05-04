## Parameters
### n_items
- **Description**: A tuple specifying the minimum and maximum number of items to be packed into bins.
- **Type**: Tuple of two integers `(min_items, max_items)`
- **Default**: `(3, 10)`
- **Reasonable Range**: 
  - `min_items`: 1 to 1000
  - `max_items`: `min_items` to 1000

### weight_range 
- **Description**: A tuple specifying the minimum and maximum weights for the items' weights.
- **Type**: Tuple of two integers `(min_weight, max_weight)`
- **Default**: `(1, 50)`
- **Reasonable Range**:
  - `min_weight`: 1 to 1000
  - `max_weight`: `min_weight` to 1000

### bin_capacity
- **Description**: The uniform capacity for all bins that items can be packed into.
- **Type**: Integer
- **Default**: `100`
- **Reasonable Range**: 
  - Should be greater than `max_weight` from weight_range
  - Typically between 50 to 5000
  - Should be set considering the weight_range to allow multiple items per bin

### seed
- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer