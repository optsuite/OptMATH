import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Capacitated Facility Location optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_facilities: Number of potential facilities
                - n_customers: Number of customers
                - fixed_cost_range: Tuple of (min, max) for facility fixed costs
                - transport_cost_range: Tuple of (min, max) for transportation costs
                - demand_range: Tuple of (min, max) for customer demands
                - capacity_range: Tuple of (min, max) for facility capacities
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "capacitated_facility_location"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose we have:
        - Set of facilities J = {1,...,n}
        - Set of customers I = {1,...,m}
        - f_j: Fixed cost of opening facility j
        - c_{ij}: Cost of serving customer i from facility j
        - d_i: Demand of customer i
        - K_j: Capacity of facility j
        $$
        \begin{aligned}
        &\text{Minimize} && \sum_{j \in J} f_j y_j + \sum_{i \in I}\sum_{j \in J} c_{ij} x_{ij} \\
        &\text{Subject to} && \sum_{j \in J} x_{ij} = d_i && \forall i \in I \\
        & && x_{ij} \leq d_i y_j && \forall i \in I, j \in J \\
        & && \sum_{i \in I} x_{ij} \leq K_j y_j && \forall j \in J \\
        & && y_j \in \{0,1\} && \forall j \in J \\
        & && x_{ij} \geq 0 && \forall i \in I, j \in J
        \end{aligned}
        $$
        """
        default_parameters = {
            "n_facilities": (3, 3),
            "n_customers": (3, 3),
            "fixed_cost_range": (80000, 120000),
            "transport_cost_range": (10, 100),
            "demand_range": (300, 500),
            "capacity_range": (800, 1200)
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
        Generate a Capacitated Facility Location problem instance and create its Gurobi model.
        
        Returns:
            gp.Model: Configured Gurobi model
        """
        # Randomly select number of facilities and customers
        self.n_facilities = random.randint(*self.n_facilities)
        self.n_customers = random.randint(*self.n_customers)
        
        # Generate facilities and customers
        facilities = [f"facility_{j}" for j in range(self.n_facilities)]
        customers = [f"customer_{i}" for i in range(self.n_customers)]
        
        # Generate problem parameters
        fixed_costs = {j: random.randint(*self.fixed_cost_range) for j in facilities}
        transport_costs = {(i, j): random.randint(*self.transport_cost_range) 
                         for i in customers for j in facilities}
        demands = {i: random.randint(*self.demand_range) for i in customers}
        capacities = {j: random.randint(*self.capacity_range) for j in facilities}

        # Create Gurobi model
        model = gp.Model("CapacitatedFacilityLocation")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create decision variables
        y = model.addVars(facilities, vtype=GRB.BINARY, name="FacilityOpen")
        x = model.addVars(customers, facilities, name="ShippedAmount")

        # Set objective: minimize total costs
        model.setObjective(
            gp.quicksum(fixed_costs[j] * y[j] for j in facilities) +
            gp.quicksum(transport_costs[i,j] * x[i,j] for i in customers for j in facilities),
            GRB.MINIMIZE
        )

        # Add demand constraints
        for i in customers:
            model.addConstr(
                gp.quicksum(x[i,j] for j in facilities) == demands[i],
                name=f"Demand_{i}"
            )

        # Add valid constraints
        for i in customers:
            for j in facilities:
                model.addConstr(
                    x[i,j] <= demands[i] * y[j],
                    name=f"Valid_{i}_{j}"
                )

        # Add capacity constraints
        for j in facilities:
            model.addConstr(
                gp.quicksum(x[i,j] for i in customers) <= capacities[j] * y[j],
                name=f"Capacity_{j}"
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