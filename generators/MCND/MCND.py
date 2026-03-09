import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize MCND (Multicommodity Capacitated Network Design) problem.
        
        Parameters:
        parameters (dict): Dictionary containing:
            - n_nodes: Number of nodes
            - n_commodities: Number of commodities
            - density: Network density (0-1)
            - capacity_range: (min, max) for u_{ij}
            - fixed_cost_range: (min, max) for f_{ij}
            - variable_cost_range: (min, max) for c_{ij}^k
            - demand_range: (min, max) for d^k
        seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "mcnd"
        self.mathematical_formulation = r"""### Mathematical Formulation

#### Parameters
- u_{ij}: Capacity provided by installing one facility on arc (i,j)
- f_{ij}: Cost of installing one facility on arc (i,j)
- c_{ij}^k: Routing cost per unit flow of commodity k on arc (i,j)

#### Decision Variables
- x_{ij}^k: Flow variable representing fraction of commodity k on arc (i,j)
- y_{ij}: Integer variable for number of facilities to install on arc (i,j)

#### Objective Function
Minimize total cost:
\min \sum_{k\in K}\sum_{(i,j)\in A} d^kc_{ij}^k x_{ij}^k + \sum_{(i,j)\in A} f_{ij}y_{ij}

#### Constraints
1. Flow Conservation:
\sum_{j\in N_i^+} x_{ij}^k - \sum_{j\in N_i^-} x_{ji}^k = \delta_i^k \quad \forall i \in N, k \in K

2. Capacity Constraints:
\sum_{k\in K} d^k x_{ij}^k \leq u_{ij}y_{ij} \quad \forall (i,j) \in A

3. Flow Bounds:
0 \leq x_{ij}^k \leq 1 \quad \forall (i,j) \in A, k \in K

4. Design Variables:
y_{ij} \geq 0, \text{ integer} \quad \forall (i,j) \in A

where:
- N_i^+ = {j \in N|(i,j) \in A}
- N_i^- = {j \in N|(j,i) \in A}
- \delta_i^k = 1 if i = O(k)
- \delta_i^k = -1 if i = D(k)
- \delta_i^k = 0 otherwise

This formulation represents a mixed-integer programming (MIP) model that can be applied to various applications in transportation, logistics, and telecommunications networks."""

        # Default parameters
        default_parameters = {
            "n_nodes": (2,10),
            "n_commodities": (2,10),
            "density": 0.3,
            "capacity_range": (10, 500),    # u_{ij}
            "fixed_cost_range": (100, 5000),  # f_{ij}
            "variable_cost_range": (1, 10),    # c_{ij}^k
            "demand_range": (10, 20)           # d^k
        }

        # Use default parameters if none are provided
        if parameters is None:
            parameters = default_parameters
        
        # Set parameters as attributes
        for key, value in parameters.items():
            setattr(self, key, value)

        # Set random seed
        self.seed = seed
        if self.seed is not None:
            random.seed(seed)

    def get_Ni_plus(self, node, arcs):
        """Return N_i^+ = {j ∈ N|(i,j) ∈ A}"""
        return [j for i, j in arcs if i == node]

    def get_Ni_minus(self, node, arcs):
        """Return N_i^- = {j ∈ N|(j,i) ∈ A}"""
        return [i for i, j in arcs if j == node]

    def get_delta(self, node, origin, destination):
        """Return δ_i^k based on node's relation to O(k) and D(k)"""
        if node == origin:
            return 1
        elif node == destination:
            return -1
        return 0

    def generate_instance(self):
        """
        Generate an MCND instance according to the mathematical formulation.
        
        Returns:
        gp.Model: Configured Gurobi model for the MCND problem
        dict: Problem instance data
        """
        
        # Randomly select number of nodes and commodities
        self.n_nodes = random.randint(*self.n_nodes)
        self.n_commodities = random.randint(*self.n_commodities)
        
        # Generate network structure
        N = list(range(self.n_nodes))        # Set of nodes
        K = list(range(self.n_commodities))  # Set of commodities
        
        # Generate arcs with given density
        A = [(i, j) for i in N for j in N 
             if i != j and random.random() < self.density]

        # Generate parameters
        # u_{ij}: Capacity for each arc
        u = {(i,j): random.randint(*self.capacity_range) for i,j in A}
        
        # f_{ij}: Fixed cost for each arc
        f = {(i,j): random.randint(*self.fixed_cost_range) for i,j in A}
        
        # c_{ij}^k: Variable cost for each commodity on each arc
        c = {(k,i,j): random.randint(*self.variable_cost_range) 
             for k in K for i,j in A}
        
        # d^k: Demand for each commodity
        d = {k: random.randint(*self.demand_range) for k in K}
        
        # O(k), D(k): Origin and destination for each commodity
        OD = {}
        for k in K:
            origin = random.choice(N)
            destination = random.choice([n for n in N if n != origin])
            OD[k] = (origin, destination)

        # Create Gurobi model
        model = gp.Model("MCND")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create variables
        # x_{ij}^k: Flow variables
        x = model.addVars(K, A, vtype=GRB.CONTINUOUS, name="x")
        
        # y_{ij}: Design variables
        y = model.addVars(A, vtype=GRB.INTEGER, name="y")

        # Set objective function
        obj = (gp.quicksum(d[k] * c[k,i,j] * x[k,i,j] for k in K for i,j in A) +
               gp.quicksum(f[i,j] * y[i,j] for i,j in A))
        model.setObjective(obj, GRB.MINIMIZE)

        # Add constraints
        # 1. Flow conservation constraints
        for k in K:
            for i in N:
                origin, destination = OD[k]
                delta = self.get_delta(i, origin, destination)
                
                model.addConstr(
                    gp.quicksum(x[k,i,j] for j in self.get_Ni_plus(i, A)) -
                    gp.quicksum(x[k,j,i] for j in self.get_Ni_minus(i, A)) == delta
                )

        # 2. Capacity constraints
        for i,j in A:
            model.addConstr(
                gp.quicksum(d[k] * x[k,i,j] for k in K) <= u[i,j] * y[i,j]
            )

        # 3. Flow bounds
        for k in K:
            for i,j in A:
                model.addConstr(x[k,i,j] >= 0)
                model.addConstr(x[k,i,j] <= 1)

        # 4. Design variables bounds
        for i,j in A:
            model.addConstr(y[i,j] >= 0)

        # Store instance data
        instance_data = {
            "N": N,
            "A": A,
            "K": K,
            "u": u,
            "f": f,
            "c": c,
            "d": d,
            "OD": OD
        }

        return model

if __name__ == '__main__':
    def test_generator():
        # Create generator
        generator = Generator()
        
        # Generate instance
        model = generator.generate_instance()
        
        model.write("mcnd.lp")
        
        # Solve model
        import time
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time

       
        print(f"Solve Time: {solve_time:.2f} seconds")
        
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
        
        print(model.NumVars, model.NumConstrs)

    test_generator()