## Parameters

### n_aircrafts

- **Description**: The number of aircraft to include in the landing schedule.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 3 to 100

### time_window

- **Description**: A tuple specifying the overall time horizon in minutes for all landings (0 represents start time).
- **Type**: Tuple of two integers `(start_time, end_time)`
- **Default**: `(0, 180)` (3-hour window)
- **Reasonable Range**:
  - `start_time`: 0
  - `end_time`: 60 to 1440 (1-24 hours)

### penalty_range

- **Description**: A tuple specifying the minimum and maximum penalty costs per minute for early/late landings.
- **Type**: Tuple of two integers `(min_penalty, max_penalty)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_penalty`: 1 to 1000
  - `max_penalty`: `min_penalty` to 5000

### separation_range

- **Description**: A tuple specifying the minimum and maximum separation times (in minutes) required between aircraft landings.
- **Type**: Tuple of two integers `(min_separation, max_separation)`
- **Default**: `(3, 15)`
- **Reasonable Range**:
  - `min_separation`: 1 to 10
  - `max_separation`: `min_separation` to 20

### target_window_size

- **Description**: The size of the preferred landing window around target time (±minutes).
- **Type**: Integer
- **Default**: `30`
- **Reasonable Range**: 10 to 60

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer

## Generated Instance Properties

For each aircraft in the generated instance:

- Target landing time is randomly assigned within the time horizon
- Earliest landing time = max(start_time, target_time - target_window_size)
- Latest landing time = min(end_time, target_time + target_window_size)
- Early and late penalties are randomly assigned within penalty_range
- Separation times between each pair of aircraft are randomly assigned within separation_range

## Example Usage

```python
# Create generator with default parameters
generator = Generator()

# Create generator with custom parameters
custom_params = {
    "n_aircrafts": 5,
    "time_window": (0, 120),
    "penalty_range": (50, 200),
    "separation_range": (2, 10),
    "target_window_size": 20
}
generator = Generator(parameters=custom_params, seed=42)

# Generate and solve instance
model = generator.generate_instance()
model.optimize()
```
