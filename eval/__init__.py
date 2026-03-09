"""Benchmark evaluation module

Supports code generation and execution evaluation for different benchmarks.
"""

__all__ = ["BenchmarkEvaluator", "EvaluationPipeline", "ScriptExecutor", "ResultEvaluator"]

# Lazy import to avoid relative import issues
def __getattr__(name):
    if name == "BenchmarkEvaluator":
        from .evaluator import BenchmarkEvaluator
        return BenchmarkEvaluator
    if name == "EvaluationPipeline":
        from .evaluator import EvaluationPipeline
        return EvaluationPipeline
    if name == "ScriptExecutor":
        from .executor import ScriptExecutor
        return ScriptExecutor
    if name == "ResultEvaluator":
        from .executor import ResultEvaluator
        return ResultEvaluator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
