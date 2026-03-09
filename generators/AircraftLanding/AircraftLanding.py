import gurobipy as gp
from gurobipy import GRB
import random


class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Aircraft Landing Problem optimization problem.
        Parameters:
        parameters (dict): Dictionary containing:
            - n_aircrafts: Number of self.aricrafts
            - time_window: Tuple of (min, max) for time window
            - penalty_range: Tuple of (min, max) for penalties
            - separation_range: Tuple of (min, max) for separation times
        seed (int, optional): Random seed for reproducibility
        """
        self.problem_type = "aircraft_landing"
        self.mathematical_formulation = r"""
        ### Mathematical Model
        Minimize total cost of early and late landings subject to:
        - Order constraints between self.aricrafts
        - Separation time requirements
        - Time window constraints
        - Early/Late landing calculations
        """

        default_parameters = {
            "n_aircrafts": (2, 30),
            "time_window": (10, 300),  # 3-hour window in minutes
            "penalty_range": (10, 100),
            "separation_range": (1, 5),  # minutes
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
        Generate an Aircraft Landing Problem instance and create its Gurobi model.
        Returns:
        gp.Model: Configured Gurobi model for the aircraft landing problem
        """
        # Generate random number of self.aricrafts
        self.n_aircrafts = random.randint(*self.n_aircrafts)
        self.aricrafts = [f"aircraft_{i}" for i in range(self.n_aircrafts)]

        # Generate parameters for each aircraft
        self.target_landing = {i: random.randint(*self.time_window) for i in self.aricrafts}
        time_window_size = 30  # +/- 30 minutes around target time

        self.earliest_landing = {
            i: max(self.time_window[0], self.target_landing[i] - time_window_size)
            for i in self.aricrafts
        }
        self.latest_landing = {
            i: min(self.time_window[1], self.target_landing[i] + time_window_size)
            for i in self.aricrafts
        }

        self.penalty_before = {i: random.randint(*self.penalty_range) for i in self.aricrafts}
        self.penalty_after = {i: random.randint(*self.penalty_range) for i in self.aricrafts}

        # Generate separation times between self.aricrafts
        separation_time = {
            (i, j): random.randint(*self.separation_range)
            for i in self.aricrafts
            for j in self.aricrafts
            if i != j
        }

        # Create Gurobi model
        model = gp.Model("AircraftLanding")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Decision variables
        landing = model.addVars(self.aricrafts, vtype=GRB.CONTINUOUS, name="Landing")
        aircraft_order = model.addVars(
            [(i, j) for i in self.aricrafts for j in self.aricrafts if i != j],
            vtype=GRB.BINARY,
            name="AircraftOrder",
        )
        early = model.addVars(self.aricrafts, vtype=GRB.CONTINUOUS, name="Early")
        late = model.addVars(self.aricrafts, vtype=GRB.CONTINUOUS, name="Late")

        # Objective: minimize total penalty
        model.setObjective(
            gp.quicksum(
                self.penalty_before[i] * early[i] + self.penalty_after[i] * late[i]
                for i in self.aricrafts
            ),
            GRB.MINIMIZE,
        )

        # Constraints
        # Order constraints
        for i in self.aricrafts:
            for j in self.aricrafts:
                if i != j:
                    model.addConstr(aircraft_order[i, j] + aircraft_order[j, i] == 1)

        # Separation constraints
        for i in self.aricrafts:
            for j in self.aricrafts:
                if i != j:
                    big_M = self.latest_landing[i] - self.earliest_landing[j]
                    model.addConstr(
                        landing[j]
                        >= landing[i]
                        + separation_time[i, j] * aircraft_order[i, j]
                        - big_M * aircraft_order[j, i]
                    )

        # Time window constraints
        for i in self.aricrafts:
            model.addConstr(landing[i] >= self.earliest_landing[i])
            model.addConstr(landing[i] <= self.latest_landing[i])

        # Early/Late constraints
        for i in self.aricrafts:
            model.addConstr(early[i] >= self.target_landing[i] - landing[i])
            model.addConstr(late[i] >= landing[i] - self.target_landing[i])

        return model
    
    def print_solution(self, model):
        """
        Print the solution of the Aircraft Landing Problem in a readable format.

        Parameters:
            model (gp.Model): Solved Gurobi model
        """
        if model.Status != GRB.OPTIMAL:
            print("No optimal solution found.")
            return

        print("\n=== Aircraft Landing Schedule ===")
        print(f"Total Cost: {model.ObjVal:.2f}")
        print("\nLanding Sequence:")
        print(f"{'Aircraft':^12} {'Landing Time':^15} {'Target Time':^15} {'Early':^10} {'Late':^10} {'Cost':^10}")
        print("-" * 75)

        # Get all landing times and sort aircraft by landing time
        landing_times = {}
        for v in model.getVars():
            if v.VarName.startswith('Landing'):
                aircraft = v.VarName.split('[')[1].split(']')[0]
                landing_times[aircraft] = v.X

        sorted_aircrafts = sorted(landing_times.keys(), key=lambda x: landing_times[x])

        for aircraft in sorted_aircrafts:
            # Get variable values
            actual_time = landing_times[aircraft]
            target_time = self.target_landing[aircraft]
            
            early_val = 0
            late_val = 0
            for v in model.getVars():
                if v.VarName == f'Early[{aircraft}]':
                    early_val = v.X
                elif v.VarName == f'Late[{aircraft}]':
                    late_val = v.X
            
            cost = (self.penalty_before[aircraft] * early_val + 
                    self.penalty_after[aircraft] * late_val)
            
            print(f"{aircraft:^12} {actual_time:^15.2f} {target_time:^15.2f} "
                    f"{early_val:^10.2f} {late_val:^10.2f} {cost:^10.2f}")

        print("\nSeparation Times:")
        print(f"{'Aircraft Pair':^25} {'Separation Time':^15}")
        print("-" * 40)

        for i in sorted_aircrafts:
            for j in sorted_aircrafts:
                if i != j and landing_times[j] > landing_times[i]:
                    sep_time = landing_times[j] - landing_times[i]
                    print(f"{i:>10} → {j:<10} {sep_time:^15.2f}")

        print("\nStatistics:")
        print(f"Number of aircraft: {len(sorted_aircrafts)}")
        print(f"Total schedule span: {landing_times[sorted_aircrafts[-1]] - landing_times[sorted_aircrafts[0]]:.2f} minutes")

        # Calculate average deviation
        total_deviation = 0
        for aircraft in sorted_aircrafts:
            for v in model.getVars():
                if v.VarName == f'Early[{aircraft}]':
                    total_deviation += v.X
                elif v.VarName == f'Late[{aircraft}]':
                    total_deviation += v.X

        avg_deviation = total_deviation / len(sorted_aircrafts)
        print(f"Average deviation from target: {avg_deviation:.2f} minutes")



if __name__ == "__main__":
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
            generator.print_solution(model)
        else:
            print("No optimal solution found")
        
        print(model.NumVars, model.NumConstrs)

    test_generator()
