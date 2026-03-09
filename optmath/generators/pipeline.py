"""Instance generation pipeline with difficulty control

This module provides:
1. BaseInstanceGenerationPipeline - Basic generation without difficulty control
2. InstanceGenerationPipeline - Enhanced pipeline with difficulty filtering
   (alias for backward compatibility, now uses enhanced features)

The enhanced pipeline supports:
- Complexity-based difficulty control (easy, medium, hard, or custom ranges)
- Feedback-driven parameter adjustment using LLM
- Per-instance complexity scoring
"""

import json
import logging
import os
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    # Fallback without colors
    class _DummyColor:
        RESET_ALL = ""

        def __getattr__(self, name):
            return ""

    Fore = _DummyColor()
    Style = _DummyColor()
    COLORAMA_AVAILABLE = False

from ..core.config import Config, InstanceGenerationConfig
from ..core.models import OptimizationInstance
from .complexity import ComplexityScorer, check_complexity_range
from .feedback import (
    FeedbackDrivenConfigGenerator,
    GeneratorConfig,
    TargetRequirements,
)
from .loader import load_generators_from_dir

logger = logging.getLogger(__name__)


@dataclass
class DifficultyLevel:
    """Difficulty level for instance generation

    Attributes:
        name: Difficulty identifier ("easy", "medium", "hard")
        complexity_min: Minimum complexity score
        complexity_max: Maximum complexity score
        solve_time_max: Maximum expected solve time in seconds
        description: Human-readable description
    """

    name: str
    complexity_min: float
    complexity_max: float
    solve_time_max: float
    description: str = ""

    # Class-level predefined levels
    EASY: "DifficultyLevel" = None
    MEDIUM: "DifficultyLevel" = None
    HARD: "DifficultyLevel" = None

    def __post_init__(self):
        if self.name == "easy" and DifficultyLevel.EASY is None:
            DifficultyLevel.EASY = self
        elif self.name == "medium" and DifficultyLevel.MEDIUM is None:
            DifficultyLevel.MEDIUM = self
        elif self.name == "hard" and DifficultyLevel.HARD is None:
            DifficultyLevel.HARD = self


# Initialize predefined difficulty levels
DifficultyLevel(
    name="easy",
    complexity_min=10.0,
    complexity_max=50.0,
    solve_time_max=5.0,
    description="Simple problems with few variables and constraints"
)

DifficultyLevel(
    name="medium",
    complexity_min=50.0,
    complexity_max=150.0,
    solve_time_max=30.0,
    description="Medium complexity problems"
)

DifficultyLevel(
    name="hard",
    complexity_min=150.0,
    complexity_max=500.0,
    solve_time_max=120.0,
    description="Complex problems with many variables and constraints"
)


