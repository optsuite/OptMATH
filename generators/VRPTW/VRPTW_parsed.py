import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize the Capacitated Vehicle Routing Problem with Time Windows (CVRPTW).

        Parameters:
            parameters (dict): Dictionary containing:
                - n_customers: Number of customers
                - demand_range: Tuple of (min, max) for customer demands
                - time_window_range: Tuple of (min, max) for time windows
                - distance_range: Tuple of (min, max) for distances between customers
                - service_time_range: Tuple of (min, max) for service times
                - vehicle_capacity: Capacity of the vehicles
                - M: A large constant for constraints
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "CVRPTW"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are C customers, each customer i (where i = 1, 2, ..., C) has the following attributes:
        - **Demand** d_i: The demand of customer i.
        - **Time Window** [a_i, b_i]: The time window for customer i.
        - **Distance** c_{i,j}: The distance between customer i and customer j.
        - **Service Time** s_i: The service time at customer i.
        - **Vehicle Capacity** Q: The capacity of the vehicles.
        - **Binary Variable** x_{i,j}: Indicates if an arc from customer i to customer j is in the route.
        - **Continuous Variable** t_i: The departure time at customer i.
        - **Continuous Variable** l_i: The load of the vehicle arriving at customer i.

        Objective:
        Minimize the total distance traveled:
        $$
        \text{Minimize} \quad \sum_{i \in \text{Customers}} \sum_{j \in \text{Customers}} c_{i,j} \cdot x_{i,j}
        $$

        Constraints:
        1. Each customer is visited exactly once:
        $$
        \sum_{j \in \text{Customers}} x_{i,j} = 1 \quad \forall i \in \text{Customers}, i > 0
        $$

        2. Flow balance:
        $$
        \sum_{j \in \text{Customers}} x_{i,j} - \sum_{j \in \text{Customers}} x_{j,i} = 0 \quad \forall i \in \text{Customers}, i > 0
        $$

        3. Schedule feasibility:
        $$
        t_i + c_{i,j} + s_i - t_j \leq M \cdot (1 - x_{i,j}) \quad \forall i, j \in \text{Customers}, i > 0, j > 0, i \neq j
        $$

        4. Time window constraints:
        $$
        a_i \leq t_i \leq b_i \quad \forall i \in \text{Customers}, i > 0
        $$

        5. Load feasibility:
        $$
        l_j + d_i - l_i \leq M \cdot (1 - x_{i,j}) \quad \forall i, j \in \text{Customers}, i > 0, j > 0, i \neq j
        $$

        6. Vehicle capacity:
        $$
        l_i \leq Q \quad \forall i \in \text{Customers}, i > 0
        $$
        """
        default_parameters = {
            "n_customers": (5, 10),
            "demand_range": (1, 10),
            "time_window_range": (0, 100),
            "distance_range": (1, 50),
            "service_time_range": (1, 10),
            "vehicle_capacity": (50, 100),
            "M": 1000
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
        Generate a CVRPTW problem instance and create its corresponding Gurobi model.

        Returns:
            gp.Model: Configured Gurobi model for the CVRPTW problem
        """
        # Randomly select number of customers
        self.n_customers = random.randint(*self.n_customers)
        self.vehicle_capacity = random.randint(*self.vehicle_capacity)
        
        # Generate customers and their properties
        customers = [f"customer_{i}" for i in range(self.n_customers + 1)]  # Include depot
        demands = {customer: random.randint(*self.demand_range) for customer in customers[1:]}  # Depot has no demand
        lower_time_windows = {customer: random.randint(*self.time_window_range) for customer in customers[1:]}
        upper_time_windows = {customer: lower_time_windows[customer] + random.randint(10, 20) for customer in customers[1:]}
        distances = {
            (i, j): random.randint(*self.distance_range) for i in customers for j in customers if i != j
        }
        service_times = {customer: random.randint(*self.service_time_range) for customer in customers[1:]}

        # Create Gurobi model
        model = gp.Model("CVRPTW")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create binary decision variables (x[i,j] = 1 if arc from i to j is in the route)
        x = model.addVars(customers, customers, vtype=GRB.BINARY, name="ArcVisit")

        # Create continuous decision variables (t[i] = departure time at customer i)
        t = model.addVars(customers, vtype=GRB.CONTINUOUS, name="DepartureTime")

        # Create continuous decision variables (l[i] = load of the vehicle arriving at customer i)
        l = model.addVars(customers, vtype=GRB.CONTINUOUS, name="Load")

        # Set objective: minimize total distance
        model.setObjective(
            gp.quicksum(distances[i, j] * x[i, j] for i in customers for j in customers if i != j),
            GRB.MINIMIZE
        )

        # Add constraints
        # 1. Each customer is visited exactly once (except depot)
        for i in customers[1:]:
            model.addConstr(
                gp.quicksum(x[i, j] for j in customers if i != j) == 1,
                name=f"CustomerSelection_{i}"
            )

        # 2. Flow balance
        for i in customers[1:]:
            model.addConstr(
                gp.quicksum(x[i, j] for j in customers if i != j) - gp.quicksum(x[j, i] for j in customers if i != j) == 0,
                name=f"FlowBalance_{i}"
            )

        # 3. Schedule feasibility
        for i in customers[1:]:
            for j in customers[1:]:
                if i != j:
                    model.addConstr(
                        t[i] + distances[i, j] + service_times[i] - t[j] <= self.M * (1 - x[i, j]),
                        name=f"ScheduleFeasibility_{i}_{j}"
                    )

        # 4. Time window constraints
        for i in customers[1:]:
            model.addConstr(
                lower_time_windows[i] <= t[i],
                name=f"TimeWindowLower_{i}"
            )
            model.addConstr(
                t[i] <= upper_time_windows[i],
                name=f"TimeWindowUpper_{i}"
            )

        # 5. Load feasibility
        for i in customers[1:]:
            for j in customers[1:]:
                if i != j:
                    model.addConstr(
                        l[j] + demands[i] - l[i] <= self.M * (1 - x[i, j]),
                        name=f"LoadFeasibility_{i}_{j}"
                    )

        # 6. Vehicle capacity
        for i in customers[1:]:
            model.addConstr(
                l[i] <= self.vehicle_capacity,
                name=f"VehicleCapacity_{i}"
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
        
        model.write("cvrptw.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()