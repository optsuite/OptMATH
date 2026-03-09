import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Multi-Factory Schedule Problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_factories: Number of factories
                - n_months: Number of months
                - fixed_cost_range: Tuple of (min, max) for fixed costs
                - min_production_range: Tuple of (min, max) for minimum production levels
                - max_production_range: Tuple of (min, max) for maximum production levels
                - unit_cost_range: Tuple of (min, max) for unit production costs
                - demand_range: Tuple of (min, max) for monthly demand
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "multi_factory_schedule"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are F factories and M months. Each factory f (where f = 1, 2, ..., F) has the following attributes:
        - **Fixed Cost** a_f: The cost of running factory f during a month.
        - **Minimum Production Level** l_f: The minimum production level of factory f.
        - **Maximum Production Level** u_f: The maximum production level of factory f.
        - **Unit Production Cost** c_f: The cost per unit produced by factory f.
        - **Demand** d_m: The demand for month m.

        Decision Variables:
        - **z_{m,f}**: Binary variable indicating whether factory f is running in month m.
        - **x_{m,f}**: Continuous variable representing the units produced by factory f in month m.

        Objective:
        Minimize the total cost, which includes fixed costs and variable production costs:
        $$
        \text{Minimize} \quad \sum_{m \in M} \sum_{f \in F} \left( a_f \cdot z_{m,f} + c_f \cdot x_{m,f} \right)
        $$

        Constraints:
        1. **Minimum Production Level**:
           If a factory f is running in month m, the production must be at least the minimum production level:
           $$
           x_{m,f} \geq l_f \cdot z_{m,f} \quad \forall m \in M, f \in F
           $$

        2. **Maximum Production Level**:
           If a factory f is running in month m, the production must not exceed the maximum production level:
           $$
           x_{m,f} \leq u_f \cdot z_{m,f} \quad \forall m \in M, f \in F
           $$

        3. **Demand Satisfaction**:
           The total production across all factories in each month must meet or exceed the demand:
           $$
           \sum_{f \in F} x_{m,f} \geq d_m \quad \forall m \in M
           $$

        4. **Binary Decision Variable**:
           The decision variable z_{m,f} is binary:
           $$
           z_{m,f} \in \{0, 1\} \quad \forall m \in M, f \in F
           $$
        """
        default_parameters = {
            "n_factories": (3, 5),
            "n_months": (3, 5),
            "fixed_cost_range": (100, 500),
            "min_production_range": (20, 40),
            "max_production_range": (70, 120),
            "unit_cost_range": (1, 10),
            "demand_range": (100, 200)
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
        Generate a Multi-Factory Schedule Problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (factories, months, costs, production levels, demand)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the multi-factory schedule problem
        """
        
        # Randomly select number of factories and months
        self.n_factories = random.randint(*self.n_factories)
        self.n_months = random.randint(*self.n_months)
        
        # Generate factories and months
        factories = [f"factory_{f}" for f in range(self.n_factories)]
        months = [f"month_{m}" for m in range(self.n_months)]
        
        # Generate problem data
        fixed_costs = {f: random.randint(*self.fixed_cost_range) for f in factories}
        min_production = {f: random.randint(*self.min_production_range) for f in factories}
        max_production = {f: random.randint(*self.max_production_range) for f in factories}
        unit_costs = {f: random.randint(*self.unit_cost_range) for f in factories}
        demand = {m: random.randint(*self.demand_range) for m in months}
        
        # Create Gurobi model
        model = gp.Model("MultiFactorySchedule")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create decision variables
        z = model.addVars(months, factories, vtype=GRB.BINARY, name="RunDecision")
        x = model.addVars(months, factories, vtype=GRB.CONTINUOUS, name="Production")
        
        # Set objective: minimize total cost (fixed + variable)
        model.setObjective(
            gp.quicksum(fixed_costs[f] * z[m, f] + unit_costs[f] * x[m, f] for m in months for f in factories),
            GRB.MINIMIZE
        )
        
        # Add constraints
        # 1. Minimum production level
        model.addConstrs(
            (x[m, f] >= min_production[f] * z[m, f] for m in months for f in factories),
            name="MinProduction"
        )
        
        # 2. Maximum production level
        model.addConstrs(
            (x[m, f] <= max_production[f] * z[m, f] for m in months for f in factories),
            name="MaxProduction"
        )
        
        # 3. Demand satisfaction
        model.addConstrs(
            (gp.quicksum(x[m, f] for f in factories) >= demand[m] for m in months),
            name="DemandSatisfaction"
        )
        
        return model


if __name__ == '__main__':
    import time
    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("multi_factory_schedule.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()