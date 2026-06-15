import cv2
import numpy as np
import pyglet
from PIL import Image
import sys
import cv2.aruco as aruco
from DIPPID import SensorUDP

# use UPD (via WiFi) for communication
PORT = 5700
CAPTURE_TIMEOUT = 10

sensor = SensorUDP(PORT)

# If turned on the image is flipped to make playing easier
FLIP_CAMERA = True

DOT_RADIUS = 20

dot_pos = None
score = 0

video_id = 0

if len(sys.argv) > 1:
    video_id = int(sys.argv[1])

def cv2glet(img,fmt):
    '''Assumes image is in BGR color space. Returns a pyimg object'''
    if fmt == 'GRAY':
      rows, cols = img.shape
      channels = 1
    else:
      rows, cols, channels = img.shape

    raw_img = Image.fromarray(img).tobytes()

    top_to_bottom_flag = -1
    bytes_per_row = channels*cols
    pyimg = pyglet.image.ImageData(width=cols,
                   height=rows,
                   fmt=fmt,
                   data=raw_img,
                   pitch=top_to_bottom_flag*bytes_per_row)
    return pyimg

# aruco setup
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
aruco_params = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, aruco_params)

# Create a video capture object for the webcam
cap = cv2.VideoCapture(video_id)

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)

def get_center(marker):
    c = marker[0]
    cx = int(np.mean(c[:, 0]))
    cy = int(np.mean(c[:, 1]))
    return (cx,cy)

def get_ordered_marker_pos(markers, ids):
    centers = []

    for marker in markers:
        centers.append(get_center(marker))

    s = np.sum(centers, axis=1)
    d = np.diff(centers, axis=1).ravel()

    # Mapp to outer points
    top_left     = markers[np.argmin(s)][0][2]
    top_right    = markers[np.argmin(d)][0][3]
    bottom_right = markers[np.argmax(s)][0][0]
    bottom_left  = markers[np.argmax(d)][0][1]

    return np.float32([top_left, top_right, bottom_right, bottom_left])


velocity = np.array([0.0, 0.0])
prediction = None

alpha = 0

def update(delta):
    global velocity
    acc = sensor.get_value('accelerometer')
    if acc is not None:
        velocity = np.array([acc['x'] * delta, acc['z'] * delta]) * 10000

@window.event
def on_draw():
    window.clear()
    ret, frame = cap.read()
    if not ret:
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    markers, ids, _ = detector.detectMarkers(gray)

    cleaned_markers = []
    other_marker = None
    if ids is not None:
        flat_ids = ids.ravel()
        for i, marker in enumerate(markers):
            if flat_ids[i] in [0, 1, 2, 3]:
                cleaned_markers.append(marker)
            else:
                other_marker = marker

    detected_markers = ids is not None and len(cleaned_markers) == 4

    # Perspective Transformation
    if detected_markers:
        pos = get_ordered_marker_pos(cleaned_markers, ids)

        frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        points_mapping = [[0,0], [frame_width-1, 0], [frame_width-1, frame_height-1], [0, frame_height-1]]
        M = cv2.getPerspectiveTransform(pos, np.float32(points_mapping))

        frame = cv2.warpPerspective(frame, M, (frame_width, frame_height))

        if other_marker is not None:
            x,y = get_center(other_marker)

            base_m_pos = np.array([[[x, y]]], dtype=np.float32)
            m_pos = cv2.perspectiveTransform(base_m_pos, M)[0,0,:]

            cv2.circle(frame, [int(p) for p in m_pos], DOT_RADIUS, (0, 0, 255), -1)

            global prediction, velocity, alpha

            if prediction is None:
                prediction = m_pos

            prediction += velocity * 1/60.0
            prediction = alpha * prediction + (1 - alpha) * m_pos

            cv2.circle(frame, [int(p) for p in prediction], DOT_RADIUS, (0, 255, 0), -1)

    # Flip camera to make the game easier
    if FLIP_CAMERA:
        frame = cv2.flip(frame, 1)

    img = cv2glet(frame, 'BGR')
    img.blit(0, 0, 0)


# Allow the game to be quited with q
@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        print("Thank you for using this programm :D")
        window.close()

    global alpha
    if symbol == pyglet.window.key.UP or symbol == pyglet.window.key.RIGHT:
        alpha = alpha + 0.1

    if symbol == pyglet.window.key.DOWN or symbol == pyglet.window.key.LEFT:
        alpha = alpha - 0.1

def reset(is_pressed):
    global alpha, prediction
    alpha = 0
    prediction = np.array([0.0, 0.0])


sensor.register_callback('button_1', reset)

pyglet.clock.schedule_interval(update, 1 / 60.0)

pyglet.app.run()

