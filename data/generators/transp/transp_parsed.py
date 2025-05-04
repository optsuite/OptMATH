import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Transportation optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_origins: Number of origins
                - n_destinations: Number of destinations
                - supply_range: Tuple of (min, max) for origin supplies
                - demand_range: Tuple of (min, max) for destination demands
                - cost_range: Tuple of (min, max) for transportation costs
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "transportation"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are m origins and n destinations. Each origin i (where i = 1, 2, ..., m) has a supply S_i, and each destination j (where j = 1, 2, ..., n) has a demand D_j. The cost of transporting one unit from origin i to destination j is C_{i,j}.

        Decision Variables:
        - x_{i,j}: Amount of goods transported from origin i to destination j.

        Objective:
        Minimize the total transportation cost:
        $$
        \text{Minimize } \sum_{i=1}^m \sum_{j=1}^n C_{i,j} \cdot x_{i,j}
        $$

        Constraints:
        1. Supply constraints: Total amount shipped from each origin must not exceed its supply.
        $$
        \sum_{j=1}^n x_{i,j} = S_i \quad \forall i = 1, 2, \ldots, m
        $$

        2. Demand constraints: Total amount shipped to each destination must meet its demand.
        $$
        \sum_{i=1}^m x_{i,j} = D_j \quad \forall j = 1, 2, \ldots, n
        $$

        3. Non-negativity constraints:
        $$
        x_{i,j} \geq 0 \quad \forall i = 1, 2, \ldots, m, \forall j = 1, 2, \ldots, n
        $$
        """
        default_parameters = {
            "n_origins": (3, 5),
            "n_destinations": (3, 5),
            "supply_range": (10, 100),
            "demand_range": (10, 100),
            "cost_range": (1, 10)
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
        Generate a Transportation problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (origins, destinations, supplies, demands, costs)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the transportation problem
        """
        
        # Randomly select number of origins and destinations
        self.n_origins = random.randint(*self.n_origins)
        self.n_destinations = random.randint(*self.n_destinations)
        
        # Generate origins and destinations
        origins = [f"origin_{i}" for i in range(self.n_origins)]
        destinations = [f"destination_{j}" for j in range(self.n_destinations)]
        
        # Generate supplies, demands, and costs
        supplies = {origin: random.randint(*self.supply_range) for origin in origins}
        demands = {destination: random.randint(*self.demand_range) for destination in destinations}

        # Balance total supply and total demand (ensures feasibility)
        total_supply = sum(supplies.values())
        total_demand = sum(demands.values())
        if total_supply > total_demand:
            # Reduce supply to match total demand
            diff = total_supply - total_demand
            for origin in supplies:
                if diff <= 0:
                    break
                reduction = min(diff, supplies[origin])
                supplies[origin] -= reduction
                diff -= reduction
        elif total_demand > total_supply:
            # Increase supply to match total demand
            diff = total_demand - total_supply
            for origin in supplies:
                supplies[origin] += diff
                break  # Modify one origin to address the imbalance

        # Match total supply and total demand explicitly
        total_supply = sum(supplies.values())
        total_demand = sum(demands.values())
        assert total_supply == total_demand, "Total supply and demand must be equal"

        costs = {(origin, destination): random.randint(*self.cost_range) for origin in origins for destination in destinations}

        # Create Gurobi model
        model = gp.Model("Transportation")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create continuous decision variables (x[i,j] = amount transported from i to j)
        x = model.addVars(origins, destinations, vtype=GRB.CONTINUOUS, name="Transport")

        # Set objective: minimize total transportation cost
        model.setObjective(
            gp.quicksum(costs[i, j] * x[i, j] for i in origins for j in destinations),
            GRB.MINIMIZE
        )

        # Add supply constraints: total amount shipped from each origin must equal its supply
        for i in origins:
            model.addConstr(
                gp.quicksum(x[i, j] for j in destinations) == supplies[i],
                name=f"Supply_{i}"
            )

        # Add demand constraints: total amount shipped to each destination must equal its demand
        for j in destinations:
            model.addConstr(
                gp.quicksum(x[i, j] for i in origins) == demands[j],
                name=f"Demand_{j}"
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
        
        model.write("transportation.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()