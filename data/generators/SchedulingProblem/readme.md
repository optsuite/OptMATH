## Parameters

### n_restaurants
- **Description**: The number of restaurant locations to be staffed.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 20
- **Note**: Represents different locations in the restaurant chain

### n_employees
- **Description**: The number of available employees in the staff pool.
- **Type**: Integer or Tuple `(min_employees, max_employees)`
- **Default**: `(10, 15)`
- **Reasonable Range**:
  - Small operations: 5 to 20 employees
  - Medium operations: 20 to 50 employees
  - Large operations: 50 to 200 employees

### n_shifts
- **Description**: The number of different shifts in a day.
- **Type**: Integer
- **Default**: `2`
- **Reasonable Range**: 1 to 4
- **Note**: Typically represents morning/evening or morning/afternoon/evening shifts

### n_skills
- **Description**: The number of different skills or positions to be filled.
- **Type**: Integer
- **Default**: `2`
- **Reasonable Range**: 1 to 10
- **Note**: Examples include cook, server, bartender, host

### demand_range
- **Description**: Range for the number of employees needed for each skill in each shift.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(1, 4)`
- **Reasonable Range**:
  - `min_demand`: 1 to 5
  - `max_demand`: `min_demand` to 10
- **Note**: Based on typical restaurant staffing needs

### skill_probability
- **Description**: Probability that an employee possesses a particular skill.
- **Type**: Float between 0 and 1
- **Default**: `0.7`
- **Reasonable Range**: 0.3 to 0.9
- **Note**: Higher values mean more flexible workforce

### availability_probability
- **Description**: Probability that an employee is available for a particular shift.
- **Type**: Float between 0 and 1
- **Default**: `0.8`
- **Reasonable Range**: 0.5 to 0.9
- **Note**: Reflects typical employee availability patterns

### preference_range
- **Description**: Range for employee preference costs (lower means more preferred).
- **Type**: Tuple of two integers `(min_preference, max_preference)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_preference`: 1 to 5
  - `max_preference`: `min_preference` to 10
- **Unit**: Cost units per assignment

### unfulfilled_cost
- **Description**: Penalty cost for each unfilled position.
- **Type**: Integer
- **Default**: `100`
- **Reasonable Range**: 50 to 1000
- **Note**: Should be significantly higher than preference costs

### seed
- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer