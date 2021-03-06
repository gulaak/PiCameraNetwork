import time
import io
import threading
import picamera
import requests

#Modification of Miguel Grinberg piCamera libray

class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    timerAccess = 0
    frames = None
    res = None
    brightness = None
    timeOut = True
	
    def __init__(self,framerate=24,resolution=(320,240),brightness=50):
        Camera.frames = framerate
        Camera.res = resolution
        Camera.brightness = brightness

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread,args=(Camera.frames,Camera.res,Camera.brightness))
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(cls,fps,res,bright):
        urlGet = "http://134.88.49.135:5000/checkStatus"
        urlPost = "http://134.88.49.135:5000/changeStatus"
        with picamera.PiCamera() as camera:
            # camera setup
			
            camera.resolution = res
            camera.framerate = fps
            camera.brightness = bright
            camera.hflip = True
            camera.vflip = True

            # let camera warm up
            camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame
                stream.seek(0)
                cls.frame = stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
                if(time.time() - cls.timerAccess >= 4):
                    timeOut = True

                if(timeOut == True):
                    cls.timerAccess = time.time()
                    timeOut = False
                    r = requests.get(urlGet)
                    response = r.json()
                    if response['status']== True:
                        try:
                                camera.framerate = int(response['fps'])
                                camera.resolution = tuple(response['resolution'])
                                camera.brightness = int(response['brightness'])
                                r = requests.post(urlPost)
                        except picamera.exc.PiCameraMMALError:
                                continue 

                #if there hasn't been any clients asking for frames in
                #the last 10 seconds stop the thread
                if time.time() - cls.last_access > 10:
                    break
        cls.thread = None