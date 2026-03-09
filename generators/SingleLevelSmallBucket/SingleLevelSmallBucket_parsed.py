import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize DLSP optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_items: Number of items (products)
                - n_machines: Number of machines
                - n_periods: Number of time periods
                - setup_cost_range: Tuple of (min, max) for setup costs
                - startup_cost_range: Tuple of (min, max) for startup costs
                - holding_cost_range: Tuple of (min, max) for holding costs
                - backlog_cost_range: Tuple of (min, max) for backlog costs
                - startup_time_range: Tuple of (min, max) for startup times
                - capacity_range: Tuple of (min, max) for machine capacities
                - demand_range: Tuple of (min, max) for product demands
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "DLSP"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Sets: Items (I), Machines (M), Time Periods (T)
        Variables: y_{imt} (production), z_{imt} (startup), x_{imt} (quantity), s_{it} (inventory), b_{it} (backlog)
        
        $$
        \begin{aligned}
        &\text{Minimize} && \sum_{i,m,t} (f y_{imt} + g z_{imt}) + \sum_{i,t} (h_i s_{it} + π_i b_{it}) \\
        &\text{Subject to:} && s_{i,t-1} - b_{i,t-1} + \sum_m x_{imt} = d_{it} + s_{it} - b_{it} && \forall i,t \\
        & && x_{imt} + ST_m z_{imt} \leq C_m y_{imt} && \forall i,m,t \\
        & && \sum_i y_{imt} \leq 1 && \forall m,t \\
        & && z_{imt} \geq y_{imt} - y_{i,m,t-1} && \forall i,m,t>1 \\
        & && z_{im1} = y_{im1} && \forall i,m
        \end{aligned}
        $$
        """
        default_parameters = {
            "n_items": (3, 5),
            "n_machines": (2, 3),
            "n_periods": (5, 8),
            "setup_cost_range": (150, 250),
            "startup_cost_range": (100, 200),
            "holding_cost_range": (1, 3),
            "backlog_cost_range": (8, 12),
            "startup_time_range": (10, 20),
            "capacity_range": (80, 120),
            "demand_range": (20, 50)
        }
        
        if parameters is None or not parameters:
            parameters = default_parameters
        for key, value in parameters.items():
            setattr(self, key, value)
        
        self.seed = seed
        if self.seed is not None:
            random.seed(seed)

    def generate_instance(self):
        """
        Generate a DLSP instance and create its corresponding Gurobi model.
        """
        # Generate problem dimensions
        n_items = random.randint(*self.n_items)
        n_machines = random.randint(*self.n_machines)
        n_periods = random.randint(*self.n_periods)

        # Generate sets
        items = range(n_items)
        machines = range(n_machines)
        periods = range(n_periods)

        # Generate parameters
        setup_cost = random.uniform(*self.setup_cost_range)
        startup_cost = random.uniform(*self.startup_cost_range)
        holding_costs = {i: random.uniform(*self.holding_cost_range) for i in items}
        backlog_costs = {i: random.uniform(*self.backlog_cost_range) for i in items}
        startup_times = {m: random.uniform(*self.startup_time_range) for m in machines}
        capacities = {m: random.uniform(*self.capacity_range) for m in machines}
        demands = {(i,t): random.uniform(*self.demand_range) for i in items for t in periods}

        # Create Gurobi model
        model = gp.Model("DLSP")
        model.Params.OutputFlag = 0

        # Create variables
        y = model.addVars(items, machines, periods, vtype=GRB.BINARY, name="Production")
        z = model.addVars(items, machines, periods, vtype=GRB.BINARY, name="Startup")
        x = model.addVars(items, machines, periods, name="Amount")
        s = model.addVars(items, periods, name="Stock")
        b = model.addVars(items, periods, name="Backlog")

        # Set objective
        model.setObjective(
            gp.quicksum(setup_cost * y[i,m,t] + startup_cost * z[i,m,t] 
                       for i in items for m in machines for t in periods) +
            gp.quicksum(holding_costs[i] * s[i,t] + backlog_costs[i] * b[i,t] 
                       for i in items for t in periods),
            GRB.MINIMIZE
        )

        # Add constraints
        # Flow balance
        for i in items:
            for t in periods:
                if t == 0:
                    model.addConstr(
                        gp.quicksum(x[i,m,t] for m in machines) == 
                        demands[i,t] + s[i,t] - b[i,t]
                    )
                else:
                    model.addConstr(
                        s[i,t-1] - b[i,t-1] + gp.quicksum(x[i,m,t] for m in machines) == 
                        demands[i,t] + s[i,t] - b[i,t]
                    )

        # Capacity constraints
        for i in items:
            for m in machines:
                for t in periods:
                    model.addConstr(
                        x[i,m,t] + startup_times[m] * z[i,m,t] <= capacities[m] * y[i,m,t]
                    )

        # Machine constraints
        for m in machines:
            for t in periods:
                model.addConstr(
                    gp.quicksum(y[i,m,t] for i in items) <= 1
                )

        # Startup constraints
        for i in items:
            for m in machines:
                # First period
                model.addConstr(z[i,m,0] == y[i,m,0])
                # Other periods
                for t in periods:
                    if t > 0:
                        model.addConstr(z[i,m,t] >= y[i,m,t] - y[i,m,t-1])
                        model.addConstr(y[i,m,t-1] + z[i,m,t] <= 1)

        return model

if __name__ == '__main__':
    import time
    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("dlsp.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
    test_generator()