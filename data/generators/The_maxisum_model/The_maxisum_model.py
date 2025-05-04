import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize the Maxisum Model for Facility Dispersion Problem.

        Parameters:
            parameters (dict): Dictionary containing:
                - n_nodes: Number of nodes (potential facility locations)
                - p_facilities: Number of facilities to be selected
                - distance_range: Tuple of (min, max) for distances between nodes
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "maxisum_facility_dispersion"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are N nodes, and we need to select p facilities such that the sum of distances between all pairs of selected facilities is maximized.

        - **Sets**:
            - N: Set of nodes (potential facility locations)
        - **Parameters**:
            - p: Number of facilities to be selected
            - d_{i,j}: Distance between node i and node j
        - **Variables**:
            - x_i: Binary variable indicating whether node i is selected as a facility
            - z_{i,j}: Binary variable indicating whether both nodes i and j are selected as facilities
        - **Objective**:
            - Maximize the total distance between selected facilities:
                $$\text{Maximize} \quad \sum_{i \in N} \sum_{j \in N} d_{i,j} \cdot z_{i,j}$$
        - **Constraints**:
            1. Select exactly p facilities:
                $$\sum_{i \in N} x_i = p$$
            2. Relationship between z_{i,j} and x_i, x_j:
                $$z_{i,j} \leq x_i \quad \forall i, j \in N$$
                $$z_{i,j} \leq x_j \quad \forall i, j \in N$$
                $$z_{i,j} \geq x_i + x_j - 1 \quad \forall i, j \in N$$
        """
        default_parameters = {
            "n_nodes": (5, 8),  # Range for number of nodes
            "p_facilities": (3, 5),  # Number of facilities to select
            "distance_range": (1, 100)  # Range for distances between nodes
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
        Generate a Maxisum Facility Dispersion problem instance and create its corresponding Gurobi model.

        This method does two things:
        1. Generates random problem data (nodes, distances)
        2. Creates and returns a configured Gurobi model ready to solve

        Returns:
            gp.Model: Configured Gurobi model for the Maxisum Facility Dispersion problem
        """
        # Randomly select number of nodes
        self.n_nodes = random.randint(*self.n_nodes)
        self.p_facilities = random.randint(*self.p_facilities)

        # Generate nodes and distances
        nodes = [f"node_{i}" for i in range(self.n_nodes)]
        distances = {
            (i, j): random.randint(*self.distance_range)
            for i in nodes for j in nodes if i != j
        }

        # Create Gurobi model
        model = gp.Model("Maxisum_Facility_Dispersion")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create binary decision variables
        x = model.addVars(nodes, vtype=GRB.BINARY, name="x")  # x[i] = 1 if node i is selected
        z = model.addVars(distances.keys(), vtype=GRB.BINARY, name="z")  # z[i,j] = 1 if both i and j are selected

        # Set objective: maximize total distance between selected facilities
        model.setObjective(
            gp.quicksum(distances[i, j] * z[i, j] for i, j in distances.keys()),
            GRB.MAXIMIZE
        )

        # Add constraints
        # 1. Select exactly p facilities
        model.addConstr(
            gp.quicksum(x[i] for i in nodes) == self.p_facilities,
            name="Select_p_Facilities"
        )

        # 2. Relationship between z[i,j] and x[i], x[j]
        for i, j in distances.keys():
            model.addConstr(z[i, j] <= x[i], name=f"z_{i}_{j}_leq_x_{i}")
            model.addConstr(z[i, j] <= x[j], name=f"z_{i}_{j}_leq_x_{j}")
            model.addConstr(z[i, j] >= x[i] + x[j] - 1, name=f"z_{i}_{j}_geq_x_{i}_plus_x_{j}_minus_1")

        return model


if __name__ == '__main__':
    import time

    def test_generator():
        generator = Generator()
        model = generator.generate_instance()

        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time

        model.write("maxisum_facility_dispersion.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()