# Quick Start

This document covers the fastest way to get OptMATH running locally with `uv`.

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

## Full Pipeline

Run the main bidirectional pipeline:

```bash
uv run bash scripts/run_full_pipeline.sh
```

Useful overrides:

```bash
OUTPUT_DIR=output/demo \
NUM_INSTANCES=1 \
MAX_WORKERS_BT=1 \
NUM_WORKERS_MODELING=1 \
MAX_WORKERS_EVAL=1 \
uv run bash scripts/run_full_pipeline.sh
```

Generated files are written under `output/` by default.

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
