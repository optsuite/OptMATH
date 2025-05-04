import gurobipy as gp
from gurobipy import GRB
import random
import json

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Set Covering optimization problem.
        Parameters:
            parameters (dict): Dictionary containing:
                - n_sets: Number of sets
                - n_elements: Number of elements
                - density: Density of set-element associations (between 0 and 1)
                - cost_range: Tuple of (min, max) for set costs
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "set_covering"
        self.mathematical_formulation = r"""
        \begin{align*}
        \min & \sum_{i=1}^{n} c_i x_i \\
        \text{s.t.} & \sum_{i \in I_j} x_i \geq 1 \quad \forall j \in M \\
        & x_i \in \{0,1\} \quad \forall i \in N
        \end{align*}
        """
        
        default_parameters = {
            "n_sets": (5, 20),
            "n_elements": (10, 30),
            "density": 0.4,
            "cost_range": (1, 100)
        }
        
        # Use default parameters if none are provided
        if parameters is None or not parameters:
            parameters = default_parameters
            
        # Set attributes from parameters
        for key, value in parameters.items():
            setattr(self, key, value)
            
        self.seed = seed
        if self.seed is not None:
            random.seed(seed)

    def generate_instance(self):
        """
        Generate a Set Covering problem instance and create its corresponding Gurobi model.
        Returns:
            gp.Model: Configured Gurobi model for the set covering problem
        """
        
        # Randomly select number of sets
        self.n_sets = random.randint(*self.n_sets)
        
        # Randomly select number of elements
        self.n_elements = random.randint(*self.n_elements)
        
        # Generate universe of elements
        elements = [f"e{j}" for j in range(1, self.n_elements + 1)]
        
        # Generate set-element associations
        total_associations = self.n_sets * self.n_elements
        num_associations = int(self.density * total_associations)
        associations = set()
        
        while len(associations) < num_associations:
            i = random.randint(1, self.n_sets)
            j = random.randint(1, self.n_elements)
            associations.add((i, j))
            
        # Construct sets
        sets = {i: set() for i in range(1, self.n_sets + 1)}
        for (i, j) in associations:
            sets[i].add(f"e{j}")
            
        # Generate costs
        costs = {i: random.randint(*self.cost_range) 
                for i in range(1, self.n_sets + 1)}
        
        # Ensure feasibility
        for e in elements:
            if not any(e in sets[i] for i in sets):
                random_set = random.choice(list(sets.keys()))
                sets[random_set].add(e)
        
        # Create Gurobi model
        model = gp.Model("SetCovering")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create binary decision variables
        x = model.addVars(sets.keys(), vtype=GRB.BINARY, name="Selected")
        
        # Set objective: minimize total cost
        model.setObjective(
            gp.quicksum(costs[i] * x[i] for i in sets.keys()),
            GRB.MINIMIZE
        )
        
        # Add coverage constraints
        for e in elements:
            model.addConstr(
                gp.quicksum(x[i] for i in sets.keys() if e in sets[i]) >= 1,
                f"Cover_{e}"
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
        
        model.write("set_covering.lp")
        
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
    
    test_generator()