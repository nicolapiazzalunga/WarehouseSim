## warehouse_sim/sim/visualizer.py
"""
Handles drawing and animating the simulation.
"""

import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend for faster rendering

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from warehouse_sim import config
import imageio.v3 as iio
import ffmpeg
import numpy as np
import os

COLORS = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'pink', 'lime']

def animate(world, all_frames, filename_gif, filename_mov=None):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, config.WAREHOUSE_WIDTH)
    ax.set_ylim(0, config.WAREHOUSE_HEIGHT)
    ax.set_aspect('equal')
    ax.set_title("Warehouse Robot Simulation")

    for label, (gx, gy, gw, gh) in world.environment.objects:
        color = 'gray' if label == 'shelf' else 'orange'
        x, y = world.environment.to_world_coords(gx, gy)
        width = gw * world.environment.resolution
        height = gh * world.environment.resolution
        ax.add_patch(plt.Rectangle((x, y), width, height, color=color, alpha=0.5))

    robot_dots = [
        ax.plot([], [], 'o', color=COLORS[i % len(COLORS)], markersize=10)[0]
        for i in range(len(world.robots))
    ]

    def init():
        for dot in robot_dots:
            dot.set_data([], [])
        return robot_dots

    def update(frame):
        for i, robot_dot in enumerate(robot_dots):
            gx, gy = all_frames[frame][i]
            wx, wy = world.environment.to_world_coords(gx, gy)

            # 🚨 Jump detection
            if not hasattr(update, "last_positions"):
                update.last_positions = [None] * len(world.robots)

            last_pos = update.last_positions[i]
            if last_pos:
                last_gx, last_gy = last_pos
                dx, dy = abs(gx - last_gx), abs(gy - last_gy)
                if dx > 1 or dy > 1:
                    print(f"[JUMP DETECTED] Robot {i} frame {frame}: ({last_gx},{last_gy}) -> ({gx},{gy})")

            update.last_positions[i] = (gx, gy)
            robot_dot.set_data([wx + 0.25], [wy + 0.25])
        return robot_dots


    ani = animation.FuncAnimation(
        fig,
        update,
        init_func=init,
        frames=len(all_frames),
        interval=config.ANIMATION_INTERVAL_MS,
        blit=True
    )

    ani.save(filename_gif, writer='pillow')
    print(f"[VIS] Animation saved to {filename_gif}")

    if filename_mov:
        print("[VIS] Converting GIF to MP4...")
        frames = []
        for frame in iio.imiter(filename_gif):
            if frame.shape[2] == 4:
                frame = frame[:, :, :3]
            frames.append(frame)

        height, width, _ = frames[0].shape

        process = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{width}x{height}', framerate=1000/config.ANIMATION_INTERVAL_MS)
            .output(filename_mov, vcodec='libx264', pix_fmt='yuv420p', movflags='faststart')
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

        for frame in frames:
            process.stdin.write(frame.astype(np.uint8).tobytes())

        process.stdin.close()
        process.wait()
        print(f"[VIS] MP4 saved to {filename_mov}")
