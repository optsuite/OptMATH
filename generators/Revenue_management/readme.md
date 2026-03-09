## Parameters

### n_resources
- **Description**: The number of flight legs (resources) in the network.
- **Type**: Integer
- **Default**: `3`
- **Reasonable Range**: 2 to 20
- **Note**: Represents different flight segments in the network

### n_packages
- **Description**: The number of travel packages (itineraries) to offer.
- **Type**: Tuple of two integers `(min_packages, max_packages)` or single Integer
- **Default**: `(4, 6)`
- **Reasonable Range**:
  - Small networks: 3 to 10 packages
  - Medium networks: 10 to 30 packages
  - Large networks: 30 to 100 packages
- **Note**: Affects problem complexity exponentially

### capacity_range
- **Description**: Range for the seat capacity of each flight leg.
- **Type**: Tuple of two integers `(min_capacity, max_capacity)`
- **Default**: `(150, 250)`
- **Reasonable Range**:
  - `min_capacity`: 50 to 200 seats
  - `max_capacity`: `min_capacity` to 400 seats
- **Note**: Based on typical aircraft capacities

### demand_range
- **Description**: Range for the demand of each travel package.
- **Type**: Tuple of two integers `(min_demand, max_demand)`
- **Default**: `(50, 150)`
- **Reasonable Range**:
  - `min_demand`: 10 to 100 bookings
  - `max_demand`: `min_demand` to 300 bookings
- **Note**: Should be proportional to flight capacities

### revenue_range
- **Description**: Range for the revenue per unit of each package.
- **Type**: Tuple of two integers `(min_revenue, max_revenue)`
- **Default**: `(200, 800)`
- **Reasonable Range**:
  - `min_revenue`: $100 to $500
  - `max_revenue`: `min_revenue` to $2000
- **Unit**: Dollars per booking
- **Note**: Should reflect market pricing

### resource_use_probability
- **Description**: Probability that a package will use an additional resource (flight leg).
- **Type**: Float between 0 and 1
- **Default**: `0.3`
- **Reasonable Range**: 0.1 to 0.5
- **Note**: Controls connectivity of the network
  - Lower values: More direct flights
  - Higher values: More connecting flights

### seed
- **Description**: Random seed for reproducibility of the generated problem instance.
- **Type**: Integer (optional)
- **Default**: `None` (random seed not set)
- **Reasonable Range**: Any valid integer
- **Usage**: Set for reproducible testing and validation