import threading
import time

import cv2
import errno
import imagezmq
import os
import socket
import argparse


def create_streamer(file, connect_to='tcp://127.0.0.1:5555', loop=True):
    print(connect_to)
    """
    You can use this function to emulate an IP camera for the counting apps.

    Parameters
    ----------
    file : str
        Path to the video file you want to stream.
    connect_to : str, optional
        Where the video shall be streamed to.
        The default is 'tcp://127.0.0.1:5555'.
    loop : bool, optional
        Whether the video shall be looped. The default is True.

    Returns
    -------
    None.

    """

    # check if file exists and open capture
    if os.path.isfile(file):
        cap = cv2.VideoCapture(file)
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)

    # prepare streaming
    sender = imagezmq.ImageSender(connect_to=connect_to)
    host_name = socket.gethostname()

    while True:
        ret, frame = cap.read()
        time.sleep(0.025)
        if ret:
            # if a frame was returned, send it
            sender.send_image(host_name, frame)
        else:
            # if no frame was returned, either restart or stop the stream
            if loop:
                cap = cv2.VideoCapture(file)
            else:
                break


ap = argparse.ArgumentParser()
ap.add_argument("-p", "--port", help="path to input port", required=True, action='append')
ap.add_argument("-v", "--video", help="path to input video", required=True, action='append')
args = vars(ap.parse_args())

if __name__ == '__main__':
    try:
        for i in range(len(args['port'])):
            t1 = threading.Thread(target=create_streamer, args=(args['video'][i], 'tcp://127.0.0.1:' + args['port'][i]))
            t1.start()
            # streamer = create_streamer('camera.mp4', 'tcp://127.0.0.1:' + i)
    except:
        print("error")
