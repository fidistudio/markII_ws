import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node


def generate_launch_description():

    # Package containing the robot description
    package_name = "description_files"

    package_share = get_package_share_directory(package_name)

    # Robot State Publisher
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(package_share, "launch", "rsp.launch.py")
        ),
        launch_arguments={"use_sim_time": "true"}.items(),
    )

    # Warehouse world file
    world_file = os.path.join(package_share, "worlds", "warehouse_world.sdf")

    # Gazebo Harmonic
    gazebo_share = get_package_share_directory("ros_gz_sim")

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_share, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": f"-r {world_file}"}.items(),
    )

    # Spawn robot in Gazebo
    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_share, "launch", "gz_spawn_model.launch.py")
        ),
        launch_arguments={
            "world": "warehouse_world",
            "topic": "/robot_description",
            "entity_name": "my_bot",
            "z": "0.5",
        }.items(),
    )

    # Give Gazebo time to start before spawning
    delayed_spawn = TimerAction(
        period=5.0,
        actions=[spawn_robot],
    )

    # Gazebo -> ROS 2 Bridges
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            # Gazebo -> ROS 2 (Simulation clock)
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            # Gazebo -> ROS 2 (LiDAR)
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
        ],
        output="screen",
    )

    # Spawn Joint State Broadcaster
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
    )

    # Spawn Differential Drive Controller
    diff_drive_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
    )

    # Start controllers after robot spawning
    delayed_joint_state_broadcaster = TimerAction(
        period=8.0,
        actions=[
            joint_state_broadcaster,
        ],
    )

    delayed_diff_drive_controller = TimerAction(
        period=10.0,
        actions=[
            diff_drive_controller,
        ],
    )

    # Launch everything
    return LaunchDescription(
        [
            rsp,
            gazebo,
            bridge,
            delayed_spawn,
            delayed_joint_state_broadcaster,
            delayed_diff_drive_controller,
        ]
    )
