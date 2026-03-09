"""Feedback-driven configuration generator for instance generation

This module implements Algorithm 1 from the paper:
Feedback-Driven Problem Data Generation

The algorithm uses LLM to iteratively adjust generator parameters
to produce instances within target complexity bounds.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..llm import create_llm_client
from .complexity import ComplexityScorer, ModelMetrics

logger = logging.getLogger(__name__)


@dataclass
class GeneratorConfig:
    """Configuration parameters for instance generator"""

    # Variable parameters
    num_vars_min: int = 10
    num_vars_max: int = 50
    binary_ratio: float = 0.2      # Ratio of binary variables
    integer_ratio: float = 0.3     # Ratio of integer variables

    # Constraint parameters
    num_constrs_min: int = 5
    num_constrs_max: int = 30
    bigm_ratio: float = 0.0        # Ratio of constraints using Big-M

    # Structure parameters
    avg_expr_length: float = 3.0    # Average terms per expression
    constraint_diversity: float = 0.5  # 0-1, diversity of constraint types

    # Domain-specific parameters (extensible)
    domain_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "num_vars_min": self.num_vars_min,
            "num_vars_max": self.num_vars_max,
            "binary_ratio": self.binary_ratio,
            "integer_ratio": self.integer_ratio,
            "num_constrs_min": self.num_constrs_min,
            "num_constrs_max": self.num_constrs_max,
            "bigm_ratio": self.bigm_ratio,
            "avg_expr_length": self.avg_expr_length,
            "constraint_diversity": self.constraint_diversity,
            "domain_params": self.domain_params,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeneratorConfig":
        """Create from dictionary"""
        return cls(
            num_vars_min=data.get("num_vars_min", 10),
            num_vars_max=data.get("num_vars_max", 50),
            binary_ratio=data.get("binary_ratio", 0.2),
            integer_ratio=data.get("integer_ratio", 0.3),
            num_constrs_min=data.get("num_constrs_min", 5),
            num_constrs_max=data.get("num_constrs_max", 30),
            bigm_ratio=data.get("bigm_ratio", 0.0),
            avg_expr_length=data.get("avg_expr_length", 3.0),
            constraint_diversity=data.get("constraint_diversity", 0.5),
            domain_params=data.get("domain_params", {}),
        )


@dataclass
class GenerationFeedback:
    """Feedback from generated instances"""

    num_samples: int = 0
    avg_complexity: float = 0.0
    min_complexity: float = 0.0
    max_complexity: float = 0.0
    avg_solve_time: float = 0.0
    feasibility_rate: float = 0.0
    within_target_range: bool = False

    # Per-metric breakdown
    avg_num_vars: int = 0
    avg_num_constrs: int = 0
    binary_ratio: float = 0.0
    bigm_ratio: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "num_samples": self.num_samples,
            "avg_complexity": self.avg_complexity,
            "min_complexity": self.min_complexity,
            "max_complexity": self.max_complexity,
            "avg_solve_time": self.avg_solve_time,
            "feasibility_rate": self.feasibility_rate,
            "within_target_range": self.within_target_range,
            "avg_num_vars": self.avg_num_vars,
            "avg_num_constrs": self.avg_num_constrs,
            "binary_ratio": self.binary_ratio,
            "bigm_ratio": self.bigm_ratio,
        }


@dataclass
class TargetRequirements:
    """Target requirements for generated instances"""

    complexity_min: float = 50.0
    complexity_max: float = 150.0
    solve_time_min: float = 0.1
    solve_time_max: float = 30.0
    feasibility_target: float = 0.9
    num_samples: int = 10  # N samples per iteration


class FeedbackDrivenConfigGenerator:
    """
    Implements Algorithm 1: Feedback-Driven Problem Data Generation

    Uses LLM to iteratively adjust generator parameters to produce
    instances within target complexity bounds.
    """

    # Prompts
    INITIAL_CONFIG_PROMPT = """You are an optimization expert. I need to configure parameters for an LP/MIP instance generator.

Target Requirements:
- Complexity score range: [{complexity_min}, {complexity_max}]
- Solve time range: [{solve_time_min}s, {solve_time_max}s]
- Feasibility rate: >= {feasibility_target}
- Problem class: {problem_class}

Suggest a configuration with these parameters:
- num_vars_min, num_vars_max: Range for total variables
- binary_ratio: Ratio of binary variables (0-1)
- integer_ratio: Ratio of integer variables (0-1)
- num_constrs_min, num_constrs_max: Range for number of constraints
- bigm_ratio: Ratio of constraints using Big-M (0-1)
- avg_expr_length: Average terms per expression (1-10)
- constraint_diversity: Diversity of constraint types (0-1)

Respond ONLY with a JSON object containing these parameters.
"""

    REFINEMENT_PROMPT = """The current configuration produced instances with these statistics:

{feedback}

Current Configuration:
{current_config}

Target Requirements:
- Complexity: [{complexity_min}, {complexity_max}] (Current avg: {avg_complexity})
- Solve time: <= {solve_time_max}s (Current avg: {avg_solve_time}s)
- Feasibility: >= {feasibility_target} (Current: {feasibility_rate})

Please adjust the configuration to better meet the targets.
Consider:
- If complexity is too high: reduce variables/constraints, simplify expressions
- If complexity is too low: increase variables/constraints, add complexity
- If solve time is too high: reduce problem size or complexity
- If feasibility is too low: adjust constraint formulations

