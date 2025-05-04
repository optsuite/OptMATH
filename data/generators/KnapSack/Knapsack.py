
import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Knapsack optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_items: Number of items
                - value_range: Tuple of (min, max) for item values
                - weight_range: Tuple of (min, max) for item weights
                - capacity_ratio: Ratio of capacity to total weight (between 0 and 1)
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "knapsack"
        self.mathematical_formulation = r"""
        ### Mathematical Model\nSuppose there are m items, each item j (where j = 1, 2, ..., m) has the following attributes:\n- **Value** c_j: The value of item j.\n- **Weight** w_j: The weight of item j.\n- **Selection Variable** x_j: A binary variable indicating whether item j is selected.\n- x_j = 1: Item j is selected.\n- x_j = 0: Item j is not selected.\n\nAdditionally, the knapsack has a maximum weight capacity denoted by the constant K.\n$$\n\\begin{aligned}\n&\\text{Maximize} && \\sum_{j=1}^m c_j x_j \\\\\n&\\text{Subject to} && \\sum_{j=1}^m w_j x_j \\leq K \\\\\n& && x_j \\in \\{0, 1\\} \\quad \\forall j = 1, 2, \\ldots, m\n\\end{aligned}\n$$
        """
        default_parameters = {
            "n_items": (3,30),
            "value_range": (10, 300),
            "weight_range": (1, 50),
            "capacity_ratio": 0.7
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
        Generate a Knapsack problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (items, values, weights, capacity)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the knapsack problem
        """
        
        # Randomly select number of items
        self.n_items = random.randint(*self.n_items)
        
        # Generate items and their properties
        items = [f"item_{i}" for i in range(self.n_items)]
        item_values = {item: random.randint(*self.value_range) for item in items}
        item_weights = {item: random.randint(*self.weight_range) for item in items}
        
        # Calculate knapsack capacity as a ratio of total weight
        total_weight = sum(item_weights.values())
        knapsack_capacity = int(total_weight * self.capacity_ratio)

        # Create Gurobi model
        model = gp.Model("Knapsack")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create binary decision variables (x[i] = 1 if item i is selected)
        x = model.addVars(items, vtype=GRB.BINARY, name="Items")

        # Set objective: maximize total value of selected items
        model.setObjective(
            gp.quicksum(item_values[i] * x[i] for i in items),
            GRB.MAXIMIZE
        )

        # Add capacity constraint: total weight must not exceed capacity
        model.addConstr(
            gp.quicksum(item_weights[i] * x[i] for i in items) <= knapsack_capacity,
            name="WeightCapacity"
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
        
        model.write("knapsack.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()