import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Capacitated Lot-Sizing Problem generator.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_products: Number of products
                - n_periods: Number of periods
                - setup_cost_range: Tuple of (min, max) for setup costs
                - production_cost_range: Tuple of (min, max) for production costs
                - holding_cost_range: Tuple of (min, max) for holding costs
                - capacity_range: Tuple of (min, max) for period capacities
                - demand_range: Tuple of (min, max) for product demands
                - resource_usage_range: Tuple of (min, max) for resource usage
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "capacitated_lot_sizing"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        I_{it} = Σ_{k=1}^t X_{ik} - Σ_{k=1}^t d_{ik}  ∀i,t
        
        Minimize Σ_{i=1}^n Σ_{t=1}^T (S_{it}Y_{it} + C_{it}X_{it} + h_{it}I_{it})
        Subject to:
        Σ_{i=1}^n a_i X_{it} ≤ R_t                 ∀t
        X_{it} ≤ M_{it}Y_{it}                      ∀i,t
        I_{it} ≥ 0                                 ∀i,t
        Y_{it} ∈ {0,1}, X_{it} ≥ 0                ∀i,t
        """
        default_parameters = {
            "n_products": (2, 2),
            "n_periods": (6, 6),
            "setup_cost_range": (1000, 2000),
            "production_cost_range": (40, 50),
            "holding_cost_range": (4, 5),
            "capacity_range": (800, 800),
            "demand_range": (50, 100),
            "resource_usage_range": (1.5, 2)
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
        Generate a CLSP instance and create its corresponding Gurobi model.
        
        Returns:
            gp.Model: Configured Gurobi model for the CLSP
        """
        # Generate problem dimensions
        n_products = random.randint(*self.n_products)
        n_periods = random.randint(*self.n_periods)
        
        # Generate sets
        products = range(n_products)
        periods = range(n_periods)
        
        # Generate parameters
        setup_costs = {(i,t): random.randint(*self.setup_cost_range) 
                      for i in products for t in periods}
        prod_costs = {(i,t): random.randint(*self.production_cost_range) 
                     for i in products for t in periods}
        hold_costs = {(i,t): random.randint(*self.holding_cost_range) 
                     for i in products for t in periods}
        demands = {(i,t): random.randint(*self.demand_range) 
                  for i in products for t in periods}
        capacities = {t: random.randint(*self.capacity_range) for t in periods}
        resource_usage = {i: random.uniform(*self.resource_usage_range) 
                         for i in products}
        
        # Calculate big-M values
        big_M = {(i,t): sum(demands[i,k] for k in range(t, n_periods)) 
                for i in products for t in periods}
        
        # Create Gurobi model
        model = gp.Model("CLSP")
        model.Params.OutputFlag = 0
        
        # Create variables
        X = model.addVars(products, periods, name="Production")
        Y = model.addVars(products, periods, vtype=GRB.BINARY, name="Setup")
        
        # Create inventory variables and expressions
        I = {}
        for i in products:
            for t in periods:
                # Inventory at t = Total production up to t - Total demand up to t
                I[i,t] = model.addVar(name=f"Inventory_{i}_{t}")
                model.addConstr(
                    I[i,t] == gp.quicksum(X[i,k] for k in range(t+1)) - 
                             gp.quicksum(demands[i,k] for k in range(t+1)),
                    name=f"InventoryBalance_{i}_{t}"
                )
        
        # Set objective
        model.setObjective(
            gp.quicksum(setup_costs[i,t] * Y[i,t] + 
                       prod_costs[i,t] * X[i,t] + 
                       hold_costs[i,t] * I[i,t] 
                       for i in products for t in periods),
            GRB.MINIMIZE
        )
        
        # Add capacity constraints
        for t in periods:
            model.addConstr(
                gp.quicksum(resource_usage[i] * X[i,t] for i in products) <= capacities[t],
                name=f"Capacity_{t}"
            )
        
        # Add setup forcing constraints
        for i in products:
            for t in periods:
                model.addConstr(
                    X[i,t] <= big_M[i,t] * Y[i,t],
                    name=f"Setup_{i}_{t}"
                )
        
        # Add non-negativity constraints for inventory
        for i in products:
            for t in periods:
                model.addConstr(I[i,t] >= 0, name=f"NonNegInventory_{i}_{t}")
        
        return model

if __name__ == '__main__':
    import time
    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("clsp.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
    
    test_generator()