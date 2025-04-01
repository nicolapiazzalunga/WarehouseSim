# streamlit_app.py

import streamlit as st
import tempfile
import os
from collections import defaultdict
from warehouse_sim import config
from warehouse_sim.core.environment import Environment
from warehouse_sim.core.reservation import ReservationTable
from warehouse_sim.core.task import TaskManager
from warehouse_sim.core.strategies import get_planner
from warehouse_sim.agents.robot import Robot
from warehouse_sim.sim.visualizer import animate
from warehouse_sim.core.conflict_resolver import ConflictResolver

st.set_page_config(page_title="WarehouseSim UI", layout="wide")
st.title("🏭 WarehouseSim Interactive Simulation")

# Sidebar controls
st.sidebar.header("Simulation Settings")
num_robots = st.sidebar.slider("Number of Robots", 1, 50, config.NUM_ROBOTS)
goal_strategy = st.sidebar.selectbox("Goal Strategy", ["random", "spread", "high_density"])
planner_strategy = st.sidebar.selectbox("Planner Strategy", ["astar"])
export_format = st.sidebar.selectbox("Export Format", ["gif", "mp4", "both"])
world_version = st.sidebar.selectbox("World Logic", ["default", "two-phase"])
run_sim = st.sidebar.button("Run Simulation")

if run_sim:
    st.info("Initializing simulation...")

    env = Environment(config.WAREHOUSE_WIDTH, config.WAREHOUSE_HEIGHT, config.GRID_RESOLUTION)
    env.place_shelves()
    env.place_pallets(config.NUM_PALLETS)

    reservation_table = ReservationTable()
    planner = get_planner(planner_strategy, env.occupancy, reservation_table)
    task_manager = TaskManager(env, strategy=goal_strategy)
    conflict_resolver = ConflictResolver("replan")

    robots = []
    used_starts = set()
    for i in range(num_robots):
        for _ in range(1000):
            start = task_manager.get_goal((0, 0))
            if start not in used_starts:
                used_starts.add(start)
                break
        end = task_manager.get_goal(start)
        robot = Robot(i, start, end, planner)
        robots.append(robot)

    # Dynamically select World class
    if world_version == "two-phase":
        from warehouse_sim.sim.world_two_phase import World
    else:
        from warehouse_sim.sim.world import World

    world = World(env, planner, robots, conflict_resolver=conflict_resolver, task_manager=task_manager)
    st.info(f"🧪 Running world logic: `{world_version}`")


    st.info("Running simulation...")
    all_frames = []
    overlap_logs = []

    for _ in range(config.ANIMATION_MAX_STEPS):
        world.step(task_manager.get_goal, task_manager.release_goal)
        frame_snapshot = []
        seen_positions = defaultdict(list)

        for robot in robots:
            pos = robot.current_position()
            frame_snapshot.append(pos)
            seen_positions[pos].append(robot.id)

        for pos, ids in seen_positions.items():
            if len(ids) > 1:
                msg = f"[OVERLAP] Frame {world.frame}: Robots {ids} at {pos}"
                overlap_logs.append(msg)

        all_frames.append(frame_snapshot)

    with tempfile.TemporaryDirectory() as tmpdir:
        gif_path = os.path.join(tmpdir, "output.gif")
        mp4_path = os.path.join(tmpdir, "output.mp4") if export_format in ("mp4", "both") else None
        animate(world, all_frames, gif_path, filename_mov=mp4_path)

        st.success("Simulation complete!")
        st.image(gif_path, caption="Simulation Result", use_container_width=True)

        if mp4_path:
            with open(mp4_path, "rb") as f:
                st.download_button("Download MP4", f, file_name="warehouse_sim_output.mp4", mime="video/mp4")

    st.json(world.get_summary())

    if overlap_logs:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📄 Overlap Log")
        st.sidebar.text_area("Recent Overlaps", value="\n".join(overlap_logs[-50:]), height=200)
    else:
        st.sidebar.markdown("---")
        st.sidebar.success("✅ No overlaps detected!")
