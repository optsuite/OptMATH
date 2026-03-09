## Parameters

### n_tasks

- **Description**: The number of tasks to include in the military personnel deployment problem.
- **Type**: Integer
- **Default**: `5`
- **Reasonable Range**: 1 to 100

### n_skills

- **Description**: The number of skills required for the tasks.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 20

### cost_range

- **Description**: A tuple specifying the minimum and maximum costs for deploying a soldier to a task.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 100)`
- **Reasonable Range**:
  - `min_cost`: 1 to 10,000
  - `max_cost`: `min_cost` to 10,000

### skill_requirement_range

- **Description**: A tuple specifying the minimum and maximum number of soldiers with a specific skill required for each task.
- **Type**: Tuple of two integers `(min_requirement, max_requirement)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_requirement`: 1 to 100
  - `max_requirement`: `min_requirement` to 100

### total_soldiers

- **Description**: The total number of soldiers available for deployment.
- **Type**: Integer
- **Default**: `50`
- **Reasonable Range**: 1 to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer