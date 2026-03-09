# Quick Start

This document focuses on the fastest way to run OptMATH locally with `uv`, and on understanding the end-to-end data generation pipeline.

## Prerequisites

- Python `3.11`
- `uv`
- A working `gurobipy` environment and license
- A DeepSeek API key exported as `LHL_DEEPSEEK_KEY`

## Installation

From the project root:

```bash
uv sync --extra dev
```

This creates `.venv` and installs runtime and test dependencies.

## Environment Variables

Export the API key before running backtranslation, modeling, or benchmark evaluation:

```bash
export LHL_DEEPSEEK_KEY="your_deepseek_api_key"
```

## Run Tests

```bash
uv run pytest -q
```

## End-to-End Pipeline

OptMATH's main pipeline has four stages:

```text
generators/
    |
    v
[1] Instance Generation
    Input: seed generator code + metadata
    Output: LP instances in instances.json
    |
    v
[2] Backtranslation
    Input: LP instances
    Output: natural-language problem descriptions in backtranslation/*.json
    |
    v
[3] Forward Modeling
    Input: natural-language descriptions
    Output: generated Python/Gurobi code in modeling/*.jsonl
    |
    v
[4] Evaluation
    Input: generated code + reference answers
    Output: execution results and correctness labels in eval_results.jsonl
```

The default shell entry point is:

```bash
uv run bash scripts/run_full_pipeline.sh
```

## Full Pipeline Parameters

The main configurable parameters live in [scripts/run_full_pipeline.sh](/Users/luhongliang/Desktop/OptMATH/scripts/run_full_pipeline.sh).

### 1. Instance Generation

These parameters control how many optimization instances are synthesized from the seed generators under [`generators/`](/Users/luhongliang/Desktop/OptMATH/generators):

- `GENERATORS_DIR`: directory containing generator subfolders
- `NUM_INSTANCES`: number of instances to generate per generator
- `MAX_ITER`: generator retry budget
- `VAR_NUM_MAX`: maximum allowed variable count
- `CONSTRAINT_NUM_MAX`: maximum allowed constraint count
- `NUM_WORKERS_GEN`: parallel workers for generation

Example:

```bash
GENERATORS_DIR=generators \
NUM_INSTANCES=2 \
MAX_ITER=50 \
VAR_NUM_MAX=40 \
CONSTRAINT_NUM_MAX=80 \
NUM_WORKERS_GEN=4 \
uv run bash scripts/run_full_pipeline.sh
```

What this stage does:

- loads generator code and `metadata.json` from each subdirectory
- samples candidate optimization models
- filters out instances that exceed variable or constraint limits
- solves the model once with Gurobi
- writes accepted LP instances to `instances.json`

Main output:

- `instances.json`

Each record contains fields such as:

- problem subclass
- mathematical expression or template
- LP text
- solve status
- objective value

### 2. Backtranslation

These parameters control the conversion from LP instances to natural-language optimization problems:

- `MODEL_BT`: LLM used for backtranslation, default `deepseek_official`
- `MAX_WORKERS_BT`: parallel requests for backtranslation
- `MAX_ITER_BT`: refinement loop count
- `SAMPLE_SIZE_BT`: number of generated LP instances to process
- `TEMPERATURE_BT`: sampling temperature

Example:

```bash
MODEL_BT=deepseek_official \
MAX_WORKERS_BT=2 \
MAX_ITER_BT=2 \
SAMPLE_SIZE_BT=5 \
TEMPERATURE_BT=0.8 \
uv run bash scripts/run_full_pipeline.sh
```

What this stage does:

- reads `instances.json`
- asks the LLM to convert LP instances into natural-language scenarios
- optionally critiques and refines descriptions across multiple iterations
- writes backtranslation results to a timestamped JSON file

Main output directory:

- `backtranslation/`

Typical output file:

- `backtranslation/backtranslation_<model>_<count>_<timestamp>.json`

Each record usually contains:

- subclass
- scenario
- problem description
- original LP data
- reference objective value

### 3. Forward Modeling

These parameters control code generation from natural-language descriptions:

- `MODEL_MODELING`: LLM used for forward modeling
- `NUM_WORKERS_MODELING`: parallel workers
- `TEMPERATURE_MODELING`: sampling temperature
- `SAMPLE_SIZE_MODELING`: number of backtranslated samples to process, `0` means all

Example:

```bash
MODEL_MODELING=deepseek_official \
NUM_WORKERS_MODELING=2 \
TEMPERATURE_MODELING=0.8 \
SAMPLE_SIZE_MODELING=10 \
uv run bash scripts/run_full_pipeline.sh
```

What this stage does:

- reads the latest backtranslation result file
- prompts the LLM to generate Python + `gurobipy` code
- saves one JSONL record per sample

Main output directory:

- `modeling/`

Typical output file:

- `modeling/generated_<model>_<timestamp>.jsonl`

Each record usually contains:

- `en_question`
- `en_answer`
- `en_math_model_code`

### 4. Evaluation

These parameters control execution and checking of generated code:

- `TIMEOUT_EVAL`: timeout per execution
- `MAX_WORKERS_EVAL`: parallel execution workers

Evaluation uses conversion fallback by default in the current implementation.

Example:

```bash
TIMEOUT_EVAL=60 \
MAX_WORKERS_EVAL=4 \
uv run bash scripts/run_full_pipeline.sh
```

What this stage does:

- executes generated Python/Gurobi code
- extracts the best solution from stdout
- compares the result with the reference answer
- records correctness and execution status

Main output:

- `eval_results.jsonl`

Each record typically includes:

- generated question
- reference answer
- generated code
- execution state
- best solution found
- correctness label
- conversion metadata

## Recommended Small-Scale Run

For a quick smoke test, use a small configuration first:

```bash
OUTPUT_DIR=output/demo \
NUM_INSTANCES=1 \
MAX_ITER=50 \
VAR_NUM_MAX=40 \
CONSTRAINT_NUM_MAX=80 \
MAX_WORKERS_BT=1 \
MAX_ITER_BT=1 \
SAMPLE_SIZE_BT=2 \
NUM_WORKERS_MODELING=1 \
SAMPLE_SIZE_MODELING=2 \
MAX_WORKERS_EVAL=1 \
uv run bash scripts/run_full_pipeline.sh
```

This is usually enough to verify:

- generator loading works
- API credentials are available
- backtranslation can return text
- modeling can return executable code
- evaluation can execute and score results

## Output Structure

When the full pipeline finishes, the output directory looks like this:

```text
output/demo_YYYYMMDD_HHMMSS/
├── instances.json
├── backtranslation/
│   └── backtranslation_<model>_<count>_<timestamp>.json
├── modeling/
│   └── generated_<model>_<timestamp>.jsonl
└── eval_results.jsonl
```

Meaning of each artifact:

- `instances.json`
  - accepted LP instances generated from seed generators
- `backtranslation/*.json`
  - natural-language versions of those LP instances
- `modeling/*.jsonl`
  - generated Python/Gurobi code from natural-language descriptions
- `eval_results.jsonl`
  - execution and correctness results for the generated code

## Benchmark Evaluation

Evaluate an existing benchmark file:

```bash
uv run bash scripts/run_eval.sh \
  --input benchmark/OptMATH_Bench.json \
  --benchmark optmath \
  --model deepseek_official
```

By default, benchmark evaluation enables conversion fallback during execution.

Evaluate existing generated code only:

```bash
uv run bash scripts/run_eval.sh \
  --input path/to/generated.jsonl \
  --skip-generation
```

Disable conversion fallback during evaluation:

```bash
uv run bash scripts/run_eval.sh \
  --input path/to/generated.jsonl \
  --skip-generation \
  --disable-conversion
```

Evaluation outputs are written under `benchmark_results/`.

## Common Files

- `scripts/run_full_pipeline.sh`: end-to-end generation, backtranslation, modeling, and evaluation
- `scripts/run_eval.sh`: benchmark evaluation entry
- `eval/cli.py`: direct benchmark evaluation CLI
- `eval/README.md`: benchmark evaluation details
- `config/default.yaml`: default model and runtime configuration
