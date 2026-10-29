import rclpy
from rclpy.node import Node
import numpy as np
import sys
import math

from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry


class RobotGoToGoal(Node):

    def __init__(self):
        super().__init__('robot_go_to_goal')
        self.vel_publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.pose_subscription = self.create_subscription(Odometry, '/odom', self.pose_callback, 10)
        timer_period = 0.2  # seconds
        self.timer = self.create_timer(timer_period, self.go_to_goal)
        self.robot_pose = Point()
        self.goal_pose = Point()
        self.vel_msg = Twist()
        self.distance_to_goal = 0
        self.angle_to_goal = 0

    def pose_callback(self, msg):
        self.robot_pose.x = msg.pose.pose.position.x
        self.robot_pose.y = msg.pose.pose.position.y
        quaternion = msg.pose.pose.orientation
        _, _, self.robot_pose.z = self.euler_from_quaternion(quaternion)
        


    def go_to_goal(self):
        self.goal_pose.x = float(sys.argv[1])
        self.goal_pose.y = float(sys.argv[2])

        self.distance_to_goal = math.sqrt(pow(self.goal_pose.x - self.robot_pose.x, 2) + pow(self.goal_pose.y - self.robot_pose.y, 2))
        self.angle_to_goal = math.atan2((self.goal_pose.y - self.robot_pose.y), (self.goal_pose.x - self.robot_pose.x))

        angle_to_turn = self.angle_to_goal - self.robot_pose.z
        if angle_to_turn > 0.1:
            self.vel_msg.angular.z = angle_to_turn
            self.vel_msg.linear.x = 0.0
        else:
            self.vel_msg.linear.x = self.distance_to_goal

        msg = f"Distance to goal: {self.distance_to_goal}, Angle to turn: {angle_to_turn}"
        self.get_logger().info(msg)

        self.vel_publisher_.publish(self.vel_msg)

    def euler_from_quaternion(self, quaternion):
        """
        Converts quaternion (w in last place) to euler roll, pitch, yaw
        quaternion = [x, y, z, w]
        Bellow should be replaced when porting for ROS 2 Python tf_conversions is done.
        """
        x = quaternion.x
        y = quaternion.y
        z = quaternion.z
        w = quaternion.w

        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        pitch = np.arcsin(sinp)

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw


def main(args=None):
    rclpy.init(args=args)

    robot_go_to_goal = RobotGoToGoal()

    rclpy.spin(robot_go_to_goal)

    robot_go_to_goal.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()