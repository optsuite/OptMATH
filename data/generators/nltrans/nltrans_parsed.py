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
                - supply_range: Tuple of (min, max) for supply amounts of origins
                - demand_range: Tuple of (min, max) for demand amounts of destinations
                - rate_range: Tuple of (min, max) for shipment rates (costs)
                - limit_range: Tuple of (min, max) for shipment limits
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "transportation"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Given:
        - Origins `i ∈ Origins` with supply capacities `Supply_i`
        - Destinations `j ∈ Destinations` with demand requirements `Demand_j`
        - Shipping rates (cost per unit) `Rate_{i,j}` between origins `i` and destinations `j`
        - Limit constraints `Limit_{i,j}` for the amount shipped
        
        Variables:
        - `Shipping_{i,j}`: Amount to be shipped from origin `i` to destination `j`
        
        Objective:
        Minimize the total transportation cost:
        $$\min \sum_{i \in Origins} \sum_{j \in Destinations} Rate_{i,j} \cdot Shipping_{i,j}$$

        Subject to:
        - Supply constraint: $ \sum_{j \in Destinations} Shipping_{i,j} = Supply_{i} $
        - Demand constraint: $ \sum_{i \in Origins} Shipping_{i,j} = Demand_{j} $
        - Shipping limits: $ Shipping_{i,j} \leq Limit_{i,j} $
        """
        default_parameters = {
            "n_origins": (2, 5),
            "n_destinations": (2, 5),
            "supply_range": (20, 50),
            "demand_range": (20, 50),
            "rate_range": (1, 10),
            "limit_range": (30, 50),
        }
        # Use default parameters if none are provided or empty dict is provided
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
        1. Generates random problem data (origins, destinations, supplies, demands, rates, and limits)
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

        # Generate supply at origins and demand at destinations
        supply = {origin: random.randint(*self.supply_range) for origin in origins}
        demand = {destination: random.randint(*self.demand_range) for destination in destinations}

        # Balance total supply and total demand (ensures feasibility)
        total_supply = sum(supply.values())
        total_demand = sum(demand.values())
        if total_supply > total_demand:
            # Reduce supply to match total demand
            diff = total_supply - total_demand
            for origin in supply:
                if diff <= 0:
                    break
                reduction = min(diff, supply[origin])
                supply[origin] -= reduction
                diff -= reduction
        elif total_demand > total_supply:
            # Increase supply to match total demand
            diff = total_demand - total_supply
            for origin in supply:
                supply[origin] += diff
                break  # Modify one origin to address the imbalance

        # Match total supply and total demand explicitly
        total_supply = sum(supply.values())
        total_demand = sum(demand.values())
        assert total_supply == total_demand, "Total supply and demand must be equal"

        # Generate shipment rates and limits between origins and destinations
        rates = {(origin, destination): random.randint(*self.rate_range) for origin in origins for destination in destinations}
        limits = {(origin, destination): random.randint(*self.limit_range) for origin in origins for destination in destinations}

        # Create Gurobi model
        model = gp.Model("Transportation")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create decision variables (continuous shipping amounts)
        shipping = model.addVars(origins, destinations, lb=0, vtype=GRB.CONTINUOUS, name="Shipping")

        # Set objective: minimize total transportation cost
        model.setObjective(
            gp.quicksum(rates[origin, destination] * shipping[origin, destination] for origin in origins for destination in destinations),
            GRB.MINIMIZE
        )

        # Add supply constraints
        model.addConstrs(
            (gp.quicksum(shipping[origin, destination] for destination in destinations) == supply[origin] for origin in origins),
            name="SupplyConstraint"
        )

        # Add demand constraints
        model.addConstrs(
            (gp.quicksum(shipping[origin, destination] for origin in origins) == demand[destination] for destination in destinations),
            name="DemandConstraint"
        )

        # Add limit constraints
        model.addConstrs(
            (shipping[origin, destination] <= limits[origin, destination] for origin in origins for destination in destinations),
            name="LimitConstraint"
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