import numpy as np
import gurobipy as gp
from gurobipy import GRB
import time

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Job Shop Problem instance.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - num_jobs: Number of jobs
                - num_machines: Number of machines
                - operations_per_job: Number of operations per job
                - processing_time_range: Tuple (min_time, max_time) for processing times
            seed (int): Random seed for reproducibility
        """
        default_parameters = {
            'num_jobs': (5,30),
            'num_machines': (3,50),
            'operations_per_job': (2, 8),
            'processing_time_range': (1, 10)
        }
        # Use default parameters if none are provided or if an empty dict is given
        if parameters is None or not parameters:
            parameters = default_parameters
         
        for key, value in parameters.items():
            setattr(self, key, value)
        
        self.seed = seed
        if seed is not None:
            np.random.seed(seed)

    def generate_instance(self):
        """
        Generate a Job Shop Problem instance.
        
        Generates:
            - self.jobs: Dictionary of jobs, each with a list of operations
            - self.p: Processing times p_{j,i}
            - self.m: Machines m_{j,i}
        """
        self.jobs = {}
        self.p = {}  # Processing times
        self.m = {}  # Machines for operations
        
        self.num_jobs = np.random.randint(*self.num_jobs)
        self.num_machines = np.random.randint(*self.num_machines)

        for j in range(self.num_jobs):
            job_operations = []
            num_ops = np.random.randint(*self.operations_per_job)  # Could be variable per job if desired
            for i in range(num_ops):
                op_id = (j, i)
                # Random processing time
                p_j_i = np.random.randint(*self.processing_time_range)
                # Random machine required
                m_j_i = np.random.randint(0, self.num_machines)
                # Store
                self.p[op_id] = p_j_i
                self.m[op_id] = m_j_i
                job_operations.append(op_id)
            self.jobs[j] = job_operations  # List of operations for job j

        # Create a new model
        model = gp.Model("JobShopProblem")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Variables:
        # Start times S_{j,i}
        S = {}
        for op_id in self.p.keys():
            S[op_id] = model.addVar(lb=0.0, vtype= GRB.INTEGER, name=f"S_{op_id}")

        # Makespan C_max
        C_max = model.addVar(lb=0.0,vtype= GRB.INTEGER, name="C_max")

        # Binary variables X_{(j,i),(k,l)} for pairs of operations on same machine
        X = {}
        # For each machine, get operations that require it
        machine_ops = {}
        for m in range(self.num_machines):
            machine_ops[m] = []

        for op_id, m_j_i in self.m.items():
            machine_ops[m_j_i].append(op_id)

        big_M = 1e5  # Some large number for the Big-M constraints

        # Add precedence constraints within jobs
        for j, operations in self.jobs.items():
            num_ops = len(operations)
            for idx in range(num_ops - 1):
                op1 = operations[idx]
                op2 = operations[idx + 1]
                model.addConstr(S[op2] >= S[op1] + self.p[op1], name=f"prec_{op1}_{op2}")

        # Add machine capacity constraints
        # For each machine
        for m in range(self.num_machines):
            ops = machine_ops[m]
            for idx1 in range(len(ops)):
                op1 = ops[idx1]
                for idx2 in range(idx1 + 1, len(ops)):
                    op2 = ops[idx2]
                    # Need to decide order between op1 and op2
                    var_name = f"X_{op1}_{op2}"
                    # X_{op1_op2} = 1 if op1 precedes op2
                    X[op1, op2] = model.addVar(vtype=GRB.BINARY, name=var_name)
                    # Constraints:
                    model.addConstr(
                        S[op1] + self.p[op1] <= S[op2] + big_M * (1 - X[op1, op2]),
                        name=f"machine_{op1}_{op2}_1")
                    model.addConstr(
                        S[op2] + self.p[op2] <= S[op1] + big_M * (X[op1, op2]),
                        name=f"machine_{op1}_{op2}_2")
        # Makespan definition constraints
        for op_id in self.p.keys():
            model.addConstr(C_max >= S[op_id] + self.p[op_id], name=f"makespan_{op_id}")

        # Set objective
        model.setObjective(C_max, GRB.MINIMIZE)

        self.model = model
        self.vars = {'S': S, 'C_max': C_max, 'X': X}

        return model

    def solve(self):
        """
        Solve the Job Shop Problem using Gurobi.
        
        Returns:
            model.Status, solve_time
        """
        try:
            # Solve the model
            start_time = time.time()
            self.model.optimize()
            solve_time = time.time() - start_time
            return self.model.Status, solve_time
        except gp.GurobiError as e:
            print(f"Error: {e}")
            return GRB.LOADED, 0.0

if __name__ == '__main__':
    ################# Parameters #################
    

    # Create and solve instance
    import random
    jsp = Generator(seed=random.randint(0, 1000))
    
    model = jsp.generate_instance()
    solve_status, solve_time = jsp.solve()

    # Print results
    status_map = {
        GRB.OPTIMAL: "Optimal",
        GRB.INFEASIBLE: "Infeasible",
        GRB.UNBOUNDED: "Unbounded",
        GRB.INF_OR_UNBD: "Infeasible or Unbounded",
        GRB.LOADED: "Model Loaded",
        GRB.TIME_LIMIT: "Time Limit Reached"
    }

    print(f"Solve Status: {status_map.get(solve_status, solve_status)}")
    print(f"Solve Time: {solve_time:.2f} seconds")

    # If solved to optimality, print solution
    if solve_status == GRB.OPTIMAL:
        S = jsp.vars['S']
        C_max = jsp.vars['C_max']

        print(f"\nOptimal Makespan: {C_max.X}\n")
        for op_id, var in S.items():
            print(f"Start time of operation {op_id}: {var.X}")