Respond ONLY with a JSON object containing the adjusted parameters.
"""

    def __init__(
        self,
        model_name: str = "deepseek_official",
        max_iterations: int = 5,
        scorer: Optional[ComplexityScorer] = None,
    ):
        """
        Initialize feedback-driven config generator.

        Args:
            model_name: LLM model to use
            max_iterations: Maximum refinement iterations
            scorer: Optional complexity scorer
        """
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.scorer = scorer or ComplexityScorer()
        self.llm = create_llm_client(model_name)

    def generate_config(
        self,
        problem_class: str,
        requirements: TargetRequirements,
        initial_config: Optional[GeneratorConfig] = None,
    ) -> Optional[GeneratorConfig]:
        """
        Run feedback-driven configuration generation.

        Args:
            problem_class: Name/description of problem class
            requirements: Target complexity/time requirements
            initial_config: Optional starting configuration

        Returns:
            Valid configuration, or None if not found
        """
        config = initial_config

        for iteration in range(self.max_iterations):
            logger.info(f"Configuration iteration {iteration + 1}/{self.max_iterations}")

            # Step 1: Initialize or refine config
            if config is None:
                config = self._initialize_config(problem_class, requirements)
                if config is None:
                    logger.error("Failed to initialize configuration")
                    return None

            # Step 2: Generate test instances
            # Note: This would require calling the actual generator
            # For now, we'll create a feedback placeholder
            feedback = self._create_placeholder_feedback(config, requirements)

            # Step 3: Check if requirements are met
            if requirements.complexity_min <= feedback.avg_complexity <= requirements.complexity_max:
                if feedback.avg_solve_time <= requirements.solve_time_max:
                    if feedback.feasibility_rate >= requirements.feasibility_target:
                        logger.info(f"Found valid configuration in {iteration + 1} iterations")
                        return config

            # Step 4: Refine configuration
            config = self._refine_config(
                config,
                feedback,
                requirements,
                problem_class
            )
            if config is None:
                logger.error("Failed to refine configuration")
                return None

        logger.warning(f"Failed to find valid configuration after {self.max_iterations} iterations")
        return None

    def _initialize_config(
        self,
        problem_class: str,
        requirements: TargetRequirements,
    ) -> Optional[GeneratorConfig]:
        """Initialize configuration using LLM"""
        prompt = self.INITIAL_CONFIG_PROMPT.format(
            complexity_min=requirements.complexity_min,
            complexity_max=requirements.complexity_max,
            solve_time_min=requirements.solve_time_min,
            solve_time_max=requirements.solve_time_max,
            feasibility_target=requirements.feasibility_target,
            problem_class=problem_class,
        )

        try:
            response, _ = self.llm.complete(
                message=prompt,
                system_message="You are an optimization modeling expert.",
                temperature=0.7,
                max_tokens=1000,
            )

            # Extract JSON from response
            config_dict = self._extract_json(response)
            if config_dict:
                return GeneratorConfig.from_dict(config_dict)
        except Exception as e:
            logger.error(f"Error initializing config: {e}")

        return None

    def _refine_config(
        self,
        current_config: GeneratorConfig,
        feedback: GenerationFeedback,
        requirements: TargetRequirements,
        problem_class: str,
    ) -> Optional[GeneratorConfig]:
        """Refine configuration using LLM with feedback"""
        prompt = self.REFINEMENT_PROMPT.format(
            feedback=json.dumps(feedback.to_dict(), indent=2),
            current_config=json.dumps(current_config.to_dict(), indent=2),
            complexity_min=requirements.complexity_min,
            complexity_max=requirements.complexity_max,
            solve_time_max=requirements.solve_time_max,
            feasibility_target=requirements.feasibility_target,
            avg_complexity=feedback.avg_complexity,
            avg_solve_time=feedback.avg_solve_time,
            feasibility_rate=feedback.feasibility_rate,
        )

        try:
            response, _ = self.llm.complete(
                message=prompt,
                system_message="You are an optimization modeling expert.",
                temperature=0.7,
                max_tokens=1000,
            )

            # Extract JSON from response
            config_dict = self._extract_json(response)
            if config_dict:
                return GeneratorConfig.from_dict(config_dict)
        except Exception as e:
            logger.error(f"Error refining config: {e}")

        return None

    def _create_placeholder_feedback(
        self,
        config: GeneratorConfig,
        requirements: TargetRequirements,
    ) -> GenerationFeedback:
        """
        Create placeholder feedback for testing.

        In production, this would:
        1. Generate N instances using the config
        2. Compute complexity scores
        3. Measure solve times
        4. Check feasibility

        For now, returns estimated feedback based on config.
        """
        # Estimate complexity from config
        est_vars = (config.num_vars_min + config.num_vars_max) / 2
        est_constrs = (config.num_constrs_min + config.num_constrs_max) / 2

        # Simplified complexity estimation
        estimated_complexity = (
            1.0 * est_vars * config.binary_ratio +
            1.5 * est_vars * config.integer_ratio +
            0.5 * est_vars * (1 - config.binary_ratio - config.integer_ratio) +
            0.5 * est_constrs +
            5.0 * config.bigm_ratio * 100 +
            0.1 * config.avg_expr_length
        )

        return GenerationFeedback(
            num_samples=requirements.num_samples,
            avg_complexity=estimated_complexity,
            min_complexity=estimated_complexity * 0.9,
            max_complexity=estimated_complexity * 1.1,
            avg_solve_time=estimated_complexity / 10,  # Rough estimate
            feasibility_rate=0.95,  # Assumed
            within_target_range=requirements.complexity_min <= estimated_complexity <= requirements.complexity_max,
            avg_num_vars=int(est_vars),
            avg_num_constrs=int(est_constrs),
            binary_ratio=config.binary_ratio,
            bigm_ratio=config.bigm_ratio,
        )

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response"""
        # Try to find JSON in response
        import re

        # Look for JSON object
        match = re.search(r'\{[^{}]*\{.*\}[^{}]*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Try direct parse
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        return None
