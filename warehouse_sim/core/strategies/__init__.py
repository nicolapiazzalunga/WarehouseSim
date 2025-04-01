## warehouse_sim/core/strategies/__init__.py
"""
Planner strategy factory for selecting different planning algorithms.
"""

from warehouse_sim.core.planner.astar import AStarPlanner
# from warehouse_sim.core.planner.greedy import GreedyPlanner  # Future extension
# from warehouse_sim.core.planner.mstar import MStarPlanner    # Future extension

def get_planner(strategy: str, occupancy, reservation_table):
    """
    Returns a planner instance based on the given strategy name.

    Args:
        strategy (str): The name of the planning strategy.
        occupancy (np.ndarray): The occupancy grid.
        reservation_table (ReservationTable): The shared reservation system.

    Returns:
        Planner instance.
    """
    strategy = strategy.lower()

    if strategy == "astar":
        return AStarPlanner(occupancy, reservation_table)

    # elif strategy == "greedy":
    #     return GreedyPlanner(occupancy, reservation_table)

    # elif strategy == "mstar":
    #     return MStarPlanner(occupancy, reservation_table)

    else:
        raise ValueError(f"Unknown planner strategy: {strategy}")
