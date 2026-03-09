import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Scooter Location optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_demand_points: Number of demand points (tuple of min, max)
                - n_candidate_locations: Number of candidate locations (tuple of min, max)
                - demand_range: Tuple of (min, max) for demand at each demand point
                - distance_range: Tuple of (min, max) for distance between demand points and candidate locations
                - num_available_scooters: Number of scooters already available (tuple of min, max)
                - max_selected_locations: Maximum number of selected locations (tuple of min, max)
                - new_max: Maximum number of new scooters that can be added (tuple of min, max)
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "scooter_location"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are:
        - Demand points: i ∈ DemandPoints
        - Candidate locations: j ∈ CandidateLocations
        - Estimated demand: EstimatedDemand_i
        - Distance: Distance_{i,j}
        - Number of available scooters: NumAvailableScooters
        - Maximum number of selected locations: MaxSelectedLocations
        - Maximum number of new scooters: NewMax
        Decision Variables:
        - SelectedLocation_j: Binary variable, 1 if candidate location j is selected; 0 otherwise
        - Assign_{i,j}: Binary variable, 1 if demand point i is assigned to candidate location j; 0 otherwise
        - NewScooters: Integer variable representing the number of new scooters to be added
        Objective:
        Minimize the total user travel distance:
        $$
        \text{Minimize} \quad \sum_{i \in \text{DemandPoints}} \sum_{j \in \text{CandidateLocations}} \text{EstimatedDemand}_i \times \text{Distance}_{i,j} \times \text{Assign}_{i,j}
        $$
        Constraints:
        1. Assign_{i,j} ≤ SelectedLocation_j ∀ i ∈ DemandPoints, j ∈ CandidateLocations
        2. \sum_{j \in \text{CandidateLocations}} Assign_{i,j} ≤ 1 ∀ i ∈ DemandPoints
        3. \sum_{i \in \text{DemandPoints}} \sum_{j \in \text{CandidateLocations}} \text{EstimatedDemand}_i \times \text{Assign}_{i,j} = \text{NewScooters} + \text{NumAvailableScooters}
        4. \sum_{j \in \text{CandidateLocations}} \text{SelectedLocation}_j ≤ \text{MaxSelectedLocations}
        5. \text{NewScooters} ≤ \text{NewMax}
        """
        # Default parameters with adjusted ranges
        default_parameters = {
            "n_demand_points": (8, 10),                
            "n_candidate_locations": (5, 8),          
            "demand_range": (10, 100),             
            "distance_range": (1, 20),                
            "num_available_scooters": (10, 200),     
            "max_selected_locations": (2, 10),        
            "new_max": (10, 100)                     
        }
        
        # Use provided parameters if they exist, otherwise fallback to defaults
        if parameters is None or not parameters:
            parameters = default_parameters
        
        for key, value in parameters.items():
            setattr(self, key, value)
        
        self.seed = seed
        if self.seed is not None:
            random.seed(seed)

    def generate_instance(self):
        """
        Generate a Scooter Location problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (demand points, candidate locations, distances, etc.)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the scooter location problem
        """
        # 1. Randomly determine parameters within ranges
        self.n_demand_points = random.randint(*self.n_demand_points)
        self.n_candidate_locations = random.randint(*self.n_candidate_locations)
        self.num_available_scooters = random.randint(*self.num_available_scooters)
        self.max_selected_locations = random.randint(*self.max_selected_locations)
        self.new_max = random.randint(*self.new_max)

        # 2. Generate data for demand points and candidate locations
        demand_points = [f"demand_{i}" for i in range(self.n_demand_points)]
        candidate_locations = [f"location_{j}" for j in range(self.n_candidate_locations)]
        
        estimated_demand = {i: random.randint(*self.demand_range) for i in demand_points}
        distance = {(i, j): random.randint(*self.distance_range) for i in demand_points for j in candidate_locations}
        
        # 3. Create Gurobi model
        model = gp.Model("ScooterLocation")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create variables
        selected_location = model.addVars(candidate_locations, vtype=GRB.BINARY, name="SelectedLocation")
        assign = model.addVars(demand_points, candidate_locations, vtype=GRB.BINARY, name="Assign")
        new_scooters = model.addVar(vtype=GRB.INTEGER, name="NewScooters")
        
        # Set objective to minimize total user travel distance
        model.setObjective(
            gp.quicksum(estimated_demand[i] * distance[i, j] * assign[i, j] 
                        for i in demand_points for j in candidate_locations),
            GRB.MINIMIZE
        )
        
        # Add constraints
        model.addConstrs(
            (assign[i, j] <= selected_location[j] for i in demand_points for j in candidate_locations),
            name="AssignConstraint1"
        )
        model.addConstrs(
            (gp.quicksum(assign[i, j] for j in candidate_locations) <= 1 for i in demand_points),
            name="AssignConstraint2"
        )
        model.addConstr(
            gp.quicksum(estimated_demand[i] * assign[i, j] for i in demand_points for j in candidate_locations) 
            == self.num_available_scooters + new_scooters,
            name="DemandCover"
        )
        model.addConstr(
            gp.quicksum(selected_location[j] for j in candidate_locations) <= self.max_selected_locations,
            name="LimitLocation"
        )
        model.addConstr(
            new_scooters <= self.new_max,
            name="UpperBoundNew"
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
        
        print(f"\nTest with adjusted parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
            print(generator.n_demand_points, generator.n_candidate_locations)

    test_generator()