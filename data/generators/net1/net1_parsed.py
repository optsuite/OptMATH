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
                - shipping_cost_range: Tuple of (min, max) for shipping costs
                - capacity_range: Tuple of (min, max) for link capacities
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "network_flow"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are `n` cities and `m` links between them. Each city `i` has:
        - **Supply**: Supply_i (amount of goods available)
        - **Demand**: Demand_i (amount of goods required)
        Each link `(i, j)` has:
        - **Shipping Cost**: ShippingCost_{i,j} (cost to ship one unit of goods)
        - **Capacity**: Capacity_{i,j} (maximum units that can be shipped)
        
        Decision Variable:
        - Ship_{i,j}: Number of units shipped from city `i` to city `j`
        
        Objective:
        Minimize the total shipping cost:
        $$
        \text{Minimize} \quad \sum_{(i,j) \in \text{Links}} \text{ShippingCost}_{i,j} \cdot \text{Ship}_{i,j}
        $$

        Constraints:
        1. Flow Balance:
        For each city `k`:
        $$
        \text{Supply}_k + \sum_{(i,k) \in \text{Links}} \text{Ship}_{i,k} = \text{Demand}_k + \sum_{(k,j) \in \text{Links}} \text{Ship}_{k,j}
        $$

        2. Capacity:
        For each link `(i,j)`:
        $$
        \text{Ship}_{i,j} \leq \text{Capacity}_{i,j}
        $$

        3. Non-Negativity:
        $$
        \text{Ship}_{i,j} \geq 0 \quad \forall (i,j) \in \text{Links}
        $$
        """
        default_parameters = {
            "n_cities": (5, 10),
            "supply_range": (10, 100),
            "demand_range": (10, 100),
            "shipping_cost_range": (1, 10),
            "capacity_range": (5, 100)
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
        
        This method does two things:
        1. Generates random problem data (cities, supply, demand, shipping costs, capacities)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the network flow problem
        """
        
        # Randomly select number of cities
        self.n_cities = random.randint(*self.n_cities)
        
        # Generate cities and their properties
        cities = [f"city_{i}" for i in range(self.n_cities)]
        supply = {city: random.randint(*self.supply_range) for city in cities}
        demand = {city: random.randint(*self.demand_range) for city in cities}
        # Adjust supply and demand to ensure feasibility
        total_supply = sum(supply.values())
        total_demand = sum(demand.values())
        
        if total_supply > total_demand:
            # Reduce supply to match demand
            diff = total_supply - total_demand
            for city in supply:
                if diff <= 0:
                    break
                reduction = min(diff, supply[city])
                supply[city] -= reduction
                diff -= reduction
        elif total_demand > total_supply:
            # Reduce demand to match supply
            diff = total_demand - total_supply
            for city in demand:
                if diff <= 0:
                    break
                reduction = min(diff, demand[city])
                demand[city] -= reduction
                diff -= reduction
        
        # Ensure total supply equals total demand
        assert sum(supply.values()) == sum(demand.values()), "Total supply and demand must be equal"
        
        # Generate links between cities
        links = [(i, j) for i in cities for j in cities if i != j]
        shipping_cost = {link: random.randint(*self.shipping_cost_range) for link in links}
        capacity = {link: random.randint(*self.capacity_range) for link in links}

        # Create Gurobi model
        model = gp.Model("NetworkFlow")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create decision variables (Ship[i,j] = units shipped from city i to city j)
        ship = model.addVars(links, vtype=GRB.CONTINUOUS, name="Ship")

        # Set objective: minimize total shipping cost
        model.setObjective(
            gp.quicksum(shipping_cost[link] * ship[link] for link in links),
            GRB.MINIMIZE
        )

        # Add flow balance constraints for each city
        for city in cities:
            inflow = gp.quicksum(ship[(i, city)] for (i, j) in links if j == city)
            outflow = gp.quicksum(ship[(city, j)] for (i, j) in links if i == city)
            model.addConstr(
                supply[city] + inflow == demand[city] + outflow,
                name=f"FlowBalance_{city}"
            )

        # Add capacity constraints for each link
        for link in links:
            model.addConstr(
                ship[link] <= capacity[link],
                name=f"Capacity_{link}"
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