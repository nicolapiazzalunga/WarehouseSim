## warehouse_sim/agents/robot.py
"""
Robot agent class encapsulating position, path, and task logic.
"""

from enum import Enum, auto

class RobotState(Enum):
    IDLE = auto()
    MOVING = auto()
    WAITING = auto()

class Robot:
    def __init__(self, robot_id, start, end, planner):
        self.id = robot_id
        self.start = start
        self.end = end
        self.planner = planner
        self.path = self.planner.plan_and_reserve(start, end, robot_id=self.id) or []
        self.step_index = 0
        self.state = RobotState.MOVING if self.path else RobotState.IDLE
        self.completed_tasks = 0
        self.waiting_for_reassignment = False

    def current_position(self):
        if self.step_index < len(self.path):
            return self.path[self.step_index]
        return self.end

    def update(self, frame, get_goal_fn, release_goal_fn):
        if self.state == RobotState.MOVING:
            self.step_index += 1
            if self.step_index >= len(self.path):
                self.state = RobotState.IDLE
                self.waiting_for_reassignment = True

        if self.state == RobotState.IDLE and self.waiting_for_reassignment:
            release_goal_fn(self.end)
            self.reassign(get_goal_fn)

    def reassign(self, get_goal_fn):
        new_start = self.current_position()
        new_end = get_goal_fn(new_start)
        new_path = self.planner.plan_and_reserve(new_start, new_end, robot_id=self.id)
        if new_path:
            self.start = new_start
            self.end = new_end
            self.path = new_path
            self.step_index = 0
            self.state = RobotState.MOVING
            self.waiting_for_reassignment = False
            self.completed_tasks += 1

    def log_event(self, tag, message):
        print(f"[Robot {self.id}] [{tag}] {message}")
