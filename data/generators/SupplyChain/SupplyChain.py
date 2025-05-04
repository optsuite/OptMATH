import gurobipy as gp
from gurobipy import GRB
import random
import numpy as np
import time


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Supply Chain optimization problem.
        Parameters:
        parameters (dict): Dictionary containing:
            - n_nodes: Number of nodes
            - cap_range: Tuple of (min, max) for arc capacities
            - fixed_cost_range: Tuple of (min, max) for fixed costs
            - unit_cost_range: Tuple of (min, max) for unit transportation costs
            - total_supply: Total supply in the system
            - n_suppliers: Number of supplier nodes
            - n_customers: Number of customer nodes
        seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "supply_chain"
        self.description = "This problem aims to design a distribution network for a supply chain. We want to select the suppliers and warehouses locations, and decide on the amount of product transported between these locations to satisfy the customers demand. The problem elements are a) a set of nodes, ie, plants, warehouses/DCs, customers, and b) a set of links/arcs, listing pairs of nodes corresponding to allowed shipment options. Each node has a supply or demand amount and a fixed cost of including the node in the network. Each link or arc has cost/unit flow and capacity. We want to determine the facilities to use and the flow of each arc to minimize the flow cost and the fixed cost of nodes."
        self.mathematical_formulation = r"""
        \begin{align*}
        \min & \sum_{i \in N}\sum_{j \in N} f_{i,j}y_{i,j} + \sum_{i \in N}\sum_{j \in N} c_{i,j}x_{i,j} \\
        \text{s.t.} & x_{i,j} \leq cap_{i,j}y_{i,j}, \quad \forall i,j \in N \\
        & \sum_{j \in N} x_{j,i} - \sum_{j \in N} x_{i,j} = d_i - s_i, \quad \forall i \in N \\
        & y_{i,j} \in \{0,1\}, x_{i,j} \geq 0 \quad \forall i,j \in N
        \end{align*}
        """

        default_parameters = {
            "n_nodes": (3, 50),
            "cap_range": (50, 200),
            "fixed_cost_range": (1000, 5000),
            "unit_cost_range": (10, 50),
            "total_supply": 1000,
            "n_suppliers": (3,10),
            "n_customers": (3,20),
        }

        if parameters is None or not parameters:
            parameters = default_parameters
        for key, value in parameters.items():
            setattr(self, key, value)

        self.seed = seed
        if self.seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def generate_instance(self):
        """
        Generate a Supply Chain problem instance and create its corresponding Gurobi model.
        Returns:
        gp.Model: Configured Gurobi model for the supply chain problem
        """
        
        # Randomly select number of nodes
        self.n_nodes = random.randint(*self.n_nodes)
        self.n_suppliers = random.randint(*self.n_suppliers)
        self.n_customers = random.randint(*self.n_customers)
        
        
        # Generate nodes
        nodes = [f"node_{i}" for i in range(self.n_nodes)]

        # Generate supplies and demands
        supplies = {node: 0 for node in nodes}
        demands = {node: 0 for node in nodes}

        # Assign supplies to supplier nodes
        supplier_nodes = nodes[: self.n_suppliers]
        total_supply = self.total_supply
        # Randomly distribute supply among suppliers
        for i, node in enumerate(supplier_nodes):
            if i == len(supplier_nodes) - 1:
                supplies[node] = (
                    total_supply  # Assign remaining supply to last supplier
                )
            else:
                supply = random.randint(1, total_supply - (len(supplier_nodes) - i - 1))
                supplies[node] = supply
                total_supply -= supply

        # Assign demands to customer nodes
        customer_nodes = nodes[-self.n_customers :]
        total_demand = self.total_supply  # Ensure total demand equals total supply
        # Randomly distribute demand among customers
        for i, node in enumerate(customer_nodes):
            if i == len(customer_nodes) - 1:
                demands[node] = total_demand  # Assign remaining demand to last customer
            else:
                demand = random.randint(1, total_demand - (len(customer_nodes) - i - 1))
                demands[node] = demand
                total_demand -= demand

        # Generate capacities and costs
        # Make sure capacities are large enough to allow feasible solutions
        max_flow = self.total_supply
        cap = {
            (i, j): random.randint(max_flow // 2, max_flow)
            for i in nodes
            for j in nodes
            if i != j
        }
        fixed_costs = {
            (i, j): random.randint(*self.fixed_cost_range)
            for i in nodes
            for j in nodes
            if i != j
        }
        unit_costs = {
            (i, j): random.randint(*self.unit_cost_range)
            for i in nodes
            for j in nodes
            if i != j
        }

        # Create Gurobi model
        model = gp.Model("SupplyChain")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Create variables
        y = model.addVars(
            [(i, j) for i in nodes for j in nodes if i != j], vtype=GRB.BINARY, name="y"
        )
        x = model.addVars(
            [(i, j) for i in nodes for j in nodes if i != j],
            lb=0,
            vtype=GRB.CONTINUOUS,
            name="x",
        )

        # Set objective
        model.setObjective(
            gp.quicksum(
                fixed_costs[i, j] * y[i, j] + unit_costs[i, j] * x[i, j]
                for i in nodes
                for j in nodes
                if i != j
            ),
            GRB.MINIMIZE,
        )

        # Add capacity constraints
        for i in nodes:
            for j in nodes:
                if i != j:
                    model.addConstr(x[i, j] <= cap[i, j] * y[i, j], name=f"cap_{i}_{j}")

        # Add flow conservation constraints
        for i in nodes:
            model.addConstr(
                gp.quicksum(x[j, i] for j in nodes if j != i)
                - gp.quicksum(x[i, j] for j in nodes if j != i)
                == demands[i] - supplies[i],
                name=f"flow_{i}",
            )

        return model


if __name__ == "__main__":

    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("SupplyChain.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")

        else:
            print("No optimal solution found")

    test_generator()
