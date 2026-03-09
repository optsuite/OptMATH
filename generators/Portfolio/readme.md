# Portfolio Optimization Problem Generator Documentation

## Parameters

### n_assets

- **Description**: The number of assets to include in the portfolio.
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 5 to 1000 assets

### budget

- **Description**: Total investment amount available.
- **Type**: Integer
- **Default**: `1000000` ($1M)
- **Reasonable Range**: 10000 to 1000000000 ($10K to $1B)

### return_range

- **Description**: A tuple specifying the minimum and maximum expected annual returns for assets.
- **Type**: Tuple of two floats `(min_return, max_return)`
- **Default**: `(0.05, 0.15)` (5-15% annual return)
- **Reasonable Range**:
  - `min_return`: -0.1 to 0.1 (-10% to 10%)
  - `max_return`: `min_return` to 0.3 (up to 30%)

### risk_range

- **Description**: A tuple specifying the minimum and maximum annual volatility for assets.
- **Type**: Tuple of two floats `(min_risk, max_risk)`
- **Default**: `(0.10, 0.30)` (10-30% annual volatility)
- **Reasonable Range**:
  - `min_risk`: 0.05 to 0.2 (5% to 20%)
  - `max_risk`: `min_risk` to 0.5 (up to 50%)

### weight_bounds

- **Description**: A tuple specifying the minimum and maximum weight allowed for any single asset.
- **Type**: Tuple of two floats `(min_weight, max_weight)`
- **Default**: `(0.0, 0.3)` (0-30% per asset)
- **Reasonable Range**:
  - `min_weight`: 0.0 to 0.1
  - `max_weight`: 0.1 to 1.0

### target_return

- **Description**: Minimum required portfolio return.
- **Type**: Float
- **Default**: `0.10` (10% annual return)
- **Reasonable Range**: 0.05 to 0.20 (5-20%)

### seed

- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer

## Generated Instance Properties

For each generated portfolio optimization instance:

- Assets are labeled as "asset_0", "asset_1", etc.
- Expected returns are randomly assigned within return_range
- Individual asset risks (volatilities) are assigned within risk_range
- Correlation matrix is generated with values between -0.2 and 0.8
- Covariance matrix is computed from correlations and volatilities
- Weight constraints ensure diversification limits

## Mathematical Formulation

The portfolio optimization is formulated as a Quadratic Programming (QP) problem with:

- Objective to minimize portfolio variance
- Linear constraints for:
  - Target return requirement
  - Budget constraint (weights sum to 1)
  - Individual weight bounds
- Positive semi-definite covariance matrix
- Continuous decision variables (weights)

## Example Usage

```python
# Create generator with default parameters
generator = Generator()

# Create generator with custom parameters
custom_params = {
    "n_assets": 20,
    "budget": 500000,
    "return_range": (0.08, 0.20),
    "risk_range": (0.15, 0.35),
    "weight_bounds": (0.02, 0.25),
    "target_return": 0.12
}
generator = Generator(parameters=custom_params, seed=42)

# Generate and solve instance
model = generator.generate_instance()
model.optimize()
generator.print_solution(model)
```
