#!/usr/bin/env python3
"""Benchmark evaluation CLI tool"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add project path
script_dir = Path(__file__).resolve().parent  # Absolute path to eval directory
# Add parent directory to path (optmath_refactored)
sys.path.insert(0, str(script_dir.parent))

# Set environment to optmath_refactored directory
project_root = script_dir.parent
os.chdir(str(project_root))

# Import without conflicting with built-in eval module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "evaluator",
    str(script_dir / "evaluator.py")
)
evaluator_module = importlib.util.module_from_spec(spec)
sys.modules['evaluator'] = evaluator_module  # Register module
spec.loader.exec_module(evaluator_module)

BenchmarkEvaluator = evaluator_module.BenchmarkEvaluator
EvalConfig = evaluator_module.EvalConfig


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="OptMATH benchmark evaluation tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Required arguments
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="Input data file path (JSON or JSONL format)",
    )

    # Benchmark config
    parser.add_argument(
        "--benchmark",
        "-b",
        type=str,
        default="optmath",
        help="Benchmark name (used to create output directory)",
    )

    # Model config
    parser.add_argument(
        "--model", "-m", type=str, default="deepseek_official", help="LLM model name"
    )

    parser.add_argument(
        "--temperature", type=float, default=0.8, help="Temperature parameter"
    )

    parser.add_argument("--max-tokens", type=int, default=8192, help="Max tokens")

    # Pass config
    parser.add_argument(
        "--pass", "-p", dest="pass_n", type=int, default=1, help="Nth attempt"
    )

    # Execution config
    parser.add_argument("--timeout", type=int, default=100, help="Code execution timeout (seconds)")

    parser.add_argument(
        "--max-workers",
        "-w",
        type=int,
        default=50,
        help="Max concurrent workers",
    )

    parser.add_argument(
        "--numerical-tolerance",
        type=float,
        default=0.05,
        help="Numerical tolerance",
    )
    parser.add_argument(
        "--enable-conversion",
        action="store_true",
        default=True,
        help="Enable conversion fallback when initial execution is incorrect",
    )
    parser.add_argument(
        "--disable-conversion",
        action="store_false",
        dest="enable_conversion",
        help="Disable conversion fallback",
    )

    # Field config
    parser.add_argument(
        "--question-field",
        type=str,
        default="en_question",
        help="Question field name",
    )

    parser.add_argument(
        "--answer-field",
        type=str,
        default="en_answer",
        help="Answer field name",
    )

    parser.add_argument(
        "--code-field",
        type=str,
        default="en_math_model_code",
        help="Code field name (only used when skip-generation=True)",
    )

    # Options
    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Skip code generation, assume generated.jsonl exists",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    return parser.parse_args()


def main():
    """Main function"""
    args = parse_args()

    # Setup logging level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Create evaluation config
    config = EvalConfig(
        benchmark_name=args.benchmark,
        model_name=args.model,
        pass_n=args.pass_n,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        max_workers=args.max_workers,
        numerical_tolerance=args.numerical_tolerance,
        enable_conversion=args.enable_conversion,
        question_field=args.question_field,
        answer_field=args.answer_field,
        code_field=args.code_field,
    )

    # Create evaluator
    evaluator = BenchmarkEvaluator(config)

    # Run evaluation
    try:
        metrics = evaluator.evaluate(
            input_file=args.input,
            dataset_name=Path(args.input).stem,
            skip_generation=args.skip_generation,
        )
        print(f"\nEvaluation complete! Results saved in: {evaluator.output_dir}")
        return 0

    except Exception as e:
        logging.error(f"Evaluation failed: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
