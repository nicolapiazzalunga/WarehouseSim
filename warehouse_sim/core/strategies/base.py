# warehouse_sim/core/planner/base.py
from abc import ABC, abstractmethod

class BasePlanner(ABC):
    @abstractmethod
    def plan(self, start, goal):
        """Return a list of (x, y) grid positions from start to goal."""
        pass

    @abstractmethod
    def plan_and_reserve(self, start, goal, robot_id=None):
        """Plan a path and reserve it in space-time."""
        pass
