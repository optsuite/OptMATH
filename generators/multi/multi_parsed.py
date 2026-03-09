import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Multi-Commodity Transportation optimization problem.
        Parameters:
            parameters (dict): Dictionary containing:
                - n_origins: Range for the number of origins (min, max)
                - n_destinations: Range for the number of destinations (min, max)
                - n_products: Range for the number of products (min, max)
                - cost_range: Tuple of (min, max) for shipping costs
                - supply_range: Tuple of (min, max) for supply quantities
                - demand_range: Tuple of (min, max) for demand quantities
                - limit_range: Tuple of (min, max) for shipment capacity
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "multi_commodity_transportation"
        self.mathematical_formulation = r"""
        ### Mathematical Model\n
        A Multi-Commodity Transportation optimization problem involves:\n
        - Sets:
            - Origins: Set of origins (i)
            - Destinations: Set of destinations (j)
            - Products: Set of products (p)
        - Parameters:
            - **Supply** (Supply_{i,p}): Amounts each origin i can supply of product p
            - **Demand** (Demand_{j,p}): Amounts each destination j requires of product p
            - **ShippingCost** (ShippingCost_{i,j,p}): Cost to ship unit of product p from origin i to destination j
            - **Limit** (Limit_{i,j}): Max total units shipped from origin i to destination j
        - Decision variable:
            - **Transport** (Transport_{i,j,p}): Number of units of product p shipped from origin i to destination j
        - Objective:
            - Minimize total cost of shipping, subject to supply, demand, and shipment capacity constraints.
        """
        default_parameters = {
            "n_origins": (8, 12),
            "n_destinations": (8, 12),
            "n_products": (2, 5),
            "cost_range": (1, 10),
            "supply_range": (30, 120),
            "demand_range": (10, 100),
            "limit_range": (50, 200)
        }
        if parameters is None or not parameters:
            parameters = default_parameters
        for key, value in parameters.items():
            setattr(self, key, value)
        self.seed = seed
        if self.seed is not None:
            random.seed(seed)

    def generate_instance(self):
        """
        Generate a Multi-Commodity Transportation problem instance and create its corresponding Gurobi model.
        Returns:
            gp.Model: Configured Gurobi model for the Multi-Commodity Transportation Problem.
        """
        # Randomly determine number of origins, destinations, and products
        self.n_origins = random.randint(*self.n_origins)
        self.n_destinations = random.randint(*self.n_destinations)
        self.n_products = random.randint(*self.n_products)

        # Generate sets
        origins = [f"origin_{i}" for i in range(self.n_origins)]
        destinations = [f"destination_{j}" for j in range(self.n_destinations)]
        products = [f"product_{p}" for p in range(self.n_products)]

        # Generate parameters
        supply = {(i, p): random.randint(*self.supply_range) for i in origins for p in products}
        demand = {(j, p): random.randint(*self.demand_range) for j in destinations for p in products}
        limit = {(i, j): random.randint(*self.limit_range) for i in origins for j in destinations}
        shipping_cost = {(i, j, p): random.randint(*self.cost_range) for i in origins for j in destinations for p in products}

        # Balance supply and demand to ensure feasibility
        for p in products:
            total_supply_p = sum(supply[i, p] for i in origins)
            total_demand_p = sum(demand[j, p] for j in destinations)
            if total_supply_p > total_demand_p:
                excess = total_supply_p - total_demand_p
                for i in origins:
                    if excess == 0:
                        break
                    reduce_amount = min(excess, supply[i, p])
                    supply[i, p] -= reduce_amount
                    excess -= reduce_amount
            else:
                deficit = total_demand_p - total_supply_p
                for j in destinations:
                    if deficit == 0:
                        break
                    reduce_amount = min(deficit, demand[j, p])
                    demand[j, p] -= reduce_amount
                    deficit -= reduce_amount

        # Create Gurobi model
        model = gp.Model("Multi-Commodity Transportation")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create variables
        transport = model.addVars(
            origins, destinations, products, vtype=GRB.CONTINUOUS, name="Transport"
        )

        # Set objective: minimize total shipping cost
        model.setObjective(
            gp.quicksum(
                shipping_cost[i, j, p] * transport[i, j, p]
                for i in origins for j in destinations for p in products
            ),
            GRB.MINIMIZE
        )

        # Add supply constraints
        for i in origins:
            for p in products:
                model.addConstr(
                    gp.quicksum(transport[i, j, p] for j in destinations) == supply[i, p],
                    name=f"Supply_{i}_{p}"
                )

        # Add demand constraints
        for j in destinations:
            for p in products:
                model.addConstr(
                    gp.quicksum(transport[i, j, p] for i in origins) == demand[j, p],
                    name=f"Demand_{j}_{p}"
                )

        # Add shipment limit constraints
        for i in origins:
            for j in destinations:
                model.addConstr(
                    gp.quicksum(transport[i, j, p] for p in products) <= limit[i, j],
                    name=f"Limit_{i}_{j}"
                )

        return model


if __name__ == "__main__":
    import time

    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        model.write("multi_commodity_transportation.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()