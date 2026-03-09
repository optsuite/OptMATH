#!/bin/bash
# OptMATH Benchmark Evaluation Script
# Purpose: Perform code generation and evaluation for different benchmarks

set -e  # Exit immediately on error

# ==================== Default Configuration ====================

# Input data
INPUT_FILE="${INPUT_FILE}"

# Benchmark configuration
BENCHMARK_NAME="${BENCHMARK_NAME:-optmath}"  # Benchmark name

# Model configuration
MODEL_NAME="${MODEL_NAME:-deepseek_official}"  # LLM model name
TEMPERATURE="${TEMPERATURE:-0.8}"             # Temperature parameter
MAX_TOKENS="${MAX_TOKENS:-8192}"              # Maximum tokens

# Pass configuration
PASS_N="${PASS_N:-1}"  # Nth attempt

# Execution configuration
TIMEOUT="${TIMEOUT:-100}"                      # Code execution timeout (seconds)
MAX_WORKERS="${MAX_WORKERS:-50}"               # Concurrency count
NUMERICAL_TOLERANCE="${NUMERICAL_TOLERANCE:-0.05}"  # Numerical tolerance
ENABLE_CONVERSION="${ENABLE_CONVERSION:-true}"      # Whether to enable conversion fallback

# Field configuration
QUESTION_FIELD="${QUESTION_FIELD:-en_question}"
ANSWER_FIELD="${ANSWER_FIELD:-en_answer}"
CODE_FIELD="${CODE_FIELD:-en_math_model_code}"

# Options
SKIP_GENERATION="${SKIP_GENERATION:-false}"  # Whether to skip code generation
VERBOSE="${VERBOSE:-false}"                  # Whether to output verbose information

# ==================== Help Information ====================

show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

OptMATH Benchmark Evaluation Tool

Required Parameters:
  --input, -i FILE          Input data file path (JSON or JSONL format)

Benchmark Configuration:
  --benchmark, -b NAME      Benchmark name (default: optmath)

Model Configuration:
  --model, -m NAME          LLM model name (default: deepseek_official)
  --temperature T           Temperature parameter (default: 0.8)
  --max-tokens N            Maximum tokens (default: 8192)

Pass Configuration:
  --pass, -p N              Nth attempt (default: 1)

Execution Configuration:
  --timeout SECONDS         Code execution timeout (default: 100)
  --max-workers, -w N       Concurrency count (default: 50)
  --numerical-tolerance T   Numerical tolerance (default: 0.05)
  --enable-conversion       Enable conversion fallback when initial execution is incorrect
  --disable-conversion      Disable conversion fallback

Field Configuration:
  --question-field FIELD    Question field name (default: en_question)
  --answer-field FIELD      Answer field name (default: en_answer)
  --code-field FIELD        Code field name (default: en_math_model_code)

Options:
  --skip-generation         Skip code generation, assume generated.jsonl already exists
  --verbose, -v             Verbose output
  --help, -h                Display this help information

Examples:
  # Evaluate OptMATH dataset
  $0 --input data/optmath_test.jsonl --benchmark optmath

  # Use different model
  $0 --input data/test.jsonl --model gpt4 --pass 1

  # Evaluate existing code only (skip generation)
  $0 --input data/test.jsonl --skip-generation

  # High concurrency evaluation
  $0 --input data/test.jsonl --max-workers 100

Environment Variables:
  Default values can be set using environment variables, e.g.:
  export INPUT_FILE=data/test.jsonl
  export MODEL_NAME=gpt4
  $0

Output Directory Structure:
  benchmark_results/
  └── {benchmark_name}/
      └── {model_name}/
          └── pass_{pass_n}/
              └── {timestamp}/
                  ├── generated.jsonl  # Generated code
                  ├── eval.jsonl       # Evaluation results
                  └── metrics.json      # Metrics summary

EOF
}

# ==================== Parameter Parsing ====================

