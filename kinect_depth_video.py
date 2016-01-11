#!/usr/bin/env python
import freenect
import cv
import frame_convert

lookup_table_depth = []


cv.NamedWindow('Depth')
cv.NamedWindow('Video')
print('Press ESC in window to stop')


def get_depth():
    depth_data = freenect.sync_get_depth()[0]
    pixel_to_look_at = depth_data[320][240]
    print(pixel_to_look_at)
    print lookup_table_depth[int(pixel_to_look_at)]
    return frame_convert.pretty_depth_cv(depth_data)


def get_video():
    return frame_convert.video_cv(freenect.sync_get_video()[0])


def generate_lookup_table():
    for i in range(2048):
        lookup_table_depth.append(1/(i * -0.0030711016 + 3.3309495161))

generate_lookup_table()

while 1:
    cv.ShowImage('Depth', get_depth())

    cv.ShowImage('Video', get_video())
    if cv.WaitKey(10) == 27:
        break
