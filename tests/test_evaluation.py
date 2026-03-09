"""Evaluation module tests"""

import json
import tempfile

import pytest

from eval import EvaluationPipeline, ResultEvaluator, ScriptExecutor


def test_result_evaluator_exact_match():
    ev = ResultEvaluator(numerical_err_tolerance=0.05)
    assert ev.evaluate_result("10", "10") is True
    assert ev.evaluate_result("10", "11") is False


def test_result_evaluator_tolerance():
    ev = ResultEvaluator(numerical_err_tolerance=0.05)
    assert ev.evaluate_result("100", "105") is True  # 5% error
    assert ev.evaluate_result("100", "110") is False  # 10% error


def test_result_evaluator_no_solution():
    ev = ResultEvaluator()
    assert ev.evaluate_result("No Best Solution", "No Best Solution") is True
    assert ev.evaluate_result("No Best Solution", "10") is False


def test_script_executor_success():
    """Test correct code execution"""
    executor = ScriptExecutor(timeout=10)
    code = """
import gurobipy as gp
from gurobipy import GRB
model = gp.Model()
x = model.addVar(lb=0, ub=10, name="x")
model.setObjective(x, GRB.MINIMIZE)
model.addConstr(x >= 1)
model.optimize()
"""
    result = executor.execute_script(code)
    assert "execution_best_solution" in result
    assert result.get("execution_best_solution") is not None


def test_script_executor_invalid_code():
    executor = ScriptExecutor(timeout=5)
    result = executor.execute_script("print(1/0)")
    assert result["execution_state"] != "Execution Successful and Best Solution Found"


def test_evaluation_pipeline(sample_jsonl_with_code, tmp_path):
    """End-to-end evaluation test"""
    pipeline = EvaluationPipeline(
        input_file=sample_jsonl_with_code,
        output_file=str(tmp_path / "eval_out.jsonl"),
        timeout=30,
        max_workers=1,
    )
    stats = pipeline.run()
    assert "accuracy" in stats
    assert stats["total"] >= 1
