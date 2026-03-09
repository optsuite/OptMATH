import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize the Production Planning optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_products: Number of products
                - production_rate_range: Tuple of (min, max) for production rates (tons per hour)
                - profit_range: Tuple of (min, max) for profit per ton
                - min_sold_range: Tuple of (min, max) for minimum tons sold
                - max_sold_range: Tuple of (min, max) for maximum tons sold
                - available_hours: Total available hours in a week
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "production_planning"
        self.mathematical_formulation = r"""
        ### Mathematical Model\nSuppose there are n products, each product p (where p = 1, 2, ..., n) has the following attributes:\n- **Production Rate** r_p: The production rate of product p (tons per hour).\n- **Profit** c_p: The profit per ton of product p.\n- **Minimum Sold** min_p: The minimum tons of product p that must be sold.\n- **Maximum Sold** max_p: The maximum tons of product p that can be sold.\n- **Production Variable** x_p: The tons of product p to be produced.\n\nAdditionally, the total available production hours in a week is denoted by the constant H.\n$$\n\\begin{aligned}\n&\\text{Maximize} && \\sum_{p=1}^n c_p x_p \\\\\n&\\text{Subject to} && \\sum_{p=1}^n \\frac{x_p}{r_p} \\leq H \\\\\n& && x_p \\geq \\text{min}_p \\quad \\forall p = 1, 2, \\ldots, n \\\\\n& && x_p \\leq \\text{max}_p \\quad \\forall p = 1, 2, \\ldots, n\n\\end{aligned}\n$$
        """
        default_parameters = {
            "n_products": (3, 5),
            "production_rate_range": (1, 10),
            "profit_range": (1, 100),
            "min_sold_range": (1, 50),
            "max_sold_range": (50, 100),
            "available_hours": 168  # 168 hours in a week
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
        Generate a Production Planning problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (products, production rates, profits, min/max sold)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the production planning problem
        """
        
        # Randomly select number of products
        self.n_products = random.randint(*self.n_products)
        
        # Generate products and their properties
        products = [f"product_{i}" for i in range(self.n_products)]
        production_rates = {p: random.randint(*self.production_rate_range) for p in products}
        profits = {p: random.randint(*self.profit_range) for p in products}
        min_sold = {p: random.randint(*self.min_sold_range) for p in products}
        max_sold = {p: random.randint(*self.max_sold_range) for p in products}
        
        # Create Gurobi model
        model = gp.Model("ProductionPlanning")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create continuous decision variables (x[p] = tons of product p to produce)
        x = model.addVars(products, vtype=GRB.CONTINUOUS, name="Production")

        # Set objective: maximize total profit from produced products
        model.setObjective(
            gp.quicksum(profits[p] * x[p] for p in products),
            GRB.MAXIMIZE
        )

        # Add time constraint: total production time must not exceed available hours
        model.addConstr(
            gp.quicksum((1 / production_rates[p]) * x[p] for p in products) <= self.available_hours,
            name="TimeCapacity"
        )

        # Add minimum and maximum production constraints
        for p in products:
            model.addConstr(x[p] >= min_sold[p], name=f"MinSold_{p}")
            model.addConstr(x[p] <= max_sold[p], name=f"MaxSold_{p}")

        return model


if __name__ == '__main__':
    import time
    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("production_planning.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()