import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Factory Planning optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_periods: Number of time periods
                - n_products: Number of products
                - n_machines: Dictionary of machine types and quantities
                - profit_range: Tuple of (min, max) for product profits
                - holding_cost: Storage cost per unit per period
                - machine_time_range: Tuple of (min, max) for processing times
                - machine_hours: Available hours per machine per period
                - max_inventory: Maximum storage capacity per product
                - sales_limit_range: Tuple of (min, max) for sales limits
                - target_inventory_ratio: Ratio for end-horizon inventory targets
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "factory_planning"
        self.mathematical_formulation = r"""
        ### Mathematical Model for Factory Planning
        [Previous mathematical formulation here]
        """
        default_parameters = {
            "n_periods": 6,
            "n_products": (3, 5),
            "n_machines": {"grinder": 4, "drill": 2, "borer": 1},
            "profit_range": (150, 300),
            "holding_cost": 20,
            "machine_time_range": (1, 3),
            "machine_hours": 160,
            "max_inventory": 100,
            "sales_limit_range": (30, 80),
            "target_inventory_ratio": 0.3
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
        Generate a Factory Planning problem instance.
        
        Returns:
            gp.Model: Configured Gurobi model for the factory planning problem
        """
        # Generate random number of products
        if isinstance(self.n_products, tuple):
            self.n_products = random.randint(*self.n_products)
        
        # Create sets
        periods = range(self.n_periods)
        products = [f"product_{i}" for i in range(self.n_products)]
        machines = list(self.n_machines.keys())
        
        # Generate parameters
        profits = {p: random.randint(*self.profit_range) for p in products}
        machine_time = {(m,p): random.randint(*self.machine_time_range) 
                       for m in machines for p in products}
        sales_limits = {(t,p): random.randint(*self.sales_limit_range) 
                       for t in periods for p in products}
        
        # Generate maintenance schedule (randomly select periods for maintenance)
        maintenance = {(t,m): 1 if random.random() < 0.1 else 0 
                      for t in periods for m in machines}
        
        # Calculate target inventory levels
        target_inventory = {p: int(self.max_inventory * self.target_inventory_ratio) 
                          for p in products}
        
        # Create Gurobi model
        model = gp.Model("FactoryPlanning")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create decision variables
        make = model.addVars(periods, products, name="Production", vtype=GRB.CONTINUOUS, lb=0)
        store = model.addVars(periods, products, name="Inventory", vtype=GRB.CONTINUOUS, lb=0)
        sell = model.addVars(periods, products, name="Sales", vtype=GRB.CONTINUOUS, lb=0)
        
        # Set objective: maximize profit minus holding costs
        model.setObjective(
            gp.quicksum(profits[p] * sell[t,p] for t in periods for p in products) -
            gp.quicksum(self.holding_cost * store[t,p] for t in periods for p in products),
            GRB.MAXIMIZE
        )
        
        # Add constraints
        # Initial balance constraints
        for p in products:
            model.addConstr(
                make[0,p] == sell[0,p] + store[0,p],
                name=f"InitialBalance_{p}"
            )
        
        # Balance constraints for remaining periods
        for t in periods[1:]:
            for p in products:
                model.addConstr(
                    store[t-1,p] + make[t,p] == sell[t,p] + store[t,p],
                    name=f"Balance_{t}_{p}"
                )
        
        # Machine capacity constraints
        for t in periods:
            for m in machines:
                model.addConstr(
                    gp.quicksum(machine_time[m,p] * make[t,p] for p in products) <= 
                    self.machine_hours * (self.n_machines[m] - maintenance[t,m]),
                    name=f"Capacity_{t}_{m}"
                )
        
        # Inventory and sales limits
        for t in periods:
            for p in products:
                model.addConstr(store[t,p] <= self.max_inventory, name=f"Storage_{t}_{p}")
                model.addConstr(sell[t,p] <= sales_limits[t,p], name=f"Sales_{t}_{p}")
        
        # End-horizon inventory targets
        for p in products:
            model.addConstr(
                store[self.n_periods-1,p] == target_inventory[p],
                name=f"Target_{p}"
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
        
        model.write("factory_planning.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Profit: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
            
    test_generator()