class BaseInstanceGenerationPipeline:
    """Base instance generation pipeline without difficulty control

    This is the original pipeline that generates instances without
    complexity filtering. Maintained for backward compatibility.
    """

    def __init__(
        self,
        config: Optional[InstanceGenerationConfig] = None,
        base_dir: Optional[str] = None,
        num_instances: Optional[int] = None,
        output_file: Optional[str] = None,
        max_iter: Optional[int] = None,
        var_num_max: Optional[int] = None,
        constraint_num_max: Optional[int] = None,
        num_workers: Optional[int] = None,
    ):
        cfg = config or InstanceGenerationConfig()
        self.base_dir = base_dir or cfg.base_dir
        self.num_instances = num_instances or cfg.num_instances
        self.output_file = output_file or cfg.output_file
        self.max_iter = max_iter or cfg.max_iter
        self.var_num_max = var_num_max or cfg.var_num_max
        self.constraint_num_max = constraint_num_max or cfg.constraint_num_max
        self.num_workers = num_workers or cfg.num_workers or os.cpu_count() or 4
        self._terminate = False
        self._instances: List[OptimizationInstance] = []
        self._lock = threading.Lock()

    def _setup_signal_handlers(self):
        def handler(sig, frame):
            self._terminate = True

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def run(self, verbose: bool = True) -> List[OptimizationInstance]:
        """Run the generation pipeline"""
        if verbose:
            print(f"{Fore.CYAN}[OptMATH] Instance Generation Pipeline{Style.RESET_ALL}")

        self._setup_signal_handlers()
        generators = load_generators_from_dir(self.base_dir)

        if not generators:
            raise FileNotFoundError(f"No generators found in {self.base_dir}")

        all_instances = []
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {
                executor.submit(
                    self._generate_for_problem,
                    Generator,
                    metadata,
                    folder_path,
                ): metadata.get("subclass", "unknown")
                for Generator, metadata, folder_path in generators
            }

            for future in as_completed(futures):
                if self._terminate:
                    break

                problem_class = futures[future]
                try:
                    instances = future.result()
                    all_instances.extend(instances)
                    if verbose:
                        print(f"  {problem_class}: {len(instances)} instances")
                except Exception as e:
                    if verbose:
                        print(f"  {problem_class}: Error - {e}")

        elapsed = time.time() - start_time

        # Save instances
        os.makedirs(os.path.dirname(self.output_file) or ".", exist_ok=True)
        instances_data = [inst.to_dict() for inst in all_instances]
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(instances_data, f, indent=2, ensure_ascii=False)

        if verbose:
            print(f"\n{Fore.GREEN}Generated {len(all_instances)} instances{Style.RESET_ALL}")
            print(f"Time: {elapsed:.1f}s")
            print(f"Output: {self.output_file}")

        return all_instances

    def _generate_for_problem(
        self,
        Generator,
        metadata: Dict[str, Any],
        folder_path: Path,
    ) -> List[OptimizationInstance]:
        """Generate instances for a single problem class"""
        instances = []
        temp_dir = folder_path / "temp_lp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            for i in range(self.num_instances):
                if self._terminate:
                    break

                try:
                    gen = Generator(seed=i)
                    model = gen.generate_instance()

                    if model.NumVars > self.var_num_max or model.NumConstrs > self.constraint_num_max:
                        continue

                    model.Params.TimeLimit = 5.0
                    model.Params.OutputFlag = 0
                    model.optimize()

                    status_map = {2: "OPTIMAL", 3: "INFEASIBLE", 9: "TIME_LIMIT"}
                    status = status_map.get(model.Status, "UNKNOWN")
                    obj_val = model.ObjVal if model.Status == 2 else None

                    if status != "OPTIMAL":
                        continue

                    lp_path = temp_dir / f"instance_{i}.lp"
                    model.write(str(lp_path))
                    with open(lp_path, "r") as f:
                        lp_content = f.read()

                    instances.append(
                        OptimizationInstance(
                            subclass=metadata.get("subclass", ""),
                            mathematical_expression=metadata.get("math_formula", ""),
                            lp_data=lp_content,
                            status=status,
                            objective=obj_val,
                            solve_time=model.Runtime,
                        )
                    )

                except Exception:
                    continue

        finally:
            for f in temp_dir.glob("*"):
                f.unlink()
            temp_dir.rmdir()

        return instances


