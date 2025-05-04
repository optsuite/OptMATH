import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Employee Assignment optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_restaurants: Number of restaurants
                - n_employees: Number of employees
                - n_shifts: Number of shifts
                - n_skills: Number of skills
                - demand_range: Tuple of (min, max) for staff demand
                - skill_probability: Probability of employee having a skill
                - availability_probability: Probability of employee being available for a shift
                - preference_range: Tuple of (min, max) for preference costs
                - unfulfilled_cost: Cost of unfulfilled position
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "employee_assignment"
        self.mathematical_formulation = r"""
        [Previous mathematical formulation here]
        """
        default_parameters = {
            "n_restaurants": 3,
            "n_employees": (10, 15),
            "n_shifts": 2,
            "n_skills": 2,
            "demand_range": (1, 4),
            "skill_probability": 0.7,
            "availability_probability": 0.8,
            "preference_range": (1, 5),
            "unfulfilled_cost": 100
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
        Generate an Employee Assignment problem instance.
        
        Returns:
            gp.Model: Configured Gurobi model for employee assignment
        """
        # Generate number of employees if range is provided
        if isinstance(self.n_employees, tuple):
            self.n_employees = random.randint(*self.n_employees)
        
        # Create sets
        restaurants = range(self.n_restaurants)
        employees = range(self.n_employees)
        shifts = range(self.n_shifts)
        skills = range(self.n_skills)
        
        # Generate parameters
        demand = {(r,s,k): random.randint(*self.demand_range) 
                 for r in restaurants for s in shifts for k in skills}
        
        employee_has_skill = {(e,k): 1 if random.random() < self.skill_probability else 0 
                            for e in employees for k in skills}
        
        employee_does_shift = {(e,s): 1 if random.random() < self.availability_probability else 0 
                             for e in employees for s in shifts}
        
        preference_cost = {(e,k): random.randint(*self.preference_range) 
                         for e in employees for k in skills}
        
        # Create Gurobi model
        model = gp.Model("EmployeeAssignment")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create decision variables
        x = model.addVars(restaurants, employees, shifts, skills, 
                         vtype=GRB.BINARY, name="Assignment")
        u = model.addVars(restaurants, shifts, skills, 
                         vtype=GRB.INTEGER, name="Unfulfilled")
        
        # Set objective: minimize total cost
        model.setObjective(
            gp.quicksum(self.unfulfilled_cost * u[r,s,k] 
                       for r in restaurants for s in shifts for k in skills) +
            gp.quicksum(preference_cost[e,k] * x[r,e,s,k] 
                       for r in restaurants for e in employees 
                       for s in shifts for k in skills),
            GRB.MINIMIZE
        )
        
        # Add constraints
        # Satisfy demand
        for r in restaurants:
            for s in shifts:
                for k in skills:
                    model.addConstr(
                        gp.quicksum(x[r,e,s,k] for e in employees) + u[r,s,k] == demand[r,s,k],
                        name=f"Demand_{r}_{s}_{k}"
                    )
        
        # Assignment satisfies shifts
        for e in employees:
            for s in shifts:
                model.addConstr(
                    gp.quicksum(x[r,e,s,k] for r in restaurants for k in skills) 
                    <= employee_does_shift[e,s],
                    name=f"ShiftAvail_{e}_{s}"
                )
        
        # Assignment satisfies skills
        for r in restaurants:
            for e in employees:
                for s in shifts:
                    for k in skills:
                        model.addConstr(
                            x[r,e,s,k] <= employee_has_skill[e,k],
                            name=f"SkillReq_{r}_{e}_{s}_{k}"
                        )
        
        # Maximum one shift per employee
        for e in employees:
            model.addConstr(
                gp.quicksum(x[r,e,s,k] 
                           for r in restaurants for s in shifts for k in skills) <= 1,
                name=f"OneShift_{e}"
            )
        
        # Store problem data
        self.demand = demand
        self.employee_has_skill = employee_has_skill
        self.employee_does_shift = employee_does_shift
        self.preference_cost = preference_cost
        
        return model

if __name__ == '__main__':
    import time
    def test_generator():
        generator = Generator()
        model = generator.generate_instance()
        
        start_time = time.time()
        model.optimize()
        solve_time = time.time() - start_time
        
        model.write("employee_assignment.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Cost: ${model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
            
    test_generator()