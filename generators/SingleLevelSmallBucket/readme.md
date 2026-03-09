## Parameters

### n_items
- **Description**: The range for number of different products to be produced
- **Type**: Tuple of two integers `(min_items, max_items)`
- **Default**: `(3, 5)`
- **Reasonable Range**: 
  - `min_items`: 1 to 20
  - `max_items`: `min_items` to 50

### n_machines
- **Description**: The range for number of parallel machines available for production
- **Type**: Tuple of two integers `(min_machines, max_machines)`
- **Default**: `(2, 3)`
- **Reasonable Range**:
  - `min_machines`: 1 to 10
  - `max_machines`: `min_machines` to 20

### n_periods
- **Description**: The range for number of time periods in the planning horizon
- **Type**: Tuple of two integers `(min_periods, max_periods)`
- **Default**: `(5, 8)`
- **Reasonable Range**:
  - `min_periods`: 1 to 50
  - `max_periods`: `min_periods` to 100

### setup_cost_range
- **Description**: Range for the cost of setting up production for any item
- **Type**: Tuple of two floats `(min_cost, max_cost)`
- **Default**: `(150, 250)`
- **Reasonable Range**:
  - `min_cost`: 0 to 1000
  - `max_cost`: `min_cost` to 5000

### startup_cost_range
- **Description**: Range for the cost of starting up production after idle time
- **Type**: Tuple of two floats `(min_cost, max_cost)`
- **Default**: `(100, 200)`
- **Reasonable Range**:
  - `min_cost`: 0 to 1000
  - `max_cost`: `min_cost` to 5000

### holding_cost_range
- **Description**: Range for the cost of holding one unit of inventory per period
- **Type**: Tuple of two floats `(min_cost, max_cost)`
- **Default**: `(1, 3)`
- **Reasonable Range**:
  - `min_cost`: 0 to 50
  - `max_cost`: `min_cost` to 100

### backlog_cost_range
- **Description**: Range for the penalty cost of backlogging one unit per period
- **Type**: Tuple of two floats `(min_cost, max_cost)`
- **Default**: `(8, 12)`
- **Reasonable Range**:
  - `min_cost`: 0 to 100
  - `max_cost`: `min_cost` to 500

### startup_time_range
- **Description**: Range for the time required to start up a machine
- **Type**: Tuple of two floats `(min_time, max_time)`
- **Default**: `(10, 20)`
- **Reasonable Range**:
  - `min_time`: 0 to 60
  - `max_time`: `min_time` to 120

### capacity_range
- **Description**: Range for the production capacity of machines per period
- **Type**: Tuple of two floats `(min_capacity, max_capacity)`
- **Default**: `(80, 120)`
- **Reasonable Range**:
  - `min_capacity`: 0 to 500
  - `max_capacity`: `min_capacity` to 1000

### demand_range
- **Description**: Range for the demand of each product in each period
- **Type**: Tuple of two floats `(min_demand, max_demand)`
- **Default**: `(20, 50)`
- **Reasonable Range**:
  - `min_demand`: 0 to 200
  - `max_demand`: `min_demand` to 500

### seed
- **Description**: Random seed for reproducibility of the generated problem instance
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer