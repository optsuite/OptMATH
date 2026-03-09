"""Data model definitions"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class OptimizationInstance:
    """Optimization problem instance (instance generation output)"""

    subclass: str
    mathematical_expression: str
    lp_data: str
    status: str  # OPTIMAL, INFEASIBLE, UNKNOWN
    objective: Any  # float or "None"
    solve_time: Optional[float] = None
    complexity: Optional[float] = None  # Complexity score (optional)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subclass": self.subclass,
            "mathematical_expression": self.mathematical_expression,
            "lp_data": self.lp_data,
            "status": self.status,
            "objective": self.objective,
            "solve_time": self.solve_time,
            "complexity": self.complexity,
        }


@dataclass
class BacktranslationResult:
    """Backtranslation result"""

    mathematical_expression: str
    lp_data: str
    objective_value: Optional[float]
    subclass: Optional[str]
    problem_description: Optional[str] = None
    criticism: Optional[str] = None
    refined_description: Optional[str] = None
    scenario: Optional[str] = None
    token_usage: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mathematical_expression": self.mathematical_expression,
            "lp_data": self.lp_data,
            "objective_value": self.objective_value,
            "subclass": self.subclass,
            "problem_description": self.problem_description,
            "criticism": self.criticism,
            "refined_description": self.refined_description,
            "scenario": self.scenario,
            "token_usage": self.token_usage,
            "error": self.error,
            # Add standardized fields for downstream processes
            "en_question": self.problem_description,
            "en_answer": str(self.objective_value) if self.objective_value is not None else None,
        }


@dataclass
class EvaluationResult:
    """Evaluation result"""

    question: str
    gt_answer: str
    pred_answer: Optional[str]
    is_correct: bool
    execution_state: str
    variable_type: Optional[str] = None
    conversion_improved: bool = False
