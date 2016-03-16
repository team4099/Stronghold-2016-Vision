#!/usr/bin/env python3
#
# Project: Video Streaming with Flask
# Author: Log0 <im [dot] ckieric [at] gmail [dot] com>
# Date: 2014/12/21
# Website: http://www.chioka.in/
# Description:
# Modified to support streaming out with webcams, and not just raw JPEGs.
# Most of the code credits to Miguel Grinberg, except that I made a small tweak. Thanks!
# Credits: http://blog.miguelgrinberg.com/post/video-streaming-with-flask
#
# Usage:
# 1. Install Python dependencies: cv2, flask. (wish that pip install works like a charm)
# 2. Run "python main.py".
# 3. Navigate the browser to the local webpage.
from flask import Flask, render_template, Response
import vision_processing
import numpy
import freenect
import frame_convert
import cv2
import operator

app = Flask(__name__)
process_flag = False
process_frame = None
depth_frames = []

def get_frame():
    success, image = get_video()
    # We are using Motion JPEG, but OpenCV defaults to capture raw images,
    # so we must encode it into JPEG in order to correctly display the
    # video stream.
    ret, jpeg = cv2.imencode('.jpg', image)
    return jpeg.tobytes()

def combine_depth_frames(frame1, frame2):
    frame2[frame2 > 2046] = 0
    return numpy.bitwise_or(frame1, frame2)

def get_video():
    global process_flag, process_frame, depth_frame
    rgb_video = freenect.sync_get_video()
    # print(depth_feed)
    # depth_cv = frame_convert.pretty_depth_cv(depth_feed[0])
    # depth_frames.append(depth_feed)
    # depth_frames = depth_frames[:10]

    if process_flag:
        ir_feed = freenect.sync_get_video(0, format=freenect.VIDEO_IR_8BIT)
        ir_feed = ir_feed[1], ir_feed[0]
        # depth_feed = freenect.sync_get_depth()
#        ir_feed = freenect.sync_get_video(0, format=freenect.VIDEO_IR_8BIT)
        # cv2.imwrite("temp_video.png", ir_feed[1])
        depth_accumulator = freenect.sync_get_depth()[0]
        depth_accumulator[depth_accumulator > 2046] = 0
        for i in range(10):
            # print(depth_accumulator)
            depth_accumulator = combine_depth_frames(depth_accumulator, freenect.sync_get_depth()[0])
        depth_accumulator[depth_accumulator > 0] = 2047
        # print(type(depth_accumulator))
        ir_feed = map(lambda row: map(operator.mul, row), ir_feed)
        ir_feed = numpy.bitwise_and(depth_accumulator, numpy.array(ir_feed[1]))
        cv2.imwrite("thing.png", frame_convert.pretty_depth_cv(ir_feed))
        process_frame = frame_convert.pretty_depth_cv(ir_feed)
        process_flag = False

    rgb_video = rgb_video[1], frame_convert.video_cv(rgb_video[0])
    #return ir_feed[1], ir_feed[0]
    #return 0, frame_convert.pretty_depth_cv(depth_feed[0])
    return rgb_video

def gen(write_flag=False):
    while True:
        frame = get_frame()
        if write_flag:
            cv2.imwrite("to_process.png", frame)

        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_angle')
def get_angle():
    """
        Calculates the lateral and vertical angles the bot needs to move by in order
        to point the distance sensor directly at the goal

        :return: -1 if goal not found or the lateral and vertical offset in the
                following format:

            Lateral Angle, Vertical Angle

    """
    global process_flag, process_frame
    process_flag = True
    while process_flag:
        pass
    try:
        print(process_frame)
        angles = vision_processing.get_kinect_angles(process_frame)
        print(angles)
        return ",".join(str(i) for i in angles)
    except vision_processing.GoalNotFoundException:
        print("No goal found")
        return "-1", 503
    except FileNotFoundError:
        print("No file found")
        return "-1", 503

@app.route("/get_trajectory")
def get_trajectory():
    """
        Calculates the vertical angle the boot needs to set the shooter in order to
        land a shot inside the goal

        :return: Vertical angle
    """
    #: Pseudocode
    # Retrieve distance from distance sensor (maybe depth imaging from kinect?)
    # Is velocity constant?
    pass

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True, port=80, threaded=True)
