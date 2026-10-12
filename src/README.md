# ROS 2 Humble Maze Solver & Path Planning Environment

Dockerized development environment for ROS 2 Humble with Gazebo Classic, RViz2, OpenCV, and GPU hardware acceleration.

---

## 🚀 Quick Start

### 1. Enable X11 GUI Access on Host
Before launching GUI tools (Gazebo / RViz / OpenCV windows), run this once per host session:
```bash
xhost +local:root
# or allow local connections:
xhost +local:docker
```

### 2. Open in Dev Container (Recommended)
1. Open this repository folder in VS Code / Antigravity.
2. When prompted, click **"Reopen in Container"** (or press `Ctrl+Shift+P` / `F1` and select **Dev Containers: Reopen in Container**).
3. VS Code will automatically build the image with your user UID/GID (1000), configure all GUI/GPU hardware mounts, and install the ROS 2 extensions.

---

### Alternative: Run directly with Docker CLI
If you ever want to run or test the container outside VS Code:

1. **Build image:**
   ```bash
   docker build -t ros2-humble-maze-solver:latest .
   ```

2. **Run container:**
   ```bash
   docker run -it --rm \
     --net=host \
     --ipc=host \
     --privileged \
     --gpus all \
     -e DISPLAY=$DISPLAY \
     -e QT_X11_NO_MITSHM=1 \
     -e ROS_DOMAIN_ID=0 \
     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
     -v /dev/dri:/dev/dri:rw \
     -v $(pwd):/workspace/src:rw \
     -w /workspace/src \
     --user 1000:1000 \
     --name ros2_maze_solver \
     ros2-humble-maze-solver:latest bash
   ```

3. **Opening additional terminals:**
   ```bash
   docker exec -it ros2_maze_solver bash
   ```

---

## 🛠️ Project Development Workflow

Inside the container (`/workspace/src`):

1. **Create your ROS 2 packages:**
   ```bash
   ros2 pkg create --build-type ament_python maze_bot --dependencies rclpy geometry_msgs sensor_msgs cv_bridge
   ```

2. **Build your workspace:**
   ```bash
   colcon build
   source /workspace/install/setup.bash
   ```
   *(Colcon is pre-configured to output `build`, `install`, and `log` to `/workspace/` outside `src`, keeping your Git repository completely clean).*

3. **Verify Simulation & GUI tools:**
   ```bash
   gazebo
   # or
   rviz2
   ```

All source files in `/workspace/src` are synchronized with your host directory (`/home/rahulpai/maze_solver/src`), while build artifacts stay in the container's `/workspace` folder.
