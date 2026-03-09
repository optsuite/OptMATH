import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize the p-dispersion optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_nodes: Number of candidate nodes (locations)
                - p: Number of facilities to select
                - distance_range: Tuple of (min, max) for distances between nodes
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "p_dispersion"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are n nodes, and we want to select p facilities such that the minimum distance between any two selected facilities is maximized.

        - **Sets**:
            - N: Set of nodes (candidate locations)
        
        - **Parameters**:
            - p: Number of facilities to select
            - d_{i,j}: Distance between node i and node j
            - M: A sufficiently large number (big-M)
        
        - **Decision Variables**:
            - x_i: Binary variable, where x_i = 1 if node i is selected, and x_i = 0 otherwise
            - D: Continuous variable representing the minimum distance between any two selected facilities
            - z_{i,j}: Binary variable, where z_{i,j} = 1 if both nodes i and j are selected, and z_{i,j} = 0 otherwise
        
        - **Objective**:
            Maximize D (the minimum distance between any two selected facilities)
        
        - **Constraints**:
            1. Select exactly p facilities: sum_{i in N} x_i = p
            2. Define the minimum distance D: D <= d_{i,j} + M * (1 - z_{i,j}) for all i, j in N
            3. Relationship between z_{i,j} and x_i, x_j:
               - z_{i,j} <= x_i for all i, j in N
               - z_{i,j} <= x_j for all i, j in N
               - z_{i,j} >= x_i + x_j - 1 for all i, j in N
        """
        default_parameters = {
            "n_nodes": (8, 12),  # Range for number of nodes
            "p": (3, 5),             # Number of facilities to select
            "distance_range": (1, 100),  # Range for distances between nodes
            "M": 1e6            # Big-M constant
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
        Generate a p-dispersion problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (nodes, distances)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the p-dispersion problem
        """
        
        # Randomly select number of nodes
        self.n_nodes = random.randint(*self.n_nodes)
        self.p = random.randint(*self.p)

        # Generate nodes and distances between them
        nodes = [f"node_{i}" for i in range(self.n_nodes)]
        distances = {}
        for i in nodes:
            for j in nodes:
                if i != j:
                    distances[(i, j)] = random.randint(*self.distance_range)
                else:
                    distances[(i, j)] = 0  # Distance to itself is 0

        # Create Gurobi model
        model = gp.Model("P_Dispersion")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create binary decision variables (x[i] = 1 if node i is selected)
        x = model.addVars(nodes, vtype=GRB.BINARY, name="Nodes")
        
        # Create continuous variable for the minimum distance
        D = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="MinDistance")
        
        # Create binary variables for pairs of nodes (z[i,j] = 1 if both i and j are selected)
        z = model.addVars(nodes, nodes, vtype=GRB.BINARY, name="PairSelection")

        # Set objective: maximize the minimum distance D
        model.setObjective(D, GRB.MAXIMIZE)

        # Add constraints
        # 1. Select exactly p facilities
        model.addConstr(
            gp.quicksum(x[i] for i in nodes) == self.p,
            name="SelectPFacilities"
        )

        # 2. Define the minimum distance D
        for i in nodes:
            for j in nodes:
                if i != j:
                    model.addConstr(
                        D <= distances[(i, j)] + self.M * (1 - z[(i, j)]),
                        name=f"MinDistance_{i}_{j}"
                    )

        # 3. Relationship between z[i,j] and x[i], x[j]
        for i in nodes:
            for j in nodes:
                if i != j:
                    model.addConstr(z[(i, j)] <= x[i], name=f"Z_leq_X_{i}_{j}")
                    model.addConstr(z[(i, j)] <= x[j], name=f"Z_leq_X_{j}_{i}")
                    model.addConstr(z[(i, j)] >= x[i] + x[j] - 1, name=f"Z_geq_Xsum_{i}_{j}")

        return model


if __name__ == '__main__':
    import time
    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("p_dispersion.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()