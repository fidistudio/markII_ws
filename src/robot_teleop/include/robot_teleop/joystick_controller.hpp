#pragma once

#include <cstddef>

#include "geometry_msgs/msg/twist_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joy.hpp"

namespace robot_teleop {

using JoyMsg = sensor_msgs::msg::Joy;
using TwistStampedMsg = geometry_msgs::msg::TwistStamped;

/**
 * Traduce los ejes del joystick (/joy) a comandos de velocidad
 * (TwistStamped) para el diff_drive_controller.
 *
 * Parámetros ROS 2:
 *  - max_linear_velocity  (double, m/s,   default 0.5)
 *  - max_angular_velocity (double, rad/s, default 1.5)
 */
class JoystickController final : public rclcpp::Node {
public:
  JoystickController();

private:
  enum class Axis : std::size_t { LeftStickX = 0, LeftStickY = 1 };

  // Cantidad mínima de ejes que debe tener un mensaje Joy válido.
  static constexpr std::size_t MinimumAxisCount{2};

  // Profundidad de cola: solo importa el comando más reciente.
  static constexpr std::size_t CmdVelQueueDepth{1};
  static constexpr std::size_t JoyQueueDepth{10};

  void onJoy(const JoyMsg &joy);

  rclcpp::Publisher<TwistStampedMsg>::SharedPtr m_cmdVelPublisher;
  rclcpp::Subscription<JoyMsg>::SharedPtr m_joySubscription;

  double m_maxLinearVelocity{0.5};  // m/s
  double m_maxAngularVelocity{1.5}; // rad/s
};

} // namespace robot_teleop
