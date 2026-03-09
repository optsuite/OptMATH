## Parameters

### n_peaks
- **Description**: The number of peaks in the NMR spectrum to be assigned
- **Type**: Integer
- **Default**: `10`
- **Reasonable Range**: 5 to 1000
- **Impact**: Larger numbers increase problem complexity and solution time

### n_acids
- **Description**: The number of amino acids in the protein sequence
- **Type**: Integer
- **Default**: `12`
- **Reasonable Range**: 5 to 1000
- **Impact**: Larger numbers increase possible assignment combinations

### n_assignments
- **Description**: The required number of peak-amino acid assignments to make
- **Type**: Integer
- **Default**: `8`
- **Reasonable Range**: 1 to min(n_peaks, n_acids)
- **Impact**: Affects problem feasibility and constraint satisfaction

### noe_density
- **Description**: The probability of NOE relations between peaks
- **Type**: Float between 0 and 1
- **Default**: `0.3`
- **Reasonable Range**: 0.1 to 0.9
- **Impact**: Higher density adds more constraints and increases problem difficulty

### nth
- **Description**: Distance threshold (in Angstroms) for NOE relations between amino acids
- **Type**: Float
- **Default**: `5.0`
- **Reasonable Range**: 2.0 to 10.0
- **Impact**: Affects the number of valid assignments due to distance constraints

### cost_range
- **Description**: A tuple specifying the minimum and maximum costs for peak-amino acid assignments
- **Type**: Tuple of two floats `(min_cost, max_cost)`
- **Default**: `(0.0, 1.0)`
- **Reasonable Range**:
  - `min_cost`: 0.0 to 100.0
  - `max_cost`: `min_cost` to 100.0
- **Impact**: Influences the objective function and solution quality

### seed
- **Description**: Random seed for reproducible problem generation
- **Type**: Integer (optional)
- **Default**: `None`
- **Reasonable Range**: Any valid integer
- **Impact**: Ensures consistent problem instances across multiple runs