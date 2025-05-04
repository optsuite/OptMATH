## Parameters
### n_participants
- **Description**: Tuple specifying the range for the number of participants to include in the car selection problem.
- **Type**: Tuple of two integers `(min_participants, max_participants)`
- **Default**: `(5, 10)`
- **Reasonable Range**: 
  - `min_participants`: 2 to 100
  - `max_participants`: `min_participants` to 1000
  - Typical usage: (5, 20) for small problems, (20, 100) for medium problems

### n_cars
- **Description**: Tuple specifying the range for the number of available cars in the selection problem.
- **Type**: Tuple of two integers `(min_cars, max_cars)`
- **Default**: `(5, 10)`
- **Reasonable Range**:
  - `min_cars`: 2 to 100
  - `max_cars`: `min_cars` to 1000
  - Typical usage: (5, 20) for small problems, (20, 100) for medium problems

### preference_density
- **Description**: The probability that a participant is interested in a particular car. Controls the sparsity of the preference matrix.
- **Type**: Float between 0 and 1
- **Default**: `0.3`
- **Reasonable Range**: 0.1 to 0.9
  - Low density (0.1-0.3): Participants are selective about cars
  - Medium density (0.3-0.6): Moderate preference distribution
  - High density (0.6-0.9): Participants are interested in many cars

### seed
- **Description**: Random seed for reproducibility of the generated problem instance. Controls the randomization of both participant numbers and preferences.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer
- **Usage Notes**: 
  - Set for reproducible results in testing
  - Leave as None for random generation in production
