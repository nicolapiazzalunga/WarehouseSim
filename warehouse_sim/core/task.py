## warehouse_sim/core/task.py
"""
TaskManager is responsible for assigning unique goal positions to robots,
with support for multiple assignment strategies.
"""

import random

class TaskManager:
    def __init__(self, environment, strategy="random"):
        self.env = environment
        self.strategy = strategy
        self.assigned_goals = set()

    def get_goal(self, start):
        """
        Returns a valid, unassigned goal position, based on strategy.
        """
        if self.strategy == "random":
            return self._get_random_goal(start)
        elif self.strategy == "spread":
            return self._get_spread_goal(start)
        elif self.strategy == "high_density":
            return self._get_high_density_goal(start)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def _get_random_goal(self, start):
        for _ in range(1000):
            x = random.randint(0, self.env.grid_width - 1)
            y = random.randint(0, self.env.grid_height - 1)
            candidate = (x, y)
            if self._is_valid_goal(candidate, start):
                self.assigned_goals.add(candidate)
                return candidate
        return start

    def _get_spread_goal(self, start, min_distance=10):
        min_dist_cells = int(min_distance / self.env.resolution)
        for _ in range(1000):
            x = random.randint(0, self.env.grid_width - 1)
            y = random.randint(0, self.env.grid_height - 1)
            candidate = (x, y)
            if not self._is_valid_goal(candidate, start):
                continue
            if all(
                abs(x - gx) + abs(y - gy) > min_dist_cells
                for gx, gy in self.assigned_goals
            ):
                self.assigned_goals.add(candidate)
                return candidate
        return self._get_random_goal(start)

    def _get_high_density_goal(self, start, neighborhood=5):
        best = None
        max_density = -1

        for _ in range(3000):
            x = random.randint(0, self.env.grid_width - 1)
            y = random.randint(0, self.env.grid_height - 1)
            candidate = (x, y)

            if not self._is_valid_goal(candidate, start):
                continue

            x0, x1 = max(0, x - neighborhood), min(self.env.grid_width, x + neighborhood + 1)
            y0, y1 = max(0, y - neighborhood), min(self.env.grid_height, y + neighborhood + 1)
            density = self.env.occupancy[x0:x1, y0:y1].sum()

            if density > max_density:
                max_density = density
                best = candidate

            if density >= 10:
                break

        if best:
            self.assigned_goals.add(best)
            return best

        return self._get_random_goal(start)

    def _is_valid_goal(self, candidate, start):
        return (
            self.env.is_free(*candidate) and
            candidate != start and
            candidate not in self.assigned_goals
        )

    def release_goal(self, pos):
        self.assigned_goals.discard(pos)
