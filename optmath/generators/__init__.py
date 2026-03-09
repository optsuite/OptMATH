"""OptMATH Instance Generation Module

This module provides instance generation capabilities with:
- Basic instance generation from problem templates
- Difficulty-controlled generation using complexity scoring
- Feedback-driven parameter adjustment
"""

from .base import BaseGenerator
from .loader import load_generators_from_dir
from .pipeline import (
    InstanceGenerationPipeline,
    BaseInstanceGenerationPipeline,
    DifficultyLevel,
)
from .complexity import (
    ComplexityScorer,
    ComplexityWeights,
    ModelMetrics,
    check_complexity_range,
)
from .feedback import (
    FeedbackDrivenConfigGenerator,
    GeneratorConfig,
    TargetRequirements,
    GenerationFeedback,
)

__all__ = [
    # Core
    "BaseGenerator",
    "load_generators_from_dir",
    # Pipeline
    "InstanceGenerationPipeline",
    "BaseInstanceGenerationPipeline",
    "DifficultyLevel",
    # Complexity
    "ComplexityScorer",
    "ComplexityWeights",
    "ModelMetrics",
    "check_complexity_range",
    # Feedback
    "FeedbackDrivenConfigGenerator",
    "GeneratorConfig",
    "TargetRequirements",
    "GenerationFeedback",
]
