# Instance Generation Pipeline

## Overview

The instance generation pipeline creates optimization problem instances from problem templates with optional difficulty control based on complexity scoring.

## Key Features

- **Basic Generation**: Generate instances from problem templates without filtering
- **Difficulty Control**: Generate instances within target complexity ranges (easy, medium, hard, or custom)
- **Complexity Scoring**: Automatic computation of instance complexity using multiple metrics
- **Feedback-Driven Adjustment**: Optional LLM-based parameter refinement for target requirements

## Quick Start

### Basic Usage

```python
from optmath.generators import InstanceGenerationPipeline

# Basic generation (no difficulty control)
pipeline = InstanceGenerationPipeline(
    base_dir="generators",
    num_instances=10,
    output_file="output/instances.json"
)

instances = pipeline.run()
```

### Difficulty-Controlled Generation

```python
# Generate medium difficulty instances
pipeline = InstanceGenerationPipeline(
    base_dir="generators",
    difficulty="medium",  # "easy", "medium", or "hard"
    num_instances=10,
    output_file="output/medium_instances.json"
)

instances = pipeline.run()
```

### Custom Complexity Range

```python
# Generate with custom complexity bounds
pipeline = InstanceGenerationPipeline(
    base_dir="generators",
    target_complexity=(80.0, 120.0),  # Custom [min, max] range
    num_instances=10,
    output_file="output/custom_instances.json"
)

instances = pipeline.run()
```

### Enable Feedback-Driven Configuration

```python
# Use LLM to adjust generation parameters
pipeline = InstanceGenerationPipeline(
    base_dir="generators",
    difficulty="hard",
    enable_feedback=True,  # Enable LLM-based parameter adjustment
    model_name="deepseek_official",
    num_instances=20
)

instances = pipeline.run()
```

## Difficulty Levels

| Level | Complexity Range | Max Time | Description |
|-------|------------------|----------|-------------|
| Easy | [10, 50] | 5s | Simple problems with few variables |
| Medium | [50, 150] | 30s | Medium complexity |
| Hard | [150, 500] | 120s | Complex problems with many constraints |

## Complexity Scoring

The complexity score is computed as:

```
S(PD) = α_bin·N_bin + α_int·N_int + α_cont·N_cont
        + β_lin·N_lin + β_indic·N_indic + β_quad·N_quad + β_gen·N_gen
        + γ_BigM·f_BigM + δ_expr·L_avg_expr
```

Where:
- **Variables**: Binary (N_bin), Integer (N_int), Continuous (N_cont) counts
- **Constraints**: Linear (N_lin), Indicator (N_indic), Quadratic (N_quad), General (N_gen) counts
- **Big-M**: Frequency of Big-M formulations (f_BigM)
- **Expressions**: Average term count per constraint (L_avg_expr)

## API Reference

### InstanceGenerationPipeline

Main pipeline class for generating instances with optional difficulty control.

**Parameters:**
- `config` (InstanceGenerationConfig): Configuration object
- `base_dir` (str): Directory containing problem generators
- `difficulty` (str): "easy", "medium", "hard", or None for no filtering
- `target_complexity` (Tuple[float, float]): Custom [min, max] complexity range
- `enable_feedback` (bool): Enable LLM-based parameter adjustment
- `model_name` (str): LLM model for feedback generation
- `**kwargs`: Additional parameters (num_instances, max_iter, var_num_max, etc.)

**Methods:**
- `run(output_file=None, verbose=True)`: Run generation and return instances

### DifficultyLevel

Dataclass representing a difficulty level.

**Attributes:**
- `name` (str): Level identifier
- `complexity_min` (float): Minimum complexity score
- `complexity_max` (float): Maximum complexity score
- `solve_time_max` (float): Maximum expected solve time (seconds)
- `description` (str): Human-readable description

**Predefined Levels:**
- `DifficultyLevel.EASY`: [10, 50], 5s max
- `DifficultyLevel.MEDIUM`: [50, 150], 30s max
- `DifficultyLevel.HARD`: [150, 500], 120s max

### ComplexityScorer

Computes complexity scores from LP files or Gurobi models.

**Methods:**
- `score_from_lp_file(lp_content: str) -> float`: Score from LP file content
- `score_from_model(model) -> float`: Score from Gurobi model

## Output Format

Generated instances are saved as JSON with the following structure:

```json
[
  {
    "subclass": "Assignment Problem",
    "mathematical_expression": "Minimize ...",
    "lp_data": "\\* Problem LP file content...",
    "status": "OPTIMAL",
    "objective": 42.0,
    "solve_time": 1.23,
    "complexity": 73.5
  }
]
```

When difficulty control is enabled, each instance includes a `complexity` field.

## Examples

See test files for complete examples:
- `test_difficulty_simple.py`: Basic difficulty control tests
- `test_difficulty_generation.py`: Full pipeline tests
- `test_complete_pipeline_difficulty.py`: End-to-end pipeline test

## Implementation Notes

### Backward Compatibility

The `InstanceGenerationPipeline` class now includes difficulty control features by default. To use the original pipeline without difficulty control:

```python
from optmath.generators import BaseInstanceGenerationPipeline

pipeline = BaseInstanceGenerationPipeline(
    base_dir="generators",
    num_instances=10
)
instances = pipeline.run()
```

### Complexity Filtering

When difficulty control is enabled:
1. Instances are generated with random parameters
2. Each instance's complexity is computed
3. Instances outside the target range are filtered out
4. Generation continues until enough instances pass the filter

This may result in more generation attempts than `num_instances` to account for filtering.
