"""pytest fixtures"""

import json
import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def generators_dir(tmp_path):
    """Create mini generator directory for testing. base_dir should be parent directory containing multiple generator subdirectories."""
    base = Path(__file__).parent.parent.parent / "generators"
    if base.exists():
        return str(base)
    # Create mock generator
    gen_dir = tmp_path / "diet_mock"
    gen_dir.mkdir()
    (gen_dir / "metadata.json").write_text(
        json.dumps({
            "subclass": "diet",
            "math_formula": "minimize cost",
        }, indent=2)
    )
    code = '''
import gurobipy as gp
from gurobipy import GRB
import random

class Generator:
    def __init__(self, parameters=None, seed=None):
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def generate_instance(self):
        model = gp.Model("diet")
        model.Params.OutputFlag = 0
        x = model.addVar(lb=0, ub=10, name="x")
        model.setObjective(x, GRB.MINIMIZE)
        model.addConstr(x >= 1)
        return model
'''
    (gen_dir / "diet_mock.py").write_text(code)
    return str(tmp_path)


@pytest.fixture
def sample_instances_json(tmp_path):
    """Sample instance JSON"""
    data = [
        {
            "subclass": "diet",
            "mathematical_expression": "min cost",
            "lp_data": "Minimize\n  x\nSubject To\n  x >= 1\nBounds\n  x >= 0\nEnd",
            "status": "OPTIMAL",
            "objective": 1.0,
        }
    ]
    path = tmp_path / "instances.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return str(path)


@pytest.fixture
def sample_jsonl_with_code(tmp_path):
    """Sample JSONL with generated code"""
    path = tmp_path / "generated.jsonl"
    with open(path, "w") as f:
        obj = {
            "en_question": "Minimize x subject to x >= 1",
            "en_answer": "1",
            "en_math_model_code": """```python
import gurobipy as gp
from gurobipy import GRB
model = gp.Model()
x = model.addVar(lb=0, ub=10, name="x")
model.setObjective(x, GRB.MINIMIZE)
model.addConstr(x >= 1)
model.optimize()
```""",
        }
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return str(path)
