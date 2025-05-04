import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Car Selection Assignment problem.
        
        Parameters:
            parameters (dict): Dictionary containing:
                - n_participants: Number of participants
                - n_cars: Number of cars
                - preference_density: Probability of a participant being interested in a car
            seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "car_selection"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Consider sets P of participants and C of cars with the following:
        - **Decision Variable**:
          - x_{p,c}: Binary variable indicating if participant p is assigned to car c
        - **Parameters**:
          - a_{p,c}: Binary parameter indicating if participant p is interested in car c
        
        $$
        \begin{aligned}
        &\text{Maximize} && \sum_{p \in P}\sum_{c \in C} x_{p,c} \\
        &\text{Subject to} && x_{p,c} \leq a_{p,c} && \forall p \in P, c \in C \\
        & && \sum_{c \in C} x_{p,c} \leq 1 && \forall p \in P \\
        & && \sum_{p \in P} x_{p,c} \leq 1 && \forall c \in C \\
        & && x_{p,c} \in \{0,1\} && \forall p \in P, c \in C
        \end{aligned}
        $$
        """
        default_parameters = {
            "n_participants": (5, 10),
            "n_cars": (5, 10),
            "preference_density": 0.3
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
        Generate a Car Selection Assignment problem instance.
        
        Returns:
            gp.Model: Configured Gurobi model for the car selection problem
        """
        # Generate random number of participants and cars
        self.n_participants = random.randint(*self.n_participants)
        self.n_cars = random.randint(*self.n_cars)
        
        # Create sets
        participants = [f"participant_{i}" for i in range(self.n_participants)]
        cars = [f"car_{i}" for i in range(self.n_cars)]
        
        # Generate random preferences
        preferences = {(p, c): 1 if random.random() < self.preference_density else 0 
                     for p in participants for c in cars}
        
        # Create Gurobi model
        model = gp.Model("CarSelection")
        model.Params.OutputFlag = 0  # Suppress Gurobi output
        
        # Create binary decision variables
        x = model.addVars(participants, cars, vtype=GRB.BINARY, name="Assignments")
        
        # Set objective: maximize total assignments
        model.setObjective(
            gp.quicksum(x[p,c] for p in participants for c in cars),
            GRB.MAXIMIZE
        )
        
        # Add constraints
        # Assignment only possible if participant is interested
        for p in participants:
            for c in cars:
                model.addConstr(x[p,c] <= preferences[p,c], name=f"Preference_{p}_{c}")
        
        # One car per participant at most
        for p in participants:
            model.addConstr(
                gp.quicksum(x[p,c] for c in cars) <= 1,
                name=f"OneCarPerParticipant_{p}"
            )
        
        # One participant per car at most
        for c in cars:
            model.addConstr(
                gp.quicksum(x[p,c] for p in participants) <= 1,
                name=f"OneParticipantPerCar_{c}"
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
        
        model.write("car_selection.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
            
    test_generator()