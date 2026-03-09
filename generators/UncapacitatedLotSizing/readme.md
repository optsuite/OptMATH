## Parameters

### n_periods

- **Description**: The number of periods to include in the Uncapacitated Lot-Sizing problem.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 1 to 100

### demand_range

- **Description**: A tuple specifying the minimum and maximum demand for each period.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_demand`: 1 to 10,000
  - `max_demand`: `min_demand` to 10,000

### fixed_cost_range

- **Description**: A tuple specifying the minimum and maximum fixed ordering costs for each period.
- **Type**: Tuple of two integers `(min_fixed_cost, max_fixed_cost)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_fixed_cost`: 1 to 10,000
  - `max_fixed_cost`: `min_fixed_cost` to 10,000

### unit_order_cost_range

- **Description**: A tuple specifying the minimum and maximum unit ordering costs for each period.
- **Type**: Tuple of two integers `(min_unit_order_cost, max_unit_order_cost)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_unit_order_cost`: 1 to 10,000
  - `max_unit_order_cost`: `min_unit_order_cost` to 10,000

### unit_holding_cost_range

- **Description**: A tuple specifying the minimum and maximum unit holding costs for each period.
- **Type**: Tuple of two integers `(min_unit_holding_cost, max_unit_holding_cost)`
- **Default**: `(1, 3)`
- **Reasonable Range**:
  - `min_unit_holding_cost`: 1 to 10,000
  - `max_unit_holding_cost`: `min_unit_holding_cost` to 10,000

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer

---

## Mathematical Formulation

The Uncapacitated Lot-Sizing (ULS) problem is formulated as follows:

### Objective:
Minimize the total cost, which includes fixed ordering costs, unit ordering costs, and holding costs:
$$
\text{Minimize } Z = \sum_{t=1}^T \left( F_t y_t + c_t x_t + h_t I_t \right)
$$

### Constraints:
1. **Flow Balance**:
   $$
   I_{t-1} + x_t = I_t + D_t \quad \forall t \in T
   $$
2. **Ordered Amount Upper Bound**:
   $$
   x_t \leq y_t \cdot \sum_{i=1}^T D_i \quad \forall t \in T
   $$
3. **Stock Loss of Generality**:
   $$
   I_0 = 0, \quad I_T = 0
   $$

---

## Usage

1. **Customize Parameters**:
   - Modify the `parameters` dictionary in the `Generator` class to customize the problem size and ranges.
   - Example:
     ```python
     parameters = {
         "n_periods": (5, 10),
         "demand_range": (10, 100),
         "fixed_cost_range": (50, 200),
         "unit_order_cost_range": (5, 20),
         "unit_holding_cost_range": (2, 10),
     }
     generator = Generator(parameters=parameters)
     ```

2. **Generate and Solve**:
   - Use the `generate_instance` method to create a Gurobi model for the ULS problem.
   - Solve the model using `model.optimize()`.

3. **Output**:
   - The model is written to a file (`uncapacitated_lot_sizing.lp`) for further inspection.
   - The solve time and optimal value are printed to the console.

---

## Example Output

```plaintext
Test with default parameters:
Solve Time: 0.05 seconds
Optimal Value: 123.45
```

---

## Notes

- The problem is "uncapacitated," meaning there is no upper limit on the order quantity in any period.
- The starting and ending inventories are assumed to be zero.
- The model uses Gurobi for optimization, and the output is suppressed by default (`model.Params.OutputFlag = 0`).