#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "robot_teleop/joystick_controller.hpp"

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<robot_teleop::JoystickController>());
  rclcpp::shutdown();
  return 0;
}
