## Parameters

### n_origins

- **Description**: The number of origins (supply points) in the transportation problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 100

### n_destinations

- **Description**: The number of destinations (demand points) in the transportation problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 100

### supply_range

- **Description**: A tuple specifying the minimum and maximum supply values for the origins.
- **Type**: Tuple of two integers `(min_supply, max_supply)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_supply`: 1 to 10,000
  - `max_supply`: `min_supply` to 10,000

### demand_range

- **Description**: A tuple specifying the minimum and maximum demand values for the destinations.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(10, 100)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### cost_range

- **Description**: A tuple specifying the minimum and maximum transportation costs between origins and destinations.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_cost`: 1 to 10,000
  - `max_cost`: `min_cost` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer

---

## Mathematical Formulation

### Sets
- **Origins**: Set of origins (supply points).
- **Destinations**: Set of destinations (demand points).

### Parameters
- **Supply**: Amount of supply available at each origin.
- **Demand**: Amount of demand required at each destination.
- **Cost**: Cost of transporting one unit from an origin to a destination.

### Decision Variables
- **Transport**: Amount of goods to be transported from an origin to a destination.

### Objective
Minimize the total transportation cost:
$$
\text{Minimize } \sum_{i \in \text{Origins}} \sum_{j \in \text{Destinations}} \text{Cost}_{i,j} \cdot \text{Transport}_{i,j}
$$

### Constraints
1. **Supply Constraints**: The total amount shipped from each origin must equal its supply.
   $$
   \sum_{j \in \text{Destinations}} \text{Transport}_{i,j} = \text{Supply}_i \quad \forall i \in \text{Origins}
   $$

2. **Demand Constraints**: The total amount shipped to each destination must equal its demand.
   $$
   \sum_{i \in \text{Origins}} \text{Transport}_{i,j} = \text{Demand}_j \quad \forall j \in \text{Destinations}
   $$

3. **Non-Negativity Constraints**: The amount transported must be non-negative.
   $$
   \text{Transport}_{i,j} \geq 0 \quad \forall i \in \text{Origins}, \forall j \in \text{Destinations}
   $$

---

## Usage

To generate and solve a transportation problem instance, use the `Generator` class as follows:

```python
generator = TransportationGenerator()
model = generator.generate_instance()
model.optimize()
```

The generated instance can be saved to a file using:
```python
model.write("transportation.lp")
```

---

## Notes
- Ensure that the total supply equals the total demand for a balanced transportation problem. If the problem is unbalanced, additional steps (e.g., introducing dummy origins or destinations) may be required.