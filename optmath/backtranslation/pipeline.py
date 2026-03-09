"""Backtranslation pipeline: LP data -> Natural language description"""

import json
import logging
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Optional

from tqdm import tqdm

from ..core.config import BacktranslationConfig
from ..core.models import BacktranslationResult
from ..llm import create_llm_client
from .prompts import GENERATE_PROMPT, CRITICIZE_PROMPT, REFINEMENT_PROMPT

# Sentinel value for distinguishing "not provided" from "explicitly None"
_UNSET = object()

# Examples for few-shot learning
DEFAULT_EXAMPLES = [
    "Imagine you are in charge of managing food supplies for six different cities...",
    "In a healthcare setting, a hospital administrator needs to allocate staff...",
    "A company plans to produce three products within a four-month timeframe...",
]

APPLICATION_DOMAINS = [
    "Supply Chain Management",
    "Finance",
    "Manufacturing",
    "Transportation",
    "Healthcare",
]


class BacktranslationPipeline:
    """Pipeline for backtranslation"""

    def __init__(
        self,
        config: Optional[BacktranslationConfig] = None,
        input_file: Optional[str] = None,
        output_dir: Optional[str] = None,
        model_name: Optional[str] = None,
        max_workers: Optional[int] = None,
        max_iter: Optional[int] = None,
        sample_size: Optional[int] = _UNSET,
        temperature: Optional[float] = None,
    ):
        cfg = config or BacktranslationConfig()
        self.input_file = input_file
        self.output_dir = output_dir or "output/backtranslation"
        self.model_name = model_name or cfg.model_name
        self.max_workers = max_workers or cfg.max_workers
        self.max_iter = max_iter or cfg.max_iter
        # sample_size: Use sentinel to distinguish "not provided" from "explicitly None"
        self.sample_size = cfg.sample_size if sample_size is _UNSET else sample_size
        self.temperature = temperature or cfg.temperature
        self.llm = create_llm_client(self.model_name)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("optmath.backtranslation")
        logger.setLevel(logging.INFO)
        os.makedirs(os.path.dirname(self.output_dir) or "logs", exist_ok=True)
        return logger

    def load_instances(self) -> List[BacktranslationResult]:
        """Load instances from input file"""
        with open(self.input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        instances = [
            BacktranslationResult(
                mathematical_expression=item["mathematical_expression"],
                lp_data=item["lp_data"],
                objective_value=item.get("objective") or item.get("objective_value"),
                subclass=item.get("subclass"),
            )
            for item in data
        ]
        if self.sample_size and self.sample_size < len(instances):
            random.shuffle(instances)
            instances = instances[: self.sample_size]
        return instances

    def _process_single(self, instance: BacktranslationResult) -> BacktranslationResult:
        """Process single instance: generate -> criticize -> refine"""
        scenario = random.choice(APPLICATION_DOMAINS)
        instance.scenario = scenario

        # 1. Generate description
        try:
            prompt = GENERATE_PROMPT.render(
                mathematical_expression=instance.mathematical_expression,
                lp_data=instance.lp_data,
                scenario=scenario,
                examples=DEFAULT_EXAMPLES,
            )
            content, usage = self.llm.complete(
                message=prompt,
                system_message="As an Operations Research Expert, translate optimization models to natural language.",
                temperature=self.temperature,
            )
            instance.problem_description = content
            instance.token_usage["generate"] = usage.total_tokens
        except Exception as e:
            instance.error = str(e)
            # Fallback: Generate basic description using LP data
            instance.problem_description = f"Optimization problem for {instance.subclass or 'unknown type'}. Please solve the following linear programming model."
            instance.token_usage["generate"] = 0
            # Don't return immediately, continue with subsequent steps

        # 2. Iterative criticism and refinement
        for _ in range(self.max_iter - 1):
            try:
                crit_prompt = CRITICIZE_PROMPT.render(
                    problem_description=instance.problem_description,
                    lp_data=instance.lp_data,
                )
                crit_content, crit_usage = self.llm.complete(
                    message=crit_prompt,
                    system_message="Analyze whether the description matches the LP data.",
                    temperature=self.temperature,
                )
                instance.criticism = crit_content
                instance.token_usage["criticize"] = (
                    instance.token_usage.get("criticize", 0) + crit_usage.total_tokens
                )
                if "Complete Instance" in (crit_content or ""):
                    break
            except Exception as e:
                instance.error = str(e)
                return instance

            try:
                ref_prompt = REFINEMENT_PROMPT.render(
                    criticism=instance.criticism,
                    mathematical_expression=instance.mathematical_expression,
                    lp_data=instance.lp_data,
                    initial_description=instance.problem_description,
                )
                ref_content, ref_usage = self.llm.complete(
                    message=ref_prompt,
                    system_message="Refine the problem description based on feedback.",
                    temperature=self.temperature,
                )
                instance.refined_description = ref_content
                instance.problem_description = ref_content
                instance.token_usage["refine"] = (
                    instance.token_usage.get("refine", 0) + ref_usage.total_tokens
                )
            except Exception as e:
                instance.error = str(e)
                return instance

        return instance

    def run(self) -> List[BacktranslationResult]:
        """Run backtranslation pipeline"""
        instances = self.load_instances()
        self.logger.info(f"Processing {len(instances)} instances with {self.max_workers} workers")
        start = time.time()
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(self._process_single, inst): inst for inst in instances}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Backtranslation"):
                try:
                    results.append(future.result())
                except Exception as e:
                    self.logger.error(f"Task failed: {e}")
        elapsed = time.time() - start
        os.makedirs(self.output_dir, exist_ok=True)
        out_path = os.path.join(
            self.output_dir,
            f"backtranslation_{self.model_name}_{len(results)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump([r.to_dict() for r in results], f, indent=2, ensure_ascii=False)
        self.logger.info(f"Saved to {out_path} in {elapsed:.1f}s")
        return results
