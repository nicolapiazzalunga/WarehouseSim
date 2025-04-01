# warehouse_sim/sim/run.py
"""
Entry point for running the warehouse simulation.
"""

import argparse
import logging
import os
from collections import defaultdict

from warehouse_sim import config
from warehouse_sim.core.environment import Environment
from warehouse_sim.core.reservation import ReservationTable
from warehouse_sim.core.task import TaskManager
from warehouse_sim.core.strategies import get_planner
from warehouse_sim.core.conflict_resolver import ConflictResolver
from warehouse_sim.agents.robot import Robot

def parse_args():
    parser = argparse.ArgumentParser(description="Warehouse multi-robot simulation")
    parser.add_argument("--goal-strategy", type=str, default="random",
                        choices=["random", "spread", "high_density"],
                        help="Goal assignment strategy")
    parser.add_argument("--planner-strategy", type=str, default="astar",
                        choices=["astar"],
                        help="Path planning algorithm to use")
    parser.add_argument("--conflict-strategy", type=str, default="wait_then_replan",
                        choices=["wait", "replan", "idle", "wait_then_replan"],
                        help="Conflict resolution strategy")
    parser.add_argument("--num-robots", type=int, default=config.NUM_ROBOTS,
                        help="Number of robots")
    parser.add_argument("--export-format", type=str, default="both",
                        choices=["gif", "mp4", "both"],
                        help="Export format")
    parser.add_argument("--world-version", type=str, default="default",
                        choices=["default", "two-phase"],
                        help="World stepper version to use")
    return parser.parse_args()

def main():
    args = parse_args()

    # Import the appropriate World class
    if args.world_version == "two-phase":
        from warehouse_sim.sim.world_two_phase import World
    else:
        from warehouse_sim.sim.world import World

    from warehouse_sim.sim.visualizer import animate

    # Setup logging
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    overlap_log = os.path.join(log_dir, "overlap.log")
    logging.basicConfig(
        filename=overlap_log,
        filemode='w',
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s'
    )

    print("[INIT] Setting up environment...")
    env = Environment(config.WAREHOUSE_WIDTH, config.WAREHOUSE_HEIGHT, config.GRID_RESOLUTION)
    env.place_shelves()
    env.place_pallets(config.NUM_PALLETS)

    print("[INIT] Initializing planner and reservation table...")
    reservation_table = ReservationTable()
    planner = get_planner(args.planner_strategy, env.occupancy, reservation_table)
    task_manager = TaskManager(env, strategy=args.goal_strategy)

    print("[INIT] Initializing conflict resolver...")
    conflict_resolver = ConflictResolver(strategy=args.conflict_strategy, max_retries=3, cooldown=2)

    print("[INIT] Spawning robots...")
    robots = []
    used_starts = set()
    for i in range(args.num_robots):
        for _ in range(1000):
            start = task_manager.get_goal((0, 0))
            if start not in used_starts:
                used_starts.add(start)
                break
        end = task_manager.get_goal(start)
        robot = Robot(i, start, end, planner)
        robots.append(robot)

    print("[INIT] Creating world...")
    world = World(
        environment=env,
        planner=planner,
        robots=robots,
        conflict_resolver=conflict_resolver,
        task_manager=task_manager
    )

    print("[RUN] Stepping simulation and capturing frames...")
    all_frames = []
    for _ in range(config.ANIMATION_MAX_STEPS):
        world.step(
            get_goal_fn=task_manager.get_goal,
            release_goal_fn=task_manager.release_goal
        )
        frame_snapshot = []
        seen_positions = defaultdict(list)

        for robot in robots:
            pos = robot.current_position()
            frame_snapshot.append(pos)
            seen_positions[pos].append(robot.id)

        for pos, ids in seen_positions.items():
            if len(ids) > 1:
                for i in range(len(ids)):
                    for j in range(i + 1, len(ids)):
                        logging.info(f"[OVERLAP] Robots {ids[i]} and {ids[j]} at {pos} on frame {world.frame}")

        all_frames.append(frame_snapshot)

    print("[DONE] Final Summary:")
    print(world.get_summary())

    print("[VIS] Starting animation...")
    gif_path = "warehouse_sim_output.gif"
    mp4_path = "warehouse_sim_output.mp4"

    if args.export_format in ("gif", "both"):
        animate(world, all_frames, gif_path, filename_mov=mp4_path if args.export_format == "both" else None)
    elif args.export_format == "mp4":
        animate(world, all_frames, None, filename_mov=mp4_path)

if __name__ == "__main__":
    main()
