import gurobipy as gp
from gurobipy import GRB
import random
import numpy as np

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Structure Based Assignment Problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_peaks: Number of peaks
                - n_acids: Number of amino acids
                - n_assignments: Number of required assignments
                - noe_density: Density of NOE relations (0-1)
                - nth: Distance threshold for NOE relations
                - cost_range: Tuple of (min, max) for assignment costs
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "structure_based_assignment"
        self.mathematical_formulation = r"""
        Min sum(i in P, j in A) c[i,j]*x[i,j]
        s.t.
        sum(i in P) x[i,j] <= 1 for all j in A
        sum(j in A) x[i,j] <= 1 for all i in P
        sum(i in P, j in A) x[i,j] = N
        x[i,j] + x[k,l] <= b[j,l] + 1 for all j,l in A, i in P, k in NOE[i]
        x[i,j] binary
        """
        
        default_parameters = {
            "n_peaks": 10,
            "n_acids": 12,
            "n_assignments": 8,
            "noe_density": 0.3,
            "nth": 5.0,
            "cost_range": (0.0, 1.0)
        }
        
        if parameters is None:
            parameters = default_parameters
        for key, value in parameters.items():
            setattr(self, key, value)
            
        self.seed = seed
        if self.seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def generate_instance(self):
        """
        Generate a Structure Based Assignment problem instance.
        
        Returns:
            gp.Model: Configured Gurobi model
        """
        # Create sets
        peaks = range(self.n_peaks)
        acids = range(self.n_acids)
        
        # Generate NOE relations for peaks
        noe_relations = {i: [] for i in peaks}
        for i in peaks:
            for j in peaks:
                if i != j and random.random() < self.noe_density:
                    noe_relations[i].append(j)
        
        # Generate distances between amino acids
        distances = {}
        for i in acids:
            for j in acids:
                if i != j:
                    distances[i,j] = random.uniform(2.0, 8.0)
                    distances[j,i] = distances[i,j]
                else:
                    distances[i,j] = 0.0
        
        # Generate binary distance indicators
        b = {(i,j): 1 if distances[i,j] < self.nth else 0 
             for i in acids for j in acids}
        
        # Generate assignment costs
        costs = {(i,j): random.uniform(*self.cost_range) 
                for i in peaks for j in acids}
        
        # Create Gurobi model
        model = gp.Model("SBA_Problem")
        model.Params.OutputFlag = 0
        
        # Decision variables
        x = model.addVars(peaks, acids, vtype=GRB.BINARY, name="x")
        
        # Objective: minimize total assignment cost
        model.setObjective(
            gp.quicksum(costs[i,j] * x[i,j] for i in peaks for j in acids),
            GRB.MINIMIZE
        )
        
        # Constraints
        # Each amino acid gets at most one peak
        model.addConstrs(
            (gp.quicksum(x[i,j] for i in peaks) <= 1 for j in acids),
            name="amino_acid_assignment"
        )
        
        # Each peak gets at most one amino acid
        model.addConstrs(
            (gp.quicksum(x[i,j] for j in acids) <= 1 for i in peaks),
            name="peak_assignment"
        )
        
        # Total number of assignments
        model.addConstr(
            gp.quicksum(x[i,j] for i in peaks for j in acids) == self.n_assignments,
            name="total_assignments"
        )
        
        # NOE constraints
        for i in peaks:
            for k in noe_relations[i]:
                for j in acids:
                    for l in acids:
                        if j != l:
                            model.addConstr(
                                x[i,j] + x[k,l] <= b[j,l] + 1,
                                name=f"NOE_{i}_{k}_{j}_{l}"
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
        
        model.write("sba_problem.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
            
    test_generator()