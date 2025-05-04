import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Fleet Routing Problem optimization.
        Parameters:
            parameters (dict): Dictionary containing problem setup details:
                - n_locations: Number of locations/cities
                - n_planes: Number of plane types
                - time_periods: Total time periods
                - max_passengers: Max number of passengers per flight
                - capacity_range: Range for plane capacity
                - cost_range: Range for plane costs
                - max_available_planes: Max number of available planes per type
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "fleet_routing"
        default_parameters = {
            "n_locations": (3, 5),
            "n_planes": (10, 15),
            "time_periods": (3, 5),
            "max_passengers": 100, 
            "capacity_range": (100, 160),
            "cost_range": (5, 20),
            "max_available_planes": 5
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
        Generate a Fleet Routing Problem instance and create its corresponding Gurobi model.
        Returns:
            gp.Model: Configured Gurobi model for the fleet routing problem
        """
        # Randomly set number of locations, planes, and periods
        self.n_locations = random.randint(*self.n_locations)
        self.n_planes = random.randint(*self.n_planes)
        self.time_periods = random.randint(*self.time_periods)
        
        locations = [f"location_{i}" for i in range(self.n_locations)]
        planes = [f"plane_{i}" for i in range(self.n_planes)]
        periods = [t for t in range(1, self.time_periods + 1)]
        
        # Generate random data for problem parameters
        capacity = {v: random.randint(*self.capacity_range) for v in planes}
        cost = {v: random.randint(*self.cost_range) for v in planes}
        available_planes = {v: self.max_available_planes for v in planes}
        delta = {(i, t, j, h): random.choice([0, 1]) for i in locations for t in periods
                 for j in locations for h in periods if i != j}
        passengers = {(i, t, j, h): random.randint(1, self.max_passengers) if delta[i, t, j, h] else 0 
                      for i, t, j, h in delta}
        
        # Create Gurobi model
        model = gp.Model("FleetRouting")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Decision variables
        num_planes = model.addVars(planes, locations, periods, locations, periods, vtype=GRB.INTEGER, 
                                   name="NumPlanes")
        num_idle_planes = model.addVars(planes, locations, periods, vtype=GRB.INTEGER, name="NumIdlePlanes")
        num_idle_planes_init = model.addVars(planes, locations, vtype=GRB.INTEGER, name="NumIdlePlanesInit")
        
        # Objective function: minimize total cost
        model.setObjective(
            gp.quicksum(cost[v] * num_planes[v, i, t, j, h] 
                        for v in planes for i in locations for t in periods
                        for j in locations for h in periods if (i, t, j, h) in delta),
            GRB.MINIMIZE
        )
        
        # Constraints
        # Flow balance constraints
        for v in planes:
            for i in locations:
                # Initial flow balance
                model.addConstr(
                    num_idle_planes_init[v, i] ==
                    num_idle_planes[v, i, 1] + gp.quicksum(
                        num_planes[v, i, 1, j, h] for j in locations for h in periods if i != j
                    ),
                    name=f"FlowBalanceInit_{v}_{i}"
                )
                for t in periods[1:]:
                    model.addConstr(
                        num_idle_planes[v, i, t] ==
                        num_idle_planes[v, i, t - 1] + gp.quicksum(
                            num_planes[v, j, p, i, t] for j in locations for p in periods if j != i
                        ) - gp.quicksum(
                            num_planes[v, i, t, j, h] for j in locations for h in periods if i != j
                        ),
                        name=f"FlowBalance_{v}_{i}_{t}"
                    )
        
        # Plane availability constraints
        for v in planes:
            model.addConstr(
                gp.quicksum(num_idle_planes_init[v, i] for i in locations) <= available_planes[v],
                name=f"PlanesAvailability_{v}"
            )
        
        # Demand satisfaction constraints
        for i in locations:
            for t in periods:
                for j in locations:
                    for h in periods:
                        if (i, t, j, h) in delta and delta[i, t, j, h] == 1:
                            model.addConstr(
                                gp.quicksum(capacity[v] * num_planes[v, i, t, j, h] for v in planes) >= 
                                passengers[i, t, j, h],
                                name=f"DemandSatisfaction_{i}_{t}_{j}_{h}"
                            )
        
        # Route restriction constraints
        for v in planes:
            for i in locations:
                for t in periods:
                    for j in locations:
                        for h in periods:
                            if (i, t, j, h) in delta:
                                model.addConstr(
                                    num_planes[v, i, t, j, h] <= available_planes[v] * delta[i, t, j, h],
                                    name=f"RouteRestriction_{v}_{i}_{t}_{j}_{h}"
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
        model.write("fleet_routing.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
    test_generator()