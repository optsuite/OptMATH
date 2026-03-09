import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize the Military Personnel Deployment Problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_tasks: Number of tasks
                - n_skills: Number of skills
                - cost_range: Tuple of (min, max) for deployment costs
                - skill_requirement_range: Tuple of (min, max) for skill requirements per task
                - total_soldiers: Total number of soldiers available
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "military_personnel_deployment"
        self.mathematical_formulation = r"""
        ### Mathematical Model\nSuppose there are n tasks and s skills. Each task i (where i = 1, 2, ..., n) has the following attributes:\n- **Cost** c_i: The cost of deploying a soldier to task i.\n- **Skill Requirement** k_{i,s}: The number of soldiers with skill s required for task i.\n- **Decision Variable** x_i: The number of soldiers assigned to task i.\n\nAdditionally, the total number of soldiers available is denoted by the constant a.\n$$\n\\begin{aligned}\n&\\text{Minimize} && \\sum_{i=1}^n c_i x_i \\\\\n&\\text{Subject to} && \\sum_{i=1}^n x_i \\leq a \\\\\n& && x_i \\geq \\sum_{s=1}^s k_{i,s} \\quad \\forall i = 1, 2, \\ldots, n \\\\\n& && x_i \\in \\mathbb{Z}^+ \\quad \\forall i = 1, 2, \\ldots, n\n\\end{aligned}\n$$
        """
        default_parameters = {
            "n_tasks": (3, 5),
            "n_skills": (2, 4),
            "cost_range": (1, 10),
            "skill_requirement_range": (1, 5),
            "total_soldiers": (80, 120)
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
        Generate a Military Personnel Deployment problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (tasks, costs, skill requirements, total soldiers)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the personnel deployment problem
        """
        
        # Randomly select number of tasks and skills
        self.n_tasks = random.randint(*self.n_tasks)
        self.n_skills = random.randint(*self.n_skills)
        
        # Generate tasks and skills
        tasks = [f"task_{i}" for i in range(self.n_tasks)]
        skills = [f"skill_{s}" for s in range(self.n_skills)]
        
        # Generate deployment costs for each task
        task_costs = {task: random.randint(*self.cost_range) for task in tasks}
        
        # Generate skill requirements for each task and skill
        skill_requirements = {
            (task, skill): random.randint(*self.skill_requirement_range)
            for task in tasks for skill in skills
        }
        
        # Total number of soldiers available
        total_soldiers = random.randint(*self.total_soldiers)

        # Create Gurobi model
        model = gp.Model("MilitaryPersonnelDeployment")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create integer decision variables (x[i] = number of soldiers assigned to task i)
        x = model.addVars(tasks, vtype=GRB.INTEGER, name="Soldiers")

        # Set objective: minimize total deployment cost
        model.setObjective(
            gp.quicksum(task_costs[i] * x[i] for i in tasks),
            GRB.MINIMIZE
        )

        # Add constraints:
        # 1. Total number of soldiers deployed must not exceed available soldiers
        model.addConstr(
            gp.quicksum(x[i] for i in tasks) <= total_soldiers,
            name="TotalSoldiers"
        )

        # 2. Each task must meet its skill requirements
        for i in tasks:
            model.addConstr(
                x[i] >= gp.quicksum(skill_requirements[i, s] for s in skills),
                name=f"SkillRequirement_{i}"
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
        
        model.write("military_personnel_deployment.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()