from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    # Obtener las rutas de instalación de los paquetes
    description_share = get_package_share_directory("description_files")

    # Launch de Gazebo y spawn del robot
    simulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(description_share, "launch", "launch_sim.launch.py")
        )
    )

    # RViz
    rviz_config = os.path.join(description_share, "config", "view_bot.rviz")

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    # Driver del joystick
    joy_node = Node(
        package="joy",
        executable="joy_node",
        name="joy_node",
        parameters=[{"autorepeat_rate": 20.0, "deadzone": 0.05}],
        output="screen",
    )

    # Nodo propio de teleoperación
    joystick_controller = Node(
        package="robot_teleop",
        executable="joystick_controller",
        name="joystick_controller",
        output="screen",
    )

    return LaunchDescription(
        [simulation_launch, rviz_node, joy_node, joystick_controller]
    )
