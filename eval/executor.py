"""Code executor and result evaluation."""

import os
import subprocess
import tempfile
from typing import Any, Dict, Optional

ADD_SCRIPT = """
if model.Status == GRB.OPTIMAL:
    print(f"Just print the best solution: {model.ObjVal}")
else:
    print("No Best Solution")
"""


class ResultEvaluator:
    """Result correctness evaluation."""

    def __init__(self, numerical_err_tolerance: float = 0.05):
        self.numerical_err_tolerance = numerical_err_tolerance

    def evaluate_result(self, gt_answer: str, pred_answer: Optional[str]) -> bool:
        if gt_answer in ["No Best Solution", "No Best Solution."]:
            return pred_answer is not None and pred_answer == gt_answer
        try:
            gt_val = gt_answer if isinstance(gt_answer, (int, float)) else float(str(gt_answer).strip())
            if pred_answer is None or pred_answer in ["No Best Solution", "No Best Solution."]:
                return False
            pred_val = float(str(pred_answer).strip())
            gt_round = round(gt_val)
            pred_round = round(pred_val)
            if gt_round == 0:
                return abs(pred_round) <= self.numerical_err_tolerance
            return abs((pred_round - gt_round) / gt_round) <= self.numerical_err_tolerance
        except (ValueError, TypeError):
            return False


class ScriptExecutor:
    """Python script executor with fallback conversion support."""

    def __init__(self, timeout: int = 300, work_dir: str = "./eval_execute"):
        self.timeout = timeout
        self.work_dir = work_dir
        os.makedirs(self.work_dir, exist_ok=True)

    def _convert_inequality(self, script: str) -> str:
        return script.replace(" > ", " >= ").replace(" < ", " <= ")

    def _convert_variable_type(self, script: str, to_integer: bool) -> str:
        if to_integer:
            return script.replace("GRB.CONTINUOUS", "GRB.INTEGER")
        return script.replace("GRB.INTEGER", "GRB.CONTINUOUS")

    def _convert_objective(self, script: str, to_max: bool) -> str:
        if to_max:
            return script.replace("GRB.MINIMIZE", "GRB.MAXIMIZE")
        return script.replace("GRB.MAXIMIZE", "GRB.MINIMIZE")

    def execute_script(self, script_content: str) -> Dict[str, Any]:
        """Execute script and parse output."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", dir=self.work_dir) as f:
            f.write((script_content + ADD_SCRIPT).encode())
            path = f.name
        try:
            proc = subprocess.run(
                ["python", path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.work_dir,
            )
            out = proc.stdout or ""
            if proc.returncode != 0:
                return {
                    "execution_result": out + (proc.stderr or ""),
                    "execution_best_solution": None,
                    "execution_state": "Execution Failed",
                }
            return self._parse_output(out)
        except subprocess.TimeoutExpired:
            return {
                "execution_result": "",
                "execution_best_solution": None,
                "execution_state": "Execution Failed: Timeout",
            }
        except Exception as e:
            return {
                "execution_result": str(e),
                "execution_best_solution": None,
                "execution_state": f"Execution Failed: {e}",
            }
        finally:
            if os.path.exists(path):
                os.remove(path)

    def _parse_output(self, output: str) -> Dict[str, Any]:
        pos = output.find("Just print the best solution:")
        if pos != -1:
            val = output[pos:].replace("Just print the best solution:", "").strip()
            if "\n" in val:
                val = val.split("\n")[0]
            return {
                "execution_result": output,
                "execution_best_solution": val,
                "execution_state": "Execution Successful and Best Solution Found",
            }
        if "No Best Solution" in output:
            return {
                "execution_result": output,
                "execution_best_solution": "No Best Solution",
                "execution_state": "Execution Successful but No Best Solution Found",
            }
        return {
            "execution_result": output,
            "execution_best_solution": None,
            "execution_state": "Execution Successful but Out of Expectation",
        }

    def execute_with_fallback(
        self, script: str, gt_answer: str, evaluator: ResultEvaluator
    ) -> Dict[str, Any]:
        """Execute script, try conversions if original result is incorrect."""
        result = self.execute_script(script)
        result["variable_type"] = "original"
        result["judge"] = evaluator.evaluate_result(str(gt_answer), result.get("execution_best_solution"))
        result["conversion_improved"] = False
        if result["judge"]:
            return result
        for modifier, args in [
            (self._convert_variable_type, (True,)),
            (self._convert_variable_type, (False,)),
            (lambda s: self._convert_inequality(s), ()),
            (lambda s: self._convert_objective(s, True), ()),
            (lambda s: self._convert_objective(s, False), ()),
        ]:
            mod_script = modifier(script, *args) if args else modifier(script)
            if mod_script == script:
                continue
            new_result = self.execute_script(mod_script)
            new_result["judge"] = evaluator.evaluate_result(
                str(gt_answer), new_result.get("execution_best_solution")
            )
            if new_result["judge"]:
                new_result["variable_type"] = (
                    "integer" if args == (True,) else "continuous" if args == (False,) else "converted"
                )
                new_result["conversion_improved"] = True
                return new_result
        return result
