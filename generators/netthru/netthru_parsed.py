import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Network Flow optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_cities: Number of cities
                - supply_range: Tuple of (min, max) for city supply
                - demand_range: Tuple of (min, max) for city demand
                - cost_range: Tuple of (min, max) for link costs
                - city_capacity_range: Tuple of (min, max) for city capacities
                - link_capacity_range: Tuple of (min, max) for link capacities
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "network_flow"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are n cities and m links between them. Each city i has:
        - **Supply** Supply_i: Amount of goods available at city i.
        - **Demand** Demand_i: Amount of goods required at city i.
        - **City Capacity** CityCapacity_i: Maximum throughput at city i.
        Each link (i, j) has:
        - **Cost** Cost_{i,j}: Cost of shipping one ton of goods over link (i, j).
        - **Link Capacity** LinkCapacity_{i,j}: Maximum shipment over link (i, j).
        The decision variable is:
        - **Shipping_{i,j}**: Amount of goods to be shipped from city i to city j.

        The objective is to minimize the total cost of shipping goods over the network:
        $$
        \begin{aligned}
        & \text{Minimize} && \sum_{(i,j) \in \text{Links}} \text{Cost}_{i,j} \cdot \text{Shipping}_{i,j} \\
        & \text{Subject to} && \text{Supply}_k + \sum_{(i,k) \in \text{Links}} \text{Shipping}_{i,k} = \text{Demand}_k + \sum_{(k,j) \in \text{Links}} \text{Shipping}_{k,j} \quad \forall k \in \text{Cities} \\
        & && \text{Shipping}_{i,j} \leq \text{LinkCapacity}_{i,j} \quad \forall (i,j) \in \text{Links} \\
        & && \text{Supply}_k + \sum_{(i,k) \in \text{Links}} \text{Shipping}_{i,k} \leq \text{CityCapacity}_k \quad \forall k \in \text{Cities} \\
        & && \text{Shipping}_{i,j} \geq 0 \quad \forall (i,j) \in \text{Links}
        \end{aligned}
        $$
        """
        default_parameters = {
            "n_cities": (8, 15),
            "supply_range": (1, 10),
            "demand_range": (1, 10),
            "cost_range": (1, 10),
            "city_capacity_range": (10, 30),
            "link_capacity_range": (5, 20)
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
        Generate a Network Flow problem instance and create its corresponding Gurobi model.
        Balances supply and demand across all cities to ensure feasibility.
        
        Returns:
            gp.Model: Configured Gurobi model for the network flow problem
        """
        # Randomly select number of cities
        self.n_cities = random.randint(*self.n_cities)
        
        # Generate cities and their properties
        cities = [f"city_{i}" for i in range(self.n_cities)]
        supplies = {city: random.randint(*self.supply_range) for city in cities}
        demands = {city: random.randint(*self.demand_range) for city in cities}
        city_capacities = {city: random.randint(*self.city_capacity_range) for city in cities}
        
        # Adjust supply and demand to ensure balance
        total_supply = sum(supplies.values())
        total_demand = sum(demands.values())
        diff = total_supply - total_demand  # Positive if supply > demand, negative otherwise
        
        if diff > 0:
            # Total supply is greater, so reduce supply across cities
            for city in cities:
                if diff == 0:
                    break
                # Calculate how much can be reduced from this city
                reduce_amount = min(supplies[city], diff)  # Ensure non-negative supply
                supplies[city] -= reduce_amount
                diff -= reduce_amount
        elif diff < 0:
            # Total demand is greater, so reduce demand across cities
            diff = -diff  # Convert to positive for similar logic
            for city in cities:
                if diff == 0:
                    break
                # Calculate how much can be reduced from this city
                reduce_amount = min(demands[city], diff)  # Ensure non-negative demand
                demands[city] -= reduce_amount
                diff -= reduce_amount

        # Check final balance again
        assert sum(supplies.values()) == sum(demands.values()), "Supply and demand are not balanced!"
                # Generate links and their properties
        links = [(i, j) for i in cities for j in cities if i != j]
        costs = {link: random.randint(*self.cost_range) for link in links}
        link_capacities = {link: random.randint(*self.link_capacity_range) for link in links}
        
        # Create Gurobi model
        model = gp.Model("NetworkFlow")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create continuous decision variables (Shipping[i,j] = amount shipped from i to j)
        shipping = model.addVars(links, vtype=GRB.CONTINUOUS, name="Shipping")
        
        # Set objective: minimize total cost of shipping
        model.setObjective(
            gp.quicksum(costs[link] * shipping[link] for link in links),
            GRB.MINIMIZE
        )
        
        # Add flow balance constraints for each city
        for city in cities:
            inflow = gp.quicksum(shipping[(i, city)] for (i, j) in links if j == city)
            outflow = gp.quicksum(shipping[(city, j)] for (i, j) in links if i == city)
            model.addConstr(
                supplies[city] + inflow == demands[city] + outflow,
                name=f"FlowBalance_{city}"
            )
        
        # Add link capacity constraints
        for link in links:
            model.addConstr(
                shipping[link] <= link_capacities[link],
                name=f"LinkCapacity_{link}"
            )
        
        # Add city capacity constraints
        for city in cities:
            inflow = gp.quicksum(shipping[(i, city)] for (i, j) in links if j == city)
            model.addConstr(
                supplies[city] + inflow <= city_capacities[city],
                name=f"CityCapacity_{city}"
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
        
        model.write("network_flow.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()