import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    # Package containing the robot description
    package_name = "description_files"

    # Robot State Publisher
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory(package_name), "launch", "rsp.launch.py"
            )
        ),
        launch_arguments={"use_sim_time": "true"}.items(),
    )

    # Gazebo Harmonic
    gazebo_share = get_package_share_directory("ros_gz_sim")

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_share, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": "-r empty.sdf"}.items(),
    )

    # Spawn robot in Gazebo
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_share, "launch", "gz_spawn_model.launch.py")
        ),
        launch_arguments={
            "world": "empty",
            "topic": "/robot_description",
            "entity_name": "my_bot",
            "z": "0.5",
        }.items(),
    )

    # Give Gazebo some time to start before spawning
    delayed_spawn = TimerAction(
        period=5.0,
        actions=[spawn_robot],
    )

    # Bridge ROS 2 cmd_vel -> Gazebo Harmonic
    cmd_vel_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            # ROS 2 -> Gazebo
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            # Gazebo -> ROS 2
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            # Gazebo -> ROS 2
            "/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model",
            "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
        ],
        output="screen",
    )

    # Launch everything
    return LaunchDescription(
        [
            rsp,
            gazebo,
            delayed_spawn,
            cmd_vel_bridge,
        ]
    )
