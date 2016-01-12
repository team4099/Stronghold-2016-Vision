#!/usr/bin/python
'''
    Author: Igor Maculan - n3wtron@gmail.com
    Added to by FRC Team 4099 for Kinect image streaming
    A Simple mjpg stream http server
'''
import cv2
import Image
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import StringIO
import time
import freenect

capture = None


class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; \
                boundary=--jpgboundary')
            self.end_headers()
            while True:
                try:
                    img, rc = freenect.sync_get_video()
                    if not rc:
                        continue
                    # imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    jpg = Image.fromarray(img)
                    tmpFile = StringIO.StringIO()
                    jpg.save(tmpFile, 'JPEG')
                    self.wfile.write("--jpgboundary")
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(tmpFile.len))
                    self.end_headers()
                    jpg.save(self.wfile, 'JPEG')
                    time.sleep(0.05)
                except KeyboardInterrupt:
                    break
            return
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>')
            self.wfile.write('<img src="/cam.mjpg"/>')
            self.wfile.write('</body></html>')
            return


def main():
    global img
    try:
        server = HTTPServer(('', 8080), CamHandler)
        print "server started"
        server.serve_forever()
    except KeyboardInterrupt:
        capture.release()
        server.socket.close()

if __name__ == '__main__':
    main()
