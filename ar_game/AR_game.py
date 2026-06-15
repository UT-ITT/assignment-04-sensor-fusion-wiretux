import cv2
import numpy as np
import pyglet
from PIL import Image
import sys
import cv2.aruco as aruco

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

def get_ordered_marker_pos(markers):
    centers = []

    for marker in markers:
        c = marker[0]
        cx = int(np.mean(c[:, 0]))
        cy = int(np.mean(c[:, 1]))
        centers.append((cx, cy))

    s = np.sum(centers, axis=1)
    d = np.diff(centers, axis=1).ravel()

    # Mapp to inner points
    top_left     = markers[np.argmin(s)][0][0]
    top_right    = markers[np.argmin(d)][0][1]
    bottom_right = markers[np.argmax(s)][0][2]
    bottom_left  = markers[np.argmax(d)][0][3]

    # Mapp to outer points
    #top_left     = markers[np.argmin(s)][0][2]
    #top_right    = markers[np.argmin(d)][0][3]
    #bottom_right = markers[np.argmax(s)][0][0]
    #bottom_left  = markers[np.argmax(d)][0][1]

    return np.float32([top_left, top_right, bottom_right, bottom_left])

# Sets the point position to a random position
def set_random_point(delta):
    global dot_pos
    x = np.random.randint(DOT_RADIUS, WINDOW_WIDTH - DOT_RADIUS)
    y = np.random.randint(DOT_RADIUS, WINDOW_HEIGHT - DOT_RADIUS)
    dot_pos = (x,y)

# Initalize the point directly
set_random_point(0)

def detect_finger(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Select the range of skin color only
    mask = cv2.inRange(hsv, np.array([0, 30, 60]), np.array([20, 150, 255]))

    # Improve the mask by bluring it
    mask = cv2.GaussianBlur(mask, (9, 9), 0)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Select the biggest contour
    maxContour = max(contours, key=cv2.contourArea)

    # Get the convex hull
    hull = cv2.convexHull(maxContour)

    # Visualize the contour detection
    #cv2.drawContours(frame, [hull], -1, (0, 255, 0), 2)

    # Get convex defects
    hull_indices = cv2.convexHull(maxContour, returnPoints=False)
    defects = cv2.convexityDefects(maxContour, hull_indices)

    if defects is None:
        return None

    # Select the first detected defect valley and get the coordinate of the finger tip
    s, _, _, _ = defects[0, 0]
    start = tuple(maxContour[s][0])

    return start

score_label = pyglet.text.Label('Score: 0',
                          font_name='Times New Roman',
                          font_size=24,
                          x=WINDOW_WIDTH//2, y= WINDOW_HEIGHT - 50,
                          anchor_x='center', anchor_y='top',
                          color=(0,0,0)
                          )

info_label = pyglet.text.Label('Please focus the play area \n with the markers again :)',
                          font_name='Times New Roman',
                          font_size=30,
                          x=window.width//2 + 50, y=window.height//2+50,
                          anchor_x='center', anchor_y='center',
                          color=(0,0,0),
                          multiline=True,
                          width = window.width - 50
                          )

@window.event
def on_draw():
    window.clear()
    ret, frame = cap.read()
    if not ret:
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    markers, ids, _ = detector.detectMarkers(gray)

    detected_markers = ids is not None and len(markers) == 4

    # Perspective Transformation
    if detected_markers:
        pos = get_ordered_marker_pos(markers)

        frame_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        points_mapping = [[0,0], [frame_width-1, 0], [frame_width-1, frame_height-1], [0, frame_height-1]]
        M = cv2.getPerspectiveTransform(pos, np.float32(points_mapping))

        frame = cv2.warpPerspective(frame, M, (frame_width, frame_height))

    # Flip camera to make the game easier
    if FLIP_CAMERA:
        frame = cv2.flip(frame, 1)

    # Game logic (draw point and detect finger)
    if detected_markers:
        global dot_pos, score, DOT_RADIUS

        finger_pos = detect_finger(frame)

        # Draw the dot to hit and the finger dot
        if dot_pos:
            cv2.circle(frame, dot_pos, DOT_RADIUS, (255, 0, 0), -1)

        if finger_pos:
            cv2.circle(frame, finger_pos, DOT_RADIUS, (0, 0, 255), -1)

        # Check if they overlapp
        if dot_pos and finger_pos:
            distance = np.hypot(finger_pos[0] - dot_pos[0], finger_pos[1] - dot_pos[1])
            if distance <= DOT_RADIUS:
                dot_pos = None
                score = score + 1
                score_label.text = f"Score: {score}"
                pyglet.clock.schedule_once(set_random_point, 2.0)
    img = cv2glet(frame, 'BGR')
    img.blit(0, 0, 0)

    # Draw the score label or info to show the paper
    if(detected_markers):
        score_label.draw()
    else:
        info_label.draw()

# Allow the game to be quited with q
@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.Q:
        print("Thank you for playing my game :D")
        window.close()

pyglet.app.run()

