## Parameters

### n_nodes

- **Description**: The number of nodes (potential facility locations) to include in the problem.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 1 to 1000

### p_facilities

- **Description**: The number of facilities to be selected from the nodes.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to `n_nodes`

### distance_range

- **Description**: A tuple specifying the minimum and maximum distances between any two nodes.
- **Type**: Tuple of two integers `(min_distance, max_distance)`
- **Default**: `(1, 100)`
- **Reasonable Range**:
  - `min_distance`: 1 to 10,000
  - `max_distance`: `min_distance` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer

## Mathematical Formulation

The Maxisum Model for Facility Dispersion Problem is formulated as follows:

### Sets:
- \( N \): Set of nodes (potential facility locations).

### Parameters:
- \( p \): Number of facilities to be selected.
- \( d_{i,j} \): Distance between node \( i \) and node \( j \), where \( i, j \in N \).

### Variables:
- \( x_i \): Binary variable indicating whether node \( i \) is selected as a facility (\( x_i = 1 \)) or not (\( x_i = 0 \)), where \( i \in N \).
- \( z_{i,j} \): Binary variable indicating whether both nodes \( i \) and \( j \) are selected as facility locations (\( z_{i,j} = 1 \)) or not (\( z_{i,j} = 0 \)), where \( i, j \in N \).

### Objective Function:
- **Maximize the total distance between selected facilities**:
  \[
  \text{Maximize} \quad \sum_{i \in N} \sum_{j \in N} d_{i,j} \cdot z_{i,j}
  \]

### Constraints:
1. **Select exactly \( p \) facilities**:
   \[
   \sum_{i \in N} x_i = p
   \]
   
2. **Relationship between \( z_{i,j} \) and \( x_i, x_j \)**:
   - \( z_{i,j} \) can only be 1 if both \( x_i \) and \( x_j \) are 1:
     \[
     z_{i,j} \leq x_i \quad \forall i, j \in N
     \]
     \[
     z_{i,j} \leq x_j \quad \forall i, j \in N
     \]
   - \( z_{i,j} \) must be 1 if both \( x_i \) and \( x_j \) are 1:
     \[
     z_{i,j} \geq x_i + x_j - 1 \quad \forall i, j \in N
     \]

## Usage

To generate and solve an instance of the Maxisum Model for Facility Dispersion Problem, use the provided Python code. The generator allows customization of the parameters such as the number of nodes, number of facilities, and distance range. The random seed can also be set for reproducibility.

### Example:
```python
generator = MaxisumModelGenerator(parameters={
    "n_nodes": 20,
    "p_facilities": 5,
    "distance_range": (10, 200),
    "seed": 42
})
model = generator.generate_instance()
model.optimize()
```

This README provides a detailed description of the parameters, the mathematical formulation, and usage instructions for the Maxisum Model for Facility Dispersion Problem.