import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Contract Allocation problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_producers: Number of producers/factories
                - n_contracts: Number of contracts
                - capacity_range: Tuple of (min, max) for producer capacities
                - contract_size_range: Tuple of (min, max) for contract sizes
                - min_delivery_ratio: Ratio for minimum delivery size
                - cost_range: Tuple of (min, max) for production costs
                - min_contributors_range: Tuple of (min, max) for minimum contributors
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "contract_allocation"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Consider sets P of producers and C of contracts with the following:
        - **Decision Variables**:
          - x_{p,c}: Amount of commodity delivered by producer p for contract c
          - y_{p,c}: Binary variable indicating if producer p delivers to contract c
        - **Parameters**:
          - c_{p,c}: Unit production cost for producer p to fulfill contract c
          - cap_p: Available capacity of producer p
          - d_c: Size of contract c
          - m_p: Minimal delivery size for producer p
          - n_c: Minimal number of contributors for contract c
        """
        default_parameters = {
            "n_producers": (3, 5),
            "n_contracts": (4, 6),
            "capacity_range": (800, 2000),
            "contract_size_range": (400, 1500),
            "min_delivery_ratio": 0.1,
            "cost_range": (10, 50),
            "min_contributors_range": (1, 3)
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
        Generate a Contract Allocation problem instance.
        
        Returns:
            gp.Model: Configured Gurobi model for the contract allocation problem
        """
        # Generate random numbers of producers and contracts
        self.n_producers = random.randint(*self.n_producers)
        self.n_contracts = random.randint(*self.n_contracts)
        
        # Create sets
        producers = [f"producer_{i}" for i in range(self.n_producers)]
        contracts = [f"contract_{i}" for i in range(self.n_contracts)]
        
        # Generate parameters
        capacities = {p: random.randint(*self.capacity_range) for p in producers}
        contract_sizes = {c: random.randint(*self.contract_size_range) for c in contracts}
        min_deliveries = {p: int(capacities[p] * self.min_delivery_ratio) for p in producers}
        min_contributors = {c: random.randint(*self.min_contributors_range) for c in contracts}
        production_costs = {(p,c): random.randint(*self.cost_range) 
                          for p in producers for c in contracts}
        
        # Create Gurobi model
        model = gp.Model("ContractAllocation")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create decision variables
        x = model.addVars(producers, contracts, name="Generation", vtype=GRB.CONTINUOUS)
        y = model.addVars(producers, contracts, name="GenerationIncidence", vtype=GRB.BINARY)
        
        # Set objective: minimize total production cost
        model.setObjective(
            gp.quicksum(production_costs[p,c] * x[p,c] 
                       for p in producers for c in contracts),
            GRB.MINIMIZE
        )
        
        # Add constraints
        # Capacity constraints
        for p in producers:
            model.addConstr(
                gp.quicksum(x[p,c] for c in contracts) <= capacities[p],
                name=f"Capacity_{p}"
            )
        
        # Contract fulfillment constraints
        for c in contracts:
            model.addConstr(
                gp.quicksum(x[p,c] for p in producers) >= contract_sizes[c],
                name=f"ContractFulfillment_{c}"
            )
        
        # Minimum contributors constraints
        for c in contracts:
            model.addConstr(
                gp.quicksum(y[p,c] for p in producers) >= min_contributors[c],
                name=f"MinContributors_{c}"
            )
        
        # Minimum delivery size constraints
        for p in producers:
            for c in contracts:
                model.addConstr(
                    x[p,c] >= min_deliveries[p] * y[p,c],
                    name=f"MinDelivery_{p}_{c}"
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
        
        model.write("contract_allocation.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Cost: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
            
    test_generator()