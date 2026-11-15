#include "robot_teleop/joystick_controller.hpp"

namespace robot_teleop {

namespace {

[[nodiscard]] double getAxisValue(const JoyMsg &joy, std::size_t index) {
  return joy.axes[index];
}

} // namespace

JoystickController::JoystickController() : Node{"joystick_controller"} {
  m_maxLinearVelocity =
      declare_parameter("max_linear_velocity", m_maxLinearVelocity);
  m_maxAngularVelocity =
      declare_parameter("max_angular_velocity", m_maxAngularVelocity);

  // QoS explícito: confiable y sin acumular comandos viejos.
  rclcpp::QoS cmdVelQos{rclcpp::KeepLast(CmdVelQueueDepth)};
  cmdVelQos.reliable();
  m_cmdVelPublisher = create_publisher<TwistStampedMsg>(
      "/diff_drive_controller/cmd_vel", cmdVelQos);

  m_joySubscription = create_subscription<JoyMsg>(
      "/joy", rclcpp::QoS{rclcpp::KeepLast(JoyQueueDepth)},
      [this](const JoyMsg &joy) { onJoy(joy); });

  RCLCPP_INFO(get_logger(), "Joystick controller initialized!");
}

void JoystickController::onJoy(const JoyMsg &joy) {
  // No se lanza una excepción desde un callback de ROS: se advierte y se
  // descarta.
  if (joy.axes.size() < MinimumAxisCount) {
    RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000,
                         "Joy message has %zu axes, at least %zu required.",
                         joy.axes.size(), MinimumAxisCount);
    return;
  }

  const double linearInput{
      getAxisValue(joy, static_cast<std::size_t>(Axis::LeftStickY))};
  const double angularInput{
      getAxisValue(joy, static_cast<std::size_t>(Axis::LeftStickX))};

  TwistStampedMsg cmd{};
  cmd.header.stamp = now();
  cmd.header.frame_id = "base_link";
  cmd.twist.linear.x = linearInput * m_maxLinearVelocity;
  cmd.twist.angular.z = angularInput * m_maxAngularVelocity;

  m_cmdVelPublisher->publish(cmd);
}

} // namespace robot_teleop
