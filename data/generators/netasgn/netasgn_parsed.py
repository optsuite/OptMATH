import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Project Assignment optimization problem.

        Parameters:
            parameters (dict): Dictionary containing:
                - n_people: Number of people
                - n_projects: Number of projects
                - supply_range: Tuple of (min, max) for available hours per person
                - demand_range: Tuple of (min, max) for required hours per project
                - cost_range: Tuple of (min, max) for cost per hour
                - limit_range: Tuple of (min, max) for person's max contribution to a project
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "project_assignment"
        self.mathematical_formulation = r"""
        ### Mathematical Model\nSuppose there are `n` people and `m` projects, where:\n- Each person `i` has:\n   - **Supply_{i}**: Available working hours.\n   - **Cost_{i,j}**: Cost of working on project `j`.\n- Each project `j` has:\n   - **Demand_{j}**: Required working hours.\n   - **Limit_{i,j}**: Max contribution of person `i` to project `j`.\n\n**Decision Variable**:\n- **Assign_{i, j}**: Hours assigned from person `i` to project `j`.\n\n##### Objective Function (Minimize total cost):\n$$\n\\text{Minimize} \\quad \\sum_{i,j} Cost_{i,j} \\cdot Assign_{i,j}\n$$\n\n##### Subject to constraints:\n1. Supply constraint:\n$$\\sum_{j} Assign_{i,j} = Supply_{i}, \\quad \\forall i$$\n2. Demand constraint:\n$$\\sum_{i} Assign_{i,j} = Demand_{j}, \\quad \\forall j$$\n3. Capacity constraint:\n$$Assign_{i,j} \\leq Limit_{i,j}, \\quad \\forall i,j$$
        """
        default_parameters = {
            "n_people": (5, 10),
            "n_projects": (5, 10),
            "supply_range": (5, 15),
            "demand_range": (5, 15),
            "cost_range": (10, 50),
            "limit_range": (3, 10),
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
        Generate a Project Assignment problem instance and create its corresponding Gurobi model.

        This method does two things:
        1. Generates random problem data (people, projects, costs, supplies, demands, limits)
        2. Creates and returns a configured Gurobi model ready to solve

        Returns:
            gp.Model: Configured Gurobi model for the project assignment problem
        """
        
        # Randomly select number of people and projects
        self.n_people = random.randint(*self.n_people)
        self.n_projects = random.randint(*self.n_projects)
        
        # Define sets for people and projects
        people = [f"person_{i}" for i in range(self.n_people)]
        projects = [f"project_{j}" for j in range(self.n_projects)]
        
        # Generate random parameters
        supply = {p: random.randint(*self.supply_range) for p in people}  # Available hours
        demand = {p: random.randint(*self.demand_range) for p in projects}  # Required hours
        cost = {(i, j): random.randint(*self.cost_range) for i in people for j in projects}  # Cost per hour
        limit = {(i, j): random.randint(*self.limit_range) for i in people for j in projects}  # Max contribution limit
        
        # Adjust supply and demand to ensure feasibility
        total_supply = sum(supply.values())
        total_demand = sum(demand.values())
        
        if total_supply > total_demand:
            # Reduce supply to match demand
            diff = total_supply - total_demand
            for person in supply:
                if diff <= 0:
                    break
                reduction = min(diff, supply[person])
                supply[person] -= reduction
                diff -= reduction
        elif total_demand > total_supply:
            # Reduce demand to match supply
            diff = total_demand - total_supply
            for project in demand:
                if diff <= 0:
                    break
                reduction = min(diff, demand[project])
                demand[project] -= reduction
                diff -= reduction
        
        # Ensure total supply equals total demand
        assert sum(supply.values()) == sum(demand.values()), "Total supply and demand must be equal"
        
        # Create Gurobi model
        model = gp.Model("ProjectAssignment")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create decision variables (Assign_{i,j} = hours assigned)
        assign = model.addVars(people, projects, vtype=GRB.CONTINUOUS, name="Assign")
        
        # Set objective: Minimize total cost of assignment
        model.setObjective(
            gp.quicksum(cost[i, j] * assign[i, j] for i in people for j in projects),
            GRB.MINIMIZE
        )
        
        # Add supply constraints: Total assigned hours from each person ≤ their supply
        model.addConstrs(
            (gp.quicksum(assign[i, j] for j in projects) == supply[i] for i in people),
            name="SupplyConstraint"
        )
        
        # Add demand constraints: Total assigned hours to each project ≥ the demand
        model.addConstrs(
            (gp.quicksum(assign[i, j] for i in people) == demand[j] for j in projects),
            name="DemandConstraint"
        )
        
        # Add capacity constraints: Assigned hours cannot exceed limit for person-project pair
        model.addConstrs(
            (assign[i, j] <= limit[i, j] for i in people for j in projects),
            name="CapacityConstraint"
        )
        
        return model


if __name__ == '__main__':
    import time
    
    def test_generator():
        generator = Generator()  # Fix seed for reproducibility
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("project_assignment.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()