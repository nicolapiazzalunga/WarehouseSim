"""
Global configuration values for simulation constants.
"""

# Warehouse dimensions (in meters)
WAREHOUSE_WIDTH = 50
WAREHOUSE_HEIGHT = 30

# Grid resolution (meters per cell)
GRID_RESOLUTION = 0.5

# Derived grid dimensions
GRID_WIDTH = int(WAREHOUSE_WIDTH / GRID_RESOLUTION)
GRID_HEIGHT = int(WAREHOUSE_HEIGHT / GRID_RESOLUTION)

# Object sizes (meters)
SHELF_SIZE = (4, 2)
PALLET_SIZE = (2, 1.5)

# Quantities
NUM_PALLETS = 80
NUM_ROBOTS = 10

# Simulation settings
ANIMATION_MAX_STEPS = 1000
ANIMATION_INTERVAL_MS = 300
GOAL_RESERVATION_DURATION = 50
