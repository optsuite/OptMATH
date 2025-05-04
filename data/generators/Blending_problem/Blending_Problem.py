import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Blending optimization problem.

        Parameters:
            parameters (dict): Dictionary containing:
                - n_alloys: Number of alloys
                - n_elements: Number of elements
                - percentage_range: Tuple of (min, max) for element percentages in alloys
                - cost_range: Tuple of (min, max) for alloy costs
                - desired_percentages: List of desired percentages for each element
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "blending"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose we have:
        - Set of alloys A = {1, 2, ..., n}
        - Set of elements E = {1, 2, ..., m}
        - p_{ea}: Percentage of element e in alloy a
        - d_e: Desired percentage of element e in final blend
        - c_a: Cost per unit of alloy a
        - x_a: Amount of alloy a to purchase

        The goal is to determine the amount of each alloy to purchase such that the final blend meets the desired percentages of each element while minimizing the total cost.

        $$
        \begin{aligned}
        &\text{Minimize} && \sum_{a \in A} c_a x_a \\\\
        &\text{Subject to} && \sum_{a \in A} p_{ea} x_a = d_e \quad \forall e \in E \\\\
        & && \sum_{a \in A} x_a = 1 \\\\
        & && x_a \geq 0 \quad \forall a \in A
        \end{aligned}
        $$
        """
        default_parameters = {
            "n_alloys": (8, 8),  # Number of alloys (fixed to 3 for simplicity)
            "n_elements": (3, 3),  # Number of elements (fixed to 3 for simplicity)
            "percentage_range": (0.35, 0.65),  # Range of element percentages in alloys
            "cost_range": (100, 1000),  # Range of alloy costs
            "desired_percentages": [],  # Desired percentages for each element
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
        Generate a Blending problem instance and create its corresponding Gurobi model.

        This method does two things:
        1. Generates random problem data (alloys, element percentages, costs, desired percentages)
        2. Creates and returns a configured Gurobi model ready to solve

        Returns:
            gp.Model: Configured Gurobi model for the blending problem
        """
        # Randomly select number of alloys and elements
        self.n_alloys = random.randint(*self.n_alloys)
        self.n_elements = random.randint(*self.n_elements)

        # Generate alloys and elements
        alloys = [f"alloy_{i}" for i in range(self.n_alloys)]
        elements = [f"element_{i}" for i in range(self.n_elements)]

        # Generate random percentages for each element in each alloy
        percentages = {
            (e, a): random.uniform(*self.percentage_range)
            for e in elements
            for a in alloys
        }

        # Generate random costs for each alloy
        costs = {a: random.randint(*self.cost_range) for a in alloys}
        # Calculate the min and max percentage for each element across all alloys
        element_percentage_ranges = {
            e: (
                min(percentages[e, a] for a in alloys),  # Minimum percentage of element e
                max(percentages[e, a] for a in alloys)   # Maximum percentage of element e
            )
            for e in elements
        }
        # Desired percentages for each element (fixed or random)
        desired_percentages = {
            e: self.desired_percentages[i] if i < len(self.desired_percentages) else random.uniform(*element_percentage_ranges[e])
            for i, e in enumerate(elements)
        }

        # Create Gurobi model
        model = gp.Model("Blending")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create decision variables (x[a] = amount of alloy a to purchase)
        x = model.addVars(alloys, lb=0, name="Alloys")

        # Set objective: minimize total cost
        model.setObjective(
            gp.quicksum(costs[a] * x[a] for a in alloys),
            GRB.MINIMIZE
        )

        # Add constraints for desired percentages of each element
        for e in elements:
            model.addConstr(
                gp.quicksum(percentages[e, a] * x[a] for a in alloys) == desired_percentages[e],
                name=f"Element_{e}"
            )

        # Add constraint: total amount of alloys must sum to 1
        model.addConstr(
            gp.quicksum(x[a] for a in alloys) == 1,
            name="TotalAlloys"
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

        model.write("blending.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Cost: {model.ObjVal:.2f}")
            for var in model.getVars():
                print(f"{var.VarName}: {var.X:.4f}")
        else:
            print("No optimal solution found")

    test_generator()