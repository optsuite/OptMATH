# OptMATH Benchmark Evaluation Tool

An independent benchmark evaluation system that supports evaluating code generation and execution results for different benchmarks.

## Features

- ✅ Support for multiple data formats (JSON/JSONL)
- ✅ Automatic code generation (using LLM)
- ✅ Concurrent code execution
- ✅ Flexible output directory structure
- ✅ Detailed evaluation metrics
- ✅ Support for skipping generation phase (evaluate existing code only)
- ✅ Conversion fallback enabled by default during evaluation

## Output Directory Structure

```
benchmark_results/
└── {benchmark_name}/              # Benchmark name
    └── {model_name}/              # Model name
        └── pass_{pass_n}/         # Nth attempt
            └── {timestamp}/       # Timestamp
                ├── generated.jsonl  # Generated code
                ├── eval.jsonl       # Evaluation results
                └── metrics.json      # Metrics summary
```

## Quick Start

### 1. Using Shell Script (Recommended)

```bash
./scripts/run_eval.sh \
  --input data/test.jsonl \
  --benchmark optmath \
  --model deepseek_official

./scripts/run_eval.sh \
  --input data/test.jsonl \
  --max-workers 100

./scripts/run_eval.sh \
  --input generated_results.jsonl \
  --skip-generation

./scripts/run_eval.sh \
  --input data/test.jsonl \
  --pass 1
./scripts/run_eval.sh \
  --input data/test.jsonl \
  --pass 2 \
  --disable-conversion
```

### 2. Direct Python Invocation

```bash
python3 eval/cli.py \
  --input data/test.jsonl \
  --benchmark optmath \
  --model deepseek_official \
  --pass 1 \
  --max-workers 50 \
  --temperature 0.8 \
  --skip-generation
```

## Parameter Description

### Required Parameters

| Parameter | Shorthand | Description |
|------|------|------|
| `--input` | `-i` | Input data file path (JSON or JSONL format) |

### Benchmark Configuration

| Parameter | Shorthand | Default | Description |
|------|------|--------|------|
| `--benchmark` | `-b` | `optmath` | Benchmark name (used for creating output directory) |

### Model Configuration

| Parameter | Shorthand | Default | Description |
|------|------|--------|------|
| `--model` | `-m` | `deepseek_official` | LLM model name |
| `--temperature` | - | `0.8` | Temperature parameter |
| `--max-tokens` | - | `8192` | Maximum tokens |

### Pass Configuration

| Parameter | Shorthand | Default | Description |
|------|------|--------|------|
| `--pass` | `-p` | `1` | Nth attempt (for multiple experiments) |

### Execution Configuration

| Parameter | Shorthand | Default | Description |
|------|------|--------|------|
| `--timeout` | - | `100` | Code execution timeout (seconds) |
| `--max-workers` | `-w` | `50` | Concurrency count |
| `--numerical-tolerance` | - | `0.05` | Numerical tolerance (5%) |
| `--enable-conversion` | - | `true` | Explicitly enable conversion fallback when initial execution is incorrect |
| `--disable-conversion` | - | `false` | Disable conversion fallback |

### Field Configuration

| Parameter | Default | Description |
|------|--------|------|
| `--question-field` | `en_question` | Question field name |
| `--answer-field` | `en_answer` | Answer field name |
| `--code-field` | `en_math_model_code` | Code field name |

### Options

| Parameter | Description |
|------|------|
| `--skip-generation` | Skip code generation, assume generated.jsonl already exists |
| `--verbose` / `-v` | Verbose output |

## Input Data Format

### JSON Format

```json
[
  {
    "en_question": "Problem description...",
    "en_answer": 123.45
  },
  ...
]
```

### JSONL Format

```jsonl
{"en_question": "Problem 1", "en_answer": 123.45}
{"en_question": "Problem 2", "en_answer": 678.90}
```

## Output File Description

### generated.jsonl

Code generation results, each record contains:
- `index`: Index
- `en_question`: Problem description
- `en_answer`: Ground truth answer
- `en_math_model_code`: Generated Python/Gurobi code
- `raw_output`: Raw LLM output
- `_tokens`: Number of tokens used
- `_error`: Error message (if any)

### eval.jsonl

