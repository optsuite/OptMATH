import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Production Planning optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_products: Number of products
                - n_stages: Number of stages
                - rate_range: Tuple of (min, max) for production rates (tons per hour)
                - available_range: Tuple of (min, max) for available hours per stage
                - profit_range: Tuple of (min, max) for profit per ton
                - commit_range: Tuple of (min, max) for minimum production commitment
                - market_range: Tuple of (min, max) for maximum market demand
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "production_planning"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are:
        - Products: Set of products \( p \)
        - Stages: Set of stages \( s \)
        
        Parameters:
        - \( \text{Rate}_{p,s} \): Production rate (tons per hour) of product \( p \) in stage \( s \)
        - \( \text{Available}_{s} \): Available hours per week in stage \( s \)
        - \( \text{Profit}_{p} \): Profit per ton for product \( p \)
        - \( \text{Commit}_{p} \): Minimum production commitment for product \( p \)
        - \( \text{Market}_{p} \): Maximum market demand for product \( p \)
        
        Decision Variable:
        - \( \text{Production}_{p} \): Tons of product \( p \) to be produced (continuous variable)
        
        Objective:
        Maximize total profit:
        \[
        \text{Maximize} \quad \sum_{p \in \text{Products}} \text{Profit}_{p} \cdot \text{Production}_{p}
        \]
        
        Constraints:
        1. Time Constraint:
        \[
        \sum_{p \in \text{Products}} \left( \frac{1}{\text{Rate}_{p,s}} \cdot \text{Production}_{p} \right) \leq \text{Available}_{s} \quad \forall s \in \text{Stages}
        \]
        2. Commit Constraint:
        \[
        \text{Commit}_{p} \leq \text{Production}_{p} \quad \forall p \in \text{Products}
        \]
        3. Market Constraint:
        \[
        \text{Production}_{p} \leq \text{Market}_{p} \quad \forall p \in \text{Products}
        \]
        """
        default_parameters = {
            "n_products": (2, 5),
            "n_stages": (5, 10),
            "rate_range": (3, 10),
            "available_range": (150, 300),
            "profit_range": (100, 500),
            "commit_range": (10, 50),
            "market_range": (120, 200)
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
        1. Generates random problem data (products, stages, rates, available hours, profits, commitments, market demands)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the production planning problem
        """
        
        # Randomly select number of products and stages
        self.n_products = random.randint(*self.n_products)
        self.n_stages = random.randint(*self.n_stages)
        
        # Generate products and stages
        products = [f"product_{i}" for i in range(self.n_products)]
        stages = [f"stage_{j}" for j in range(self.n_stages)]
        
        # Generate random parameters
        rate = {(p, s): random.randint(*self.rate_range) for p in products for s in stages}
        available = {s: random.randint(*self.available_range) for s in stages}
        profit = {p: random.randint(*self.profit_range) for p in products}
        commit = {p: random.randint(*self.commit_range) for p in products}
        market = {p: random.randint(*self.market_range) for p in products}
        
        # Create Gurobi model
        model = gp.Model("ProductionPlanning")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create continuous decision variables (Production[p] = tons of product p to produce)
        production = model.addVars(products, vtype=GRB.CONTINUOUS, name="Production")
        
        # Set objective: maximize total profit
        model.setObjective(
            gp.quicksum(profit[p] * production[p] for p in products),
            GRB.MAXIMIZE
        )
        
        # Add time constraints for each stage
        for s in stages:
            model.addConstr(
                gp.quicksum((1 / rate[p, s]) * production[p] for p in products) <= available[s],
                name=f"Time_{s}"
            )
        
        # Add commit and market constraints for each product
        for p in products:
            model.addConstr(
                production[p] >= commit[p],
                name=f"Commit_{p}"
            )
            model.addConstr(
                production[p] <= market[p],
                name=f"Market_{p}"
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
        
        model.write("production_planning.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()
