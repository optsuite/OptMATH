import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Diet optimization problem.
        Parameters:
            parameters (dict): Dictionary containing:
                - n_nutrients: Number of nutrients
                - n_foods: Number of foods
                - cost_range: Tuple of (min, max) for food costs
                - nutrient_range: Tuple of (min, max) for nutrient values in food
                - nutrient_requirement_range: Tuple of (min, max) for required nutrient range
                - food_amount_range: Tuple of (min, max) for food amounts
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "diet_problem"
        self.mathematical_formulation = r"""
        ### Mathematical Model\nSuppose there are N nutrients and F foods. Each food j (where j ∈ {1, 2, ..., F})
        has the following attributes:\n- **Cost** Cost_{j}: The cost of buying one unit of food j.\n- **Range of Amounts**
        [MinAmount_{j}, MaxAmount_{j}]: The permissible range for buying food j.\n- **Nutrient Contribution** NutrientAmount_{i,j}:
        The amount of nutrient i in one unit of food j.\n\nEach nutrient i (where i ∈ {1, 2, ..., N}) has a required range:
        [MinNutrient_{i}, MaxNutrient_{i}], denoting the permissible amount to consume.\nThe objective is to minimize the
        total cost of food purchased while satisfying all nutrient requirements.\n$$\n\\begin{aligned}\n&\\text{Minimize}
        && \\sum_{j=1}^F \\text{Cost}_j \\cdot \\text{Buy}_j \\\\\n&\\text{Subject to}\n& \\text{For each nutrient i:}\n
        & \\text{MinNutrient}_i \\leq \\sum_{j=1}^F \\text{NutrientAmount}_{i,j} \\cdot \\text{Buy}_j \\leq \\text{MaxNutrient}_i,\\,\,
        \\forall i \\in \\{1, 2, \\ldots, N\\}\\\\\n&\\text{For each food j:}\n& \\text{Buy}_j \\in [\\text{MinAmount}_j, \\text{MaxAmount}_j]
        \\quad \\forall j \\in \\{1, 2, \\ldots, F\\}\n\\end{aligned}\n$$
        """
        
        default_parameters = {
            "n_nutrients": (2, 4),  # Number of nutrients
            "n_foods": (12, 15),  # Number of foods
            "cost_range": (1, 10),  # Cost range for foods
            "nutrient_range": (1, 4),  # Range for nutrient contribution per food
            "nutrient_requirement_range": (3, 15),  # Range for required nutrient intake
            "food_amount_range": (0, 10)  # Range for food purchasing amounts
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
        Generate a Diet problem instance and create its corresponding Gurobi model.
        This method does two things:
        1. Generates random problem data (foods, nutrients, costs, etc.)
        2. Creates and returns a configured Gurobi model ready to solve
        Returns:
            gp.Model: Configured Gurobi model for the diet problem
        """
        # Randomly determine the number of nutrients and foods
        self.n_nutrients = random.randint(*self.n_nutrients)
        self.n_foods = random.randint(*self.n_foods)

        # Generate random data
        nutrients = [f"nutrient_{i}" for i in range(self.n_nutrients)]
        foods = [f"food_{j}" for j in range(self.n_foods)]

        costs = {food: random.randint(*self.cost_range) for food in foods}
        nutrient_amount = {
            (nutrient, food): random.randint(*self.nutrient_range)
            for nutrient in nutrients for food in foods
        }
        min_nutrient = {nutrient: random.randint(*self.nutrient_requirement_range) for nutrient in nutrients}
        max_nutrient = {nutrient: random.randint(min_nutrient[nutrient], min_nutrient[nutrient] + 25) for nutrient in nutrients}
        min_amount = {food: self.food_amount_range[0] for food in foods}
        max_amount = {food: self.food_amount_range[1] for food in foods}

        # Create Gurobi model
        model = gp.Model("DietProblem")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Decision variables: amount of food to buy (continuous variables)
        buy = model.addVars(foods, lb=min_amount, ub=max_amount, vtype=GRB.CONTINUOUS, name="Buy")

        # Objective: Minimize total cost
        model.setObjective(
            gp.quicksum(costs[food] * buy[food] for food in foods),
            GRB.MINIMIZE
        )

        # Add nutrient constraints
        for nutrient in nutrients:
            model.addConstr(
                gp.quicksum(nutrient_amount[(nutrient, food)] * buy[food] for food in foods) >= min_nutrient[nutrient],
                name=f"{nutrient}_min"
            )
            model.addConstr(
                gp.quicksum(nutrient_amount[(nutrient, food)] * buy[food] for food in foods) <= max_nutrient[nutrient],
                name=f"{nutrient}_max"
            )

        return model

if __name__ == '__main__':
    import time

    def test_generator():
        generator = Generator()  # Fixed seed for reproducibility
        model = generator.generate_instance()
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Total Cost: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
    test_generator()