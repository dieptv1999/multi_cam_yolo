import datetime
import json
from importlib import import_module
from flask import Flask, render_template, Response, request
import cv2
import time
from flask_cors import CORS

app = Flask(__name__)
app.debug = True
CORS(app)

data = {}
port_list = [5566, 5555, 5577]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data')
def data_count():
    def generate():
        yield json.dumps(data)

    return Response(generate(), mimetype='text')


@app.route('/add_camera')
def add_camera():
    path = request.args.get('path')
    port = request.args.get('port')

    port_list.append(port)

    from object_counting.camera_client import ClientCameraThread
    thread = ClientCameraThread(
        thread_name='camera'+str(port),
        thread_id='camera'+str(port),
        path=path,
        port=port
    )

    thread.start()

    def generate():
        yield "Success"

    return Response(generate(), mimetype='text')


def gen(camera_stream, feed_type, device):
    unique_name = (feed_type, device)

    num_frames = 0
    total_time = 0
    cam_id = -1
    frame = {}
    count = None
    while True:
        time_start = time.time()

        if feed_type == 'camera':
            cam_id, frame = camera_stream.get_frame(unique_name)
        else:
            cam_id, frame, count = camera_stream.get_frame(unique_name)
        if frame is None:
            break

        if count is not None:
            data['yolo' + device] = str(count)

        num_frames += 1

        time_now = time.time()
        total_time += time_now - time_start
        fps = num_frames / total_time

        # camera name
        cv2.putText(frame, cam_id, (int(20), int(20 * 5e-3 * frame.shape[0])), 0, 2e-3 * frame.shape[0],
                    (255, 255, 255), 2)

        if feed_type == 'yolo':
            cv2.putText(frame, "FPS: %.2f" % fps, (int(20), int(40 * 5e-3 * frame.shape[0])), 0, 2e-3 * frame.shape[0],
                        (255, 255, 255), 2)

        frame = cv2.imencode('.jpg', frame)[1].tobytes()  # Remove this line for test camera
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


camera_stream_yolo = import_module('camera_yolo').Camera


@app.route('/video_feed/<feed_type>/<device>')
def video_feed(feed_type, device):
    if feed_type == 'camera':
        camera_stream = import_module('camera_server').Camera
        return Response(
            gen(camera_stream=camera_stream(feed_type, device, port_list), feed_type=feed_type, device=device),
            mimetype='multipart/x-mixed-replace; boundary=frame')

    elif feed_type == 'yolo':
        return Response(
            gen(camera_stream=camera_stream_yolo(feed_type, device, port_list), feed_type=feed_type, device=device),
            mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
