# Maze Solving Robot 🤖

A modular, Dockerized ROS 2 Humble mobile robot simulation and navigation environment for autonomous maze solving, path planning, and mapping.

---

## 📌 Overview

**Maze Solving Robot** is an autonomous differential drive robot built and simulated using **ROS 2 Humble**, **Gazebo Classic**, and **RViz2**. The project provides a containerized development workflow with hardware acceleration (NVIDIA GPU / DRI OpenGL support) and full GUI integration, allowing easy reproduction without dependency conflicts.

Key capabilities:
- Custom differential drive robot URDF definition with realistic inertial properties and 3D mesh components (wheels, caster, base chassis).
- Headless or GUI-based simulation in Gazebo Classic.
- Robot state visualization and joint inspection in RViz2.
- Containerized development using Docker, Dev Containers, and Docker Compose with colcon workspace configurations.

---

## 📁 Repository Structure

```text
.
├── .devcontainer/                  # VS Code Dev Container configuration
│   └── devcontainer.json
├── maze_bot/                       # Main ROS 2 package
│   ├── launch/                     # ROS 2 Python launch scripts
│   │   ├── gazebo.launch.py        # Gazebo simulation world & entity spawner
│   │   └── rviz.launch.py          # RViz2 visualization and state publishers
│   ├── meshes/                     # 3D STL collision & visual models
│   │   ├── base_link.stl
│   │   ├── front_caster.stl
│   │   ├── wheel_l.stl
│   │   └── wheel_r.stl
│   ├── urdf/                       # Robot description
│   │   └── maze_bot.urdf           # Links, joints, transmissions & physical parameters
│   ├── maze_bot/                   # Python source modules
│   ├── package.xml                 # Package metadata and dependencies
│   ├── setup.py                    # Package installation and launch/URDF data files
│   └── test/                       # Linters and unit tests (flake8, pep257, copyright)
├── Dockerfile                      # ROS 2 Humble development environment container
├── docker-compose.yml              # Container configuration with GPU/GUI pass-through
├── entrypoint.sh                   # Container entrypoint and environment sourcing
├── .gitignore                      # Git ignore rules (build artifacts, logs, caches)
└── README.md                       # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://docs.docker.com/engine/install/) & [Docker Compose](https://docs.docker.com/compose/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) (Optional, for NVIDIA GPU acceleration)
- Host Linux with X11 window system

---

### Step 1: Enable Host X11 Forwarding
Allow Docker to access the local X display server for rendering Gazebo and RViz:
```bash
xhost +local:root
# or for local docker user
xhost +local:docker
```

---

### Step 2: Running via Docker Compose / Dev Containers

#### Option A: VS Code Dev Containers (Recommended)
1. Open the repository root folder in VS Code.
2. When prompted, select **Reopen in Container** (or open command palette `Ctrl+Shift+P` -> `Dev Containers: Reopen in Container`).
3. The environment mounts your repository to `/workspace/src` inside the container, preserving the standard ROS 2 workspace layout while keeping the host Git repository clean.

#### Option B: Docker Compose CLI
Start the interactive workspace container:
```bash
docker compose run --rm maze-solver
```
To attach another shell into the running container:
```bash
docker exec -it ros2_maze_solver bash
```

---

### Step 3: Building the Workspace
Inside the container (`/workspace/src`):
```bash
colcon build --symlink-install
source /workspace/install/setup.bash
```

---

## 🎮 Launching the Robot

### 1. Visualizing in RViz
Inspect the robot model, joints, and transforms:
```bash
ros2 launch maze_bot rviz.launch.py
```

### 2. Simulating in Gazebo
Spawn the robot into the Gazebo simulation world:
```bash
ros2 launch maze_bot gazebo.launch.py
```

---

## 🛠️ Tech Stack & Dependencies

- **ROS Distribution**: ROS 2 Humble Hawksbill
- **Simulator**: Gazebo Classic 11 (`gazebo_ros_pkgs`)
- **Visualization**: RViz2, `robot_state_publisher`, `joint_state_publisher_gui`
- **Robotics & Math**: `rclpy`, `geometry_msgs`, `sensor_msgs`, `transforms3d`, `scipy`, `numpy`
- **Vision**: OpenCV (`cv_bridge`, `opencv-contrib-python`)

---

## 📜 License & Acknowledgements
- Developed for autonomous maze solving and robotics navigation research.
