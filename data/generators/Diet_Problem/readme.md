## Parameters

### n_foods
- **Description**: Range for the number of different food items available for selection.
- **Type**: Tuple of two integers `(min_foods, max_foods)`
- **Default**: `(5, 10)`
- **Reasonable Range**:
  - `min_foods`: 3 to 50
  - `max_foods`: `min_foods` to 100
  - Small problems: 5-15
  - Medium problems: 15-30
  - Large problems: 30-100

### n_nutrients
- **Description**: Range for the number of nutrients to track and balance in the diet.
- **Type**: Tuple of two integers `(min_nutrients, max_nutrients)`
- **Default**: `(3, 5)`
- **Reasonable Range**:
  - `min_nutrients`: 2 to 10
  - `max_nutrients`: `min_nutrients` to 20
- **Note**: Common nutrients include calories, protein, carbohydrates, fats, vitamins, minerals

### cost_range
- **Description**: Range for the cost per serving of each food item.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(1, 10)`
- **Reasonable Range**:
  - `min_cost`: 1 to 100
  - `max_cost`: `min_cost` to 1000
- **Note**: Represents monetary units per serving

### nutrient_range
- **Description**: Range for the amount of each nutrient per serving of food.
- **Type**: Tuple of two integers `(min_amount, max_amount)`
- **Default**: `(1, 50)`
- **Reasonable Range**:
  - `min_amount`: 0 to 100
  - `max_amount`: `min_amount` to 500
- **Note**: Units vary by nutrient type (e.g., grams, milligrams, calories)

### volume_range
- **Description**: Range for the volume or portion size of each food item.
- **Type**: Tuple of two integers `(min_volume, max_volume)`
- **Default**: `(1, 5)`
- **Reasonable Range**:
  - `min_volume`: 1 to 10
  - `max_volume`: `min_volume` to 50
- **Note**: Represents standardized serving sizes or portions

### volume_capacity_ratio
- **Description**: Ratio determining the maximum total volume of food that can be consumed relative to the sum of all food volumes.
- **Type**: Float between 0 and 1
- **Default**: `0.7`
- **Reasonable Range**: 0.3 to 0.9
- **Note**: Controls the overall diet size constraint

### seed
- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer
- **Usage**: Set for reproducible testing results