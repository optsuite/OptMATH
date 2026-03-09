import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Profit Maximization optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_items: Number of items
                - a_range: Tuple of (min, max) for parameter a[j]
                - c_range: Tuple of (min, max) for parameter c[j]
                - u_range: Tuple of (min, max) for parameter u[j]
                - b_ratio: Ratio of b to total (sum of (1/a[j]) * u[j])
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "profit_maximization"
        self.mathematical_formulation = r"""
        ### Mathematical Model\nSuppose there are m items, each item j (where j = 1, 2, ..., m) has the following attributes:\n- **Parameter** a_j: A parameter for each item j.\n- **Parameter** c_j: The profit coefficient for item j.\n- **Parameter** u_j: The upper bound for the variable X_j.\n- **Variable** X_j: A continuous variable representing the quantity or level of activity for item j.\n\nAdditionally, there is a global parameter b representing a resource or capacity constraint.\n$$\n\\begin{aligned}\n&\\text{Maximize} && \\sum_{j=1}^m c_j X_j \\\\\n&\\text{Subject to} && \\sum_{j=1}^m \\frac{1}{a_j} X_j \\leq b \\\\\n& && 0 \\leq X_j \\leq u_j \\quad \\forall j = 1, 2, \\ldots, m\n\\end{aligned}\n$$
        """
        default_parameters = {
            "n_items": (3, 3),
            "a_range": (1, 10),
            "c_range": (1, 50),
            "u_range": (1, 100),
            "b_ratio": 0.7
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
        Generate a Profit Maximization problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (items, a[j], c[j], u[j], b)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the profit maximization problem
        """
        
        # Randomly select number of items
        self.n_items = random.randint(*self.n_items)
        
        # Generate items and their properties
        items = [f"item_{i}" for i in range(self.n_items)]
        a_values = {item: random.randint(*self.a_range) for item in items}
        c_values = {item: random.randint(*self.c_range) for item in items}
        u_values = {item: random.randint(*self.u_range) for item in items}
        
        # Calculate b as a ratio of total (sum of (1/a[j]) * u[j])
        total = sum((1 / a_values[i]) * u_values[i] for i in items)
        b = int(total * self.b_ratio)

        # Create Gurobi model
        model = gp.Model("ProfitMaximization")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create continuous decision variables (X[j] represents the quantity for item j)
        X = model.addVars(items, vtype=GRB.CONTINUOUS, name="X")

        # Set objective: maximize total profit
        model.setObjective(
            gp.quicksum(c_values[i] * X[i] for i in items),
            GRB.MAXIMIZE
        )

        # Add resource constraint: sum of (1/a[j]) * X[j] must not exceed b
        model.addConstr(
            gp.quicksum((1 / a_values[i]) * X[i] for i in items) <= b,
            name="ResourceConstraint"
        )

        # Add variable bounds: 0 <= X[j] <= u[j]
        for i in items:
            model.addConstr(X[i] >= 0, name=f"LowerBound_{i}")
            model.addConstr(X[i] <= u_values[i], name=f"UpperBound_{i}")

        return model


if __name__ == '__main__':
    import time
    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("profit_maximization.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()