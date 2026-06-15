import cv2
import cv2.aruco as aruco
import numpy as np

# Board Size. Here: DIN A4
WIDTH = 3508
HEIGHT = 2480

# Size of the markers and margin around them
MARKER_SIZE = 400
MARGIN = 100

# Name of the output
OUTPUTNAME = 'game_board.png'

# Create white board of the size
board = np.ones((HEIGHT, WIDTH)) * 255

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)

# Create the markers
marker_0 = aruco.generateImageMarker(aruco_dict, 0, MARKER_SIZE)
marker_1 = aruco.generateImageMarker(aruco_dict, 1, MARKER_SIZE)
marker_2 = aruco.generateImageMarker(aruco_dict, 2, MARKER_SIZE)
marker_3 = aruco.generateImageMarker(aruco_dict, 3, MARKER_SIZE)

# Pre calc the positions (To make the code easier to read)
pos_bottom = HEIGHT - MARGIN
pos_top    = MARGIN
pos_left   = MARGIN
pos_right  = WIDTH - MARGIN

# id 0: Top right
board[pos_top : pos_top + MARKER_SIZE, pos_right - MARKER_SIZE : pos_right ] = marker_0

# id 1: Top left
board[pos_top : pos_top + MARKER_SIZE, pos_left : pos_left + MARKER_SIZE ]   = marker_1

# id 2: Bottom left
board[pos_bottom - MARKER_SIZE : pos_bottom, pos_left : pos_left + MARKER_SIZE ]   = marker_2

# id 3: Bottom right
board[pos_bottom - MARKER_SIZE : pos_bottom, pos_right - MARKER_SIZE : pos_right ] = marker_3

# Save the output
cv2.imwrite(OUTPUTNAME, board)
print(f"Board created and saved as {OUTPUTNAME} :D")
