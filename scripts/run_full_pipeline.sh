#!/bin/bash
# OptMATH Full Pipeline Test Script
# Purpose: Generate instances -> Backtranslation -> Forward modeling -> Evaluation

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# ==================== Configuration ====================

require_env() {
    local var_name="$1"
    if [ -z "${!var_name}" ]; then
        echo "Error: Required environment variable is not set: ${var_name}"
        exit 1
    fi
}

require_env "LHL_DEEPSEEK_KEY"

# Output directory (keeps generated files)
OUTPUT_DIR="${OUTPUT_DIR:-output/demo_$(date +%Y%m%d_%H%M%S)}"

# ========== Step 1: Instance Generation ==========
GENERATORS_DIR="${GENERATORS_DIR:-${PROJECT_ROOT}/generators}"  # Generator directory
NUM_INSTANCES="${NUM_INSTANCES:-3}"                # Instances per problem class
MAX_ITER="${MAX_ITER:-100}"                        # Max iterations
VAR_NUM_MAX="${VAR_NUM_MAX:-30}"                   # Max variables
CONSTRAINT_NUM_MAX="${CONSTRAINT_NUM_MAX:-50}"     # Max constraints
NUM_WORKERS_GEN="${NUM_WORKERS_GEN:-4}"            # Concurrent workers

# ========== Step 2: Backtranslation ==========
MODEL_BT="${MODEL_BT:-deepseek_official}"          # Model name
MAX_WORKERS_BT="${MAX_WORKERS_BT:-2}"              # Concurrent workers
MAX_ITER_BT="${MAX_ITER_BT:-2}"                    # Refinement iterations
SAMPLE_SIZE_BT="${SAMPLE_SIZE_BT:-5}"              # Sample size
TEMPERATURE_BT="${TEMPERATURE_BT:-0.8}"            # Temperature

# ========== Step 3: Forward Modeling ==========
MODEL_MODELING="${MODEL_MODELING:-deepseek_official}"  # Model name
NUM_WORKERS_MODELING="${NUM_WORKERS_MODELING:-2}"  # Concurrent workers
TEMPERATURE_MODELING="${TEMPERATURE_MODELING:-0.8}" # Temperature
SAMPLE_SIZE_MODELING="${SAMPLE_SIZE_MODELING:-0}"  # 0=process all

# ========== Step 4: Evaluation ==========
TIMEOUT_EVAL="${TIMEOUT_EVAL:-60}"                 # Execution timeout (seconds)
MAX_WORKERS_EVAL="${MAX_WORKERS_EVAL:-4}"          # Concurrent workers

# ==================== Script Start ====================

echo "============================================================"
echo "  OptMATH Full Pipeline Test"
echo "============================================================"
echo ""
echo "Output directory: $OUTPUT_DIR"
echo "Project root: $PROJECT_ROOT"
echo "Generator directory: $GENERATORS_DIR"
echo ""
echo "--- Step 1: Instance Generation ---"
echo "  Instances per class: $NUM_INSTANCES"
echo "  Max iterations: $MAX_ITER"
echo "  Max variables: $VAR_NUM_MAX"
echo "  Max constraints: $CONSTRAINT_NUM_MAX"
echo ""
echo "--- Step 2: Backtranslation ---"
echo "  Model: $MODEL_BT"
echo "  Concurrent workers: $MAX_WORKERS_BT"
echo "  Sample size: $SAMPLE_SIZE_BT"
echo ""
echo "--- Step 3: Forward Modeling ---"
echo "  Model: $MODEL_MODELING"
echo "  Concurrent workers: $NUM_WORKERS_MODELING"
echo ""
echo "--- Step 4: Evaluation ---"
echo "  Timeout: ${TIMEOUT_EVAL}s"
echo "  Concurrent workers: $MAX_WORKERS_EVAL"
echo ""
echo "============================================================"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# File paths
INSTANCES_FILE="$OUTPUT_DIR/instances.json"
BACKTRANSLATION_DIR="$OUTPUT_DIR/backtranslation"
MODELING_DIR="$OUTPUT_DIR/modeling"
EVAL_OUTPUT="$OUTPUT_DIR/eval_results.jsonl"

# ==================== Step 1: Instance Generation ====================
echo ""
echo ">>> Step 1: Instance Generation (Generator -> LP files)"
echo "============================================================"

python -c "
import sys
sys.path.insert(0, '.')
from optmath.generators import InstanceGenerationPipeline

