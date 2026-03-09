import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Team Formulation optimization problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_people: Number of people (staff)
                - n_projects: Number of projects
                - n_skills: Number of skills
                - skill_range: Tuple of (min, max) for skill levels
                - required_skill_range: Tuple of (min, max) for required skill levels
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "team_formulation"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Suppose there are:
        - P: Set of people (staff)
        - C: Set of projects
        - S: Set of skills

        Parameters:
        - RequiredSkill_{c,s}: Required level of skill s for project c
        - IndividualSkill_{p,s}: Level of skill s of individual p

        Variables:
        - Assign_{p,c}: Binary variable, 1 if individual p is assigned to project c
        - AttainedSkill_{c,s}: Continuous variable, attained level of skill s for project c
        - MaxSkillShortage: Continuous variable, maximum skill shortage over all projects

        Objective:
        Minimize MaxSkillShortage

        Constraints:
        1. Each person is assigned to only one project:
           \sum_{c \in C} Assign_{p,c} = 1 \quad \forall p \in P
        2. Attained skill level for each project is the maximum level of individuals assigned to the project:
           IndividualSkill_{p,s} * Assign_{p,c} <= AttainedSkill_{c,s} \quad \forall p \in P, c \in C, s \in S
        3. The maximum skill shortage:
           RequiredSkill_{c,s} - AttainedSkill_{c,s} <= MaxSkillShortage \quad \forall c \in C, s \in S
        """
        default_parameters = {
            "n_people": (5, 8),
            "n_projects": (3, 5),
            "n_skills": (2, 3),
            "skill_range": (1, 10),
            "required_skill_range": (5, 15)
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
        Generate a Team Formulation problem instance and create its corresponding Gurobi model.
        
        This method does two things:
        1. Generates random problem data (people, projects, skills, skill levels, required skill levels)
        2. Creates and returns a configured Gurobi model ready to solve
        
        Returns:
            gp.Model: Configured Gurobi model for the team formulation problem
        """
        
        # Randomly select number of people, projects, and skills
        self.n_people = random.randint(*self.n_people)
        self.n_projects = random.randint(*self.n_projects)
        self.n_skills = random.randint(*self.n_skills)
        
        # Generate sets
        people = [f"person_{i}" for i in range(self.n_people)]
        projects = [f"project_{i}" for i in range(self.n_projects)]
        skills = [f"skill_{i}" for i in range(self.n_skills)]
        
        # Generate individual skill levels
        individual_skill = {
            (p, s): random.randint(*self.skill_range) for p in people for s in skills
        }
        
        # Generate required skill levels for projects
        required_skill = {
            (c, s): random.randint(*self.required_skill_range) for c in projects for s in skills
        }

        # Create Gurobi model
        model = gp.Model("TeamFormulation")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create binary decision variables (Assign[p,c] = 1 if person p is assigned to project c)
        assign = model.addVars(people, projects, vtype=GRB.BINARY, name="Assign")
        
        # Create continuous variables for attained skill levels and maximum skill shortage
        attained_skill = model.addVars(projects, skills, vtype=GRB.CONTINUOUS, name="AttainedSkill")
        max_skill_shortage = model.addVar(vtype=GRB.CONTINUOUS, name="MaxSkillShortage")

        # Set objective: minimize the maximum skill shortage
        model.setObjective(max_skill_shortage, GRB.MINIMIZE)

        # Add constraints
        # 1. Each person is assigned to only one project
        for p in people:
            model.addConstr(
                gp.quicksum(assign[p, c] for c in projects) == 1,
                name=f"Assignment_{p}"
            )
        
        # 2. Attained skill level for each project is the maximum level of individuals assigned to the project
        for c in projects:
            for s in skills:
                for p in people:
                    model.addConstr(
                        individual_skill[p, s] * assign[p, c] <= attained_skill[c, s],
                        name=f"SkillLevel_{p}_{c}_{s}"
                    )
        
        # 3. The maximum skill shortage
        for c in projects:
            for s in skills:
                model.addConstr(
                    required_skill[c, s] - attained_skill[c, s] <= max_skill_shortage,
                    name=f"SkillShortage_{c}_{s}"
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
        
        model.write("team_formulation.lp")

        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")

    test_generator()