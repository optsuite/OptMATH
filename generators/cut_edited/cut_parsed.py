import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Cutting Stock optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_widths: Number of widths to be cut
                - roll_width: Width of the raw rolls
                - orders_range: Tuple of (min, max) for number of orders per width
                - num_patterns: Number of cutting patterns
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "cutting_stock"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are:
        - A set of widths `Width` to be cut.
        - A set of patterns `Patterns`.
        - Each pattern `j` has a certain number of rolls of each width `i` (`NumRollsWidth_{i,j}`).
        - Each width `i` has a certain number of orders (`Orders_i`).
        - The raw roll has a fixed width `RollWidth`.
        Decision Variables:
        - `Cut_j`: Number of rolls cut using pattern `j`.
        Objective:
        - Minimize the total number of raw rolls cut:
        $$\text{Minimize} \quad \sum_{j \in \text{Patterns}} \text{Cut}_j$$
        Constraints:
        1. For each width `i`, the total number of rolls cut must meet the orders:
        $$\sum_{j \in \text{Patterns}} \text{NumRollsWidth}_{i,j} \cdot \text{Cut}_j \geq \text{Orders}_i \quad \forall i \in \text{Width}$$
        2. For each pattern `j`, the total width of rolls must not exceed the raw roll width:
        $$\sum_{i \in \text{Width}} i \cdot \text{NumRollsWidth}_{i,j} \leq \text{RollWidth} \quad \forall j \in \text{Patterns}$$
        """
        default_parameters = {
            "n_widths": (3, 5),
            "roll_width": (50, 120),
            "orders_range": (10, 50),
            "num_patterns": (10, 20),
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
        Generate a Cutting Stock problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (widths, orders, patterns, and rolls per pattern)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the Cutting Stock problem
        """
        
        # Generate widths as numbers (integers)
        self.n_widths = random.randint(*self.n_widths)  
        self.roll_width = random.randint(*self.roll_width)
        self.num_patterns = random.randint(*self.num_patterns)
        
        widths = list(range(1, self.n_widths + 1))  # Widths are now integers [1, 2, ..., n_widths]
        orders = {width: random.randint(*self.orders_range) for width in widths}
        
        # Generate patterns and their rolls per width
        patterns = [f"pattern_{j}" for j in range(self.num_patterns)]
        num_rolls_width = {
            (width, pattern): random.randint(0, 5)  # Randomly assign rolls per width in each pattern
            for width in widths
            for pattern in patterns
        }
        
        # Create Gurobi model
        model = gp.Model("CuttingStock")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create decision variables (Cut_j = number of rolls cut using pattern j)
        cut = model.addVars(patterns, vtype=GRB.INTEGER, name="Cut")
        
        # Set objective: minimize total number of raw rolls cut
        model.setObjective(
            gp.quicksum(cut[j] for j in patterns),
            GRB.MINIMIZE
        )
        
        # Add constraints:
        # 1. For each width, the total number of rolls cut must meet the orders
        for width in widths:
            model.addConstr(
                gp.quicksum(num_rolls_width[width, j] * cut[j] for j in patterns) >= orders[width],
                name=f"Fill_{width}"
            )
        
        # 2. For each pattern, the total width of rolls must not exceed the raw roll width
        for pattern in patterns:
            model.addConstr(
                gp.quicksum(width * num_rolls_width[width, pattern] for width in widths) <= self.roll_width,
                name=f"Check_{pattern}"
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
        
        model.write("cutting_stock.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
    test_generator()