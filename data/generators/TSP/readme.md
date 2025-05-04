# Traveling Salesman Problem Generator Documentation

## Parameters

### n_cities

- **Description**: The number of cities to include in the TSP route.
- **Type**: Integer or Tuple of two integers
- **Default**: `(5, 20)` (Random between 5 and 20 cities)
- **Reasonable Range**: 3 to 100 cities

### distance_range

- **Description**: A tuple specifying the minimum and maximum distances between cities.
- **Type**: Tuple of two integers `(min_distance, max_distance)`
- **Default**: `(10, 1000)`
- **Reasonable Range**:
  - `min_distance`: 1 to 1000
  - `max_distance`: `min_distance` to 5000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer

## Generated Instance Properties

For each generated TSP instance:

- Cities are labeled as "city_0", "city_1", etc.
- Distances between cities are randomly assigned within distance_range
- Distance matrix is asymmetric (distance from A to B may differ from B to A)
- Each city must be visited exactly once
- Tour must start and end at the same city
- No subtours are allowed in the solution

## Example Usage

```python
# Create generator with default parameters
generator = Generator()

# Create generator with custom parameters
custom_params = {
    "n_cities": 10,  # Fixed number of cities
    "distance_range": (50, 500)
}
generator = Generator(parameters=custom_params, seed=42)

# Generate and solve instance
model = generator.generate_instance()
model.optimize()
generator.print_solution(model)
```
