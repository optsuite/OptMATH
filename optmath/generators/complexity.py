"""Complexity scoring module for optimization problems

This module implements the complexity scoring function from the paper:
S(PD) = α_bin*N_bin + α_int*N_int + α_cont*N_cont
        + β_lin*N_lin + β_indic*N_indic + β_quad*N_quad + β_gen*N_gen
        + γ_BigM*f_BigM + δ_expr*L_avg_expr

Where:
- N_*: counts of different variable/constraint types
- f_BigM: frequency of Big-M formulations
- L_avg_expr: average expression length
- α, β, γ, δ: tunable weights
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ComplexityWeights:
    """Weights for complexity scoring function"""

    # Variable type weights
    alpha_bin: float = 1.0    # Binary variables
    alpha_int: float = 1.5    # Integer variables
    alpha_cont: float = 0.5   # Continuous variables

    # Constraint type weights
    beta_lin: float = 0.5     # Linear constraints
    beta_indic: float = 2.0   # Indicator constraints
    beta_quad: float = 2.5    # Quadratic constraints
    beta_gen: float = 3.0     # General nonlinear constraints

    # Special modeling techniques
    gamma_bigm: float = 5.0   # Big-M formulations
    delta_expr: float = 0.1   # Expression complexity


@dataclass
class ModelMetrics:
    """Metrics extracted from an optimization model"""

    # Variable counts
    num_binary: int = 0
    num_integer: int = 0
    num_continuous: int = 0

    # Constraint counts
    num_linear: int = 0
    num_indicator: int = 0
    num_quadratic: int = 0
    num_general: int = 0

    # Special features
    bigm_frequency: float = 0.0  # 0-1, proportion of constraints using Big-M
    avg_expr_length: float = 1.0   # Average terms per expression

    @property
    def total_variables(self) -> int:
        return self.num_binary + self.num_integer + self.num_continuous

    @property
    def total_constraints(self) -> int:
        return self.num_linear + self.num_indicator + self.num_quadratic + self.num_general


class ComplexityScorer:
    """Computes complexity scores for optimization models"""

    def __init__(self, weights: Optional[ComplexityWeights] = None):
        """
        Initialize complexity scorer.

        Args:
            weights: Optional custom weights for scoring function
        """
        self.weights = weights or ComplexityWeights()

    def score_from_lp_file(self, lp_content: str) -> float:
        """
        Compute complexity score from LP file content.

        Args:
            lp_content: LP file content as string

        Returns:
            Complexity score S(PD)
        """
        metrics = self._extract_metrics_from_lp(lp_content)
        return self._compute_score(metrics)

    def score_from_model(self, model) -> float:
        """
        Compute complexity score from Gurobi model.

        Args:
            model: Gurobi model object

        Returns:
            Complexity score S(PD)
        """
        metrics = self._extract_metrics_from_model(model)
        return self._compute_score(metrics)

    def _compute_score(self, metrics: ModelMetrics) -> float:
        """Compute weighted score from metrics"""
        score = (
            # Variable contributions
            self.weights.alpha_bin * metrics.num_binary +
            self.weights.alpha_int * metrics.num_integer +
            self.weights.alpha_cont * metrics.num_continuous +

            # Constraint contributions
            self.weights.beta_lin * metrics.num_linear +
            self.weights.beta_indic * metrics.num_indicator +
            self.weights.beta_quad * metrics.num_quadratic +
            self.weights.beta_gen * metrics.num_general +

            # Special features
            self.weights.gamma_bigm * metrics.bigm_frequency * 100 +  # Scale up
            self.weights.delta_expr * metrics.avg_expr_length
        )
        return score

    def _extract_metrics_from_lp(self, lp_content: str) -> ModelMetrics:
        """Extract metrics from LP file content"""
        metrics = ModelMetrics()

        # Count variable declarations
        # Variables: x, y, z (binary/integer/continuous)
        var_pattern = r'(?:binary|integer|general|positives?)?\s*([\w\s,]+?)(?:\s*:)'
        for match in re.finditer(r'\b(?:binary|integer|general)\b', lp_content, re.IGNORECASE):
            if 'binary' in match.group().lower():
                # Extract count from variable declarations
                continue

        # Simple heuristic: count variables from bounds section
        bounds_section = re.search(r'Bounds:(.*?)(?:\n\S|\nEnd)', lp_content, re.DOTALL)
        if bounds_section:
            var_lines = bounds_section.group(1).split('\n')
            unique_vars = set()
            for line in var_lines:
                # Extract variable names
                vars_in_line = re.findall(r'\b([a-zA-Z_]\w*)\b', line)
                unique_vars.update(vars_in_line)
            metrics.num_continuous = len(unique_vars)

        # Count constraints
        # Subject To / s.t. section
        constraints_match = re.search(r'(?:Subject To|s\.t\.)(.*?)(?:\nEnd|$)', lp_content, re.DOTALL | re.IGNORECASE)
        if constraints_match:
            constraints_text = constraints_match.group(1)
            constraint_lines = [line.strip() for line in constraints_text.split('\n') if line.strip() and not line.strip().startswith('\\')]

            for line in constraint_lines:
                # Classify constraint type
                if '*' in line or '^2' in line:
                    metrics.num_quadratic += 1
                elif any(keyword in line for keyword in ['=', '<=', '>=']):
                    metrics.num_linear += 1

                # Check for Big-M (large constant multiplied by binary)
                if re.search(r'\d{3,}\s*\*\s*[a-zA-Z_]', line):
                    metrics.bigm_frequency += 1

                # Estimate expression length
                terms = re.findall(r'[+-]?\s*[\d.]*\s*\*\s*[a-zA-Z_]\w*', line)
                if terms:
                    metrics.avg_expr_length += len(terms)

        # Normalize Big-M frequency
        if metrics.total_constraints > 0:
            metrics.bigm_frequency = metrics.bigm_frequency / metrics.total_constraints
        if metrics.total_constraints > 0:
            metrics.avg_expr_length = metrics.avg_expr_length / metrics.total_constraints

        return metrics

    def _extract_metrics_from_model(self, model) -> ModelMetrics:
        """Extract metrics from Gurobi model object"""
        metrics = ModelMetrics()

        # Get variable info
        for v in model.getVars():
            vtype = v.VType
            if vtype == 1:  # GRB.BINARY
                metrics.num_binary += 1
            elif vtype == 2:  # GRB.INTEGER
                metrics.num_integer += 1
            else:  # GRB.CONTINUOUS
                metrics.num_continuous += 1

        # Get constraint info
        for c in model.getConstrs():
            # Check constraint type by analyzing expression
            # This is simplified; actual implementation would need deeper analysis
            metrics.num_linear += 1

        # Average expression length (simplified)
        if metrics.total_constraints > 0:
            metrics.avg_expr_length = 3.0  # Default estimate

        return metrics


def check_complexity_range(
    score: float,
    min_score: float,
    max_score: float
) -> bool:
    """Check if score is within target range"""
    return min_score <= score <= max_score
