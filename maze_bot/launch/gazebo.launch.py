import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node


def generate_launch_description():
    package_share_dir = get_package_share_directory("maze_bot")
    urdf_file = os.path.join(package_share_dir, "urdf", "maze_bot.urdf")
    world_file = os.path.join(package_share_dir, "worlds", "empty.world")

    with open(urdf_file, "r") as infp:
        robot_description_content = infp.read()

    pkg_parent_dir = os.path.dirname(package_share_dir)
    default_model_paths = [
        pkg_parent_dir,
        os.path.join(package_share_dir, "models"),
        "/usr/share/gazebo-11/models",
        os.path.expanduser("~/.gazebo/models"),
    ]
    existing_model_path = os.environ.get("GAZEBO_MODEL_PATH", "")
    if existing_model_path:
        default_model_paths.append(existing_model_path)
    gazebo_model_path = ":".join([p for p in default_model_paths if p])

    return LaunchDescription(
        [
            # Prevent Gazebo from hanging on startup trying to connect to dead models.gazebosim.org
            SetEnvironmentVariable(name="GAZEBO_MODEL_DATABASE_URI", value=""),
            SetEnvironmentVariable(name="GAZEBO_MODEL_PATH", value=gazebo_model_path),

            ExecuteProcess(
                cmd=["gazebo", "--verbose", world_file, "-s", "libgazebo_ros_factory.so"],
                output="screen",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                output="screen",
                parameters=[{
                    "robot_description": robot_description_content,
                    "use_sim_time": True,
                }],
            ),
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=["-entity", "maze_bot", "-topic", "robot_description", "-z", "0.01"],
                output="screen",
            ),
        ]
    )
