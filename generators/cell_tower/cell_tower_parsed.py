import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize the Cell Tower optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_towers: Number of potential tower sites
                - n_regions: Number of regions to cover
                - cost_range: Tuple of (min, max) for tower setup costs
                - population_range: Tuple of (min, max) for region populations
                - budget_ratio: Ratio of budget to total cost (between 0 and 1)
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "cell_tower"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are:
        - `n_towers` potential tower sites.
        - `n_regions` regions to cover.
        - Each tower site `i` has a setup cost `Cost_i`.
        - Each region `j` has a population `Population_j`.
        - A binary parameter `Delta_{i,j}` indicates whether tower `i` covers region `j`.
        - A budget `Budget` is available for building towers.

        Decision Variables:
        - `Build_i`: Binary variable indicating whether tower `i` is built.
        - `Covered_j`: Binary variable indicating whether region `j` is covered.

        Objective:
        - Maximize the total population covered:
          $$\text{Maximize} \quad \sum_{j=1}^{n\_regions} \text{Population}_j \times \text{Covered}_j$$

        Constraints:
        - Coverage constraint: For each region `j`, at least one tower covering it must be built:
          $$\sum_{i=1}^{n\_towers} \text{Delta}_{i,j} \times \text{Build}_i \geq \text{Covered}_j \quad \forall j$$
        - Budget constraint: Total cost of building towers must not exceed the budget:
          $$\sum_{i=1}^{n\_towers} \text{Cost}_i \times \text{Build}_i \leq \text{Budget}$$
        """
        default_parameters = {
            "n_towers": (3, 5),
            "n_regions": (5, 8),
            "cost_range": (10, 100),
            "population_range": (100, 1000),
            "budget_ratio": 0.7
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
        Generate a Cell Tower problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (towers, regions, costs, populations, coverage)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the cell tower problem
        """
        
        # Randomly select number of towers and regions
        self.n_towers = random.randint(*self.n_towers)
        self.n_regions = random.randint(*self.n_regions)
        
        # Generate tower sites and regions
        towers = [f"tower_{i}" for i in range(self.n_towers)]
        regions = [f"region_{j}" for j in range(self.n_regions)]
        
        # Generate random costs for towers
        tower_costs = {tower: random.randint(*self.cost_range) for tower in towers}
        
        # Generate random populations for regions
        region_populations = {region: random.randint(*self.population_range) for region in regions}
        
        # Generate random coverage matrix (Delta_{i,j})
        coverage = {
            (tower, region): random.randint(0, 1) for tower in towers for region in regions
        }
        
        # Calculate budget as a ratio of total cost
        total_cost = sum(tower_costs.values())
        budget = int(total_cost * self.budget_ratio)

        # Create Gurobi model
        model = gp.Model("CellTower")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create binary decision variables
        build = model.addVars(towers, vtype=GRB.BINARY, name="Build")
        covered = model.addVars(regions, vtype=GRB.BINARY, name="Covered")

        # Set objective: maximize total population covered
        model.setObjective(
            gp.quicksum(region_populations[region] * covered[region] for region in regions),
            GRB.MAXIMIZE
        )

        # Add coverage constraints
        for region in regions:
            model.addConstr(
                gp.quicksum(coverage[tower, region] * build[tower] for tower in towers) >= covered[region],
                name=f"Coverage_{region}"
            )

        # Add budget constraint
        model.addConstr(
            gp.quicksum(tower_costs[tower] * build[tower] for tower in towers) <= budget,
            name="Budget"
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
        
        model.write("cell_tower.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()