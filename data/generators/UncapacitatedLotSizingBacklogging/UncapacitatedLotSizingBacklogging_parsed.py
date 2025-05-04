import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Uncapacitated Lot-Sizing with Backlogging (ULSB) problem.

        Parameters:
            parameters (dict): Dictionary containing:
                - n_periods: Number of periods
                - demand_range: Tuple of (min, max) for demand in each period
                - fixed_cost_range: Tuple of (min, max) for fixed ordering cost
                - unit_order_cost_range: Tuple of (min, max) for unit ordering cost
                - unit_holding_cost_range: Tuple of (min, max) for unit holding cost
                - unit_backlog_penalty_range: Tuple of (min, max) for unit backlogging penalty
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "uncapacitated_lot_sizing_backlogging"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are T periods, each period t (where t = 1, 2, ..., T) has the following attributes:
        - **Demand** D_t: Demand in period t.
        - **Fixed Ordering Cost** F_t: Fixed cost if an order is placed in period t.
        - **Unit Ordering Cost** c_t: Cost per unit ordered in period t.
        - **Unit Holding Cost** h_t: Cost per unit held in inventory at the end of period t.
        - **Unit Backlogging Penalty** p_t: Penalty per unit backlogged in period t.

        Decision Variables:
        - **x_t**: Ordered amount in period t (continuous).
        - **I_t**: Ending inventory in period t (continuous).
        - **y_t**: Binary variable indicating whether an order is placed in period t (1 if placed, 0 otherwise).
        - **B_t**: Backlogged amount in period t (continuous).

        Objective:
        Minimize the total cost:
        $$
        \text{Minimize} \quad Z = \sum_{t=1}^T \left( F_t y_t + c_t x_t + h_t I_t + p_t B_t \right)
        $$

        Constraints:
        1. **Flow Balance**:
           $$
           I_{t-1} + x_t - B_{t-1} = I_t + D_t - B_t \quad \forall t \in T
           $$
        2. **Ordered Upper Bound**:
           $$
           x_t \leq y_t \cdot \sum_{i=1}^T D_i \quad \forall t \in T
           $$
        3. **Stock Loss of Generality**:
           $$
           I_0 = I_T = 0
           $$
        4. **Backlogging Loss of Generality**:
           $$
           B_0 = B_T = 0
           $$
        """
        default_parameters = {
            "n_periods": (3, 8),
            "demand_range": (10, 100),
            "fixed_cost_range": (50, 200),
            "unit_order_cost_range": (1, 10),
            "unit_holding_cost_range": (1, 5),
            "unit_backlog_penalty_range": (5, 20),
        }
        # Use default parameters if none are provided or if an empty dict is given
        if parameters is None or not parameters:
            parameters = default_parameters
        for key, value in parameters.items():
            setattr(self, key, value)

        self.seed = seed
        if self.seed is not None:
            random.seed(seed)

    def generate_instance(self):
        """
        Generate a ULSB problem instance and create its corresponding Gurobi model.

        This method does two things:
        1. Generates random problem data (demands, costs, penalties)
        2. Creates and returns a configured Gurobi model ready to solve

        Returns:
            gp.Model: Configured Gurobi model for the ULSB problem
        """
        # Randomly select number of periods
        self.n_periods = random.randint(*self.n_periods)

        # Generate periods
        periods = [f"period_{t}" for t in range(1, self.n_periods + 1)]

        # Generate random data
        demands = {t: random.randint(*self.demand_range) for t in periods}
        fixed_costs = {t: random.randint(*self.fixed_cost_range) for t in periods}
        unit_order_costs = {t: random.randint(*self.unit_order_cost_range) for t in periods}
        unit_holding_costs = {t: random.randint(*self.unit_holding_cost_range) for t in periods}
        unit_backlog_penalties = {t: random.randint(*self.unit_backlog_penalty_range) for t in periods}

        # Create Gurobi model
        model = gp.Model("UncapacitatedLotSizingBacklogging")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Decision variables
        x = model.addVars(periods, vtype=GRB.CONTINUOUS, name="OrderedAmount")
        I = model.addVars(periods, vtype=GRB.CONTINUOUS, name="EndingInventory")
        y = model.addVars(periods, vtype=GRB.BINARY, name="OrderIsPlaced")
        B = model.addVars(periods, vtype=GRB.CONTINUOUS, name="BackloggedAmount")

        # Objective: Minimize total cost
        model.setObjective(
            gp.quicksum(
                fixed_costs[t] * y[t]
                + unit_order_costs[t] * x[t]
                + unit_holding_costs[t] * I[t]
                + unit_backlog_penalties[t] * B[t]
                for t in periods
            ),
            GRB.MINIMIZE,
        )

        # Constraints
        # Flow balance constraint
        for t in periods:
            if t == "period_1":
                model.addConstr(
                    x[t] - B[t] == I[t] + demands[t] - B[t],
                    name=f"FlowBalance_{t}",
                )
            else:
                prev_t = f"period_{int(t.split('_')[1]) - 1}"
                model.addConstr(
                    I[prev_t] + x[t] - B[prev_t] == I[t] + demands[t] - B[t],
                    name=f"FlowBalance_{t}",
                )

        # Ordered upper bound constraint
        for t in periods:
            model.addConstr(
                x[t] <= y[t] * sum(demands.values()),
                name=f"OrderedUpperBound_{t}",
            )

        # Stock loss of generality (starting and ending inventory = 0)
        model.addConstr(I["period_1"] == 0, name="StartingInventoryZero")
        model.addConstr(I[f"period_{self.n_periods}"] == 0, name="EndingInventoryZero")

        # Backlogging loss of generality (starting and ending backlog = 0)
        model.addConstr(B["period_1"] == 0, name="StartingBacklogZero")
        model.addConstr(B[f"period_{self.n_periods}"] == 0, name="EndingBacklogZero")

        return model


if __name__ == "__main__":
    import time

    def test_generator():
        generator = Generator()
        model = generator.generate_instance()

        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time

        model.write("ulsb.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()