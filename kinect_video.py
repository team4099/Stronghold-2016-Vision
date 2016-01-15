#!/usr/bin/env python
import freenect
import cv2
import frame_convert
import time
import vision_processing
import numpy

lookup_table_depth = []


# cv.NamedWindow('Depth')
cv2.namedWindow('Video')
cv2.namedWindow('Thresholded')

print('Press ESC in window to stop')


def depth_in_meters_at_pixel(x, y, depth_data):
    if depth_data:
        pixel_to_look_at = depth_data[x][y]
        return lookup_table_depth[int(pixel_to_look_at)]
    else:
        return


def get_depth():
    depth_data = freenect.sync_get_depth()[0]
    print(depth_in_meters_at_pixel(320, 240, depth_data))
    print(lookup_table_depth[int(pixel_to_look_at)])
    return frame_convert.pretty_depth_cv(depth_data)


def get_video():
    video_data = freenect.sync_get_video()
    return video_data[1], frame_convert.video_cv(video_data[0])


def generate_lookup_table():
    for i in range(2048):
        lookup_table_depth.append(1/(i * -0.0030711016 + 3.3309495161))


generate_lookup_table()

while 1:
    # cv.ShowImage('Depth', get_depth())
    ret, video_frame = get_video()
    # print type(video_frame)
    video_frame = numpy.asarray(video_frame[:,:]) # access as mat
    # print video_frame.shape
    if video_frame.size <= 10:
        continue
    # print type(video_frame)
    thresholded_image = vision_processing.threshold_image_for_tape(video_frame)
    cv2.imshow('Video', video_frame)
    cv2.imshow('Thresholded', thresholded_image)
    save = raw_input("Save?")
    if save.upper() == "EXIT":
        break;
    if "V" in save.upper():
        cv2.imwrite("img/video_" + str(int(time.time()/100)) + ".png",
                    video_frame)
    if "T" in save.upper():
        cv2.imwrite("img/thresholded_" + str(int(time.time()/100)) + ".png",
                    thresholded_image)
