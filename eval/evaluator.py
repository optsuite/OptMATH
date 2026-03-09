"""Benchmark evaluator

Supports code generation and evaluation for different benchmarks.
Result format: benchmark_name/model_name/pass_n/timestamp/
"""

import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tqdm import tqdm

# Try multiple import methods
try:
    # Run as optmath.benchmark.evaluator
    from ..core.config import load_config
    from ..llm import create_llm_client
    from .executor import ResultEvaluator, ScriptExecutor
except (ImportError, ValueError):
    try:
        # Run as benchmark.evaluator (direct import)
        from optmath.core.config import load_config
        from optmath.llm import create_llm_client
        from eval.executor import ResultEvaluator, ScriptExecutor
    except ImportError:
        # Run as standalone module
        import sys
        from pathlib import Path
        # Add project root to path
        project_root = Path(__file__).parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from optmath.core.config import load_config
        from optmath.llm import create_llm_client
        from eval.executor import ResultEvaluator, ScriptExecutor


@dataclass
class EvalConfig:
    """Evaluation configuration"""

    benchmark_name: str = "optmath"
    model_name: str = "deepseek_official"
    pass_n: int = 1  # Nth attempt
    temperature: float = 0.8
    max_tokens: int = 8192
    timeout: int = 100
    max_workers: int = 50
    numerical_tolerance: float = 0.05
    enable_conversion: bool = True
    question_field: str = "en_question"
    answer_field: str = "en_answer"
    code_field: str = "en_math_model_code"


@dataclass
class GenerationResult:
    """Code generation result"""

    index: int
    question: str
    ground_truth: Optional[float]
    generated_code: str
    raw_output: str
    error: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ExecutionResult:
    """Code execution result"""

    index: int
    execution_state: str
    predicted_value: Optional[float]
    execution_output: str
    is_correct: bool
    judge_reason: str = ""
    execution_time: float = 0.0
    conversion_improved: bool = False
    conversion_mode: str = "disabled"


@dataclass
class EvalMetrics:
    """Evaluation metrics"""

    total: int = 0
    code_generated: int = 0
    code_executed: int = 0
    correct: int = 0
    accuracy: float = 0.0
    generation_success_rate: float = 0.0
    execution_success_rate: float = 0.0
    total_tokens: int = 0
    avg_tokens_per_sample: float = 0.0
    total_time: float = 0.0


class BenchmarkEvaluator:
    """Benchmark evaluator"""

    # Code extraction patterns
    CODE_PATTERN = re.compile(r"```(?:python)?\n*(.*?)```", re.DOTALL)
    CODE_FIELDS = ["en_math_model_code", "code", "generated_code"]

    # Code output markers
    SOLUTION_MARKER = "Just print the best solution:"
    NO_SOLUTION_MARKER = "No Best Solution"

    def __init__(self, config: Optional[EvalConfig] = None):
        """Initialize evaluator

        Args:
            config: Evaluation config, uses default if None
        """
        self.config = config or EvalConfig()
        self.llm = None
        self.logger = self._setup_logger()
        self.executor = ScriptExecutor(timeout=self.config.timeout)
        self.result_evaluator = ResultEvaluator(self.config.numerical_tolerance)

        # Create output directory
        self.output_dir = self._create_output_dir()
        self.logger.info(f"Output directory: {self.output_dir}")

    def _setup_logger(self) -> logging.Logger:
        """Setup logger"""
        logger = logging.getLogger("benchmark.evaluator")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _create_output_dir(self) -> Path:
        """Create output directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = (
            Path("benchmark_results")
            / self.config.benchmark_name
            / self.config.model_name
            / f"pass_{self.config.pass_n}"
            / timestamp
        )
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _extract_code(self, content: str) -> Optional[str]:
        """Extract Python code from generated content"""
        for key in self.CODE_FIELDS:
            if key in content and isinstance(content, dict):
                content = content[key]

        # Method 1: Extract code block using regex
        match = self.CODE_PATTERN.search(content)
        if match:
            code = match.group(1).strip()
            if code and ("import gurobipy" in code or "import gp" in code):
                return code

        # Method 2: Find import gurobipy
        if "import gurobipy" in content:
            idx = content.find("import gurobipy")
            remaining = content[idx:]
            if "```" in remaining[20:]:
                end_idx = remaining.find("```", 20)
                code = remaining[:end_idx].strip()
                if code.startswith("```python"):
                    code = code[9:].strip()
                elif code.startswith("```"):
                    code = code[3:].strip()
                return code
            else:
                return content[idx:].strip()

        return None

    def _generate_code(self, example: Dict[str, Any], index: int) -> GenerationResult:
        """Generate code for a single example"""
        try:
            if self.llm is None:
                self.llm = create_llm_client(self.config.model_name)
            question = example.get(self.config.question_field, "")
            if not question:
                raise ValueError(f"Missing {self.config.question_field} field")

            # Build CoT prompt
            prompt = self._build_cot_prompt(question)

            # Call LLM to generate code
            content, usage = self.llm.complete(
                message=prompt,
                system_message="You are an expert in operations research and optimization.",
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            # Extract code
            code = self._extract_code(content) or ""

            ground_truth = example.get(self.config.answer_field)

            return GenerationResult(
                index=index,
                question=question,
                ground_truth=float(ground_truth) if ground_truth else None,
                generated_code=code,
                raw_output=content,
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
            )

        except Exception as e:
            self.logger.error(f"Generation failed (index={index}): {e}")
            return GenerationResult(
                index=index,
                question=example.get(self.config.question_field, ""),
                ground_truth=example.get(self.config.answer_field),
                generated_code="",
                raw_output="",
                error=str(e),
            )

    def _build_cot_prompt(self, question: str) -> str:
        """Build Chain-of-Thought prompt"""
        return f"""Below is an operations research question. Build a mathematical model and corresponding python code using `gurobipy` that appropriately addresses the question.

# Question:
{question}

# Instructions:
1. Output ONLY the Python code within a ```python code block
2. Start your code with: import gurobipy as gp
3. Name your model variable as `model`
4. Use <= instead of < in Gurobi constraints
5. After solving, print the objective value using: print(model.objVal)

# Response:
```python
import gurobipy as gp
from gurobipy import GRB

# Your code here

model.optimize()
print(model.objVal)
```"""

    def _execute_code(
        self, generation_result: GenerationResult
    ) -> ExecutionResult:
        """Execute generated code"""
        if not generation_result.generated_code:
            return ExecutionResult(
                index=generation_result.index,
                execution_state="No code generated",
                predicted_value=None,
                execution_output="",
                is_correct=False,
                judge_reason="No code",
                conversion_mode="disabled",
            )

        start_time = time.time()

        try:
            if self.config.enable_conversion:
                raw_result = self.executor.execute_with_fallback(
                    generation_result.generated_code,
                    generation_result.ground_truth,
                    self.result_evaluator,
                )
            else:
                raw_result = self.executor.execute_script(generation_result.generated_code)
                raw_result["judge"] = self.result_evaluator.evaluate_result(
                    generation_result.ground_truth,
                    raw_result.get("execution_best_solution"),
                )
                raw_result["conversion_improved"] = False
                raw_result["variable_type"] = "original"

            execution_time = time.time() - start_time
            predicted_value = self._normalize_predicted_value(
                raw_result.get("execution_best_solution")
            )
            is_correct = bool(raw_result.get("judge", False))
            judge_reason = self._build_judge_reason(
                predicted_value,
                generation_result.ground_truth,
                is_correct,
            )

            return ExecutionResult(
                index=generation_result.index,
                execution_state=raw_result.get("execution_state", "Execution Failed"),
                predicted_value=predicted_value,
                execution_output=raw_result.get("execution_result", ""),
                is_correct=is_correct,
                judge_reason=judge_reason,
                execution_time=execution_time,
                conversion_improved=bool(raw_result.get("conversion_improved", False)),
                conversion_mode=str(raw_result.get("variable_type", "original")),
            )

        except Exception as e:
            return ExecutionResult(
                index=generation_result.index,
                execution_state=f"Execution Failed: {str(e)}",
                predicted_value=None,
                execution_output="",
                is_correct=False,
                judge_reason=str(e),
                execution_time=time.time() - start_time,
                conversion_mode="error",
            )

    def _normalize_predicted_value(self, predicted: Any) -> Optional[float]:
        """Normalize execution output to float when possible."""
        if predicted in [None, self.NO_SOLUTION_MARKER, "No Best Solution."]:
            return None
        try:
            return float(predicted)
        except (ValueError, TypeError):
            return None

    def _build_judge_reason(
        self,
        predicted: Optional[float],
        ground_truth: Any,
        is_correct: bool,
    ) -> str:
        """Build judge reason string."""
        if ground_truth is None:
            return "No ground truth"
        if predicted is None:
            return "No prediction"
        return (
            f"Correct: {predicted} vs {ground_truth}"
            if is_correct
            else f"Wrong: {predicted} vs {ground_truth}"
        )

    def evaluate(
        self,
        input_file: str,
        dataset_name: Optional[str] = None,
        skip_generation: bool = False,
    ) -> EvalMetrics:
        """Evaluate benchmark

        Args:
            input_file: Input data file path (JSON or JSONL)
            dataset_name: Dataset name for logging
            skip_generation: Skip code generation (assume generated.jsonl exists)

        Returns:
            Evaluation metrics
        """
        start_time = time.time()
        dataset_name = dataset_name or Path(input_file).stem

        self.logger.info(f"Starting evaluation: {dataset_name}")
        self.logger.info(f"Input file: {input_file}")
        self.logger.info(f"Model: {self.config.model_name}")
        self.logger.info(f"Pass: {self.config.pass_n}")

        # Load data
        examples = self._load_input_data(input_file)
        self.logger.info(f"Loaded data: {len(examples)} samples")

        # Phase 1: Code generation
        if skip_generation:
            self.logger.info(f"Skipping code generation, using input file: {input_file}")
            generation_results = self._load_generation_results(input_file)
            # Also save to output directory for record
            generated_file = self.output_dir / "generated.jsonl"
            self._save_generation_results(generation_results, generated_file)
        else:
            self.logger.info("Phase 1: Code generation...")
            generation_results = self._generate_codes(examples)
            generated_file = self.output_dir / "generated.jsonl"
            self._save_generation_results(generation_results, generated_file)

        # Phase 2: Code execution
        self.logger.info("Phase 2: Code execution...")
        execution_results = self._execute_codes(generation_results)

        # Phase 3: Calculate metrics
        self.logger.info("Phase 3: Calculate metrics...")
        metrics = self._calculate_metrics(
            generation_results, execution_results, time.time() - start_time
        )

        # Save evaluation results
        eval_file = self.output_dir / "eval.jsonl"
        self._save_eval_results(
            generation_results, execution_results, eval_file
        )

        # Save metrics summary
        metrics_file = self.output_dir / "metrics.json"
        self._save_metrics(metrics, metrics_file)

        # Print results
        self._print_results(metrics)

        return metrics

    def _load_input_data(self, input_file: str) -> List[Dict[str, Any]]:
        """Load input data"""
        examples = []
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content.startswith("["):
                # JSON format
                data = json.loads(content)
                examples = data if isinstance(data, list) else [data]
            else:
                # JSONL format
                for line in content.split("\n"):
                    if line.strip():
                        examples.append(json.loads(line))
        return examples

    def _generate_codes(
        self, examples: List[Dict[str, Any]]
    ) -> List[GenerationResult]:
        """Batch generate code"""
        results = []

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(self._generate_code, ex, i): (ex, i)
                for i, ex in enumerate(examples)
            }

            for future in tqdm(
                as_completed(futures), total=len(futures), desc="Generating code"
            ):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Generation failed: {e}")
                    example, index = futures[future]
                    results.append(
                        GenerationResult(
                            index=index,
                            question=example.get(self.config.question_field, ""),
                            ground_truth=example.get(self.config.answer_field),
                            generated_code="",
                            raw_output="",
                            error=str(e),
                        )
                    )

        # Sort by index
        results.sort(key=lambda x: x.index)
        return results

    def _execute_codes(
        self, generation_results: List[GenerationResult]
    ) -> List[ExecutionResult]:
        """Batch execute code"""
        results = []

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(self._execute_code, gen): gen
                for gen in generation_results
            }

            for future in tqdm(
                as_completed(futures), total=len(futures), desc="Executing code"
            ):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Execution failed: {e}")
                    gen_result = futures[future]
                    results.append(
                        ExecutionResult(
                            index=gen_result.index,
                            execution_state=f"Execution Failed: {str(e)}",
                            predicted_value=None,
                            execution_output="",
                            is_correct=False,
                            judge_reason=str(e),
                            conversion_mode="error",
                        )
                    )

        # Sort by index
        results.sort(key=lambda x: x.index)
        return results

    def _calculate_metrics(
        self,
        generation_results: List[GenerationResult],
        execution_results: List[ExecutionResult],
        total_time: float,
    ) -> EvalMetrics:
        """Calculate evaluation metrics"""
        total = len(generation_results)
        code_generated = sum(
            1 for r in generation_results if r.generated_code and not r.error
        )
        code_executed = sum(
            1
            for r in execution_results
            if "Execution Successful" in r.execution_state
        )
        correct = sum(1 for r in execution_results if r.is_correct)
        total_tokens = sum(r.total_tokens for r in generation_results)

        return EvalMetrics(
            total=total,
            code_generated=code_generated,
            code_executed=code_executed,
            correct=correct,
            accuracy=correct / total if total > 0 else 0.0,
            generation_success_rate=code_generated / total if total > 0 else 0.0,
            execution_success_rate=code_executed / total if total > 0 else 0.0,
            total_tokens=total_tokens,
            avg_tokens_per_sample=total_tokens / total if total > 0 else 0.0,
            total_time=total_time,
        )

    def _save_generation_results(
        self, results: List[GenerationResult], output_file: Path
    ):
        """Save code generation results"""
        with open(output_file, "w", encoding="utf-8") as f:
            for r in results:
                record = {
                    "index": r.index,
                    "en_question": r.question,
                    "en_answer": r.ground_truth,
                    "en_math_model_code": r.generated_code,
                    "raw_output": r.raw_output,
                    "_tokens": r.total_tokens,
                    "_error": r.error,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.logger.info(f"Saved: {output_file}")

    def _save_eval_results(
        self,
        generation_results: List[GenerationResult],
        execution_results: List[ExecutionResult],
        output_file: Path,
    ):
        """Save evaluation results"""
        # Create index to result mapping
        exec_map = {r.index: r for r in execution_results}

        with open(output_file, "w", encoding="utf-8") as f:
            for gen in generation_results:
                exec_result = exec_map.get(gen.index)
                record = {
                    "index": gen.index,
                    "en_question": gen.question,
                    "en_answer": gen.ground_truth,
                    "en_math_model_code": gen.generated_code,
                    "execution_state": exec_result.execution_state
                    if exec_result
                    else "Not executed",
                    "execution_best_solution": exec_result.predicted_value
                    if exec_result
                    else None,
                    "judge": exec_result.is_correct if exec_result else False,
                    "judge_reason": exec_result.judge_reason
                    if exec_result
                    else "",
                    "conversion_improved": exec_result.conversion_improved
                    if exec_result
                    else False,
                    "conversion_mode": exec_result.conversion_mode
                    if exec_result
                    else "disabled",
                    "execution_time": exec_result.execution_time
                    if exec_result
                    else 0.0,
                    "_tokens": gen.total_tokens,
                    "_error": gen.error,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.logger.info(f"Saved: {output_file}")

    def _save_metrics(self, metrics: EvalMetrics, output_file: Path):
        """Save metrics"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(metrics.__dict__, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Saved: {output_file}")

    def _load_generation_results(
        self, input_file: Path
    ) -> List[GenerationResult]:
        """Load existing code generation results"""
        results = []
        with open(input_file, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                data = json.loads(line)
                # Support different field names
                question = (
                    data.get("en_question")
                    or data.get("problem_description")
                    or data.get("question", "")
                )
                ground_truth = (
                    data.get("en_answer")
                    or data.get("objective")
                    or data.get("objective_value")
                )
                generated_code = data.get("en_math_model_code", "")

                # Clean markdown markers from code
                if generated_code and "```" in generated_code:
                    extracted = self._extract_code(generated_code)
                    if extracted:
                        generated_code = extracted

                results.append(
                    GenerationResult(
                        index=idx,  # Use sequential index
                        question=question,
                        ground_truth=ground_truth,
                        generated_code=generated_code,
                        raw_output=data.get("raw_output", ""),
                        error=data.get("_error"),
                        prompt_tokens=data.get("_tokens", 0),
                        completion_tokens=0,
                        total_tokens=data.get("_tokens", 0),
                    )
                )
        return results

    def _print_results(self, metrics: EvalMetrics):
        """Print evaluation results"""
        print("\n" + "=" * 60)
        print("Evaluation Results")
        print("=" * 60)
        print(f"Total samples: {metrics.total}")
        print(f"Code generated: {metrics.code_generated} ({metrics.generation_success_rate:.2%})")
        print(f"Code executed: {metrics.code_executed} ({metrics.execution_success_rate:.2%})")
        print(f"Correct predictions: {metrics.correct}")
        print(f"Accuracy: {metrics.accuracy:.2%}")
        print(f"Total tokens: {metrics.total_tokens}")
        print(f"Avg tokens/sample: {metrics.avg_tokens_per_sample:.0f}")
        print(f"Total time: {metrics.total_time:.1f}s")
        print("=" * 60 + "\n")


class EvaluationPipeline:
    """Compatibility wrapper that reuses benchmark execution logic."""

    def __init__(
        self,
        config: Optional[EvalConfig] = None,
        input_file: Optional[str] = None,
        output_file: Optional[str] = None,
        timeout: Optional[int] = None,
        max_workers: Optional[int] = None,
        numerical_tolerance: Optional[float] = None,
        question_field: Optional[str] = None,
        answer_field: Optional[str] = None,
        enable_conversion: Optional[bool] = None,
    ):
        cfg = config or EvalConfig()
        self.input_file = input_file
        self.output_file = output_file or "output/eval_results.jsonl"
        self.config = EvalConfig(
            benchmark_name=cfg.benchmark_name,
            model_name=cfg.model_name,
            pass_n=cfg.pass_n,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
            timeout=timeout or cfg.timeout,
            max_workers=max_workers or cfg.max_workers,
            numerical_tolerance=numerical_tolerance or cfg.numerical_tolerance,
            enable_conversion=cfg.enable_conversion if enable_conversion is None else enable_conversion,
            question_field=question_field or cfg.question_field,
            answer_field=answer_field or cfg.answer_field,
            code_field=cfg.code_field,
        )
        self.evaluator = BenchmarkEvaluator(self.config)

    def run(self) -> Dict[str, float]:
        generation_results = self.evaluator._load_generation_results(self.input_file)
        execution_results = self.evaluator._execute_codes(generation_results)
        all_results_path = Path(self.output_file)
        all_results_path.parent.mkdir(parents=True, exist_ok=True)
        self.evaluator._save_eval_results(generation_results, execution_results, all_results_path)

        executed = [r for r in execution_results if "Execution" in r.execution_state]
        correct = sum(1 for r in executed if r.is_correct)
        total = len(executed)
        accuracy = correct / total if total > 0 else 0.0
        return {"accuracy": accuracy, "correct": correct, "total": total}
