## Parameters

### n_sets

- **Description**: The number of sets in the set covering problem.
- **Type**: Integer
- **Default**: `20`
- **Reasonable Range**: 5 to 1000
- **Note**: This represents the number of available sets that can be selected to cover the elements.

### n_elements

- **Description**: The number of elements that need to be covered in the universe.
- **Type**: Integer
- **Default**: `100`
- **Reasonable Range**: 10 to 10000
- **Note**: These are the elements that must be covered by at least one selected set.

### density

- **Description**: The probability of an element being included in a set, determining how many elements each set contains on average.
- **Type**: Float between 0 and 1
- **Default**: `0.4`
- **Reasonable Range**: 0.1 to 0.9
- **Note**: Higher density means more elements per set on average, making the problem potentially easier to solve.

### cost_range

- **Description**: A tuple specifying the minimum and maximum costs for selecting sets.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 100)`
- **Reasonable Range**:
  - `min_cost`: 1 to 1000
  - `max_cost`: `min_cost` to 10000
- **Note**: These costs represent the objective function coefficients for each set.

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer
- **Note**: Setting this parameter ensures the same problem instance is generated each time.

## Usage Example

```python
# Using default parameters
generator = SetCoveringGenerator()
model = generator.generate_instance()

# Using custom parameters
custom_params = {
    "n_sets": 30,
    "n_elements": 150,
    "density": 0.5,
    "cost_range": (1, 200)
}
generator = SetCoveringGenerator(parameters=custom_params, seed=42)
model = generator.generate_instance()
```
