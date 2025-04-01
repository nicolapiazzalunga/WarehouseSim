"""
ConflictResolver module
------------------------
Scalable, production-ready system for handling robot conflicts.
Supports configurable strategies with retry, cooldown, and replan triggers.
"""

from enum import Enum, auto

class ResolutionAction(Enum):
    WAIT = auto()
    REPLAN = auto()
    IDLE = auto()
    NONE = auto()


class ConflictResolver:
    def __init__(self, strategy="wait_then_replan", max_retries=3, cooldown=2):
        """
        Initialize the conflict resolver.

        Args:
            strategy (str): Strategy to apply when a robot is blocked.
                Options:
                - "wait_then_replan"
                - "always_wait"
                - "always_replan"
                - "idle_on_block"
            max_retries (int): How many times to try waiting before replanning.
            cooldown (int): Cooldown period before next action after replanning.
        """
        self.strategy = strategy
        self.max_retries = max_retries
        self.cooldown = cooldown
        self.robot_state = {}  # robot_id -> {retries, cooldown_remaining}

    def resolve(self, robot_id, frame):
        """
        Resolve a conflict for the given robot at the current frame.

        Args:
            robot_id (int): ID of the robot in conflict.
            frame (int): Current simulation frame.

        Returns:
            ResolutionAction: Suggested resolution step.
        """
        state = self.robot_state.setdefault(robot_id, {
            "retries": 0,
            "cooldown_remaining": 0
        })

        # Apply cooldown if active
        if state["cooldown_remaining"] > 0:
            state["cooldown_remaining"] -= 1
            return ResolutionAction.WAIT

        # Strategy resolution
        if self.strategy == "wait_then_replan":
            if state["retries"] < self.max_retries:
                state["retries"] += 1
                return ResolutionAction.WAIT
            else:
                state["retries"] = 0
                state["cooldown_remaining"] = self.cooldown
                return ResolutionAction.REPLAN

        elif self.strategy == "always_wait":
            return ResolutionAction.WAIT

        elif self.strategy == "always_replan":
            return ResolutionAction.REPLAN

        elif self.strategy == "idle_on_block":
            return ResolutionAction.IDLE

        return ResolutionAction.NONE

    def reset(self, robot_id):
        """
        Reset retry and cooldown state for a robot (e.g., after successful move).
        """
        if robot_id in self.robot_state:
            self.robot_state[robot_id] = {
                "retries": 0,
                "cooldown_remaining": 0
            }

    def update_config(self, strategy=None, max_retries=None, cooldown=None):
        """
        Dynamically update strategy or thresholds.
        """
        if strategy:
            self.strategy = strategy
        if max_retries is not None:
            self.max_retries = max_retries
        if cooldown is not None:
            self.cooldown = cooldown
