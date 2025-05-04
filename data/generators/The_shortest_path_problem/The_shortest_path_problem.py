import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize the Shortest Path Problem.

        Parameters:
            parameters (dict): Dictionary containing:
                - n_nodes: Number of nodes in the graph
                - arc_cost_range: Tuple of (min, max) for arc costs
                - start_node: Starting node (default is 0)
                - end_node: Ending node (default is n_nodes - 1)
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "shortest_path"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there is a graph with nodes N and arcs E. Each arc (i,j) has a cost a_{i,j}.
        The goal is to find the path from a start node to an end node with the minimum total cost.

        Variables:
        - x_{i,j}: Binary variable indicating whether arc (i,j) is in the path.

        Objective:
        Minimize the total cost of the path:
        $$
        \text{Minimize} \quad \sum_{(i,j) \in E} a_{i,j} \cdot x_{i,j}
        $$

        Constraints:
        - Flow balance at each node:
        $$
        \sum_{j \in N \mid (i,j) \in E} x_{i,j} - \sum_{k \in N \mid (k,i) \in E} x_{k,i} = b_i \quad \forall i \in N
        $$
        where:
        - b_i = 1 if i is the start node,
        - b_i = -1 if i is the end node,
        - b_i = 0 otherwise.
        """
        default_parameters = {
            "n_nodes": (5, 8),
            "arc_cost_range": (1, 10),
            "start_node": 0,
            "end_node": None
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
        Generate a Shortest Path Problem instance and create its corresponding Gurobi model.

        This method does two things:
        1. Generates random problem data (nodes, arcs, costs)
        2. Creates and returns a configured Gurobi model ready to solve

        Returns:
            gp.Model: Configured Gurobi model for the shortest path problem
        """
        # Randomly select number of nodes
        self.n_nodes = random.randint(*self.n_nodes)
        
        # Generate nodes
        nodes = [f"node_{i}" for i in range(self.n_nodes)]
        
        # Generate arcs (fully connected graph for simplicity)
        arcs = [(i, j) for i in nodes for j in nodes if i != j]
        
        # Generate random arc costs
        arc_costs = {(i, j): random.randint(*self.arc_cost_range) for (i, j) in arcs}
        
        # Set start and end nodes
        if self.end_node is None:
            self.end_node = self.n_nodes - 1
        start_node = nodes[self.start_node]
        end_node = nodes[self.end_node]
        
        # Create Gurobi model
        model = gp.Model("ShortestPath")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create binary decision variables (x[i,j] = 1 if arc (i,j) is in the path)
        x = model.addVars(arcs, vtype=GRB.BINARY, name="Arcs")

        # Set objective: minimize total cost of the path
        model.setObjective(
            gp.quicksum(arc_costs[i, j] * x[i, j] for (i, j) in arcs),
            GRB.MINIMIZE
        )

        # Add flow balance constraints
        for i in nodes:
            if i == start_node:
                b_i = 1
            elif i == end_node:
                b_i = -1
            else:
                b_i = 0
            model.addConstr(
                gp.quicksum(x[i, j] for j in nodes if (i, j) in arcs) -
                gp.quicksum(x[k, i] for k in nodes if (k, i) in arcs) == b_i,
                name=f"FlowBalance_{i}"
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
        
        model.write("shortest_path.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()