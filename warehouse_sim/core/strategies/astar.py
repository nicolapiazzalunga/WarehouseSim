## warehouse_sim/core/planner/astar.py
"""
A* planner with space-time reservation handling.
"""

import heapq
from warehouse_sim import config
from warehouse_sim.core.planner.base import BasePlanner

class AStarPlanner(BasePlanner):
    def __init__(self, occupancy_grid, reservation_table):
        self.grid = occupancy_grid
        self.reservation_table = reservation_table

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def plan(self, start, goal):
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]  # up, down, left, right, wait
        open_set = []
        heapq.heappush(open_set, (0, 0, start))  # (f_score, time, position)

        came_from = {}
        g_score = {(start, 0): 0}

        while open_set:
            _, t, current = heapq.heappop(open_set)

            if current == goal:
                path = [current]
                while (current, t) in came_from:
                    current, t = came_from[(current, t)]
                    path.append(current)
                return list(reversed(path))

            for dx, dy in moves:
                nx, ny = current[0] + dx, current[1] + dy

                if not (0 <= nx < config.GRID_WIDTH and 0 <= ny < config.GRID_HEIGHT):
                    continue
                if self.grid[nx, ny] == 1:
                    continue
                if self.reservation_table.is_reserved(nx, ny, t + 1):
                    continue
                if self.reservation_table.is_edge_reserved(current, (nx, ny), t + 1):
                    continue

                next_pos = (nx, ny)
                key = (next_pos, t + 1)
                tentative_g = g_score.get((current, t), float('inf')) + 1

                if tentative_g < g_score.get(key, float('inf')):
                    g_score[key] = tentative_g
                    f_score = tentative_g + self.heuristic(next_pos, goal)
                    heapq.heappush(open_set, (f_score, t + 1, next_pos))
                    came_from[key] = (current, t)

        return None

    def plan_and_reserve(self, start, goal, robot_id=None):
        path = self.plan(start, goal)
        if path:
            self.reservation_table.reserve_path(path, robot_id=robot_id)
            self.reservation_table.reserve_edges(path)
            self.reservation_table.reserve_goal_forever(
                path[-1][0], path[-1][1], start_time=len(path), robot_id=robot_id
            )
            self.reservation_table.reserve_cell(start[0], start[1], 0, robot_id=robot_id)
        return path
