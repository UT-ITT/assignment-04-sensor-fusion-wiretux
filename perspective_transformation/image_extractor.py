import cv2
import numpy as np
import argparse
import time

PROGRAMM_NAME = 'Image extractor'

# Parse the parameters with argparse
parser = argparse.ArgumentParser(prog=PROGRAMM_NAME, usage='%(prog)s [-i path] [-o path] [-r width height]')

parser.add_argument('-i', '--input', help='Path to the input file', required=True)
parser.add_argument('-o', '--output', help='Path to the output file', required=True)
parser.add_argument('-r', '--resolution', nargs=2, type=int, help='Output resolution in width height', required=True)

args = parser.parse_args()

output_path = args.output
res_w, res_h = args.resolution
input_img = cv2.imread(args.input)

# Make sure the input image is correct
if input_img is None:
    raise FileNotFoundError(f"The file {args.input} could not be found")

img = input_img.copy()
output = None

cv2.namedWindow(PROGRAMM_NAME)

points = []

def mouse_callback(event, x, y, flags, param):
    global img, points, res_w, res_h, input_img, output

    if event == cv2.EVENT_LBUTTONDOWN:

        if len(points) < 4:
            #If the points are below collect points
            points.append([x,y])
            img = cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
            cv2.imshow(PROGRAMM_NAME, img)

            if len(points) == 4:
                #If we collect enough points we do the transform
                points_mapping = [[0,0], [res_w - 1, 0], [res_w - 1, res_h - 1], [0, res_h - 1]]

                points_matrix = np.float32(points)
                points_mapping_matrix = np.float32(points_mapping)

                M = cv2.getPerspectiveTransform(points_matrix, points_mapping_matrix)
                output = cv2.warpPerspective(input_img.copy(), M, (res_w, res_h))
                cv2.imshow(PROGRAMM_NAME, output)


cv2.imshow(PROGRAMM_NAME, img)
cv2.setMouseCallback(PROGRAMM_NAME, mouse_callback)

while True:
    key = cv2.waitKey(0)

    if key == ord('s'):
        if output is None:
            print("There is no output yet")
        else:
            cv2.imwrite(output_path, output)
            print(f"Saved image to {output_path}")
    elif key == 27:
        #Reset on esc
        output = None
        img = input_img.copy()
        points.clear()
        cv2.imshow(PROGRAMM_NAME, img)
        print("All points deleted")
    elif key == ord('q'):
        break

    time.sleep(0.1)
