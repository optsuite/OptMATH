## Parameters

### n_people

- **Description**: The number of people (staff) to include in the team formulation problem.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 100

### n_projects

- **Description**: The number of projects to include in the team formulation problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 50

### n_skills

- **Description**: The number of skills (expertise areas) to include in the team formulation problem.
- **Type**: Integer
- **Default**: `2`
- **Reasonable Range**: 1 to 20

### skill_range

- **Description**: A tuple specifying the minimum and maximum levels for the individuals' skill levels.
- **Type**: Tuple of two integers `(min_skill, max_skill)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_skill`: 1 to 100
  - `max_skill`: `min_skill` to 100

### required_skill_range

- **Description**: A tuple specifying the minimum and maximum levels for the required skill levels for projects.
- **Type**: Tuple of two integers `(min_required_skill, max_required_skill)`
- **Default**: `(5, 15)`
- **Reasonable Range**:
  - `min_required_skill`: 1 to 100
  - `max_required_skill`: `min_required_skill` to 100

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer