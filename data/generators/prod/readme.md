## Parameters

### n_items

- **Description**: The number of items to include in the profit maximization problem.
- **Type**: Integer
- **Default**: `50`
- **Reasonable Range**: 1 to 1000

### a_range

- **Description**: A tuple specifying the minimum and maximum values for the parameter \( a[j] \), which is associated with each item \( j \).
- **Type**: Tuple of two integers `(min_a, max_a)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_a`: 1 to 100
  - `max_a`: `min_a` to 100

### c_range

- **Description**: A tuple specifying the minimum and maximum values for the parameter \( c[j] \), which represents the profit coefficient for each item \( j \).
- **Type**: Tuple of two integers `(min_c, max_c)`
- **Default**: `(1, 50)`
- **Reasonable Range**:
  - `min_c`: 1 to 10,000
  - `max_c`: `min_c` to 10,000

### u_range

- **Description**: A tuple specifying the minimum and maximum values for the parameter \( u[j] \), which represents the upper bound for the variable \( X[j] \) for each item \( j \).
- **Type**: Tuple of two integers `(min_u, max_u)`
- **Default**: `(1, 100)`
- **Reasonable Range**:
  - `min_u`: 1 to 10,000
  - `max_u`: `min_u` to 10,000

### b_ratio

- **Description**: The ratio of the global parameter \( b \) to the total sum of \( \frac{1}{a[j]} \cdot u[j] \). Determines the resource or capacity constraint relative to the total weighted sum of the upper bounds.
- **Type**: Float between 0 and 1
- **Default**: `0.7`
- **Reasonable Range**: 0.1 to 1.0

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer