# 🏢 WarehouseSim

**WarehouseSim** is a modular, multi-agent simulation platform for testing motion planning, task assignment, and conflict resolution strategies in structured warehouse environments.

---

## 🚀 Features

- ⬆️ A* planner with space-time reservation tables
- 🔌 Plug-in strategy architecture (A*, M*, etc.)
- 🧠 Flexible task assignment: `random`, `spread`, `high_density`
- ⚠️ Conflict resolution strategies: `wait`, `replan`, `idle`, cooldowns
- 📹 Streamlit UI for live simulation control and export
- ⚖️ CLI for headless batch runs and benchmarking
- 📊 Animated outputs (GIF, MP4) with overlap logging
- 🌐 PyPI-ready packaging with `pyproject.toml`

---

## 🧱 Architecture

```text
+------------------------------+
|        run.py (CLI)         |
+------------------------------+
              |
              v
+------------------------------+
|      Simulation Engine       |  <-- world.py / world_two_phase.py
|  - Multi-robot world logic   |
+------------------------------+
              |
              v
+------------------------------+
|         Robot Agents         |  <-- agents/robot.py
| - Task, state, motion logic  |
+------------------------------+
              |
              v
+------------------------------+
|         Core Modules         |
| + environment.py             |
| + task.py                    |
| + reservation.py             |
| + conflict_resolver.py       |
| + planner (A*, M*)           |
+------------------------------+
              |
              v
+------------------------------+
|        visualizer.py         |  <-- sim/
| - Draw, animate, export      |
+------------------------------+
```

---

## 👨‍💻 Installation

```bash
pip install .
```

---

## 🏃 CLI Usage

```bash
python -m warehouse_sim.sim.run \
  --goal-strategy spread \
  --planner-strategy astar \
  --num-robots 15 \
  --world-version two-phase \
  --export-format both
```

### 💡 Options

| Flag                | Description                                        |
|---------------------|----------------------------------------------------|
| `--goal-strategy`   | `random`, `spread`, `high_density`                |
| `--planner-strategy`| `astar`, `mstar` *(when implemented)*             |
| `--conflict-strategy` | `wait`, `replan`, `idle`, `wait_then_replan`     |
| `--num-robots`      | Number of robots                                  |
| `--export-format`   | `gif`, `mp4`, `both`                               |
| `--world-version`   | `default` (direct) or `two-phase` (intent-based)  |

---

## 💻 Streamlit App

Launch the interactive UI:

```bash
streamlit run streamlit_app.py
```

### UI Capabilities
- Adjust simulation params live
- See animated warehouse runs
- Download the MP4 output
- View overlap log sidebar

---

## 📂 Project Layout

```
warehouse_sim/
├── agents/               # Robot logic
├── core/                 # Planning + task infra
│   ├── planner/          # A* (future: M*, CBS...)
│   └── strategies/       # Planner selection
├── sim/                  # World logic + runner
├── utils/                # Config, logging
├── streamlit_app.py      # UI dashboard
├── run.py                # CLI entrypoint
├── visualizer.py         # Rendering + export
```

---

## 🚜 Roadmap

- [x] A* path planner with reservation
- [x] ConflictResolver with replan/idle/wait
- [x] Streamlit interface with animation export
- [ ] Add M*/CBS planner support
- [ ] Task metrics + path stats
- [ ] Heatmap + visual debug layers
- [ ] Unit tests (pytest)
- [ ] Optional OpenAI Gym interface

---

## 📄 License

MIT License

---

## 👤 Author

**Nicola Piazzalunga**  
[@nicolapiazzalunga](https://github.com/nicolapiazzalunga)

