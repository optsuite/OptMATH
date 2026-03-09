import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Uncapacitated Lot-Sizing (ULS) optimization problem.

        Parameters:
            parameters (dict): Dictionary containing:
                - n_periods: Number of periods
                - demand_range: Tuple of (min, max) for demand in each period
                - fixed_cost_range: Tuple of (min, max) for fixed ordering cost in each period
                - unit_order_cost_range: Tuple of (min, max) for unit ordering cost in each period
                - unit_holding_cost_range: Tuple of (min, max) for unit holding cost in each period
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "uncapacitated_lot_sizing"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are T periods, each period t (where t = 1, 2, ..., T) has the following attributes:
        - **Demand** D_t: Demand in period t.
        - **Fixed Cost** F_t: Fixed ordering cost in period t.
        - **Unit Order Cost** c_t: Unit ordering cost in period t.
        - **Unit Holding Cost** h_t: Unit holding cost in period t.
        - **Ordered Amount** x_t: Continuous variable representing the amount ordered in period t.
        - **Ending Inventory** I_t: Continuous variable representing the ending inventory in period t.
        - **Order Indicator** y_t: Binary variable indicating whether an order is placed in period t.

        Objective:
        Minimize the total cost, which includes fixed ordering costs, unit ordering costs, and holding costs:
        $$
        \text{Minimize } Z = \sum_{t=1}^T \left( F_t y_t + c_t x_t + h_t I_t \right)
        $$

        Constraints:
        1. Flow Balance: Ending inventory in period t is equal to the ending inventory from the previous period plus the ordered amount minus the demand in period t:
        $$
        I_{t-1} + x_t = I_t + D_t \quad \forall t \in T
        $$
        2. Ordered Amount Upper Bound: The ordered amount in period t is zero if no order is placed (y_t = 0), and otherwise, it is bounded by the total demand over all periods:
        $$
        x_t \leq y_t \cdot \sum_{i=1}^T D_i \quad \forall t \in T
        $$
        3. Stock Loss of Generality: Starting and ending inventories are zero:
        $$
        I_0 = 0, \quad I_T = 0
        $$
        """
        default_parameters = {
            "n_periods": (3, 5),
            "demand_range": (1, 10),
            "fixed_cost_range": (10, 50),
            "unit_order_cost_range": (1, 5),
            "unit_holding_cost_range": (1, 3),
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
        Generate an Uncapacitated Lot-Sizing problem instance and create its corresponding Gurobi model.

        This method does two things:
        1. Generates random problem data (demands, costs, etc.)
        2. Creates and returns a configured Gurobi model ready to solve

        Returns:
            gp.Model: Configured Gurobi model for the ULS problem
        """
        # Randomly select number of periods
        self.n_periods = random.randint(*self.n_periods)

        # Generate periods and their properties
        periods = [f"period_{t}" for t in range(1, self.n_periods + 1)]
        demands = {t: random.randint(*self.demand_range) for t in periods}
        fixed_costs = {t: random.randint(*self.fixed_cost_range) for t in periods}
        unit_order_costs = {t: random.randint(*self.unit_order_cost_range) for t in periods}
        unit_holding_costs = {t: random.randint(*self.unit_holding_cost_range) for t in periods}

        # Create Gurobi model
        model = gp.Model("UncapacitatedLotSizing")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create decision variables
        x = model.addVars(periods, vtype=GRB.CONTINUOUS, name="OrderedAmount")
        I = model.addVars(periods, vtype=GRB.CONTINUOUS, name="EndingInventory")
        y = model.addVars(periods, vtype=GRB.BINARY, name="OrderIsPlaced")

        # Set objective: minimize total cost
        model.setObjective(
            gp.quicksum(
                fixed_costs[t] * y[t] + unit_order_costs[t] * x[t] + unit_holding_costs[t] * I[t]
                for t in periods
            ),
            GRB.MINIMIZE,
        )

        # Add constraints
        for t in periods:
            # Flow balance constraint
            if t == "period_1":
                model.addConstr(x[t] == I[t] + demands[t], name=f"FlowBalance_{t}")
            else:
                prev_t = f"period_{int(t.split('_')[1]) - 1}"
                model.addConstr(I[prev_t] + x[t] == I[t] + demands[t], name=f"FlowBalance_{t}")

            # Ordered amount upper bound
            model.addConstr(
                x[t] <= y[t] * sum(demands.values()), name=f"OrderedUpperBound_{t}"
            )

        # Stock loss of generality: starting and ending inventories are zero
        model.addConstr(I["period_1"] == 0, name="StartingInventory")
        model.addConstr(I[f"period_{self.n_periods}"] == 0, name="EndingInventory")

        return model


if __name__ == "__main__":
    import time

    def test_generator():
        generator = Generator()
        model = generator.generate_instance()

        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time

        model.write("uncapacitated_lot_sizing.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()