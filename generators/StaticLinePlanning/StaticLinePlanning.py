import gurobipy as gp
from gurobipy import GRB
import random
import json

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Static Line Planning optimization problem.
        Parameters:
        parameters (dict): Dictionary containing:
            - n_nodes: Number of nodes
            - n_lines: Number of lines
            - n_od_pairs: Number of OD pairs
            - fixed_cost_range: Tuple of (min, max) for fixed costs
            - operational_cost_range: Tuple of (min, max) for operational costs
            - capacity_range: Tuple of (min, max) for capacity
            - demand_range: Tuple of (min, max) for demand
            - penalty_range: Tuple of (min, max) for penalty
            - trip_time_range: Tuple of (min, max) for trip time
            - density: Network density (between 0 and 1)
        seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "static_line_planning"
        self.mathematical_formulation = r"""
        \begin{align*}
        \min & \sum_{l \in L} (fc_l x_l + oc_l f_l) + \sum_{c \in C} p_c s_c \\
        \text{s.t.} & \sum_{l \in L} cap_l service_{lc} f_l + s_c \geq d_c & \forall c \in C \\
        & f_l \leq max\_freq_l x_l & \forall l \in L \\
        & f_l \geq min\_freq_l x_l & \forall l \in L \\
        & \sum_{l \in L} tt_l f_l \leq total\_vehicles \\
        & \sum_{l \in L} x_l pass_{ln} \geq 2y_n & \forall n \in N
        \end{align*}
        """
        
        default_parameters = {
            "n_nodes": (3, 30),
            "n_lines": (3, 30),
            "n_od_pairs": (3, 50),
            "fixed_cost_range": (1000, 5000),
            "operational_cost_range": (100, 500),
            "capacity_range": (100, 200),
            "demand_range": (10, 50),
            "penalty_range": (500, 1000),
            "trip_time_range": (60, 180),
            "density": 0.3
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
        Generate a Static Line Planning problem instance and create its corresponding Gurobi model.
        Returns:
            gp.Model: Configured Gurobi model for the static line planning problem
        """
        
        # Randomly select number of nodes, lines, and OD pairs
        self.n_nodes = random.randint(*self.n_nodes)
        self.n_lines = random.randint(*self.n_lines)
        self.n_od_pairs = random.randint(*self.n_od_pairs)
    
        # Generate nodes
        nodes = list(range(self.n_nodes))

        # Generate arcs
        arcs = []
        for i in nodes:
            for j in nodes:
                if i != j and random.random() < self.density:
                    arcs.append((i,j))

        # Generate lines and commodities
        lines = [f"L_{i}" for i in range(self.n_lines)]
        commodities = set()
        while len(commodities) < min(self.n_od_pairs, self.n_nodes * (self.n_nodes-1)):
            origin = random.choice(nodes)
            dest = random.choice([n for n in nodes if n != origin])
            commodities.add(f"OD_{origin}_{dest}")
        commodities = list(commodities)

        # Generate parameters
        line_info = {l: {
            "fixed_cost": random.randint(*self.fixed_cost_range),
            "operational_cost": random.randint(*self.operational_cost_range),
            "capacity": random.randint(*self.capacity_range),
            "trip_time": random.randint(*self.trip_time_range),
            "min_freq": 2,
            "max_freq": 10
        } for l in lines}

        od_info = {c: {
            "demand": random.randint(*self.demand_range),
            "penalty": random.randint(*self.penalty_range)
        } for c in commodities}

        # Generate service and pass-through matrices
        service_matrix = {f"{l}_{c}": 1 if random.random() < 0.3 else 0 
                         for l in lines for c in commodities}
        pass_through = {f"{l}_{n}": 1 if random.random() < 0.3 else 0 
                       for l in lines for n in nodes}

        # Create Gurobi model
        model = gp.Model("StaticLinePlanning")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create variables
        x = model.addVars(lines, vtype=GRB.BINARY, name="x")
        f = model.addVars(lines, vtype=GRB.CONTINUOUS, name="f")
        s = model.addVars(commodities, vtype=GRB.CONTINUOUS, name="s")
        y = model.addVars(nodes, vtype=GRB.BINARY, name="y")

        # Set objective
        obj = (gp.quicksum(line_info[l]["fixed_cost"] * x[l] + 
                          line_info[l]["operational_cost"] * f[l] for l in lines) +
               gp.quicksum(od_info[c]["penalty"] * s[c] for c in commodities))
        model.setObjective(obj, GRB.MINIMIZE)

        # Add constraints
        for c in commodities:
            model.addConstr(
                gp.quicksum(line_info[l]["capacity"] * service_matrix[f"{l}_{c}"] * f[l]
                           for l in lines) + s[c] >= od_info[c]["demand"]
            )

        for l in lines:
            model.addConstr(f[l] <= line_info[l]["max_freq"] * x[l])
            model.addConstr(f[l] >= line_info[l]["min_freq"] * x[l])

        model.addConstr(
            gp.quicksum(line_info[l]["trip_time"] * f[l] for l in lines) <= 
            self.n_lines * 5
        )

        for n in nodes:
            model.addConstr(
                gp.quicksum(x[l] * pass_through[f"{l}_{n}"] for l in lines) >= 2 * y[n]
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

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
        
        print(model.NumVars, model.NumConstrs)

    test_generator()