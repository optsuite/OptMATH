import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Facility Location optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_locations: Number of locations
                - n_commodities: Number of commodities
                - n_product_plants: Number of product plants
                - n_distribution_centers: Number of distribution centers
                - n_customer_zones: Number of customer zones
                - supply_range: Tuple of (min, max) for supply values
                - demand_range: Tuple of (min, max) for demand values
                - max_throughput_range: Tuple of (min, max) for maximum throughput values
                - min_throughput_range: Tuple of (min, max) for minimum throughput values
                - unit_throughput_cost_range: Tuple of (min, max) for unit throughput costs
                - fixed_throughput_cost_range: Tuple of (min, max) for fixed throughput costs
                - variable_cost_range: Tuple of (min, max) for variable costs
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "facility_location"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are:
        - Locations: \( \mathcal{L} \)
        - Commodities: \( \mathcal{C} \)
        - Product Plants: \( \mathcal{P} \subseteq \mathcal{L} \)
        - Distribution Centers: \( \mathcal{D} \subseteq \mathcal{L} \)
        - Customer Zones: \( \mathcal{Z} \subseteq \mathcal{L} \)

        The objective is to minimize the total cost of the distribution system, which includes:
        - Variable costs for shipping commodities.
        - Fixed and unit throughput costs for distribution centers.

        The constraints ensure:
        - Supply and demand balance.
        - Throughput limits for distribution centers.
        - Each customer zone is served by exactly one distribution center.
        """
        default_parameters = {
            "n_locations": (10, 11),
            "n_commodities": (3, 5),
            "n_product_plants": (3, 5),
            "n_distribution_centers": (3, 5),
            "n_customer_zones": (4, 6),
            "supply_range": (100, 500),
            "demand_range": (10, 100),
            "max_throughput_range": (500, 1000),
            "min_throughput_range": (100, 300),
            "unit_throughput_cost_range": (1, 10),
            "fixed_throughput_cost_range": (1000, 5000),
            "variable_cost_range": (1, 20)
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
        Generate a Facility Location problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (locations, commodities, product plants, distribution centers, customer zones, etc.)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the facility location problem
        """
        
        # Randomly select number of locations, commodities, product plants, distribution centers, and customer zones
        self.n_locations = random.randint(*self.n_locations)
        self.n_commodities = random.randint(*self.n_commodities)
        self.n_product_plants = random.randint(*self.n_product_plants)
        self.n_distribution_centers = random.randint(*self.n_distribution_centers)
        self.n_customer_zones = random.randint(*self.n_customer_zones)

        # Generate sets
        locations = [f"location_{i}" for i in range(self.n_locations)]
        commodities = [f"commodity_{i}" for i in range(self.n_commodities)]
        product_plants = [f"plant_{i}" for i in range(self.n_product_plants)]
        distribution_centers = [f"dc_{i}" for i in range(self.n_distribution_centers)]
        customer_zones = [f"zone_{i}" for i in range(self.n_customer_zones)]

        # Generate parameters
        supply = {(c, p): random.randint(*self.supply_range) for c in commodities for p in product_plants}
        demand = {(c, z): random.randint(*self.demand_range) for c in commodities for z in customer_zones}
        max_throughput = {d: random.randint(*self.max_throughput_range) for d in distribution_centers}
        min_throughput = {d: random.randint(*self.min_throughput_range) for d in distribution_centers}
        unit_throughput_cost = {d: random.randint(*self.unit_throughput_cost_range) for d in distribution_centers}
        fixed_throughput_cost = {d: random.randint(*self.fixed_throughput_cost_range) for d in distribution_centers}
        variable_cost = {(c, p, d, z): random.randint(*self.variable_cost_range) for c in commodities for p in product_plants for d in distribution_centers for z in customer_zones}

        # Create Gurobi model
        model = gp.Model("FacilityLocation")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create decision variables
        shipped = model.addVars(commodities, product_plants, distribution_centers, customer_zones, vtype=GRB.CONTINUOUS, name="Shipped")
        selected = model.addVars(distribution_centers, vtype=GRB.BINARY, name="Selected")
        served = model.addVars(distribution_centers, customer_zones, vtype=GRB.BINARY, name="Served")

        # Set objective: minimize total cost
        model.setObjective(
            gp.quicksum(variable_cost[c, p, d, z] * shipped[c, p, d, z] for c in commodities for p in product_plants for d in distribution_centers for z in customer_zones) +
            gp.quicksum(fixed_throughput_cost[d] * selected[d] + unit_throughput_cost[d] * gp.quicksum(demand[c, z] * served[d, z] for c in commodities for z in customer_zones) for d in distribution_centers),
            GRB.MINIMIZE
        )

        # Add constraints
        # Supply constraint
        for c in commodities:
            for p in product_plants:
                model.addConstr(
                    gp.quicksum(shipped[c, p, d, z] for d in distribution_centers for z in customer_zones) <= supply[c, p],
                    name=f"Supply_{c}_{p}"
                )

        # Demand constraint
        for c in commodities:
            for d in distribution_centers:
                for z in customer_zones:
                    model.addConstr(
                        gp.quicksum(shipped[c, p, d, z] for p in product_plants) >= demand[c, z] * served[d, z],
                        name=f"Demand_{c}_{d}_{z}"
                    )

        # Minimum throughput constraint
        for d in distribution_centers:
            model.addConstr(
                gp.quicksum(demand[c, z] * served[d, z] for c in commodities for z in customer_zones) >= selected[d] * min_throughput[d],
                name=f"MinThroughput_{d}"
            )

        # Maximum throughput constraint
        for d in distribution_centers:
            model.addConstr(
                gp.quicksum(demand[c, z] * served[d, z] for c in commodities for z in customer_zones) <= selected[d] * max_throughput[d],
                name=f"MaxThroughput_{d}"
            )

        # Allocation constraint
        for z in customer_zones:
            model.addConstr(
                gp.quicksum(served[d, z] for d in distribution_centers) == 1,
                name=f"Allocation_{z}"
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
        
        model.write("facility_location.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()