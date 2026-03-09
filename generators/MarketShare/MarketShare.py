import gurobipy as gp
from gurobipy import GRB
import random
import numpy as np

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Market Sharing optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_companies: Number of companies
                - n_markets: Number of markets
                - n_products: Number of products
                - demand_range: Tuple of (min, max) for market demand
                - cost_range: Tuple of (min, max) for unit costs
                - revenue_range: Tuple of (min, max) for unit revenues
            seed (int, optional): Random seed for repro
        """
        self.problem_type = "market_sharing"
        
        self.mathematical_formulation = r"""# Market Allocation Problem Mathematical Formulation
## Sets and Indices
- $I$: Set of companies, $i \in I$
- $J$: Set of markets, $j \in J$
- $K$: Set of products, $k \in K$
## Parameters
- $d_{jk}$: Demand of market $j$ for product $k$
- $c_{ijk}$: Unit cost for company $i$ to supply product $k$ to market $j$
- $r_{ijk}$: Unit revenue for company $i$ selling product $k$ in market $j$
## Decision Variables
- $x_{ijk}$: Quantity of product $k$ supplied by company $i$ to market $j$ (continuous)
## Objective Function
Maximize total profit:
$$\max \sum_{i\in I}\sum_{j\in J}\sum_{k\in K} (r_{ijk} - c_{ijk})x_{ijk}$$
## Constraints
1. Demand Satisfaction:
$$\sum_{i\in I} x_{ijk} = d_{jk} \quad \forall j\in J, \forall k\in K$$
2. Non-negativity:
$$x_{ijk} \geq 0 \quad \forall i\in I, \forall j\in J, \forall k\in K$$
"""
        
        default_parameters = {
            "n_companies": (1,20),
            "n_markets": (2,20),
            "n_products": (1,20),
            "demand_range": (10, 30),    
            "cost_range": (1, 5),        
            "revenue_range": (8, 15),     
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
        Generate a Market Sharing problem instance and create its Gurobi model.
        """
        
        # Randomly select number of companies, markets, and products
        self.n_companies = random.randint(*self.n_companies)
        self.n_markets = random.randint(*self.n_markets)
        self.n_products = random.randint(*self.n_products)
        
        # Create sets
        companies = range(self.n_companies)
        markets = range(self.n_markets)
        products = range(self.n_products)

        # Generate random parameters
        demand = {}
        for j in markets:
            for k in products:
                demand[j,k] = random.randint(*self.demand_range)

        # Generate random costs and revenues, ensuring that revenues exceed costs
        costs = {}
        revenues = {}
        for i in companies:
            for j in markets:
                for k in products:
                    cost = random.randint(*self.cost_range)
                    costs[i,j,k] = cost
                    # Ensure that revenue is at least 1 unit higher than cost
                    revenues[i,j,k] = cost + random.randint(3, 10)

        # Create Gurobi model
        model = gp.Model("MarketSharing")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Decision variables, x[i,j,k] = supply of product k by company i to market j
        x = model.addVars(companies, markets, products, 
                         vtype=GRB.INTEGER, 
                         name="supply")

        # Objective: maximize profit
        model.setObjective(
            gp.quicksum((revenues[i,j,k] - costs[i,j,k]) * x[i,j,k]
                       for i in companies for j in markets for k in products),
            GRB.MAXIMIZE
        )

        # Demand satisfaction constraints
        for j in markets:
            for k in products:
                model.addConstr(
                    gp.quicksum(x[i,j,k] for i in companies) == demand[j,k],
                    f"demand_{j}_{k}"
                )

        # Non-negativity constraints
        for i in companies:
            for j in markets:
                for k in products:
                    model.addConstr(x[i,j,k] >= 0, f"nonneg_{i}_{j}_{k}")

        # Store the parameters for solution analysis
        self.demand = demand
        self.costs = costs
        self.revenues = revenues

        return model

    def print_solution(self, model):
        """Print the solution details"""
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal objective value: {model.ObjVal:.2f}")
            
            # Print summary statistics
            total_supply = 0
            total_revenue = 0
            total_cost = 0
            
            for i in range(self.n_companies):
                for j in range(self.n_markets):
                    for k in range(self.n_products):
                        var_name = f"supply[{i},{j},{k}]"
                        for v in model.getVars():
                            if v.VarName == var_name and v.X > 1e-6:  # Non-zero supply
                                supply = v.X
                                revenue = self.revenues[i,j,k] * supply
                                cost = self.costs[i,j,k] * supply
                                total_supply += supply
                                total_revenue += revenue
                                total_cost += cost
                                print(f"Company {i} -> Market {j}, Product {k}: "
                                      f"Supply = {supply:.2f}, "
                                      f"Revenue = {revenue:.2f}, "
                                      f"Cost = {cost:.2f}")
            
            print(f"\nSummary:")
            print(f"Total Supply: {total_supply:.2f}")
            print(f"Total Revenue: {total_revenue:.2f}")
            print(f"Total Cost: {total_cost:.2f}")
            print(f"Total Profit: {total_revenue - total_cost:.2f}")
        else:
            print("No optimal solution found")
            print(f"Status code: {model.Status}")
            # Print model statistics
            print(f"\nModel Statistics:")
            print(f"Number of variables: {model.NumVars}")
            print(f"Number of constraints: {model.NumConstrs}")
            # Try to compute IIS
            try:
                model.computeIIS()
                print("\nInfeasible constraints:")
                for c in model.getConstrs():
                    if c.IISConstr:
                        print(f"Constraint {c.ConstrName} is infeasible")
            except:
                print("Could not compute IIS")

if __name__ == '__main__':
    import time
    
    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        generator.print_solution(model)
        
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        
        print(model.NumVars, model.NumConstrs)

    test_generator()