## warehouse_sim/sim/world.py
"""
Simulates a world of multiple robots, stepping each frame.
"""

from warehouse_sim.core.conflict_resolver import ConflictResolver, ResolutionAction

class World:
    def __init__(self, environment, planner, robots, conflict_resolver=None, task_manager=None):
        self.environment = environment
        self.planner = planner
        self.robots = robots
        self.frame = 0
        self.conflict_resolver = conflict_resolver
        self.task_manager = task_manager  # Required for replanning

    def step(self, get_goal_fn, release_goal_fn):
        self.frame += 1

        for robot in self.robots:
            if robot.state.name == "MOVING" and 0 <= robot.step_index < len(robot.path):
                current_pos = robot.current_position()
                next_pos = robot.path[robot.step_index]

                blocked = False

                # Check for reservation conflicts
                reserved_by_other = self.planner.reservation_table.cell_reservations.get(next_pos, {}).get(self.frame)
                if reserved_by_other is not None and reserved_by_other != robot.id:
                    robot.log_event("BLOCKED", f"Cell {next_pos} at frame {self.frame} reserved by Robot {reserved_by_other}")
                    blocked = True

                if self.planner.reservation_table.is_edge_reserved(current_pos, next_pos, self.frame):
                    robot.log_event("BLOCKED", f"Edge conflict: {current_pos} → {next_pos} at frame {self.frame}")
                    blocked = True

                if blocked:
                    if self.conflict_resolver:
                        action = self.conflict_resolver.resolve(robot.id, self.frame)

                        if action == ResolutionAction.REPLAN:
                            new_start = robot.current_position()
                            new_goal = self.task_manager.get_goal(new_start)
                            new_path = self.planner.plan_and_reserve(new_start, new_goal, robot_id=robot.id)

                            if new_path:
                                robot.path = new_path
                                robot.step_index = 0
                                robot.end = new_goal
                                self.conflict_resolver.reset(robot.id)
                                robot.log_event("RESOLVE", "Replanned path.")
                            else:
                                robot.log_event("RESOLVE", "Replan failed, waiting.")

                        elif action == ResolutionAction.IDLE:
                            robot.state = robot.state.IDLE
                            robot.log_event("RESOLVE", "Idled due to conflict.")
                        # WAIT: no-op

                    continue  # Skip this robot’s move/reservation

                # Reserve movement
                self.planner.reservation_table.reserve_cell(
                    next_pos[0], next_pos[1], self.frame, robot_id=robot.id
                )
                self.planner.reservation_table.reserve_edge(
                    current_pos, next_pos, self.frame, robot_id=robot.id
                )

                # Reset conflict state
                if self.conflict_resolver:
                    self.conflict_resolver.reset(robot.id)

            robot.update(
                frame=self.frame,
                get_goal_fn=get_goal_fn,
                release_goal_fn=release_goal_fn
            )

    def get_summary(self):
        return {
            "frame": self.frame,
            "completed_tasks": {
                robot.id: robot.completed_tasks for robot in self.robots
            }
        }