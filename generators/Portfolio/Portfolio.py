import gurobipy as gp
from gurobipy import GRB
import random
import numpy as np

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Portfolio Optimization problem.
        Parameters:
        parameters (dict): Dictionary containing:
            - n_assets: Number of assets
            - budget: Total investment budget
            - return_range: Tuple of (min, max) for expected returns
            - risk_range: Tuple of (min, max) for risk (std dev)
            - weight_bounds: Tuple of (min, max) for asset weights
        """
        self.problem_type = "portfolio_optimization"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Minimize portfolio risk subject to:
        - Target return constraint
        - Budget constraint (sum of weights = 1)
        - Individual asset weight limits
        """

        default_parameters = {
            "n_assets": (3, 100),
            "budget": 1000000,  # $1M investment
            "return_range": (0.05, 0.15),  # 5-15% annual return
            "risk_range": (0.10, 0.30),  # 10-30% annual volatility
            "weight_bounds": (0.0, 0.3),  # 0-30% per asset
        }

        if parameters is None or not parameters:
            parameters = default_parameters
        for key, value in parameters.items():
            setattr(self, key, value)

        self.seed = seed
        if self.seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def generate_instance(self):
        """
        Generate a Portfolio Optimization instance and create its Gurobi model.
        Returns:
            gp.Model: Configured Gurobi model for portfolio optimization
        """
        
        self.n_assets = random.randint(*self.n_assets)
        
        # Generate assets
        self.assets = [f"asset_{i}" for i in range(self.n_assets)]

        # Generate expected returns
        self.returns = {i: random.uniform(*self.return_range) for i in self.assets}

        # Generate covariance matrix
        # Using a simplified approach for demonstration
        self.volatilities = {i: random.uniform(*self.risk_range) for i in self.assets}
        correlation_matrix = np.random.uniform(
            -0.2, 0.8, size=(self.n_assets, self.n_assets)
        )
        correlation_matrix = (
            correlation_matrix + correlation_matrix.T
        ) / 2  # Make symmetric
        np.fill_diagonal(correlation_matrix, 1)  # Diagonal = 1

        self.covariance = {}
        for i, asset1 in enumerate(self.assets):
            for j, asset2 in enumerate(self.assets):
                self.covariance[(asset1, asset2)] = (
                    correlation_matrix[i, j]
                    * self.volatilities[asset1]
                    * self.volatilities[asset2]
                )

        # Create Gurobi model
        model = gp.Model("PortfolioOptimization")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Decision variables: portfolio weights
        weights = model.addVars(
            self.assets,
            lb=self.weight_bounds[0],
            ub=self.weight_bounds[1],
            name="Weights",
        )

        # Portfolio variance variable
        port_var = model.addVar(name="PortfolioVariance")

        # Objective: minimize portfolio variance
        model.setObjective(port_var, GRB.MINIMIZE)

        # Constraints
        # Portfolio variance calculation
        model.addQConstr(
            gp.quicksum(
                weights[i] * weights[j] * self.covariance[(i, j)]
                for i in self.assets
                for j in self.assets
            )
            == port_var
        )

        # Budget constraint (weights sum to 1)
        model.addConstr(gp.quicksum(weights[i] for i in self.assets) == 1)

        # Target return constraint
        target_return = 0.10  # 10% target return
        model.addConstr(
            gp.quicksum(weights[i] * self.returns[i] for i in self.assets)
            >= target_return
        )

        return model

    def print_solution(self, model):
        """
        Print the solution of the Portfolio Optimization in a readable format.
        Parameters:
            model (gp.Model): Solved Gurobi model
        """
        if model.Status != GRB.OPTIMAL:
            print("No optimal solution found.")
            return

        print("\n=== Portfolio Optimization Results ===")
        print(
            f"Portfolio Risk (Std Dev): {np.sqrt(model.getVarByName('PortfolioVariance').X):.4f}"
        )

        # Get portfolio weights
        weights = {}
        for v in model.getVars():
            if v.VarName.startswith("Weights"):
                asset = v.VarName.split("[")[1].split("]")[0]
                weights[asset] = v.X

        # Calculate portfolio return
        port_return = sum(weights[i] * self.returns[i] for i in self.assets)

        print("\nPortfolio Allocation:")
        print(f"{'Asset':^12} {'Weight':^10} {'Return':^10} {'Risk':^10}")
        print("-" * 45)

        for asset in self.assets:
            print(
                f"{asset:^12} {weights[asset]:^10.4f} "
                f"{self.returns[asset]:^10.4f} "
                f"{self.volatilities[asset]:^10.4f}"
            )

        print("\nPortfolio Statistics:")
        print(f"Number of assets: {len(self.assets)}")
        print(f"Portfolio expected return: {port_return:.4f}")
        print(f"Highest individual weight: {max(weights.values()):.4f}")
        print(f"Lowest individual weight: {min(weights.values()):.4f}")

        # Calculate diversification metrics
        herfindahl = sum(w * w for w in weights.values())
        print(f"Herfindahl Index (concentration): {herfindahl:.4f}")


if __name__ == "__main__":
    import time

    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(
                f"Optimal Portfolio Variance: {model.getVarByName('PortfolioVariance').X:.6f}"
            )
            generator.print_solution(model)
        else:
            print("No optimal solution found")

    test_generator()
