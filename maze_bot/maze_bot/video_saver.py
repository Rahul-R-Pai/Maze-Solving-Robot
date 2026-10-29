import rclpy
import cv2
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import os

class Video(Node):
    def __init__(self):
        super().__init__('video_subscriber') # Node name

        # creating a subscriber
        self.subscriber = self.create_subscriber(Image, 'upper_camera/image_raw', self.process_data, 10)

        # settings for writing frames in video
        video_path = os.path.join(os.getcwd(), "output.avi")
        self.out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (1280, 720))
        self.bridge = CvBridge() #converting ros frames into opencv data

        def process_data(self, data):
            frame = self.bridge.imgmsg_to_cv2(data, 'bgr8')
            self.out.write(frame)
            cv2.imshow('output', frame)
            cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    image_subscriber = Video()
    rclpy.spin(image_subscriber)
    rclpy.shutdown()

if __name__ == '__main__':
    main()