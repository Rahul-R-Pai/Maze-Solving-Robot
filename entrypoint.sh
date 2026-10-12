#!/usr/bin/env bash
set -e

# Ensure DISPLAY is set for GUI / RViz / Gazebo
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
fi

# Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# Source local ROS workspace if built
if [ -f /workspace/install/setup.bash ]; then
    source /workspace/install/setup.bash
elif [ -d /workspace ]; then
    for ws_setup in /workspace/*/install/setup.bash; do
        if [ -f "$ws_setup" ]; then
            source "$ws_setup"
            break
        fi
    done
fi

exec "$@"
