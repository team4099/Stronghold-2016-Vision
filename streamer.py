#!/usr/bin/env python
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

app = Flask(__name__)
process_flag = False

def get_frame():
    success, image = get_video()
    # We are using Motion JPEG, but OpenCV defaults to capture raw images,
    # so we must encode it into JPEG in order to correctly display the
    # video stream.
    ret, jpeg = cv2.imencode('.jpg', image)
    return jpeg.tobytes()

def get_video():
    global process_flag
#    rgb_video = freenect.sync_get_video()
    ir_feed = freenect.sync_get_video(0, format=freenect.VIDEO_IR_8BIT)

    if process_flag:
#        ir_feed = freenect.sync_get_video(0, format=freenect.VIDEO_IR_8BIT)
        cv2.imwrite("temp_video.png", ir_feed[1])
        process_flag = False

    rgb_video = ir_feed[1], ir_feed[0]
    return rgb_video

def gen(write_flag=False):
    frame = get_frame()
    if write_flag:
        cv2.imwrite("to_process.png", frame)
        
    return (b'--frame\r\n'
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
    global process_flag
    process_flag = True
    while process_flag:
        pass
    try:
        angles = vision_processing.get_kinect_angles(cv2.imread("temp_video.png"))
        print(angles)
        return ",".join(str(i) for i in angles)
    except vision_processing.GoalNotFoundException:
        return "-1", 503
    except FileNotFoundError:
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
    app.run("0.0.0.0", debug=True, port=80)
