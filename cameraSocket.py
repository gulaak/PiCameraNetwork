import time
import io
import threading
import picamera
import struct
import socket
import requests
import cv2
#Courtesy of Miguel Grinberg

class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    frames = None
    res = None
    brightness = None
    client_socket = None
    connection = None
    def __init__(self,addr,port):
        Camera.client_socket = socket.socket()
        Camera.client_socket.connect((addr,port))
        Camera.connection = Camera.client_socket.makefile('wb')
        Camera.port = port
        

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    def closeConnection(self):
        Camera.client_socket.close()
        Camera.connection.close()

    @classmethod
    def _thread(cls):
        urlGet = "http://134.88.49.135:5000/checkStatus"
        urlPost = "http://134.88.49.135:5000/changeStatus"
        if Camera.port == 10000:
            selectorTarget = 1
        else:
            selectorTarget = 2
        with picamera.PiCamera() as camera:
            # camera setup
            global framerate
            camera.resolution = (320,240)
            camera.hflip = True
            camera.vflip = True

            # let camera warm up
            camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # r = requests.get(urlGet)
                # response = r.json()
                # if response['status']== True:
                #     try:
                #             camera.framerate = int(response['fps'])
                #             camera.resolution = tuple(response['resolution'])
                #             camera.brightness = int(response['brightness'])
                #             r = requests.post(urlPost)
                #     except picamera.exc.PiCameraMMALError:
                #             continue
                # print(int(str(response['selector'])))
                # if int(str(response['selector'])) == selectorTarget: 
                Camera.connection.write(struct.pack('<L',stream.tell()))
                Camera.connection.flush()
                # store frame
                stream.seek(0)
                cls.frame = stream.read()
                Camera.connection.write(cls.frame)

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()




                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 10:
                    break
            cls.thread = None