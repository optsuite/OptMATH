"""Forward modeling pipeline: Natural language questions -> Python/Gurobi code (CoT)"""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Optional

from tqdm import tqdm

from ..core.config import ModelingConfig
from ..llm import create_llm_client

COT_PROMPT_TEMPLATE = """\
Below is an operations research question. Build a mathematical model and corresponding python code using `gurobipy` that appropriately addresses the question.

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
```
"""


class ModelingPipeline:
    """Forward modeling pipeline (CoT generation)"""

    def __init__(
        self,
        config: Optional[ModelingConfig] = None,
        dataset_path: Optional[str] = None,
        output_dir: Optional[str] = None,
        model_name: Optional[str] = None,
        num_workers: Optional[int] = None,
        temperature: Optional[float] = None,
        sample_size: Optional[int] = None,
    ):
        cfg = config or ModelingConfig()
        self.dataset_path = dataset_path
        self.output_dir = output_dir or "output/modeling"
        self.model_name = model_name or cfg.model_name
        self.num_workers = num_workers or cfg.num_workers
        self.temperature = temperature or cfg.temperature
        self.sample_size = sample_size
        self.llm = create_llm_client(self.model_name)
        self.logger = logging.getLogger("optmath.modeling")

    def load_data(self) -> List[dict]:
        """Load dataset (JSON or JSONL format)"""
        records = []
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content.startswith("["):
            records = json.loads(content)
        else:
            for line in content.split("\n"):
                if line.strip():
                    records.append(json.loads(line))
        for r in records:
            if "en_question" not in r:
                r["en_question"] = r.get("problem_description") or r.get("question", "")
        if self.sample_size:
            records = records[: self.sample_size]
        return records

    def _generate_single(self, example: dict) -> dict:
        """Generate for single example"""
        try:
            question = example.get("en_question", example.get("problem_description", ""))
            if not question:
                raise ValueError("No question found in example")

            prompt = COT_PROMPT_TEMPLATE.format(question=question.strip())
            content, usage = self.llm.complete(
                message=prompt,
                system_message="You are an expert in operations research and optimization.",
                temperature=self.temperature,
            )
            example = dict(example)
            example["q2mc_en_prompt"] = prompt
            example["en_math_model_code"] = content
            example["_tokens"] = usage.total_tokens
            return example
        except Exception as e:
            self.logger.error(f"Generate failed for {example.get('subclass', 'unknown')}: {e}")
            example = dict(example)
            example["en_math_model_code"] = ""
            example["_error"] = str(e)
            return example

    def run(self) -> str:
        """Run forward modeling pipeline"""
        records = self.load_data()
        self.logger.info(f"Generating for {len(records)} examples")
        results = []
        with ThreadPoolExecutor(max_workers=self.num_workers) as ex:
            futures = {ex.submit(self._generate_single, r): r for r in records}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Modeling"):
                try:
                    r = future.result()
                    results.append(r)
                except Exception as e:
                    # Log errors even if future.result() raises exception
                    self.logger.error(f"Task future failed: {e}")
                    # Create an error record
                    results.append({
                        "_error": str(e),
                        "en_math_model_code": "",
                    })
        os.makedirs(self.output_dir, exist_ok=True)
        out_path = os.path.join(
            self.output_dir,
            f"generated_{self.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
        )
        with open(out_path, "w", encoding="utf-8") as f:
            for r in results:
                dump = {k: v for k, v in r.items() if not k.startswith("_")}
                f.write(json.dumps(dump, ensure_ascii=False) + "\n")
        self.logger.info(f"Saved {len(results)} results to {out_path}")
        return out_path
