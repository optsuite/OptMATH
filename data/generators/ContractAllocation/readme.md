## Parameters

### n_producers
- **Description**: Range for the number of producers/factories to include in the problem.
- **Type**: Tuple of two integers `(min_producers, max_producers)`
- **Default**: `(3, 5)`
- **Reasonable Range**: 
  - `min_producers`: 2 to 50
  - `max_producers`: `min_producers` to 100
  - Small problems: 3-10
  - Medium problems: 10-30
  - Large problems: 30-100

### n_contracts
- **Description**: Range for the number of contracts to be allocated.
- **Type**: Tuple of two integers `(min_contracts, max_contracts)`
- **Default**: `(4, 6)`
- **Reasonable Range**:
  - `min_contracts`: 2 to 50
  - `max_contracts`: `min_contracts` to 100
  - Small problems: 4-12
  - Medium problems: 12-40
  - Large problems: 40-100

### capacity_range
- **Description**: Range for producer production capacities.
- **Type**: Tuple of two integers `(min_capacity, max_capacity)`
- **Default**: `(800, 2000)`
- **Reasonable Range**:
  - `min_capacity`: 100 to 5,000
  - `max_capacity`: `min_capacity` to 20,000
- **Note**: Should be set considering contract sizes

### contract_size_range
- **Description**: Range for the size of individual contracts.
- **Type**: Tuple of two integers `(min_size, max_size)`
- **Default**: `(400, 1500)`
- **Reasonable Range**:
  - `min_size`: 50 to 3,000
  - `max_size`: `min_size` to 10,000
- **Note**: Should be less than total producer capacity

### min_delivery_ratio
- **Description**: Ratio determining minimum delivery size as a fraction of producer capacity.
- **Type**: Float between 0 and 1
- **Default**: `0.1`
- **Reasonable Range**: 0.05 to 0.3
- **Note**: Lower values allow more flexible allocations

### cost_range
- **Description**: Range for production costs per unit.
- **Type**: Tuple of two integers `(min_cost, max_cost)`
- **Default**: `(10, 50)`
- **Reasonable Range**:
  - `min_cost`: 1 to 100
  - `max_cost`: `min_cost` to 500
- **Note**: Represents combined production and transportation costs

### min_contributors_range
- **Description**: Range for minimum number of producers required per contract.
- **Type**: Tuple of two integers `(min_contributors, max_contributors)`
- **Default**: `(1, 3)`
- **Reasonable Range**:
  - `min_contributors`: 1 to 5
  - `max_contributors`: `min_contributors` to 10
- **Note**: Should not exceed total number of producers

### seed
- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer
- **Usage**: Set for reproducible results in testing