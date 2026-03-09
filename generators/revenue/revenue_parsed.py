import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Revenue Maximization optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_flight_legs: Number of flight legs
                - n_packages: Number of packages
                - demand_range: Tuple of (min, max) for package demand
                - revenue_range: Tuple of (min, max) for package revenue
                - available_seats_range: Tuple of (min, max) for available seats per flight leg
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "revenue_maximization"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are:
        - FlightLegs: Set of flight legs (one-way non-stop flights)
        - Packages: Set of flight packages (itineraries) that can be sold

        Parameters:
        - AvailableSeats_r: Number of available seats for flight leg r
        - Demand_p: Estimated demand for package p
        - Revenue_p: Revenue gained from selling one unit of package p
        - Delta_p,r: Binary parameter indicating if package p uses flight leg r

        Decision Variable:
        - Sell_p: Number of units of package p to sell (integer)

        Objective:
        Maximize the total revenue:
        $$
        \text{Maximize} \quad \sum_{p \in \text{Packages}} \text{Revenue}_p \times \text{Sell}_p
        $$

        Constraints:
        1. Demand Constraint:
        $$
        \text{Sell}_p \leq \text{Demand}_p \quad \forall p \in \text{Packages}
        $$

        2. Capacity Constraint:
        $$
        \sum_{p \in \text{Packages}} \Delta_{p,r} \times \text{Sell}_p \leq \text{AvailableSeats}_r \quad \forall r \in \text{FlightLegs}
        $$
        """
        default_parameters = {
            "n_flight_legs": (3, 5),
            "n_packages": (3, 5),
            "demand_range": (1, 10),
            "revenue_range": (100, 500),
            "available_seats_range": (50, 200)
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
        Generate a Revenue Maximization problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (flight legs, packages, demand, revenue, available seats)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the revenue maximization problem
        """
        
        # Randomly select number of flight legs and packages
        self.n_flight_legs = random.randint(*self.n_flight_legs)
        self.n_packages = random.randint(*self.n_packages)
        
        # Generate flight legs and packages
        flight_legs = [f"flight_leg_{i}" for i in range(self.n_flight_legs)]
        packages = [f"package_{i}" for i in range(self.n_packages)]
        
        # Generate random parameters
        available_seats = {r: random.randint(*self.available_seats_range) for r in flight_legs}
        demand = {p: random.randint(*self.demand_range) for p in packages}
        revenue = {p: random.randint(*self.revenue_range) for p in packages}
        
        # Generate Delta_p,r: Binary parameter indicating if package p uses flight leg r
        delta = {}
        for p in packages:
            for r in flight_legs:
                delta[p, r] = random.choice([0, 1])  # Randomly assign 0 or 1

        # Create Gurobi model
        model = gp.Model("RevenueMaximization")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create integer decision variables (Sell_p: Number of units of package p to sell)
        sell = model.addVars(packages, vtype=GRB.INTEGER, name="Sell")

        # Set objective: maximize total revenue
        model.setObjective(
            gp.quicksum(revenue[p] * sell[p] for p in packages),
            GRB.MAXIMIZE
        )

        # Add demand constraints
        for p in packages:
            model.addConstr(
                sell[p] <= demand[p],
                name=f"Demand_{p}"
            )

        # Add capacity constraints
        for r in flight_legs:
            model.addConstr(
                gp.quicksum(delta[p, r] * sell[p] for p in packages) <= available_seats[r],
                name=f"Capacity_{r}"
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
        
        model.write("revenue_maximization.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()