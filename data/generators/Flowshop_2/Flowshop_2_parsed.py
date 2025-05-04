import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Flow Shop Scheduling optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_jobs: Number of jobs to schedule
                - n_machines: Number of machines in series
                - processing_time_range: Tuple of (min, max) for processing times
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "flow_shop_scheduling"
        self.mathematical_formulation = r"""
        ### Mathematical Model for Flow Shop Scheduling
        [Previous mathematical formulation here]
        """
        default_parameters = {
            "n_jobs": (3, 5),
            "n_machines": 3,
            "processing_time_range": (1, 5)
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
        Generate a Flow Shop Scheduling problem instance.
        
        Returns:
            gp.Model: Configured Gurobi model for the flow shop scheduling problem
        """
        # Generate random number of jobs if range is provided
        if isinstance(self.n_jobs, tuple):
            self.n_jobs = random.randint(*self.n_jobs)
        
        # Create sets
        jobs = range(self.n_jobs)
        schedules = range(self.n_jobs)  # Schedule positions equal to number of jobs
        machines = range(self.n_machines)
        
        # Generate processing times
        process_times = {(j,m): random.randint(*self.processing_time_range) 
                        for j in jobs for m in machines}
        
        # Create Gurobi model
        model = gp.Model("FlowShopScheduling")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create decision variables
        x = model.addVars(jobs, schedules, vtype=GRB.BINARY, name="JobSchedule")
        t = model.addVars(schedules, machines, lb=0, vtype=GRB.CONTINUOUS, name="StartTime")
        
        # Set objective: minimize makespan
        makespan = t[self.n_jobs-1, self.n_machines-1] + \
                  gp.quicksum(process_times[j,self.n_machines-1] * x[j,self.n_jobs-1] 
                             for j in jobs)
        model.setObjective(makespan, GRB.MINIMIZE)
        
        # Add constraints
        # One job per schedule position
        for s in schedules:
            model.addConstr(
                gp.quicksum(x[j,s] for j in jobs) == 1,
                name=f"OneJobPerSchedule_{s}"
            )
        
        # One schedule position per job
        for j in jobs:
            model.addConstr(
                gp.quicksum(x[j,s] for s in schedules) == 1,
                name=f"OneSchedulePerJob_{j}"
            )
        
        # Machine precedence constraints
        for s in schedules:
            for m in range(self.n_machines-1):
                model.addConstr(
                    t[s,m+1] >= t[s,m] + 
                    gp.quicksum(process_times[j,m] * x[j,s] for j in jobs),
                    name=f"MachinePrecedence_{s}_{m}"
                )
        
        # Job precedence constraints
        for s in range(self.n_jobs-1):
            for m in machines:
                model.addConstr(
                    t[s+1,m] >= t[s,m] + 
                    gp.quicksum(process_times[j,m] * x[j,s] for j in jobs),
                    name=f"JobPrecedence_{s}_{m}"
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
        
        model.write("flow_shop.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Makespan: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
            
    test_generator()