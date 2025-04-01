# warehouse_sim/sim/world_two_phase.py

from collections import defaultdict
from warehouse_sim.core.conflict_resolver import ConflictResolver, ResolutionAction

class World:
    def __init__(self, environment, planner, robots, conflict_resolver=None, task_manager=None):
        self.environment = environment
        self.planner = planner
        self.robots = robots
        self.frame = 0
        self.conflict_resolver = conflict_resolver
        self.task_manager = task_manager

    def step(self, get_goal_fn, release_goal_fn):
        self.frame += 1

        intents = {}            # robot_id -> next_pos
        conflicts = defaultdict(list)  # next_pos -> list of robot_ids
        approved = set()        # robot_ids allowed to move

        # --- Phase 1: Collect Intents ---
        for robot in self.robots:
            if robot.state.name == "MOVING" and 0 <= robot.step_index < len(robot.path):
                next_pos = robot.path[robot.step_index]
                intents[robot.id] = next_pos
                conflicts[next_pos].append(robot.id)

        # --- Phase 2: Resolve Conflicts ---
        for pos, robot_ids in conflicts.items():
            if len(robot_ids) == 1:
                approved.add(robot_ids[0])
            else:
                winner = min(robot_ids)
                approved.add(winner)
                for loser in robot_ids:
                    if loser != winner:
                        loser_robot = self.robots[loser]
                        loser_robot.log_event("BLOCKED", f"Conflict at {pos}, blocked by Robot {winner}")
                        if self.conflict_resolver:
                            action = self.conflict_resolver.resolve(loser_robot.id, self.frame)
                            if action == ResolutionAction.REPLAN:
                                new_start = loser_robot.current_position()
                                new_goal = self.task_manager.get_goal(new_start)
                                new_path = self.planner.plan_and_reserve(new_start, new_goal, robot_id=loser_robot.id)
                                if new_path:
                                    loser_robot.path = new_path
                                    loser_robot.step_index = 0
                                    loser_robot.end = new_goal
                                    self.conflict_resolver.reset(loser_robot.id)
                                    loser_robot.log_event("RESOLVE", "Replanned path.")
                            elif action == ResolutionAction.IDLE:
                                loser_robot.state = loser_robot.state.IDLE
                                loser_robot.log_event("RESOLVE", "Idled due to conflict.")

        # --- Phase 3: Move Approved Robots ---
        for robot in self.robots:
            if robot.id not in approved:
                continue

            if robot.step_index >= len(robot.path):
                continue  # path exhausted, do not move

            current_pos = robot.current_position()
            next_pos = robot.path[robot.step_index]

            # Prevent teleportation
            dx, dy = abs(next_pos[0] - current_pos[0]), abs(next_pos[1] - current_pos[1])
            if dx > 1 or dy > 1:
                robot.log_event("JUMP DETECTED", f"From {current_pos} to {next_pos} at frame {self.frame}")
                continue

            # Final reservation checks
            reserved_by_other = self.planner.reservation_table.cell_reservations.get(next_pos, {}).get(self.frame)
            if reserved_by_other is not None and reserved_by_other != robot.id:
                robot.log_event("BLOCKED", f"Final check failed: Cell {next_pos} reserved by Robot {reserved_by_other}")
                continue

            if self.planner.reservation_table.is_edge_reserved(current_pos, next_pos, self.frame):
                robot.log_event("BLOCKED", f"Final check failed: Edge {current_pos}->{next_pos} reserved")
                continue

            # Reserve and move
            self.planner.reservation_table.reserve_cell(
                next_pos[0], next_pos[1], self.frame, robot_id=robot.id
            )
            self.planner.reservation_table.reserve_edge(
                current_pos, next_pos, self.frame, robot_id=robot.id
            )

            robot.step_index += 1
            if self.conflict_resolver:
                self.conflict_resolver.reset(robot.id)

            # Update state if path is done
            if robot.step_index >= len(robot.path):
                robot.state = robot.state.IDLE
                robot.waiting_for_reassignment = True

            robot.log_event("MOVE", f"Moved to {next_pos} at frame {self.frame}")

        # --- Phase 4: Update robots (including IDLE state reassignments) ---
        for robot in self.robots:
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
