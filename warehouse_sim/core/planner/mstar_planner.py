"""
M* Path Planner (stub)
Designed for collision-aware multi-agent planning.
"""

from warehouse_sim import config
import heapq
import logging

class MStarPlanner:
    def __init__(self, occupancy_grid, reservation_table):
        self.grid = occupancy_grid
        self.res_table = reservation_table

    def plan(self, start, goal):
        """
        Fallback single-agent A* path. Used for individual agents initially.
        """
        logging.info(f"[M*] Planning single-agent path from {start} to {goal}")
        return self._a_star(start, goal)

    def plan_multiple(self, agents):
        """
        Plan all agents' paths with shared space-time awareness.
        Placeholder: independent A* plans (to be replaced with full M* logic).
        """
        logging.info(f"[M*] Planning for {len(agents)} agents (stub mode)")
        planned_paths = {}
        for agent in agents:
            path = self._a_star(agent.start, agent.end)
            if path:
                planned_paths[agent.id] = path
                self._reserve_path(path, agent.id)
            else:
                logging.warning(f"[M*] No path found for Robot {agent.id}")
        return planned_paths

    def _a_star(self, start, goal):
        """
        Basic A* for fallback or early development. Integrate M* conflict sets later.
        """
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
        open_set = []
        heapq.heappush(open_set, (0, 0, start))
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
                if self.res_table.is_reserved(nx, ny, t + 1):
                    continue
                next_pos = (nx, ny)
                key = (next_pos, t + 1)
                tentative_g = g_score.get((current, t), float("inf")) + 1
                if tentative_g < g_score.get(key, float("inf")):
                    g_score[key] = tentative_g
                    f_score = tentative_g + abs(goal[0] - nx) + abs(goal[1] - ny)
                    heapq.heappush(open_set, (f_score, t + 1, next_pos))
                    came_from[key] = (current, t)

        return None

    def _reserve_path(self, path, robot_id):
        self.res_table.reserve_path(path, robot_id=robot_id)
        self.res_table.reserve_edges(path)
        self.res_table.reserve_goal_forever(path[-1][0], path[-1][1], len(path), robot_id=robot_id)
