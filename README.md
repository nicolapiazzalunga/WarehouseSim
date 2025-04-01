# 🏭 WarehouseSim

**WarehouseSim** is a modular, multi-agent warehouse simulation platform designed to test and visualize motion planning, task coordination, and conflict resolution strategies in structured environments.

---

## 🚀 Features

- ✅ A* planner with space-time reservation tables  
- 🔌 Planner strategy injection (`A*`, Greedy, CBS-ready)  
- 🧠 Task assignment with customizable strategies (`random`, `spread`, `high_density`)  
- ⚠️ Conflict detection & resolution (wait, replan, idle)  
- 🎥 Animated visualizer with GIF/MP4 export  
- 🖥️ **Streamlit UI for interactive simulation control**  
- 🧪 CLI-driven batch mode for benchmarking  
- 📦 Packaged via `pyproject.toml` for installability  

---

## 🧱 Architecture Diagram

```text
+-----------------------------+
|        run.py (CLI)        |
+-----------------------------+
             |
             v
+-----------------------------+
|       Simulation Engine     | <-- world.py
|  - Steps agents each frame  |
|  - Handles movement logic   |
+-----------------------------+
             |
             v
+-----------------------------+
|        Robot Agents         | <-- agents/robot.py
| - Path + task logic         |
+-----------------------------+
             |
             v
+-----------------------------+
|      Core Modules           |
|                             |
| + Environment (grid)        |
| + ReservationTable          |
| + TaskManager               |
| + Planner (A*)              |
+-----------------------------+
             |
             v
+-----------------------------+
|       Visualizer (sim/)     |
| - Draws frames + export     |
+-----------------------------+
```

---

## 🧑‍💻 Install (After Cloning)

```bash
pip install .
```

---

## 🏃 CLI Usage

```bash
python -m warehouse_sim.sim.run \
  --goal-strategy spread \
  --planner-strategy astar \
  --num-robots 10 \
  --export-format both \
  --world-version two-phase
```

### 💡 CLI Options

| Flag                | Description                                                  |
|---------------------|--------------------------------------------------------------|
| `--goal-strategy`   | `random`, `spread`, `high_density`                           |
| `--planner-strategy`| `astar`, `greedy`, `mstar` (if implemented)                  |
| `--num-robots`      | Number of robots to simulate                                 |
| `--export-format`   | Format to save the output: `gif`, `mp4`, or `both`           |
| `--world-version`   | World logic engine: `default` (standard) or `two-phase` (atomic intent-based) |

---

## 🖥️ Interactive UI

WarehouseSim includes a Streamlit-powered dashboard for interactive control and visualization of simulations.

### ▶️ Launch it

```bash
streamlit run streamlit_app.py
```

### Features
- Adjust number of robots, planner, goal strategy
- Run simulation in-browser
- View animated result instantly
- Download MP4 directly

---

## 🗂 Project Structure

```
warehouse_sim/
├── core/              # Planning, environment, reservations
├── sim/               # World logic and visualizer
├── agents/            # Robot agent class
├── utils/             # Configuration constants
├── generate_scaffold.py
```

---

## 📸 Sample Output

> ![WarehouseSim Animation](warehouse_sim_output.gif)

---

## 📦 Roadmap

- [x] Modular planner injection system  
- [x] A* planning with reservations  
- [x] Replanning via ConflictResolver  
- [x] Streamlit UI  
- [ ] Add Greedy/CBS/M* planners  
- [ ] Heatmap + overlap visualization  
- [ ] Test suite with `pytest`  
- [ ] Streamlit: per-robot stats + path plotting  
- [ ] Optional Gym wrapper for RL agents  

---

## 📄 License

MIT License

---

## 👤 Author
**Nicola Piazzalunga** – [@gmail.com](https://github.com/nicolapiazzalunga)
