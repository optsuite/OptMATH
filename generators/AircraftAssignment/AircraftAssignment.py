import gurobipy as gp 
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Aircraft Assignment optimization problem.
        Parameters:
        parameters (dict): Dictionary containing:
            - n_aircraft: Number of aircraft types
            - n_routes: Number of routes
            - availability_range: Tuple of (min, max) for aircraft availability
            - demand_range: Tuple of (min, max) for route demand
            - capabilities_range: Tuple of (min, max) for aircraft capabilities
            - cost_range: Tuple of (min, max) for assignment costs
        seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "aircraft_assignment"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Sets:
        - A: Set of aircraft types
        - R: Set of routes
        
        Parameters:
        - availability_a: Availability of aircraft type a
        - demand_r: Demand for route r
        - capabilities_ar: Capabilities of aircraft a for route r
        - costs_ar: Cost of assigning aircraft a to route r
        
        Variables:
        - allocation_ar: Number of aircraft type a assigned to route r (integer)
        
        $$
        \begin{aligned}
        &\text{Minimize} && \sum_{a \in A}\sum_{r \in R} costs_{ar} \cdot allocation_{ar} \\
        &\text{Subject to} && \sum_{r \in R} allocation_{ar} \leq availability_a && \forall a \in A \\
        & && \sum_{a \in A} allocation_{ar} \cdot capabilities_{ar} = demand_r && \forall r \in R \\
        & && allocation_{ar} \geq 0, \text{ integer} && \forall a \in A, r \in R
        \end{aligned}
        $$
        """
        
        default_parameters = {
            "n_aircraft": (10, 30),
            "n_routes": (3, 30),
            "availability_range": (1, 10),
            "demand_range": (100, 500),
            "capabilities_range": (50, 200),
            "cost_range": (1000, 5000)
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
        Generate an Aircraft Assignment problem instance and create its corresponding Gurobi model.
        Returns:
        gp.Model: Configured Gurobi model for the aircraft assignment problem
        """
        # Randomly select number of aircraft types and routes
        self.n_aircraft = random.randint(*self.n_aircraft)
        self.n_routes = random.randint(*self.n_routes)

        # Generate sets
        self.aircraft = [f"aircraft_{i}" for i in range(self.n_aircraft)]
        self.routes = [f"route_{i}" for i in range(self.n_routes)]

        # Generate parameters and save them as class attributes
        self.availability = {a: random.randint(*self.availability_range) for a in self.aircraft}
        self.demand = {r: random.randint(*self.demand_range) for r in self.routes}
        self.capabilities = {(a,r): random.randint(*self.capabilities_range) 
                            for a in self.aircraft for r in self.routes}
        self.costs = {(a,r): random.randint(*self.cost_range) 
                    for a in self.aircraft for r in self.routes}

        # Create Gurobi model
        model = gp.Model("AircraftAssignment")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create integer decision variables
        allocation = model.addVars(self.aircraft, self.routes, vtype=GRB.INTEGER, name="Allocation")

        # Set objective: minimize total cost
        model.setObjective(
            gp.quicksum(self.costs[a,r] * allocation[a,r] 
                        for a in self.aircraft for r in self.routes),
            GRB.MINIMIZE
        )

        # Add availability constraints
        for a in self.aircraft:
            model.addConstr(
                gp.quicksum(allocation[a,r] for r in self.routes) <= self.availability[a],
                name=f"Availability_{a}"
            )

        # Add demand constraints
        for r in self.routes:
            model.addConstr(
                gp.quicksum(allocation[a,r] * self.capabilities[a,r] for a in self.aircraft) >= self.demand[r],
                name=f"Demand_{r}"
            )

        return model
    
    def print_solution(self, model):
        """Print the solution details for the Aircraft Assignment Problem"""
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal total cost: {model.ObjVal:.2f}")
            
            # Get sets from variable names
            aircraft = [f"aircraft_{i}" for i in range(self.n_aircraft)]
            routes = [f"route_{i}" for i in range(self.n_routes)]
            
            # Print allocation details and calculate statistics
            total_aircraft_used = 0
            total_capacity_provided = 0
            
            print("\nDetailed Allocation:")
            print("-" * 60)
            for a in aircraft:
                aircraft_count = 0
                for r in routes:
                    var_name = f"Allocation[{a},{r}]"
                    for v in model.getVars():
                        if v.VarName == var_name and v.X > 0:  # Non-zero allocation
                            allocation = int(v.X)  # Should be integer
                            aircraft_count += allocation
                            capacity = allocation * self.capabilities[a,r]
                            cost = allocation * self.costs[a,r]
                            total_aircraft_used += allocation
                            total_capacity_provided += capacity
                            
                            print(f"{a} -> {r}: "
                                f"Allocated: {allocation} aircraft, "
                                f"Capacity: {capacity}, "
                                f"Cost: {cost:.2f}")
                
                print(f"Total {a} used: {aircraft_count}")
                print("-" * 30)
            
            print("\nSummary Statistics:")
            print("-" * 60)
            print(f"Total Aircraft Used: {total_aircraft_used}")
            print(f"Total Capacity Provided: {total_capacity_provided}")
            print(f"Total Cost: {model.ObjVal:.2f}")
            
            # Check capacity vs demand
            print("\nRoute Demand Satisfaction:")
            print("-" * 60)
            for r in routes:
                total_route_capacity = sum(
                    model.getVarByName(f"Allocation[{a},{r}]").X * self.capabilities[a,r]
                    for a in aircraft
                )
                print(f"{r}: Demand = {self.demand[r]}, "
                    f"Capacity Provided = {total_route_capacity}")
                
        else:
            print("No optimal solution found")
            print(f"Status code: {model.Status}")
        
        # Print model statistics
        print(f"\nModel Statistics:")
        print("-" * 60)
        print(f"Number of variables: {model.NumVars}")
        print(f"Number of constraints: {model.NumConstrs}")
        
        # If model is infeasible, try to compute IIS
        if model.Status == GRB.INFEASIBLE:
            print("\nAnalyzing Infeasibility:")
            print("-" * 60)
            try:
                model.computeIIS()
                print("Infeasible constraints:")
                for c in model.getConstrs():
                    if c.IISConstr:
                        print(f"Constraint {c.ConstrName} is infeasible")
                        
                # Additional analysis for availability constraints
                print("\nAvailability Analysis:")
                for a in aircraft:
                    total_allocated = sum(
                        model.getVarByName(f"Allocation[{a},{r}]").X 
                        for r in routes
                    )
                    print(f"{a}: Available = {self.availability[a]}, "
                        f"Allocated = {total_allocated}")
                    
                # Analysis for demand constraints
                print("\nDemand Analysis:")
                for r in routes:
                    total_capacity = sum(
                        model.getVarByName(f"Allocation[{a},{r}]").X * self.capabilities[a,r]
                        for a in aircraft
                    )
                    print(f"{r}: Required = {self.demand[r]}, "
                        f"Provided = {total_capacity}")
                    
            except:
                print("Could not compute IIS")
                
        # Print computation time if available
        if hasattr(model, "Runtime"):
            print(f"\nSolution time: {model.Runtime:.2f} seconds")

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
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
        
        generator.print_solution(model)

    test_generator()