Evaluation results, each record contains all fields from generated.jsonl, plus:
- `execution_state`: Execution status
- `execution_best_solution`: Solution obtained from execution
- `judge`: Whether correct
- `judge_reason`: Judgment reason
- `conversion_improved`: Whether conversion fallback improves the result
- `conversion_mode`: Execution mode used (`disabled`, `original`, `integer`, `continuous`, `converted`, etc.)
- `execution_time`: Execution time

### metrics.json

Overall evaluation metrics:
```json
{
  "total": 159,              // Total samples
  "code_generated": 159,     // Successfully generated code count
  "code_executed": 159,      // Successfully executed code count
  "correct": 82,             // Correct count
  "accuracy": 0.5157,        // Accuracy
  "generation_success_rate": 1.0,  // Code generation success rate
  "execution_success_rate": 1.0,   // Code execution success rate
  "total_tokens": 0,         // Total tokens
  "avg_tokens_per_sample": 0.0,  // Average tokens per sample
  "total_time": 4.79         // Total time (seconds)
}
```

## Usage Examples

### Example 1: Evaluate OptMATH Dataset

```bash
./scripts/run_eval.sh \
  --input data/optmath_test.jsonl \
  --benchmark optmath \
  --model deepseek_official \
  --pass 1
```

### Example 2: Compare Different Models

```bash
# DeepSeek
./scripts/run_eval.sh \
  --input data/test.jsonl \
  --benchmark comparison \
  --model deepseek_official \
  --pass 1

# GPT-4
./scripts/run_eval.sh \
  --input data/test.jsonl \
  --benchmark comparison \
  --model gpt4 \
  --pass 1
```

### Example 3: Evaluate Existing Code Only

```bash
# When generated code already exists, skip generation phase and evaluate directly.
# Conversion fallback remains enabled by default.
./scripts/run_eval.sh \
  --input path/to/generated.jsonl \
  --skip-generation
```

### Example 4: Custom Field Names

```bash
# If data uses different field names
./scripts/run_eval.sh \
  --input data/custom.jsonl \
  --question-field problem \
  --answer-field solution \
  --code-field generated_code
```

### Example 5: Disable Conversion Fallback

```bash
# Turn off conversion fallback and use only the first execution result
./scripts/run_eval.sh \
  --input path/to/generated.jsonl \
  --skip-generation \
  --disable-conversion
```

## Environment Variables

Default values can be set through environment variables:

```bash
export INPUT_FILE=data/test.jsonl
export MODEL_NAME=deepseek_official
export MAX_WORKERS=100

# Then run directly
./scripts/run_eval.sh
```

## Supported Models

All models configured through `config/default.yaml` can be used, including:
- `deepseek_official`: DeepSeek official API
- `gpt`: GPT-4o
- `claude`: Claude 3.5 Sonnet
- `gemini`: Gemini 2.5 Pro
- `minimax`: MiniMax

## Troubleshooting

### 1. Import Errors

Ensure running from project root directory:
```bash
cd /path/to/optmath_refactored
python3 eval/cli.py --input ...
```

### 2. API Key Issues

Ensure correct environment variables are set:
```bash
export LHL_DEEPSEEK_KEY=your_api_key
source ~/.zshrc
```

### 3. Code Execution Failures

Check if Gurobi is properly installed:
```bash
python3 -c "import gurobipy; print(gurobipy.__version__)"
```

## Performance Optimization Recommendations

1. **Concurrency**: For I/O-intensive tasks, higher concurrency can be set (50-100)
2. **Timeout**: Adjust timeout based on problem complexity (default 100 seconds)
3. **Skip Generation**: If only re-evaluation is needed, using `--skip-generation` can save significant time

## Differences from Original Evaluation System

| Feature | Original System (eval/) | New System (benchmark/) |
|------|----------------|---------------------|
| Output Directory | Single directory | Structured directory (benchmark/model/pass/time) |
| Configuration | Hard-coded | Flexible command-line parameters |
| Pass Support | None | Support multiple attempts |
| Skip Generation | None | Support `--skip-generation` |
| Conversion Fallback | None | Enabled by default, can be disabled with `--disable-conversion` |
| Metrics Output | Console | JSON file |

## License

Same as OptMATH project
