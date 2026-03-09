## Parameters

### n_nodes

- **Description**: The number of nodes in the graph for the shortest path problem.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 2 to 1000

### arc_cost_range

- **Description**: A tuple specifying the minimum and maximum costs for the arcs in the graph.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 100)`
- **Reasonable Range**:
  - `min_cost`: 1 to 10,000
  - `max_cost`: `min_cost` to 10,000

### start_node

- **Description**: The starting node for the shortest path problem.
- **Type**: Integer (index of the node)
- **Default**: `0` (first node)
- **Reasonable Range**: 0 to `n_nodes - 1`

### end_node

- **Description**: The ending node for the shortest path problem.
- **Type**: Integer (index of the node)
- **Default**: `n_nodes - 1` (last node)
- **Reasonable Range**: 0 to `n_nodes - 1`

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer