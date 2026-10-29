FROM osrf/ros:humble-desktop

# Avoid interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

# Configure NVIDIA container runtime environment variables
ENV NVIDIA_VISIBLE_DEVICES=${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES=${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics,compute,utility,display

# Install Gazebo Classic 11 and essential ROS 2 / CV dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Gazebo simulation & plugins
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros \
    ros-humble-gazebo-plugins \
    # Robot modeling & visualization
    ros-humble-xacro \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-robot-state-publisher \
    # Computer Vision & ROS Messages
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-geometry-msgs \
    ros-humble-sensor-msgs \
    ros-humble-nav-msgs \
    # Teleop & navigation helpers
    ros-humble-teleop-twist-keyboard \
    # Build tools & system utilities
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    python3-opencv \
    mesa-utils \
    libgl1-mesa-dri \
    libgl1-mesa-glx \
    x11-apps \
    sudo \
    git \
    nano \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements for maze solving, path planning & computer vision
# Pin numpy==1.26.4 to maintain ABI compatibility with ros-humble-cv-bridge & OpenCV
RUN pip3 install --no-cache-dir --upgrade \
    "numpy==1.26.4" \
    "opencv-contrib-python<4.9" \
    pygame \
    transforms3d \
    scipy \
    matplotlib

# Create a non-root user matching the host UID/GID (default 1000)
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Copy and set permissions for entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create workspace directory structure
RUN mkdir -p /workspace/src && chown -R $USERNAME:$USERNAME /workspace

# Configure colcon to place build, install, and log in /workspace (outside /workspace/src)
RUN mkdir -p /home/$USERNAME/.colcon && \
    printf '"":\n  log-base: /workspace/log\nbuild:\n  build-base: /workspace/build\n  install-base: /workspace/install\n  symlink-install: true\n' > /home/$USERNAME/.colcon/defaults.yaml && \
    chown -R $USERNAME:$USERNAME /home/$USERNAME/.colcon

# Configure Gazebo Classic to prevent hanging on startup when querying offline model database
RUN mkdir -p /home/$USERNAME/.gazebo/config && \
    printf '<?xml version="1.0" ?>\n<gazebo_config>\n  <uri></uri>\n</gazebo_config>\n' > /home/$USERNAME/.gazebo/config/default.xml && \
    chown -R $USERNAME:$USERNAME /home/$USERNAME/.gazebo

# Setup environment in user's bashrc
USER $USERNAME
WORKDIR /workspace/src
ENV DISPLAY=:0

# Source ROS2 and any local workspace overlay in bashrc automatically
RUN echo 'export DISPLAY="${DISPLAY:-:0}"' >> ~/.bashrc \
    && echo 'export __NV_PRIME_RENDER_OFFLOAD=1' >> ~/.bashrc \
    && echo 'export __GLX_VENDOR_LIBRARY_NAME=nvidia' >> ~/.bashrc \
    && echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc \
    && echo 'if [ -f /workspace/install/setup.bash ]; then source /workspace/install/setup.bash; fi' >> ~/.bashrc \
    && echo 'if [ -f /workspace/*/install/setup.bash ]; then for f in /workspace/*/install/setup.bash; do source "$f"; break; done; fi' >> ~/.bashrc

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