pipeline = InstanceGenerationPipeline(
    base_dir='$GENERATORS_DIR',
    num_instances=$NUM_INSTANCES,
    max_iter=$MAX_ITER,
    var_num_max=$VAR_NUM_MAX,
    constraint_num_max=$CONSTRAINT_NUM_MAX,
    num_workers=$NUM_WORKERS_GEN,
    output_file='$INSTANCES_FILE',
)

instances = pipeline.run()
print(f'\n✓ Generated {len(instances)} instances')
" || exit 1

# ==================== Step 2: Backtranslation ====================
echo ""
echo ">>> Step 2: Backtranslation (LP -> Natural Language)"
echo "============================================================"

python -c "
import sys
sys.path.insert(0, '.')
from optmath.backtranslation import BacktranslationPipeline

pipeline = BacktranslationPipeline(
    input_file='$INSTANCES_FILE',
    output_dir='$BACKTRANSLATION_DIR',
    model_name='$MODEL_BT',
    max_workers=$MAX_WORKERS_BT,
    max_iter=$MAX_ITER_BT,
    sample_size=$SAMPLE_SIZE_BT,
    temperature=$TEMPERATURE_BT,
)

results = pipeline.run()
print(f'\n✓ Backtranslation completed, processed {len(results)} instances')

# Display first example
if results:
    r = results[0]
    print(f'\nExample:')
    print(f'  Subclass: {r.subclass}')
    print(f'  Scenario: {r.scenario}')
    print(f'  Problem description: {r.problem_description[:150]}...')
    print(f'  Objective value (en_answer): {r.objective_value}')
" || exit 1

# Get backtranslation output file
BT_OUTPUT_FILE=$(ls -t "$BACKTRANSLATION_DIR"/backtranslation_*.json 2>/dev/null | head -1)
if [ -z "$BT_OUTPUT_FILE" ]; then
    echo "Error: Backtranslation output file not found"
    exit 1
fi

echo "Backtranslation output: $BT_OUTPUT_FILE"

# ==================== Step 3: Forward Modeling ====================
echo ""
echo ">>> Step 3: Forward Modeling (Natural Language -> Python/Gurobi Code)"
echo "============================================================"

python -c "
import sys
sys.path.insert(0, '.')
from optmath.modeling import ModelingPipeline

pipeline = ModelingPipeline(
    dataset_path='$BT_OUTPUT_FILE',
    output_dir='$MODELING_DIR',
    model_name='$MODEL_MODELING',
    num_workers=$NUM_WORKERS_MODELING,
    temperature=$TEMPERATURE_MODELING,
    sample_size=$SAMPLE_SIZE_MODELING,
)

output_file = pipeline.run()
print(f'\n✓ Forward modeling completed')
print(f'Output file: {output_file}')
" || exit 1

# Get forward modeling output file
MODELING_OUTPUT_FILE=$(ls -t "$MODELING_DIR"/generated_*.jsonl 2>/dev/null | head -1)
if [ -z "$MODELING_OUTPUT_FILE" ]; then
    echo "Error: Forward modeling output file not found"
    exit 1
fi

echo "Forward modeling output: $MODELING_OUTPUT_FILE"

# ==================== Step 4: Evaluation ====================
echo ""
echo ">>> Step 4: Evaluation (Execute Code -> Verify Results)"
echo "============================================================"

python -c "
import sys
sys.path.insert(0, '.')
from eval import EvaluationPipeline

pipeline = EvaluationPipeline(
    input_file='$MODELING_OUTPUT_FILE',
    output_file='$EVAL_OUTPUT',
    timeout=$TIMEOUT_EVAL,
    max_workers=$MAX_WORKERS_EVAL,
    enable_conversion=True,
)

stats = pipeline.run()
print(f'\n✓ Evaluation completed')
print(f'\nEvaluation Statistics:')
print(f'  Total: {stats[\"total\"]}')
print(f'  Correct: {stats[\"correct\"]}')
print(f'  Incorrect: {stats[\"total\"] - stats[\"correct\"]}')
print(f'  Accuracy: {stats[\"accuracy\"]:.2%}')
" || exit 1

# ==================== Summary ====================
echo ""
echo "============================================================"
echo "  Test Completed!"
echo "============================================================"
echo ""
echo "All generated files saved in: $OUTPUT_DIR"
echo ""
echo "File List:"
echo "  - instances.json              : Generated LP instances"
echo "  - backtranslation/            : Backtranslation results"
echo "  - modeling/                   : Forward modeling results"
echo "  - eval_results.jsonl          : Evaluation results"
echo ""
echo "View evaluation results:"
echo "  cat $EVAL_OUTPUT | jq '.en_question, .execution_state, .judge'"
echo ""
