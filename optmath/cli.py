"""OptMATH unified CLI entry point"""

import argparse

from .core.config import load_config
from .generators import InstanceGenerationPipeline
from .backtranslation import BacktranslationPipeline
from .modeling import ModelingPipeline
from eval import EvaluationPipeline


def cmd_generate(args):
    config = load_config(args.config, getattr(args, "_overrides", None))
    cfg = config.instance_generation
    pipeline = InstanceGenerationPipeline(
        config=cfg,
        base_dir=args.base_dir or cfg.base_dir,
        num_instances=args.num_instances or cfg.num_instances,
        output_file=args.output or cfg.output_file,
        max_iter=args.max_iter or cfg.max_iter,
        var_num_max=args.var_num_max or cfg.var_num_max,
        constraint_num_max=args.constraint_num_max or cfg.constraint_num_max,
    )
    pipeline.run()


def cmd_backtranslate(args):
    config = load_config(args.config, getattr(args, "_overrides", None))
    cfg = config.backtranslation
    pipeline = BacktranslationPipeline(
        config=cfg,
        input_file=args.input,
        output_dir=args.output_dir or "output/backtranslation",
        model_name=args.model or cfg.model_name,
        max_workers=args.max_workers or cfg.max_workers,
        max_iter=args.max_iter or cfg.max_iter,
        sample_size=args.sample_size or cfg.sample_size,
        temperature=args.temperature or cfg.temperature,
    )
    pipeline.run()


def cmd_model(args):
    config = load_config(args.config, getattr(args, "_overrides", None))
    cfg = config.modeling
    pipeline = ModelingPipeline(
        config=cfg,
        dataset_path=args.dataset,
        output_dir=args.output_dir or "output/modeling",
        model_name=args.model or cfg.model_name,
        num_workers=args.num_workers or cfg.num_workers,
        temperature=args.temperature or cfg.temperature,
        sample_size=args.sample_size,
    )
    pipeline.run()


def cmd_evaluate(args):
    config = load_config(args.config, getattr(args, "_overrides", None))
    cfg = config.evaluation
    pipeline = EvaluationPipeline(
        input_file=args.input,
        output_file=args.output or "output/eval_results.jsonl",
        timeout=args.timeout or cfg.timeout,
        max_workers=args.max_workers or cfg.max_workers,
        question_field=args.question_field or cfg.question_field,
        answer_field=args.answer_field or cfg.answer_field,
        enable_conversion=args.enable_conversion,
    )
    pipeline.run()


def main():
    parser = argparse.ArgumentParser(prog="optmath", description="OptMATH optimization math problem framework")
    parser.add_argument("-c", "--config", default=None, help="Configuration file path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_gen = subparsers.add_parser("generate", help="Instance generation")
    p_gen.add_argument("--base-dir", help="Generator directory")
    p_gen.add_argument("--output", "-o", help="Output file")
    p_gen.add_argument("--num-instances", type=int, help="Instances per class")
    p_gen.add_argument("--max-iter", type=int, help="Maximum iterations")
    p_gen.add_argument("--var-num-max", type=int, help="Maximum variables")
    p_gen.add_argument("--constraint-num-max", type=int, help="Maximum constraints")
    p_gen.set_defaults(func=cmd_generate)

    p_bt = subparsers.add_parser("backtranslate", help="Backtranslation")
    p_bt.add_argument("--input", "-i", required=True, help="Input JSON file")
    p_bt.add_argument("--output-dir", "-o", help="Output directory")
    p_bt.add_argument("--model", "-m", help="Model name")
    p_bt.add_argument("--max-workers", type=int, help="Concurrent workers")
    p_bt.add_argument("--max-iter", type=int, help="Refinement iterations")
    p_bt.add_argument("--sample-size", type=int, help="Sample size")
    p_bt.add_argument("--temperature", type=float, help="Temperature")
    p_bt.set_defaults(func=cmd_backtranslate)

    p_model = subparsers.add_parser("model", help="Forward modeling (CoT)")
    p_model.add_argument("--dataset", "-i", required=True, help="Input dataset (JSON/JSONL)")
    p_model.add_argument("--output-dir", "-o", help="Output directory")
    p_model.add_argument("--model", "-m", help="Model name")
    p_model.add_argument("--num-workers", type=int, help="Concurrent workers")
    p_model.add_argument("--temperature", type=float, help="Temperature")
    p_model.add_argument("--sample-size", type=int, help="Sample size")
    p_model.set_defaults(func=cmd_model)

    p_eval = subparsers.add_parser("evaluate", help="Evaluation")
    p_eval.add_argument("--input", "-i", required=True, help="Input JSONL (with generated code)")
    p_eval.add_argument("--output", "-o", help="Output JSONL")
    p_eval.add_argument("--timeout", type=int, help="Execution timeout (seconds)")
    p_eval.add_argument("--max-workers", type=int, help="Concurrent workers")
    p_eval.add_argument("--question-field", default="en_question", help="Question field")
    p_eval.add_argument("--answer-field", default="en_answer", help="Answer field")
    p_eval.add_argument(
        "--enable-conversion",
        action="store_true",
        default=True,
        help="Enable conversion fallback during evaluation",
    )
    p_eval.add_argument(
        "--disable-conversion",
        action="store_false",
        dest="enable_conversion",
        help="Disable conversion fallback during evaluation",
    )
    p_eval.set_defaults(func=cmd_evaluate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
