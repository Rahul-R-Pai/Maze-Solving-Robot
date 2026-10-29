import rclpy
import cv2
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import os

class Video(Node):
    def __init__(self):
        super().__init__('video_subscriber') # Node name

        # creating a subscriber
        self.subscriber = self.create_subscriber(Image, 'upper_camera/image_raw', self.get_video_feed, 10)

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        time_period = 0.5
        self.timer = self.create_timer(time_period, self.maze_solving)

        # settings for writing frames in video
        self.bridge = CvBridge() #converting ros frames into opencv data

        def get_video_feed(self, data):
            frame = self.bridge.imgmsg_to_cv2(data, 'bgr8')
            cv2.imshow('output', frame)
            cv2.waitKey(1)

        def maze_solving(self):
            msg = Twist()
            
            self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    image_subscriber = Video()
    rclpy.spin(image_subscriber)
    rclpy.shutdown()

if __name__ == '__main__':
    main()