import threading

import imagezmq
from imutils.video import VideoStream


class ClientCameraThread(threading.Thread):
    def __init__(self, thread_name, thread_id, path, port):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_id
        self.path = path
        self.port

        # helper function to execute the threads

    def run(self):
        cap = VideoStream(self.path)

        sender = imagezmq.ImageSender(
            connect_to='tcp://localhost:' + str(self.port))  # change to IP address and port of server thread
        cam_id = 'Camera 1'  # this name will be displayed on the corresponding camera stream

        stream = cap.start()

        while True:
            frame = stream.read()
            sender.send_image(cam_id, frame)