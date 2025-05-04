import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Bin Packing optimization problem.
        Parameters:
            parameters (dict): Dictionary containing:
                - n_items: Number of items (tuple of min, max)
                - weight_range: Tuple of (min, max) for item weights
                - bin_capacity: Capacity of each bin
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "binpacking"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Consider n items, where each item i has:
        - **Weight** s_i: The weight of item i
        - **Bin Capacity** c: The uniform capacity of each bin
        - **Bin Usage Variable** y_j: A binary variable indicating whether bin j is used
        - **Assignment Variable** x_{i,j}: A binary variable indicating whether item i is assigned to bin j

        $$
        \begin{aligned}
        &\text{Minimize} && \sum_{j=1}^n y_j \\
        &\text{Subject to} && \sum_{i=1}^n s_i x_{i,j} \leq c y_j && \forall j = 1,\ldots,n \\
        & && \sum_{j=1}^n x_{i,j} = 1 && \forall i = 1,\ldots,n \\
        & && x_{i,j}, y_j \in \{0,1\} && \forall i,j = 1,\ldots,n
        \end{aligned}
        $$
        """
        
        default_parameters = {
            "n_items": (3, 10),
            "weight_range": (1, 50),
            "bin_capacity": 100
        }
        
        # Use default parameters if none are provided
        if parameters is None or not parameters:
            parameters = default_parameters
        for key, value in parameters.items():
            setattr(self, key, value)
            
        self.seed = seed
        if self.seed is not None:
            random.seed(seed)
            
    def generate_instance(self):
        """
        Generate a Bin Packing problem instance and create its corresponding Gurobi model.
        
        Returns:
            gp.Model: Configured Gurobi model for the bin packing problem
        """
        # Randomly select number of items
        self.n_items = random.randint(*self.n_items)
        
        # Generate items and their weights
        items = list(range(self.n_items))
        item_weights = {i: random.randint(*self.weight_range) for i in items}
        
        # Create Gurobi model
        model = gp.Model("BinPacking")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create binary decision variables
        # x[i,j] = 1 if item i is assigned to bin j
        x = model.addVars(items, items, vtype=GRB.BINARY, name="x")
        # y[j] = 1 if bin j is used
        y = model.addVars(items, vtype=GRB.BINARY, name="y")
        
        # Set objective: minimize number of bins used
        model.setObjective(gp.quicksum(y[j] for j in items), GRB.MINIMIZE)
        
        # Add capacity constraints
        for j in items:
            model.addConstr(
                gp.quicksum(item_weights[i] * x[i,j] for i in items) <= 
                self.bin_capacity * y[j],
                name=f"Capacity_{j}"
            )
        
        # Add assignment constraints: each item must be assigned to exactly one bin
        for i in items:
            model.addConstr(
                gp.quicksum(x[i,j] for j in items) == 1,
                name=f"Assignment_{i}"
            )
            
        # Store problem data
        model._items = items
        model._weights = item_weights
        model._bin_capacity = self.bin_capacity
        
        return model

if __name__ == '__main__':
    import time
    
    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("binpacking.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal number of bins: {model.ObjVal:.0f}")
        else:
            print("No optimal solution found")
            
    test_generator()