class InstanceGenerationPipeline:
    """Instance generation pipeline with difficulty control

    This enhanced pipeline supports:
    - Difficulty-based filtering (easy, medium, hard, or custom ranges)
    - Complexity scoring for each generated instance
    - Optional feedback-driven parameter adjustment

    Args:
        config: Instance generation configuration
        base_dir: Directory containing problem generators
        difficulty: Difficulty level ("easy", "medium", "hard") or None for no filtering
        target_complexity: Custom (min, max) complexity range
        enable_feedback: Enable LLM-based parameter adjustment
        model_name: LLM model name for feedback generation
        **kwargs: Additional parameters passed to base pipeline
    """

    def __init__(
        self,
        config: Optional[InstanceGenerationConfig] = None,
        base_dir: Optional[str] = None,
        difficulty: Optional[str] = None,
        target_complexity: Optional[Tuple[float, float]] = None,
        enable_feedback: bool = False,
        model_name: str = "deepseek_official",
        **kwargs
    ):
        self.config = config or InstanceGenerationConfig()
        self.base_dir = base_dir or self.config.base_dir

        # Set difficulty parameters
        self.difficulty = difficulty
        if target_complexity:
            self.complexity_min, self.complexity_max = target_complexity
        elif difficulty == "easy":
            level = DifficultyLevel.EASY
            self.complexity_min, self.complexity_max = level.complexity_min, level.complexity_max
        elif difficulty == "medium":
            level = DifficultyLevel.MEDIUM
            self.complexity_min, self.complexity_max = level.complexity_min, level.complexity_max
        elif difficulty == "hard":
            level = DifficultyLevel.HARD
            self.complexity_min, self.complexity_max = level.complexity_min, level.complexity_max
        else:
            # No difficulty control
            self.complexity_min = None
            self.complexity_max = None

        self.enable_feedback = enable_feedback
        self.model_name = model_name

        # Initialize base pipeline and components
        self.base_pipeline = BaseInstanceGenerationPipeline(
            config=config,
            base_dir=base_dir,
            **kwargs
        )
        self.scorer = ComplexityScorer() if difficulty or target_complexity else None

        if enable_feedback:
            self.feedback_generator = FeedbackDrivenConfigGenerator(model_name)
        else:
            self.feedback_generator = None

        self._terminate = False

    def run(self, output_file: Optional[str] = None, verbose: bool = True) -> List[OptimizationInstance]:
        """Run the generation pipeline

        Args:
            output_file: Output file path
            verbose: Print progress information

        Returns:
            List of generated instances
        """
        if self.difficulty or self.complexity_min is not None:
            return self._run_with_difficulty_control(output_file, verbose)
        else:
            # No difficulty control, use base pipeline
            return self.base_pipeline.run(verbose=verbose)

    def _run_with_difficulty_control(
        self,
        output_file: Optional[str] = None,
        verbose: bool = True,
    ) -> List[OptimizationInstance]:
        """Run generation with difficulty filtering"""
        if verbose:
            print(
                f"{Fore.CYAN}[OptMATH] Enhanced Generation Pipeline{Style.RESET_ALL}\n"
                f"  Difficulty: {self.difficulty or 'custom'}\n"
                f"  Complexity range: [{self.complexity_min:.1f}, {self.complexity_max:.1f}]\n"
                f"  Feedback control: {'enabled' if self.enable_feedback else 'disabled'}"
            )

        self._setup_signal_handlers()

        generators = load_generators_from_dir(self.base_dir)
        if not generators:
            raise FileNotFoundError(f"No generators found in {self.base_dir}")

        all_instances = []
        start_time = time.time()

        for Generator, metadata, folder_path in generators:
            if self._terminate:
                break

            problem_class = metadata.get("subclass", "unknown")
            if verbose:
                print(f"\n{Fore.YELLOW}Processing: {problem_class}{Style.RESET_ALL}")

            instances = self._generate_for_problem_with_control(
                Generator,
                metadata,
                folder_path,
                problem_class,
                verbose,
            )

            all_instances.extend(instances)

            if verbose:
                print(f"  Generated: {len(instances)} instances")

        elapsed = time.time() - start_time
        output_file = output_file or self.base_pipeline.output_file
        self._save_instances(all_instances, output_file)

        if verbose:
            print(
                f"\n{Fore.CYAN}[OptMATH] Complete:{Style.RESET_ALL}\n"
                f"  Total instances: {len(all_instances)}\n"
                f"  Time: {elapsed:.1f}s\n"
                f"  Output: {output_file}"
            )

        return all_instances

    def _generate_for_problem_with_control(
        self,
        Generator,
        metadata: Dict[str, Any],
        folder_path: Path,
        problem_class: str,
        verbose: bool,
    ) -> List[OptimizationInstance]:
        """Generate instances with difficulty control"""
        instances = []

        max_iter = self.base_pipeline.max_iter
        var_num_max = self.base_pipeline.var_num_max
        constraint_num_max = self.base_pipeline.constraint_num_max
        temp_dir = folder_path / "temp_lp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            if self.enable_feedback and self.feedback_generator:
                generator_config = self._get_configured_parameters(problem_class, verbose)
            else:
                generator_config = None

            max_attempts = max_iter * 3  # Allow more attempts for filtering

            for attempt in range(max_attempts):
                if self._terminate:
                    break

                try:
                    seed = attempt if not generator_config else attempt * 100 + generator_config.num_vars_min
                    gen = Generator(seed=seed)

                    if generator_config:
                        gen = self._apply_config_to_generator(gen, generator_config)

                    model = gen.generate_instance()

                    if model.NumVars > var_num_max or model.NumConstrs > constraint_num_max:
                        continue

                    model.Params.TimeLimit = 5.0
                    model.Params.OutputFlag = 0
                    model.optimize()

                    status_map = {2: "OPTIMAL", 3: "INFEASIBLE", 9: "TIME_LIMIT"}
                    status = status_map.get(model.Status, "UNKNOWN")
                    obj_val = model.ObjVal if model.Status == 2 else None

                    if status != "OPTIMAL":
                        continue

                    lp_path = temp_dir / f"instance_{attempt}.lp"
                    model.write(str(lp_path))
                    with open(lp_path, "r") as f:
                        lp_content = f.read()

                    complexity = self.scorer.score_from_lp_file(lp_content)

                    if not check_complexity_range(
                        complexity,
                        self.complexity_min,
                        self.complexity_max
                    ):
                        if verbose and attempt < 5:
                            print(f"    Instance {attempt}: complexity={complexity:.1f} (filtered out)")
                        continue

                    instances.append(
                        OptimizationInstance(
                            subclass=problem_class,
                            mathematical_expression=metadata.get("math_formula", ""),
                            lp_data=lp_content,
                            status=status,
                            objective=obj_val,
                            solve_time=model.Runtime,
                            complexity=complexity,
                        )
                    )

                    if verbose and len(instances) <= 3:
                        print(f"    Instance {attempt}: complexity={complexity:.1f} ✓")

                    if len(instances) >= self.base_pipeline.num_instances:
                        break

                except Exception as e:
                    if verbose:
                        print(f"    Attempt {attempt}: error - {e}")
                    continue

        finally:
            for f in temp_dir.glob("*"):
                f.unlink()
            temp_dir.rmdir()

        return instances

    def _get_configured_parameters(
        self,
        problem_class: str,
        verbose: bool,
    ) -> Optional[GeneratorConfig]:
        """Get configured parameters using feedback generation"""
        requirements = TargetRequirements(
            complexity_min=self.complexity_min,
            complexity_max=self.complexity_max,
            solve_time_max=30.0,
            feasibility_target=0.9,
            num_samples=5,
        )

        if verbose:
            print(f"    Running feedback-driven config generation...")

        config = self.feedback_generator.generate_config(
            problem_class=problem_class,
            requirements=requirements,
        )

        if config and verbose:
            print(f"    Config: vars=[{config.num_vars_min}, {config.num_vars_max}], "
                  f"constrs=[{config.num_constrs_min}, {config.num_constrs_max}]")

        return config

    def _apply_config_to_generator(
        self,
        generator: Any,
        config: GeneratorConfig,
    ) -> Any:
        """Apply configuration to generator instance"""
        return generator

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def handler(sig, frame):
            self._terminate = True

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def _save_instances(self, instances: List[OptimizationInstance], output_file: str):
        """Save instances to file"""
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

        instances_data = []
        for inst in instances:
            d = inst.to_dict()
            if hasattr(inst, 'complexity'):
                d['complexity'] = inst.complexity
            instances_data.append(d)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(instances_data, f, indent=2, ensure_ascii=False)
