import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Multi-Commodity Network Flow optimization problem.

        Parameters:
            parameters (dict): Problem parameters.
            seed (int, optional): Random seed for reproducibility.
        """
        self.problem_type = "multi_commodity_network_flow"
        default_parameters = {
            "n_cities": (5, 10),                # Cities range (minimum, maximum)
            "n_products": (3, 5),              # Products range (minimum, maximum)
            "supply_range": (50, 100),         # Supply range (more moderate range)
            "demand_range": (50, 100),         # Demand range
            "shipment_cost_range": (1, 10),    # Shipment cost range
            "capacity_range": (50, 100),       # Increase capacity range
            "joint_capacity_ratio": 0.9        # Increase joint capacity ratio
        }

        self.parameters = parameters or default_parameters
        for key, value in self.parameters.items():
            setattr(self, key, value)

        self.seed = seed
        if self.seed is not None:
            random.seed(seed)

    def generate_instance(self):
        """
        Generate a Multi-Commodity Network Flow problem instance and return the Gurobi model.
        """
        # Randomly select number of cities and products
        self.n_cities = random.randint(*self.n_cities)
        self.n_products = random.randint(*self.n_products)

        # Generate cities, products, and links
        cities = [f"city_{i}" for i in range(self.n_cities)]
        products = [f"product_{p}" for p in range(self.n_products)]
        links = [(i, j) for i in cities for j in cities if i != j]

        # Generate supply, demand, shipment costs, and capacities
        supply = {i: {p: random.randint(*self.supply_range) for p in products} for i in cities}
        demand = {i: {p: random.randint(*self.demand_range) for p in products} for i in cities}

        # Adjust supply and demand to ensure balance
        total_demand = {p: sum(demand[i][p] for i in cities) for p in products}
        total_supply = {p: sum(supply[i][p] for i in cities) for p in products}

        for p in products:
            diff = total_demand[p] - total_supply[p]
            if diff != 0:
                # Evenly distribute the supply adjustments across multiple cities
                adjustment_per_city = diff // len(cities)
                remaining_adjustment = diff % len(cities)
                for i, city in enumerate(cities):
                    if adjustment_per_city + supply[city][p] >= 0:  # Ensure no negative supply
                        supply[city][p] += adjustment_per_city
                    if i == 0:  # Assign the remaining adjustment to the first city
                        supply[city][p] += remaining_adjustment

        # Ensure no city has negative demand or supply
        supply = {i: {p: max(0, supply[i][p]) for p in products} for i in cities}
        demand = {i: {p: max(0, demand[i][p]) for p in products} for i in cities}

        shipment_cost = {(i, j): {p: random.randint(*self.shipment_cost_range) for p in products} for (i, j) in links}
        capacity = {(i, j): {p: random.randint(*self.capacity_range) for p in products} for (i, j) in links}

        # Joint capacity: calculated as a ratio of total capacity
        total_capacity = sum(capacity[(i, j)][p] for (i, j) in links for p in products)
        joint_capacity = {(i, j): int(total_capacity * self.joint_capacity_ratio / max(1, len(links))) for (i, j) in links}

        # Create the Gurobi model
        model = gp.Model("MultiCommodityNetworkFlow")
        model.Params.OutputFlag = 1  # Enable Gurobi output

        # Create decision variables
        ship = model.addVars(links, products, vtype=GRB.CONTINUOUS, name="Ship")

        # Set the objective: minimize total shipment cost
        model.setObjective(
            gp.quicksum(shipment_cost[(i, j)][p] * ship[i, j, p] for (i, j) in links for p in products),
            GRB.MINIMIZE
        )

        # Add flow balance constraints
        for k in cities:
            for p in products:
                model.addConstr(
                    supply[k][p] + gp.quicksum(ship[i, k, p] for (i, k2) in links if k2 == k) ==
                    demand[k][p] + gp.quicksum(ship[k, j, p] for (k2, j) in links if k2 == k),
                    name=f"FlowBalance_{k}_{p}"
                )

        # Add joint capacity constraints
        for (i, j) in links:
            model.addConstr(
                gp.quicksum(ship[i, j, p] for p in products) <= joint_capacity[(i, j)],
                name=f"JointCapacity_{i}_{j}"
            )

        # Add product-specific capacity constraints
        for (i, j) in links:
            for p in products:
                model.addConstr(
                    ship[i, j, p] <= capacity[(i, j)][p],
                    name=f"Capacity_{i}_{j}_{p}"
                )
        return model

if __name__ == '__main__':
    import time

    def test_generator():
        generator = Generator()  # Fix the random seed for reproducibility
        model = generator.generate_instance()

        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()