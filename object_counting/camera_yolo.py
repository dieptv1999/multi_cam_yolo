from __future__ import division, print_function, absolute_import

import cv2
from base_camera import BaseCamera

import warnings
import numpy as np
from PIL import Image
from yolo import YOLO
from deep_sort import preprocessing
from deep_sort.detection import Detection
from deep_sort.detection_yolo import Detection_YOLO
from importlib import import_module
from collections import Counter, deque
import datetime

warnings.filterwarnings('ignore')
pts = [deque(maxlen=30) for _ in range(9999)]
COLORS = np.random.randint(0, 255, size=(200, 3),
                           dtype="uint8")


class Camera(BaseCamera):
    def __init__(self, feed_type, device, port_list):
        super(Camera, self).__init__(feed_type, device, port_list)

    @staticmethod
    def yolo_frames(unique_name):
        device = unique_name[1]
        counter = []

        tracking = True

        if tracking:
            gdet = import_module('tools.generate_detections')
            nn_matching = import_module('deep_sort.nn_matching')
            Tracker = import_module('deep_sort.tracker').Tracker

            max_cosine_distance = 0.3
            nn_budget = None

            # deep_sort
            model_filename = 'model_data/mars-small128.pb'
            encoder = gdet.create_box_encoder(model_filename, batch_size=1)

            metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
            tracker = Tracker(metric)

        yolo = YOLO()
        nms_max_overlap = 1.0

        num_frames = 0

        get_feed_from = ('camera', device)

        current_date = datetime.datetime.now().date()
        count_dict = {}
        while True:
            cam_id, frame = BaseCamera.get_frame(get_feed_from)

            if frame is None:
                break

            num_frames += 1

            if num_frames % 2 != 0:
                continue

            image = Image.fromarray(frame[..., ::-1])  # convert bgr to rgb
            boxes, confidence, classes = yolo.detect_image(image)
            detections = []
            features = encoder(frame, boxes)

            detections = [Detection(bbox, confidence, cls, feature) for bbox, cls, confidence, feature in
                          zip(boxes, classes, confidence, features)]
            boxes = np.array([d.tlwh for d in detections])
            scores = np.array([d.confidence for d in detections])
            indices = preprocessing.non_max_suppression(boxes, nms_max_overlap, scores)
            detections = [detections[i] for i in indices]

            class_counter = Counter()

            if tracking:
                # Call the tracker
                tracker.predict()
                tracker.update(detections)

                track_count = int(0)
                index_i_ds = []

                for track in tracker.tracks:
                    if not track.is_confirmed() or track.time_since_update > 1:
                        continue
                    index_i_ds.append(int(track.track_id))
                    counter.append(int(track.track_id))
                    bbox = track.to_tlbr()
                    color = [int(c) for c in COLORS[index_i_ds[track_count] % len(COLORS)]]

                    cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 255, 255),
                                  1)  # WHITE BOX
                    cv2.putText(frame, "ID: " + str(track.track_id), (int(bbox[0]), int(bbox[1])), 0,
                                1.5e-3 * frame.shape[0], (0, 255, 0), 1)

                    track_count += 1

                    # Theo doi tracking
                    center = (int(((bbox[0]) + (bbox[2])) / 2), int(((bbox[1]) + (bbox[3])) / 2))
                    pts[track.track_id].append(center)
                    thickness = 5
                    cv2.circle(frame, center, 1, color, thickness)

                    for j in range(1, len(pts[track.track_id])):
                        if pts[track.track_id][j - 1] is None or pts[track.track_id][j] is None:
                            continue
                        thickness = int(np.sqrt(64 / float(j + 1)) * 2)
                        cv2.line(frame, (pts[track.track_id][j - 1]), (pts[track.track_id][j]), (color), thickness)

                cv2.putText(frame, "Current total count: " + str(track_count),
                            (int(20), int(60 * 5e-3 * frame.shape[0])), 0, 2e-3 * frame.shape[0],
                            (255, 255, 255), 2)

            det_count = int(0)
            for det in detections:
                bbox = det.to_tlbr()
                score = "%.2f" % (det.confidence * 100) + "%"
                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 0, 0),
                              1)
                if len(classes) > 0:
                    cls = det.cls
                    cv2.putText(frame, str(cls) + " " + score, (int(bbox[0]), int(bbox[3])), 0,
                                1.5e-3 * frame.shape[0], (0, 255, 0), 1)
                    class_counter[cls] += 1
                det_count += 1

            y = 80 * 5e-3 * frame.shape[0]
            for cls in class_counter:
                class_count = class_counter[cls]
                cv2.putText(frame, str(cls) + " " + str(class_count), (int(20), int(y)), 0, 2e-3 * frame.shape[0],
                            (255, 255, 255), 2)
                y += 20 * 5e-3 * frame.shape[0]

            # use YOLO counts if tracking is turned off
            if tracking:
                count = track_count
            else:
                count = det_count

            # if count > 0:
            #     print(count, "count")
            #     bordersize = 4
            #     frame = cv2.copyMakeBorder(
            #         frame,
            #         top=bordersize,
            #         bottom=bordersize,
            #         left=bordersize,
            #         right=bordersize,
            #         borderType=cv2.BORDER_REPLICATE,
            #         value=[255, 0, 0]
            #     )

            now = datetime.datetime.now()
            rounded_now = now - datetime.timedelta(microseconds=now.microsecond)
            current_minute = now.time().minute

            if current_minute == 0 and len(count_dict) > 1:
                count_dict = {}
            else:
                write_interval = 5
                if current_minute % write_interval == 0:
                    if current_minute not in count_dict:
                        count_dict[current_minute] = True
                        total_filename = 'Total counts for {}, camera {}.txt'.format(current_date, device)
                        total_count_file = open(total_filename, 'a')
                        print('Writing current total count ({}) to file.'.format(count))
                        total_count_file.write(str(rounded_now) + ", " + device + ', ' + str(count) + "\n")
                        total_count_file.close()

                        for cls in class_counter:
                            class_count = class_counter[cls]
                            class_filename = '{} counts for {}, camera {}.txt'.format(cls, current_date, device)
                            class_count_file = open(class_filename, 'a')
                            print('Writing current {} count ({}) to file.'.format(cls, class_count))
                            class_count_file.write(str(rounded_now) + ", " + device + ', ' + str(class_count) + "\n")
                            class_count_file.close()

            yield cam_id, frame, count
