import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        """
        Initialize Farm Planning optimization problem.

        Parameters:
            See original code.
        """
        self.problem_type = "farm_planning"
        self.mathematical_formulation = """Mathematical Model (unchanged for brevity)"""
        
        default_parameters = {
            "n_crops": (3, 5),
            "n_months": (10, 12),
            "n_consumption_bundles": (2, 4),
            "yield_range": (1, 10),
            "price_range": (10, 100),
            "land_available": (100, 200),
            "labor_required_range": (1, 10),
            "water_requirement_range": (0.1, 1.0),
            "water_limit": (50, 80),
            "annual_water_available": (500, 1000),
            "wage_rates": {
                "family": 10000,
                "permanent": 15000,
                "temporary": 10
            },
            "price_of_water": 1,  # Added Price of Water (dollars per cubic km)
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
        Generate a Farm Planning problem instance and create its corresponding Gurobi model.
        """
        # Randomly select number of crops, months, and consumption bundles
        self.n_crops = random.randint(*self.n_crops)
        self.n_months = random.randint(*self.n_months)
        self.n_consumption_bundles = random.randint(*self.n_consumption_bundles)
        self.land_available = random.randint(*self.land_available)
        self.water_limit = random.randint(*self.water_limit)
        self.annual_water_available = random.randint(*self.annual_water_available)

        # Generate sets
        crops = [f"crop_{i}" for i in range(self.n_crops)]
        months = [f"month_{i}" for i in range(self.n_months)]
        consumption_bundles = [f"bundle_{i}" for i in range(self.n_consumption_bundles)]

        # Generate parameters
        yield_c = {crop: random.randint(*self.yield_range) for crop in crops}
        price_c = {crop: random.randint(*self.price_range) for crop in crops}
        labor_required = {(month, crop): random.randint(*self.labor_required_range) for month in months for crop in crops}
        water_requirement = {(month, crop): random.uniform(*self.water_requirement_range) for month in months for crop in crops}
        amount_in_bundle = {(crop, bundle): random.uniform(0.1, 1.0) for crop in crops for bundle in consumption_bundles}
        fraction_occupies_land = {(month, crop): random.uniform(0.1, 1.0) for month in months for crop in crops}  # Added here
        working_hours = 160  # Example: 160 hours per month per laborer

        # Create Gurobi model
        model = gp.Model("FarmPlanning")
        model.Params.OutputFlag = 0  # Suppress Gurobi output

        # Decision variables
        amount_planted = model.addVars(crops, vtype=GRB.CONTINUOUS, name="AmountPlanted")
        permanent_labor_hired = model.addVar(vtype=GRB.CONTINUOUS, name="PermanentLaborHired")
        temporary_labor_hired = model.addVars(months, vtype=GRB.CONTINUOUS, name="TemporaryLaborHired")
        family_labor_available = model.addVar(vtype=GRB.CONTINUOUS, name="FamilyLaborAvailable")
        sales = model.addVars(crops, vtype=GRB.CONTINUOUS, name="Sales")
        fraction_consumed = model.addVars(consumption_bundles, vtype=GRB.CONTINUOUS, name="FractionConsumed")
        bp_land = model.addVars(crops, vtype=GRB.BINARY, name="BP_Land")  # Binary variable for whether to plant crop

        # Objective function
        model.setObjective(
            gp.quicksum(price_c[crop] * sales[crop] for crop in crops) -
            self.wage_rates["family"] * family_labor_available -
            self.wage_rates["permanent"] * permanent_labor_hired -
            self.wage_rates["temporary"] * gp.quicksum(temporary_labor_hired[month] for month in months) -
            self.price_of_water * gp.quicksum(water_requirement[(month, crop)] * amount_planted[crop] for month in months for crop in crops),
            GRB.MAXIMIZE
        )

        # Constraints
        # Updated Land Limitation to include FractionOccupiesLand
        model.addConstrs(
            gp.quicksum(fraction_occupies_land[(month, crop)] * amount_planted[crop] for crop in crops) <= self.land_available
            for month in months
        )

        # Link Binary Variable BP_Land with AmountPlanted
        model.addConstrs(
            amount_planted[crop] <= self.land_available * bp_land[crop] for crop in crops
        )

        # Labor requirements
        model.addConstrs(
            gp.quicksum(labor_required[(month, crop)] * amount_planted[crop] for crop in crops) <=
            working_hours * (family_labor_available + permanent_labor_hired) + temporary_labor_hired[month]
            for month in months
        )

        # Water requirements 1
        model.addConstrs(
            gp.quicksum(water_requirement[(month, crop)] * amount_planted[crop] for crop in crops) <= self.water_limit
            for month in months
        )

        # Water requirements 2
        model.addConstr(
            gp.quicksum(water_requirement[(month, crop)] * amount_planted[crop] for month in months for crop in crops) <= self.annual_water_available
        )

        # Family consumption 1
        model.addConstrs(
            yield_c[crop] * amount_planted[crop] == gp.quicksum(amount_in_bundle[(crop, bundle)] * fraction_consumed[bundle] for bundle in consumption_bundles) + sales[crop]
            for crop in crops
        )

        # Family consumption 2
        model.addConstr(
            gp.quicksum(fraction_consumed[bundle] for bundle in consumption_bundles) == 1
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

        model.write("farm_planning.lp")
        print(f"\nTest with default parameters:")
        print(f"Solve Time: {solve_time:.2f} seconds")
        if model.Status == GRB.OPTIMAL:
            print(f"Optimal Value: {model.ObjVal:.2f}")
        else:
            print("No optimal solution found")
    test_generator()