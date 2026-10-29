import rclpy
import cv2
import numpy as np
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import os
from .bot_localization import bot_localizer

class Video(Node):
    def __init__(self):
        super().__init__('video_subscriber') # Node name

        # creating a subscriber
        self.subscriber = self.create_subscription(Image, 'upper_camera/image_raw', self.get_video_feed, 10)

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        time_period = 0.5
        self.timer = self.create_timer(time_period, self.maze_solving)
        self.sat_view = np.zeros((100, 100))
        self.vel_msg = Twist()

        self.bot_localizer = bot_localizer()

        # settings for writing frames in video
        self.bridge = CvBridge() #converting ros frames into opencv data

    def get_video_feed(self, data):
        frame = self.bridge.imgmsg_to_cv2(data, 'bgr8')
        self.sat_view = frame
        cv2.imshow('output', self.sat_view)
        cv2.waitKey(1)

    def maze_solving(self):
        frame_display = self.sat_view.copy()
        self.bot_localizer.localize_bot(self.sat_view, frame_display)
        self.vel_msg.linear.x = 0.0
        self.vel_msg.angular.z = 0.0

        self.publisher.publish(self.vel_msg)

def main(args=None):
    rclpy.init(args=args)
    image_subscriber = Video()
    rclpy.spin(image_subscriber)
    rclpy.shutdown()

if __name__ == '__main__':
    main()