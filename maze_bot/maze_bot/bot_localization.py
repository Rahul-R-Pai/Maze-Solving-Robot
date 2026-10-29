import os

import cv2
import numpy as np

from .utilities import ret_smallest_obj, ret_largest_obj


class bot_localizer():
    def __init__(self):
        self.is_bg_extracted = False
        self.bg_model = []
        self.maze_og = []

        #transformation crop + rotation parameters
        self.orig_X = 0
        self.orig_Y = 0
        self.orig_rows = 0
        self.orig_cols = 0
        self.transform_array = []
        self.orig_rot = 0
        self.rot_matrix = 0
        self.rot_matrix_rev = 0
        self.loc_car = 0

    def ret_roi_boundinghull(self, roi_mask, contours):
        maze_enclosure = np.zeros_like(roi_mask)
        if contours:
            contours_ = np.concatenate(contours)
            contours_ = np.array(contours_)
            cv2.fillConvexPoly(maze_enclosure, contours_, 255)
        contours_largest = cv2.findContours(maze_enclosure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
        hull = cv2.convexHull(contours_largest[0])
        cv2.drawContours(maze_enclosure, [hull], 0, 255)

        return hull

    def update_frameofrefrence_parameters(self,X,Y,W,H,rot_angle):
        self.orig_X = X; self.orig_Y = Y; self.orig_rows = H; self.orig_cols = W; self.orig_rot = rot_angle # 90 degree counterClockwise
        self.transform_array = [X,Y,W,H]
        # Rotation Matrix
        self.rot_matrix = np.array(
                                [
                                 [ np.cos(np.deg2rad(self.orig_rot)) , np.sin(np.deg2rad(self.orig_rot))],
                                 [-np.sin(np.deg2rad(self.orig_rot)) , np.cos(np.deg2rad(self.orig_rot))]
                                ]
                               )
        self.rot_matrix_rev = np.array(
                                [
                                 [ np.cos(np.deg2rad(-self.orig_rot)) , np.sin(np.deg2rad(-self.orig_rot))],
                                 [-np.sin(np.deg2rad(-self.orig_rot)) , np.cos(np.deg2rad(-self.orig_rot))]
                                ]
                               )

    def get_centroid(contour):
        M = cv2.moments(contour)
        cx= int(M['m10']/M['m00'])
        cy= int(M['m01']/M['m00'])
        return (cy, cx)

    def get_car_loc(self, car_contour, car_mask):
        bot_center = self.get_centroid(car_contour)
        # converting point tuple to array and changes coordi x and y for image (y,x) -> (x,y)
        bot_center_array = np.array(bot_center[1], bot_center[0])
        bot_center_translated = np.zeros_like(bot_center_array)
        bot_center_translated[0] = bot_center_array[0] - self.orig_X
        bot_center_translated[1] = bot_center_array[1] - self.orig_Y

        bot_on_maze = (self.rot_matrix @ bot_center_translated.T).T

        #translating origin if necessary
        rot_columns = self.orig_rows
        rot_rows = self.orig_cols
        bot_on_maze[0] += (rot_columns * (bot_on_maze[0]<0))
        bot_on_maze[1] += (rot_rows * (bot_on_maze[1]<0))

        #updating placeholder for relative loc of car
        self.loc_car = (int(bot_on_maze[0]), int(bot_on_maze[1]))

    def extract_bg(self, frame):
        #Extract a mask of all rois
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_frame, 50, 150, None, 3)
        contours = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]

        # Masks must be single-channel arrays matching the frame height/width
        roi_mask = np.zeros(frame.shape[:2], dtype=np.uint8)

        for i,_ in enumerate(contours):
            cv2.drawContours(roi_mask, contours, i, 255, -1) # -1 added to fill the contour

        #Now to remove car from ROI, assuming that it is the smallest object in the frame
        min_contour_index = ret_smallest_obj(contours)
        roi_no_car_mask = roi_mask.copy()
        if min_contour_index != -1:
            cv2.drawContours(roi_no_car_mask, contours, min_contour_index, 0, -1) # 0 is put in color to remove it

            #Creating a mask of the car
            car_mask = np.zeros_like(roi_mask)
            cv2.drawContours(car_mask, contours, min_contour_index, 255, -1)
            cv2.drawContours(car_mask, contours, min_contour_index, 255, 3) # Used to dilate the image with that much thickness
            not_car_mask = cv2.bitwise_not(car_mask)

            frame_car_removed = cv2.bitwise_and(frame, frame, mask= not_car_mask)

            #Replacing the removed part of the frame with the ground color
            base_color = frame[0][0]
            ground_replica = np.ones_like(frame)*base_color

            #Generating backgound model
            self.bg_model = cv2.bitwise_and(ground_replica, ground_replica, mask= car_mask)
            self.bg_model = cv2.bitwise_or(self.bg_model, frame_car_removed)

            # finding dimension of hull enclosing largest contour
            hull = self.ret_roi_boundinghull(roi_mask, contours)
            [x, y, w, h] = cv2.boundingRect(hull)

            #cropping maze_mask from image
            maze = roi_no_car_mask[y:y+h, x:x+w]

            #finding the area bot can traverse
            maze_occupancygrid = cv2.bitwise_not(maze)

            #to make entry point of maze on top, we rotate the grid
            self.maze_og = cv2.rotate(maze_occupancygrid, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # Storing Crop and Rot Parameters required to maintain frame of refrence in the orig image
            self.update_frameofrefrence_parameters(x, y, w, h, 90)

            cv2.imshow('1a. rois_mask',roi_mask)
            cv2.imshow('1b. frame_car_remvd',frame_car_removed)
            cv2.imshow('1c. Ground_replica',ground_replica)
            cv2.imshow('1d. bg_model',self.bg_model)
            cv2.imshow('2. maze_og',self.maze_og)
            cv2.waitKey(0)
            cv2.destroyAllWindows() 

    def localize_bot(self, current_frame, frame_to_disp):
        if not self.is_bg_extracted:
            self.extract_bg(current_frame)
            self.is_bg_extracted = True

        # Foreground extraction
        change = cv2.absdiff(current_frame, self.bg_model)
        change_gray = cv2.cvtColor(change, cv2.COLOR_BGR2GRAY)
        change_mask = cv2.threshold(change_gray, 15, 255, cv2.THRESH_BINARY)[1]

        #removing the noise by considering only the largest object
        car_mask, car_contour = ret_largest_obj(change_mask)

        self.get_car_loc(car_contour, car_mask)

         # Drawing bounding circle around detected car
        center, radii = cv2.minEnclosingCircle(car_contour)
        car_circular_mask = cv2.circle(car_mask.copy(), (int(center[0]), int(center[1])), int(radii+(radii*0.4)), 255, 3)
        car_circular_mask = cv2.bitwise_xor(car_circular_mask, car_mask)
        frame_to_disp[car_mask>0]  = frame_to_disp[car_mask>0] + (0,64,0)
        frame_to_disp[car_circular_mask>0]  = (0,0,255)

        # Displaying Extracted Car_mask and Localized car in frame
        cv2.imshow("change_mask(Noise Visible)", change_mask) 
        cv2.imshow("Detected_foreground(car)", car_mask) 
        cv2.imshow("car_localized", frame_to_disp)