while [[ $# -gt 0 ]]; do
    case $1 in
        --input|-i)
            INPUT_FILE="$2"
            shift 2
            ;;
        --benchmark|-b)
            BENCHMARK_NAME="$2"
            shift 2
            ;;
        --model|-m)
            MODEL_NAME="$2"
            shift 2
            ;;
        --temperature)
            TEMPERATURE="$2"
            shift 2
            ;;
        --max-tokens)
            MAX_TOKENS="$2"
            shift 2
            ;;
        --pass|-p)
            PASS_N="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --max-workers|-w)
            MAX_WORKERS="$2"
            shift 2
            ;;
        --numerical-tolerance)
            NUMERICAL_TOLERANCE="$2"
            shift 2
            ;;
        --enable-conversion)
            ENABLE_CONVERSION="true"
            shift
            ;;
        --disable-conversion)
            ENABLE_CONVERSION="false"
            shift
            ;;
        --question-field)
            QUESTION_FIELD="$2"
            shift 2
            ;;
        --answer-field)
            ANSWER_FIELD="$2"
            shift 2
            ;;
        --code-field)
            CODE_FIELD="$2"
            shift 2
            ;;
        --skip-generation)
            SKIP_GENERATION="true"
            shift
            ;;
        --verbose|-v)
            VERBOSE="true"
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown parameter: $1"
            show_help
            exit 1
            ;;
    esac
done

# ==================== Parameter Validation ====================

if [ -z "$INPUT_FILE" ]; then
    echo "Error: Must specify input file (--input)"
    show_help
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file does not exist: $INPUT_FILE"
    exit 1
fi

# ==================== Print Configuration ====================

echo "============================================================"
echo "  OptMATH Benchmark Evaluation"
echo "============================================================"
echo ""
echo "Input file: $INPUT_FILE"
echo "Benchmark name: $BENCHMARK_NAME"
echo "Model: $MODEL_NAME"
echo "Pass: $PASS_N"
echo "Concurrency: $MAX_WORKERS"
echo "Timeout: ${TIMEOUT}s"
echo "Skip generation: $SKIP_GENERATION"
echo "Enable conversion: $ENABLE_CONVERSION"
echo ""
echo "============================================================"

# ==================== Execute Evaluation ====================

cd "$(dirname "$0")/.."

# Build Python command
PYTHON_CMD="python3 eval/cli.py"

PYTHON_CMD="$PYTHON_CMD --input '$INPUT_FILE'"
PYTHON_CMD="$PYTHON_CMD --benchmark '$BENCHMARK_NAME'"
PYTHON_CMD="$PYTHON_CMD --model '$MODEL_NAME'"
PYTHON_CMD="$PYTHON_CMD --pass $PASS_N"
PYTHON_CMD="$PYTHON_CMD --temperature $TEMPERATURE"
PYTHON_CMD="$PYTHON_CMD --max-tokens $MAX_TOKENS"
PYTHON_CMD="$PYTHON_CMD --timeout $TIMEOUT"
PYTHON_CMD="$PYTHON_CMD --max-workers $MAX_WORKERS"
PYTHON_CMD="$PYTHON_CMD --numerical-tolerance $NUMERICAL_TOLERANCE"
PYTHON_CMD="$PYTHON_CMD --question-field '$QUESTION_FIELD'"
PYTHON_CMD="$PYTHON_CMD --answer-field '$ANSWER_FIELD'"
PYTHON_CMD="$PYTHON_CMD --code-field '$CODE_FIELD'"

if [ "$SKIP_GENERATION" = "true" ]; then
    PYTHON_CMD="$PYTHON_CMD --skip-generation"
fi

if [ "$ENABLE_CONVERSION" = "true" ]; then
    PYTHON_CMD="$PYTHON_CMD --enable-conversion"
else
    PYTHON_CMD="$PYTHON_CMD --disable-conversion"
fi

if [ "$VERBOSE" = "true" ]; then
    PYTHON_CMD="$PYTHON_CMD --verbose"
fi

# Execute evaluation
eval $PYTHON_CMD

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✓ Evaluation completed!"
else
    echo ""
    echo "✗ Evaluation failed (exit code: $exit_code)"
fi

exit $exit_code
