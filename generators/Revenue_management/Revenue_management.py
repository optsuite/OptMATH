import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Revenue Management optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_resources: Number of flight legs
                - n_packages: Number of travel packages
                - capacity_range: Tuple of (min, max) for flight capacities
                - demand_range: Tuple of (min, max) for package demands
                - revenue_range: Tuple of (min, max) for package revenues
                - resource_use_probability: Probability of a package using a resource
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "revenue_management"
        self.mathematical_formulation = r"""
        ### Mathematical Model for Revenue Management
        [Previous mathematical formulation here]
        """
        default_parameters = {
            "n_resources": 3,
            "n_packages": (4, 6),
            "capacity_range": (150, 250),
            "demand_range": (50, 150),
            "revenue_range": (200, 800),
            "resource_use_probability": 0.3
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
        Generate a Revenue Management problem instance.
        
        Returns:
            gp.Model: Configured Gurobi model for revenue management
        """
        # Generate number of packages if range is provided
        if isinstance(self.n_packages, tuple):
            self.n_packages = random.randint(*self.n_packages)
        
        # Create sets
        resources = range(self.n_resources)
        packages = range(self.n_packages)
        
        # Generate parameters
        capacities = {r: random.randint(*self.capacity_range) 
                     for r in resources}
        demands = {p: random.randint(*self.demand_range) 
                  for p in packages}
        revenues = {p: random.randint(*self.revenue_range) 
                   for p in packages}
        
        # Generate resource usage matrix (ensuring each package uses at least one resource)
        resource_usage = {(p,r): 0 for p in packages for r in resources}
        for p in packages:
            # Ensure at least one resource is used
            first_resource = random.choice(list(resources))
            resource_usage[p,first_resource] = 1
            # Randomly use additional resources
            for r in resources:
                if r != first_resource and random.random() < self.resource_use_probability:
                    resource_usage[p,r] = 1
        
        # Create Gurobi model
        model = gp.Model("RevenueManagement")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create decision variables
        x = model.addVars(packages, vtype=GRB.INTEGER, name="PackageSales")
        
        # Set objective: maximize total revenue
        model.setObjective(
            gp.quicksum(revenues[p] * x[p] for p in packages),
            GRB.MAXIMIZE
        )
        
        # Add demand constraints
        for p in packages:
            model.addConstr(
                x[p] <= demands[p],
                name=f"DemandLimit_{p}"
            )
        
        # Add capacity constraints
        for r in resources:
            model.addConstr(
                gp.quicksum(resource_usage[p,r] * x[p] for p in packages) <= capacities[r],
                name=f"CapacityLimit_{r}"
            )
        
        # Store problem data
        self.capacities = capacities
        self.demands = demands
        self.revenues = revenues
        self.resource_usage = resource_usage
        
        return model

if __name__ == '__main__':
    import time
    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("revenue_management.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Revenue: ${model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
            
    test_generator()